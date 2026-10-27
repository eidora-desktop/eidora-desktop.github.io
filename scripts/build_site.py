"""Build a static Pages artifact; no browser JavaScript or third-party packages."""
import argparse
import hashlib
from html import escape
import json
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


def download_details(platform, *, checksums=False, release=None):
    parts = ['<div class="download-actions">']
    if "store_url" in platform:
        parts.append(f'<a class="download-link download-primary" href="{escape(platform["store_url"], quote=True)}">Microsoft Store</a>')
    else:
        for asset in platform["downloads"]:
            label = {"dmg": "DMG", "deb": "DEB"}.get(asset["format"], asset["format"])
            parts.append(
                f'<a class="download-link download-primary" href="{escape(asset["url"], quote=True)}" aria-label="Download {escape(asset["name"], quote=True)}">'
                f'Download {escape(label)}</a>'
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
        url = asset["url"] if asset else platform["store_url"]
        meta = escape(description)
        if asset:
            meta += f' · {asset["size"] / 1024**2:.1f}&nbsp;MiB'
        meta += f' · v{version}'
        return (
            f'<div class="prototype-option"><a class="prototype-button" href="{escape(url, quote=True)}" '
            f'aria-label="Download EIDORA {version} — {escape(label, quote=True)}">'
            f'{escape(label)}<span aria-hidden="true">↓</span></a><p class="prototype-option-meta">{meta}</p></div>'
        )

    parts.append('<div class="prototype-grid">')
    parts.append('<article class="prototype-card" aria-labelledby="prototype-macos"><h2 id="prototype-macos">macOS</h2>')
    parts.append('<div class="prototype-options">' + option("macos-arm64", "Apple Silicon (M-Series)", "DMG", "dmg") + option("macos-x86_64", "Intel (older Macs)", "DMG", "dmg") + '</div>')
    mac_requirements = {catalog["releases"][version]["platforms"][key]["requirements"]
                        for key in ("macos-arm64", "macos-x86_64") if (version := catalog["latest"][key])}
    parts.append(f'<div class="prototype-card-footer"><p>{escape(" · ".join(sorted(mac_requirements)) or "macOS 15 or later")}</p>')
    parts.append('<details class="prototype-help"><summary>Which Mac do I have?</summary><p>Open Apple menu → About This Mac. If “Chip” says Apple M-series, choose Apple Silicon. If “Processor” says Intel, choose Intel.</p></details></div></article>')

    parts.append('<article class="prototype-card prototype-card-pending" aria-labelledby="prototype-windows"><h2 id="prototype-windows">Windows</h2>')
    if catalog["latest"]["windows-x86_64"]:
        parts.append('<div class="prototype-options">' + option("windows-x86_64", "Microsoft Store", "Windows x64") + '</div>')
    else:
        parts.append('<div class="prototype-coming-soon"><span>Coming soon</span><p>No experimental Windows download yet.</p></div>')
    parts.append('<div class="prototype-card-footer"><p>Windows 10 or 11 · x64</p></div></article>')

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
        parts.append(f'<p class="prototype-note-date">{release["published_at"]} · {release["channel"].capitalize()}</p><p class="release-notes">{escape(release["notes"])}</p>')
        parts.append(f'<p><a href="https://github.com/eidora-desktop/EIDORA/releases/tag/v{version}">View this release on GitHub</a></p></div></details>')
    parts.append('</div><p class="prototype-public-link"><a href="/download/">Looking for a stable release?</a></p></div>')
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
<nav aria-label="Main navigation"><a href="/download/">Downloads</a><a href="/releases/">Releases</a></nav></header>
<main id="main" class="wrap release-page"><h1>{escape(heading or title)}</h1>{content}</main>
<footer class="site-footer wrap"><p>EIDORA · The Embedding Space Explorer</p><a href="https://github.com/eidora-desktop/EIDORA">Source code</a></footer>
</body></html>'''


def history(catalog, *, experimental=False):
    if not catalog["releases"]:
        if experimental:
            return '<p>No experimental installers have been posted yet. Builds and their release notes will appear here when available.</p>'
        return '<p>There are no public application releases yet. Downloads and release notes will appear here after publication.</p><p><a href="/download/">View platform availability</a></p>'
    parts = []
    for version in sorted(catalog["releases"], key=version_tuple, reverse=True):
        release = catalog["releases"][version]
        parts.append(f'<article class="release-entry" id="v{version}"><h2>EIDORA {version}</h2><p>{release["published_at"]} · {release["channel"].capitalize()}</p>')
        if release["channel"] in ("prototype", "preview"):
            parts.append(f'<p>{PROTOTYPE_NOTICE}</p>')
        parts.append(f'<p class="release-notes">{escape(release["notes"])}</p>')
        for key, platform in release["platforms"].items():
            parts.append(f'<section class="download-card history-platform"><h3>{PLATFORMS[key][0]}</h3>')
            parts.append(download_details(platform, checksums=True))
            if key == "windows-x86_64":
                parts.append('<p class="release-meta">Microsoft Store offers its current version; historical Windows packages are not hosted here.</p>')
            parts.append('</section>')
        parts.append('</article>')
    return "".join(parts)


def render_landing_downloads(index, catalog):
    """Replace a marked download section with catalog-generated cards, if present."""
    if START not in index and END not in index:
        return index
    if index.count(START) != 1 or index.count(END) != 1 or index.index(START) > index.index(END):
        raise ValueError("Keep exactly one ordered pair of EIDORA DOWNLOADS markers in index.html.")
    before, rest = index.split(START)
    _, after = rest.split(END)
    return before + START + cards(catalog) + '<p class="download-footnote"><a href="/download/">Installation and download details</a><a href="/releases/">Release history</a></p>' + END + after


def build(source=ROOT):
    source = Path(source)
    raw = (source / "updates.json").read_bytes()
    if len(raw) > MAX_CATALOG_BYTES:
        raise ValueError("The update catalog must remain below 1 MiB.")
    catalog = validate_catalog(json.loads(raw))
    public_catalog = catalog_for_channels(catalog, {"stable"})
    experimental_catalog = catalog_for_channels(catalog, {"prototype", "preview"})
    stylesheet_revision = hashlib.sha256((source / "release-pages.css").read_bytes()).hexdigest()[:12]
    index = render_landing_downloads((source / "index.html").read_text(), public_catalog)
    index = index.replace('href="release-pages.css"', f'href="release-pages.css?v={stylesheet_revision}"')
    output = source / "_site"
    if output.is_symlink():
        raise ValueError("The build output must not be a symlink.")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    for name in ("styles.css", "release-pages.css", "CNAME", "request-access.html", "EIDORA_logo.svg"):
        shutil.copyfile(source / name, output / name)
    shutil.copytree(source / "assets", output / "assets", ignore=shutil.ignore_patterns(".DS_Store", "*.md"))
    (output / "index.html").write_text(index)
    (output / "updates.json").write_text(json.dumps(public_catalog, indent=2, ensure_ascii=False) + "\n")
    (output / ".nojekyll").touch()
    content = '<p>Choose your operating system and architecture. Each platform shows the stable version currently available for it.</p>' + cards(public_catalog, checksums=True)
    content += '''<section class="installation"><h2>Installing and updating</h2>
<h3>Windows</h3><p>Install EIDORA from Microsoft Store when available. The Store manages subsequent updates.</p>
<h3>macOS</h3><p>Choose Apple Silicon or Intel to match your Mac. Quit EIDORA, open the downloaded DMG, and copy EIDORA into Applications, replacing the previous application when updating.</p>
<h3>Linux</h3><p>Use the DEB package on compatible Debian-based distributions, or the AppImage on supported Linux systems. Install a newer DEB over the previous package. For AppImage, quit EIDORA, replace the old file, and make the new file executable. Updates are downloaded manually.</p>
<p>Keep your project folders when replacing the application. Read each release's compatibility notes before opening existing projects.</p>
<p><a href="/releases/">Release notes and previous versions</a></p></section>'''
    experimental_content = experimental_downloads(experimental_catalog)
    for path, title, body in (("download", "Download EIDORA", content), ("releases", "EIDORA releases", history(public_catalog)), ("experimental", "Experimental builds", experimental_content)):
        directory = output / path
        directory.mkdir()
        (directory / "index.html").write_text(page(title, body, path, noindex=path == "experimental", stylesheet_revision=stylesheet_revision, heading="Download EIDORA" if path == "experimental" else None))
    return output


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(f"Built {build()}")
