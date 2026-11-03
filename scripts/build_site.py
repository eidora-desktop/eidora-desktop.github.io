"""Build a static Pages artifact; no browser JavaScript or third-party packages."""
import argparse
import hashlib
from html import escape
import json
import re
from pathlib import Path
import shutil

from catalog import MAX_CATALOG_BYTES, PLATFORMS, validate_catalog, version_tuple

ROOT = Path(__file__).resolve().parents[1]
START = "<!-- EIDORA DOWNLOADS START -->"
END = "<!-- EIDORA DOWNLOADS END -->"
PROTOTYPE_NOTICE = "Experimental, untested prototype software. Builds may crash, lose data, or change without notice. Use only copies of your data and projects; do not rely on these builds for production work."
PLATFORM_REQUIREMENTS = {
    "macos-arm64": "macOS 15 or later",
    "macos-x86_64": "macOS 15 or later",
    "windows-x86_64": "Windows 10 or 11",
}


def action_icon(*, store=False):
    path = 'M14 3h7v7M21 3l-9 9M10 3H3v18h18v-7' if store else 'M12 3v12m-5-5 5 5 5-5M4 21h16'
    kind = 'open' if store else 'download'
    return (f'<svg class="action-icon action-icon-{kind}" width="18" height="18" viewBox="0 0 24 24" '
            f'fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{path}"/></svg>')


def store_app_url(platform):
    """Derive the native Store link from the catalog's validated product URL."""
    return 'ms-windows-store://pdp/?ProductId=' + platform["store_url"].rsplit('/', 1)[1]


def release_notes_html(notes):
    """Render our Markdown notes subset safely; preserve older plain-text notes."""
    if not re.search(r"^### ", notes, re.MULTILINE):
        return f'<p class="release-notes">{escape(notes)}</p>'

    def inline(text):
        parts = []
        cursor = 0
        for match in re.finditer(r"\*\*([^*\n]+)\*\*|\[([^\]\n]+)\]\((https://[^\s)]+)\)", text):
            parts.append(escape(text[cursor:match.start()]))
            if match.group(1):
                parts.append(f'<strong>{escape(match.group(1))}</strong>')
            else:
                parts.append(f'<a href="{escape(match.group(3), quote=True)}" target="_blank" rel="noopener noreferrer">{escape(match.group(2))}</a>')
            cursor = match.end()
        parts.append(escape(text[cursor:]))
        return ''.join(parts)

    parts = ['<div class="release-notes release-notes-formatted">']
    for block in re.split(r'\n\s*\n', notes.strip()):
        lines = block.splitlines()
        if len(lines) == 1 and block.startswith('### '):
            parts.append(f'<h3>{inline(block[4:])}</h3>')
        elif all(line.startswith('- ') for line in lines):
            parts.append('<ul>' + ''.join(f'<li>{inline(line[2:])}</li>' for line in lines) + '</ul>')
        else:
            parts.append(f'<p>{inline(block)}</p>')
    parts.append('</div>')
    return ''.join(parts)


def store_browser_link(platform):
    return f'<a class="store-browser-link" href="{escape(platform["store_url"], quote=True)}" target="_blank" rel="noopener noreferrer">open in browser</a>'


def store_installer_link(platform, *, css_class="download-link download-primary"):
    """Use Microsoft's product endpoint so the installer follows Store releases."""
    url = 'https://get.microsoft.com/installer/download/' + platform["store_url"].rsplit('/', 1)[1]
    return (f'<a class="{css_class}" href="{escape(url, quote=True)}" '
            f'aria-label="Download EIDORA Microsoft Store installer (.exe)">'
            f'Download installer (.exe){action_icon()}</a>')


