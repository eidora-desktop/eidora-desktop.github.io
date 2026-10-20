"""Validate the public release contract before building or deploying the site."""
from datetime import date
import re

PLATFORMS = {
    "macos-arm64": ("macOS · Apple Silicon", ("dmg",)),
    "macos-x86_64": ("macOS · Intel", ("dmg",)),
    "windows-x86_64": ("Windows · x64", ()),
    "linux-x86_64": ("Linux · x64", ("deb", "AppImage")),
}
REPOSITORY = "https://github.com/eidora-desktop/EIDORA"
MAX_CATALOG_BYTES = 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def version_tuple(value):
    require(isinstance(value, str) and re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value),
            "Versions must use MAJOR.MINOR.PATCH without a v prefix.")
    return tuple(int(part) for part in value.split("."))


def text(value, field, limit=20000):
    require(isinstance(value, str) and bool(value.strip()) and len(value) <= limit,
            f"{field} must be nonempty text of at most {limit} characters.")


def validate_catalog(catalog):
    require(isinstance(catalog, dict), "The catalog must be an object.")
    require(type(catalog.get("schema_version")) is int and catalog["schema_version"] == 1,
            "Unsupported schema_version.")
    latest, releases = catalog.get("latest"), catalog.get("releases")
    require(isinstance(latest, dict) and set(latest) == set(PLATFORMS), "latest must list all four platforms.")
    require(isinstance(releases, dict), "releases must be an object keyed by version.")
    for version, release in releases.items():
        version_tuple(version)
        require(isinstance(release, dict), f"Release {version} must be an object.")
        require(release.get("channel") in ("prototype", "preview", "stable"), "Invalid release channel.")
        published = release.get("published_at")
        require(isinstance(published, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", published), "Invalid publication date.")
        require(date.fromisoformat(published) <= date.today(), "A release cannot have a future publication date.")
        text(release.get("notes"), "notes")
        platforms = release.get("platforms")
        require(isinstance(platforms, dict) and platforms and set(platforms) <= set(PLATFORMS), "Invalid release platforms.")
        for key, platform in platforms.items():
            require(isinstance(platform, dict), "Each platform must be an object.")
            text(platform.get("requirements"), "requirements", 1000)
            if key == "windows-x86_64":
                url = platform.get("store_url")
                require(isinstance(url, str) and re.fullmatch(r"https://apps\.microsoft\.com/detail/[A-Za-z0-9]+", url),
                        "Windows requires a verified Microsoft Store product URL.")
                require("downloads" not in platform, "Windows is distributed through Microsoft Store only.")
                continue
            downloads = platform.get("downloads")
            require(isinstance(downloads, list) and downloads, "Each available Mac/Linux platform needs downloads.")
            formats = set()
            for download in downloads:
                require(isinstance(download, dict), "Each download must be an object.")
                extension = download.get("format")
                require(extension in PLATFORMS[key][1] and extension not in formats, "Invalid or duplicate download format.")
                formats.add(extension)
                name = f"EIDORA-{version}-{key}.{extension}"
                require(download.get("name") == name, "Asset name must match its version, platform, and format.")
                require(download.get("url") == f"{REPOSITORY}/releases/download/v{version}/{name}",
                        "Downloads must use exact versioned assets in the official EIDORA repository.")
                size = download.get("size")
                require(type(size) is int and 0 < size < 2 * 1024**3, "Invalid release asset size.")
                digest = download.get("sha256")
                require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), "Invalid SHA-256 checksum.")
    for key, version in latest.items():
        if version is not None:
            version_tuple(version)
            require(version in releases and key in releases[version]["platforms"],
                    f"Recommended release for {key} must actually contain that platform.")
    return catalog
