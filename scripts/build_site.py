"""Build a static Pages artifact; no browser JavaScript or third-party packages."""
import argparse
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


def page(title, content, path, *, noindex=False):
    robots = '<meta name="robots" content="noindex, nofollow">' if noindex else ""
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — EIDORA</title>
{robots}
<link rel="canonical" href="https://www.eidora.org/{path}/">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/brand/favicon-32.png">
<link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/release-pages.css">
</head><body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header wrap"><a class="brand" href="/" aria-label="EIDORA home">
<img class="brand-icon" src="/assets/brand/eidora_icon.svg" alt="" width="44" height="44">
<img class="wordmark" src="/assets/brand/eidora_wordmark.svg" alt="EIDORA" width="136" height="24"></a>
<nav aria-label="Main navigation"><a href="/download/">Downloads</a><a href="/releases/">Releases</a></nav></header>
<main id="main" class="wrap release-page"><h1>{escape(title)}</h1>{content}</main>
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
    index = render_landing_downloads((source / "index.html").read_text(), public_catalog)
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
    experimental_content = f'''<p>Early builds for people who want to try EIDORA while it is still in development.</p>
<aside class="experimental-notice" aria-labelledby="experimental-warning"><h2 id="experimental-warning">Before you download</h2>
<p>{PROTOTYPE_NOTICE}</p></aside>
<p>Choose your platform below. Check the requirements and release notes for each build before installing.</p>'''
    experimental_content += cards(experimental_catalog, checksums=True, experimental=True)
    experimental_content += '<section class="installation" aria-labelledby="experimental-notes"><h2 id="experimental-notes">Experimental release notes</h2>' + history(experimental_catalog, experimental=True) + '</section>'
    experimental_content += '<p><a href="/download/">View public release availability</a></p>'
    for path, title, body in (("download", "Download EIDORA", content), ("releases", "EIDORA releases", history(public_catalog)), ("experimental", "Experimental builds", experimental_content)):
        directory = output / path
        directory.mkdir()
        (directory / "index.html").write_text(page(title, body, path, noindex=path == "experimental"))
    return output


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(f"Built {build()}")