def download_details(platform, *, checksums=False, release=None):
    parts = ['<div class="download-actions">']
    if "store_url" in platform:
        parts.append(f'<a class="download-link download-primary" href="{escape(store_app_url(platform), quote=True)}" aria-label="Open EIDORA in Microsoft Store">Microsoft Store{action_icon(store=True)}</a>')
        parts.append(store_browser_link(platform))
        parts.append(store_installer_link(platform))
    else:
        for asset in platform["downloads"]:
            label = {"dmg": "DMG", "deb": "DEB"}.get(asset["format"], asset["format"])
            parts.append(
                f'<a class="download-link download-primary" href="{escape(asset["url"], quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="Download {escape(asset["name"], quote=True)}">'
                f'Download {escape(label)}{action_icon()}</a>'
            )
    parts.append('</div><div class="download-details">')
    if release is not None:
        parts.append(f'<p class="release-meta">Version {release["version"]} · {release["published_at"]} · {release["channel"].capitalize()}</p>')
    parts.append(f'<p class="release-meta">{escape(platform["requirements"])}</p>')
    if "downloads" in platform:
        for asset in platform["downloads"]:
            label = {"dmg": "DMG", "deb": "DEB"}.get(asset["format"], asset["format"])
            parts.append(f'<div class="installer"><p class="release-meta">{escape(label)} · {asset["size"] / 1024**2:.1f}&nbsp;MiB</p>')
            if checksums:
                parts.append(f'<details class="checksum"><summary>SHA-256 checksum</summary><code>{asset["sha256"]}</code></details>')
            parts.append('</div>')
    parts.append('</div>')
    return "".join(parts)


def catalog_for_channels(catalog, channels):
    """Keep channel recommendations separate, falling back to the newest matching build."""
    releases = {version: release for version, release in catalog["releases"].items()
                if release["channel"] in channels}
    latest = {}
    for key, recommended in catalog["latest"].items():
        available = [version for version, release in releases.items() if key in release["platforms"]]
        latest[key] = recommended if recommended in available else max(available, key=version_tuple, default=None)
    return {"schema_version": catalog["schema_version"], "latest": latest, "releases": releases}


def update_feed(catalog):
    """Publish only explicitly recommended releases, regardless of their label."""
    versions = {version for version in catalog["latest"].values() if version is not None}
    return {"schema_version": catalog["schema_version"], "latest": dict(catalog["latest"]),
            "releases": {version: catalog["releases"][version] for version in sorted(versions, key=version_tuple)}}


def platform_card(catalog, key, *, checksums=False, experimental=False):
    version = catalog["latest"][key]
    parts = [f'<article class="download-card" id="{key}"><h3>{PLATFORMS[key][0]}</h3>']
    if version is None:
        parts.append('<div class="download-actions"><span class="download-pending">Not available yet</span></div><div class="download-details">')
        if key in PLATFORM_REQUIREMENTS:
            parts.append(f'<p class="release-meta">{escape(PLATFORM_REQUIREMENTS[key])}</p>')
        status = "No experimental build available yet" if experimental else "Public release coming soon"
        parts.append(f'<p class="release-meta">{status}</p></div>')
    else:
        release = catalog["releases"][version]
        parts.append(download_details(release["platforms"][key], checksums=checksums, release={**release, "version": version}))
        notes_path = "experimental" if experimental else "releases"
        parts.append(f'<a class="download-link" href="/{notes_path}/#v{version}">Release notes</a>')
    parts.append('</article>')
    return "".join(parts)


def cards(catalog, *, checksums=False, experimental=False):
    return '<div class="download-grid release-grid">' + "".join(platform_card(catalog, key, checksums=checksums, experimental=experimental) for key in PLATFORMS) + '</div>'


def landing_cards(catalog):
    """Keep one homepage card per OS, with architecture/format choices inside."""
    groups = (
        ("macOS", (("macos-arm64", "Apple Silicon (M-Series)", "dmg"),
                   ("macos-x86_64", "Intel (older Macs)", "dmg"))),
        ("Windows", (("windows-x86_64", "Microsoft Store", None),)),
        ("Linux", (("linux-x86_64", "AppImage", "AppImage"),
                   ("linux-x86_64", "DEB package", "deb"))),
    )
    parts = ['<div class="download-grid landing-download-grid">']
    for title, options in groups:
        parts.append(f'<article class="download-card"><div class="platform-heading"><h3>{title}</h3></div>')
        versions = sorted({catalog["latest"][key] for key, _, _ in options
                           if catalog["latest"][key]}, key=version_tuple, reverse=True)
        for version in versions:
            release = catalog["releases"][version]
            channel = release["channel"].capitalize()
            parts.append(f'<p class="release-meta">Version {version} · {release["published_at"]} · {channel}</p>')
        requirements = []
        for key, label, extension in options:
            version = catalog["latest"][key]
            platform = catalog["releases"][version]["platforms"][key] if version else None
            requirement = platform["requirements"] if platform else PLATFORM_REQUIREMENTS.get(key, "Linux x64")
            if requirement not in requirements:
                requirements.append(requirement)
            asset = next((item for item in platform.get("downloads", [])
                          if item["format"] == extension), None) if platform else None
            parts.append('<div class="installer">')
            if not platform or (extension and asset is None):
                parts.append(f'<span class="installer-label">{escape(label)}</span><span class="download-pending">Coming soon</span>')
            else:
                url = asset["url"] if asset else store_app_url(platform)
                target = ' target="_blank" rel="noopener noreferrer"' if asset else ''
                action_label = f"Download EIDORA {version} — {label}" if asset else "Open EIDORA in Microsoft Store"
                parts.append(f'<a class="download-link download-primary" href="{escape(url, quote=True)}"{target} aria-label="{escape(action_label, quote=True)}">{escape(label)}{action_icon(store=not asset)}</a>')
                meta = f'{asset["format"].upper() if extension != "AppImage" else "AppImage"} · {asset["size"] / 1024**2:.1f}&nbsp;MiB' if asset else "Windows x64"
                if len(versions) > 1:
                    meta += f' · v{version}'
                if not asset:
                    parts.append(f'<p class="release-meta installer-meta"><span>{meta}</span>{store_browser_link(platform)}</p>')
                else:
                    parts.append(f'<p class="release-meta">{meta}</p>')
            parts.append('</div>')
            if platform and "store_url" in platform:
                parts.append('<div class="installer">' + store_installer_link(platform) + '<p class="release-meta" title="Downloads EIDORA during installation.">Windows x64 · Web installer</p></div>')
        parts.append(f'<div class="download-card-footer"><p class="release-meta">{escape(" · ".join(requirements))}</p>')
        for version in versions:
            label = f"Release notes · {version}" if len(versions) > 1 else "Release notes"
            parts.append(f'<a class="download-link" href="/releases/#v{version}">{label}</a>')
        parts.append('</div></article>')
    parts.append('</div>')
    return "".join(parts)


def experimental_downloads(catalog):
    """Group choices by operating system, with technical information out of the way."""
    versions = {version for version in catalog["latest"].values() if version is not None}
    series = {version_tuple(version)[:2] for version in versions}
    parts = ['<div class="prototype-downloads">']
    if len(series) == 1:
        major, minor = next(iter(series))
        latest_version = max(versions, key=version_tuple)
        parts.append(f'<p class="prototype-version"><span class="prototype-badge">Experimental</span>{major}.{minor} series<a href="/experimental/#v{latest_version}">Release notes</a></p>')
    else:
        parts.append('<p class="prototype-version"><span class="prototype-badge">Experimental</span>Choose a download for your computer.</p>')
    parts.append('<p class="prototype-warning">This is untested prototype software. Use copies of your projects.</p>')

    def option(key, label, description, extension=None):
        version = catalog["latest"][key]
        platform = catalog["releases"][version]["platforms"][key] if version else None
        asset = next((item for item in platform.get("downloads", []) if item["format"] == extension), None) if platform else None
        if not platform or (extension and asset is None):
            return f'<div class="prototype-option"><span class="prototype-unavailable">{escape(label)}<span>Coming soon</span></span></div>'
        url = asset["url"] if asset else store_app_url(platform)
        target = ' target="_blank" rel="noopener noreferrer"' if asset else ''
        browser_link = store_browser_link(platform) if not asset else ''
        action_label = f"Download EIDORA {version} — {label}" if asset else "Open EIDORA in Microsoft Store"
        meta = escape(description)
        if asset:
            meta += f' · {asset["size"] / 1024**2:.1f}&nbsp;MiB'
        meta += f' · v{version}'
        return (
            f'<div class="prototype-option"><a class="prototype-button" href="{escape(url, quote=True)}"{target} '
            f'aria-label="{escape(action_label, quote=True)}">'
            f'{escape(label)}{action_icon(store=not asset)}</a><p class="prototype-option-meta">{meta}</p>{browser_link}</div>'
        )

    parts.append('<div class="prototype-grid">')
    parts.append('<article class="prototype-card" aria-labelledby="prototype-macos"><h2 id="prototype-macos">macOS</h2>')
    parts.append('<div class="prototype-options">' + option("macos-arm64", "Apple Silicon (M-Series)", "DMG", "dmg") + option("macos-x86_64", "Intel (older Macs)", "DMG", "dmg") + '</div>')
    mac_requirements = {catalog["releases"][version]["platforms"][key]["requirements"]
                        for key in ("macos-arm64", "macos-x86_64") if (version := catalog["latest"][key])}
    parts.append(f'<div class="prototype-card-footer"><p>{escape(" · ".join(sorted(mac_requirements)) or "macOS 15 or later")}</p>')
    parts.append('<details class="prototype-help"><summary>Which Mac do I have?</summary><p>Open Apple menu → About This Mac. If “Chip” says Apple M-series, choose Apple Silicon. If “Processor” says Intel, choose Intel.</p></details></div></article>')

    windows_version = catalog["latest"]["windows-x86_64"]
    windows_class = "prototype-card" if windows_version else "prototype-card prototype-card-pending"
    parts.append(f'<article class="{windows_class}" aria-labelledby="prototype-windows"><h2 id="prototype-windows">Windows</h2>')
    if catalog["latest"]["windows-x86_64"]:
        windows_platform = catalog["releases"][windows_version]["platforms"]["windows-x86_64"]
        parts.append('<div class="prototype-options">' + option("windows-x86_64", "Microsoft Store", "Windows x64")
                     + '<div class="prototype-option">' + store_installer_link(windows_platform, css_class="prototype-button")
                     + '<p class="prototype-option-meta" title="Downloads EIDORA during installation.">Windows x64 · Web installer</p></div></div>')
    else:
        parts.append('<div class="prototype-coming-soon"><span>Coming soon</span><p>No experimental Windows download yet.</p></div>')
    windows_requirement = catalog["releases"][windows_version]["platforms"]["windows-x86_64"]["requirements"] if windows_version else "Windows 10 or 11 · x64"
    parts.append(f'<div class="prototype-card-footer"><p>{escape(windows_requirement)}</p></div></article>')

    parts.append('<article class="prototype-card" id="linux-x86_64" aria-labelledby="prototype-linux"><h2 id="prototype-linux">Linux</h2>')
    parts.append('<div class="prototype-options">' + option("linux-x86_64", "AppImage", "Standalone app", "AppImage") + option("linux-x86_64", "DEB package", "Ubuntu / Debian package", "deb") + '</div>')
    linux_version = catalog["latest"]["linux-x86_64"]
    linux_requirement = catalog["releases"][linux_version]["platforms"]["linux-x86_64"]["requirements"] if linux_version else "Linux x64"
    parts.append(f'<div class="prototype-card-footer"><p>{escape(linux_requirement)}</p></div></article></div>')

    parts.append('<div class="prototype-extras"><details class="prototype-extra"><summary>Checksums &amp; compatibility</summary><div class="prototype-extra-body">')
    if not versions:
        parts.append('<p>No experimental installers have been posted yet.</p>')
    for key, version in catalog["latest"].items():
        if not version:
            continue
        platform = catalog["releases"][version]["platforms"][key]
        parts.append(f'<section class="prototype-technical"><h3>{PLATFORMS[key][0]} · v{version}</h3><p>{escape(platform["requirements"])}</p>')
        if key == "linux-x86_64":
            parts.append('<p>Native installation and other distributions remain unverified. Make the AppImage executable before running it; install the DEB with your package manager.</p>')
        for asset in platform.get("downloads", []):
            parts.append(f'<p class="prototype-filename">{escape(asset["name"])}</p><code>{asset["sha256"]}</code>')
        parts.append('</section>')
    parts.append('</div></details>')
    for version in sorted(catalog["releases"], key=version_tuple, reverse=True):
        release = catalog["releases"][version]
        parts.append(f'<details class="prototype-extra" id="v{version}"><summary>Release notes · {version}</summary><div class="prototype-extra-body">')
        parts.append(f'<p class="prototype-note-date">{release["published_at"]} · {release["channel"].capitalize()}</p>' + release_notes_html(release["notes"]))
        parts.append(f'<p><a href="https://github.com/eidora-desktop/EIDORA/releases/tag/v{version}" target="_blank" rel="noopener noreferrer">View this release on GitHub</a></p></div></details>')
    parts.append('</div><p class="prototype-public-link"><a href="/#downloads">Back to current downloads</a></p></div>')
    return "".join(parts)


def page(title, content, path, *, noindex=False, stylesheet_revision="", heading=None):
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — EIDORA</title>
{robots}
<link rel="canonical" href="https://www.eidora.org/{path}/">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/release-pages.css?v={stylesheet_revision}">
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header wrap"><a class="brand" href="/" aria-label="EIDORA home">
<img class="brand-icon" src="/assets/brand/eidora_icon.svg" alt="" width="44" height="44">
<img class="wordmark" src="/assets/brand/eidora_wordmark.svg" alt="EIDORA" width="136" height="24"></a>
<nav aria-label="Main navigation"><a href="/#downloads">Downloads</a><a href="/releases/">Releases</a></nav></header>
<main id="main" class="wrap release-page"><h1>{escape(heading or title)}</h1>{content}</main>
<footer class="site-footer wrap"><p>EIDORA · The Embedding Space Explorer</p><a href="https://github.com/eidora-desktop/EIDORA" target="_blank" rel="noopener noreferrer">Source code</a></footer>
</body></html>'''


def history(catalog, *, experimental=False):
    if not catalog["releases"]:
        if experimental:
            return '<p>No experimental installers have been posted yet. Builds and their release notes will appear here when available.</p>'
        return '<p>There are no published releases yet. Downloads and release notes will appear here after publication.</p><p><a href="/#downloads">View platform availability</a></p>'
    parts = []
    for version in sorted(catalog["releases"], key=version_tuple, reverse=True):
        release = catalog["releases"][version]
        parts.append(f'<article class="release-entry" id="v{version}"><h2>EIDORA {version}</h2><p>{release["published_at"]} · {release["channel"].capitalize()}</p>')
        if release["channel"] in ("prototype", "preview"):
            parts.append(f'<p>{PROTOTYPE_NOTICE}</p>')
        parts.append(release_notes_html(release["notes"]))
        for key, platform in release["platforms"].items():
            parts.append(f'<section class="download-card history-platform"><h3>{PLATFORMS[key][0]}</h3>')
            parts.append(download_details(platform, checksums=True))
            if key == "windows-x86_64":
                parts.append('<p class="release-meta">Microsoft Store offers its current version; historical Windows packages are not hosted here.</p>')
            parts.append('</section>')
        parts.append('</article>')
    return "".join(parts)


def render_landing_downloads(index, catalog, experimental_catalog=None):
    """Replace a marked download section with catalog-generated cards, if present."""
    if START not in index and END not in index:
        return index
    if index.count(START) != 1 or index.count(END) != 1 or index.index(START) > index.index(END):
        raise ValueError("Keep exactly one ordered pair of EIDORA DOWNLOADS markers in index.html.")
    before, rest = index.split(START)
    _, after = rest.split(END)
    if not any(catalog["latest"].values()) and experimental_catalog and any(experimental_catalog["latest"].values()):
        downloads = landing_cards(experimental_catalog)
    else:
        downloads = landing_cards(catalog)
    downloads += '<p class="download-footnote"><a href="/releases/">Release notes, checksums, and installation details</a></p>'
    return before + START + downloads + END + after


def build(source=ROOT):
    source = Path(source)
    raw = (source / "updates.json").read_bytes()
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("The update catalog must remain below 1 MiB.")
    catalog = validate_catalog(json.loads(raw))
    public_catalog = catalog_for_channels(catalog, {"stable"})
    experimental_catalog = catalog_for_channels(catalog, {"prototype", "preview"})
    stylesheet_revision = hashlib.sha256((source / "release-pages.css").read_bytes()).hexdigest()[:12]
    index = render_landing_downloads((source / "index.html").read_text(), public_catalog, experimental_catalog)
    index = index.replace('href="release-pages.css"', f'href="release-pages.css?v={stylesheet_revision}"')
    output = source / "_site"
    if output.is_symlink():
        raise ValueError("The build output must not be a symlink.")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for name in ("styles.css", "release-pages.css", "CNAME", "EIDORA_logo.svg"):
        shutil.copyfile(source / name, output / name)
    shutil.copytree(source / "assets", output / "assets", ignore=shutil.ignore_patterns(".DS_Store", "*.md"))
    (output / "index.html").write_text(index)
    (output / "updates.json").write_text(json.dumps(update_feed(catalog), indent=2, ensure_ascii=False) + "\n")
    (output / ".nojekyll").touch()
    installation = '''<section class="installation" id="installation"><h2>Installing and updating</h2>
<h3>Windows</h3><p>Open Microsoft Store or choose Download installer (.exe) to download Microsoft's EIDORA installer directly, without visiting the Store website. The installer downloads the current version available to your device from Microsoft Store; the Store manages subsequent updates for both options.</p>
<p>The downloaded installer can work when only the Store app is blocked. It still requires access to Microsoft's installation services and may be restricted by your university's IT policies.</p>
<h3>macOS</h3><p>Choose Apple Silicon or Intel to match your Mac. Quit EIDORA, open the downloaded DMG, and copy EIDORA into Applications, replacing the previous application when updating.</p>
<h3>Linux</h3><p>Use the DEB package on compatible Debian-based distributions, or the AppImage on supported Linux systems. Install a newer DEB over the previous package. For AppImage, quit EIDORA, replace the old file, and make the new file executable. Updates are downloaded manually.</p>
<p>Keep your project folders when replacing the application. Read each release's compatibility notes before opening existing projects.</p>
<p><a href="/#downloads">Back to current downloads</a></p></section>'''
    release_content = '<p>Release notes and downloads for published versions, including prototypes and previews labelled by release type. <a href="#installation">Installing and updating</a></p>' + history(catalog) + installation
    experimental_content = experimental_downloads(experimental_catalog)
    for path, title, body in (("releases", "EIDORA releases", release_content), ("experimental", "Experimental builds", experimental_content)):
        directory = output / path
        directory.mkdir()
        (directory / "index.html").write_text(page(title, body, path, noindex=path == "experimental", stylesheet_revision=stylesheet_revision, heading="Download EIDORA" if path == "experimental" else None))
    (output / "download").mkdir()
    (output / "download/index.html").write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Downloads — EIDORA</title>
<meta http-equiv="refresh" content="0; url=/#downloads">
<link rel="canonical" href="https://www.eidora.org/#downloads">
</head><body><p>Downloads have moved to the homepage. <a href="/#downloads">Go to EIDORA downloads</a>.</p></body></html>''')
    return output


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(f"Built {build()}")
