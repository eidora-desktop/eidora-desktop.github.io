"""Prepare a Mac/Linux catalog entry from a published, public GitHub release.

This edits updates.json locally for review; it does not commit or deploy.
Windows Store availability must be confirmed separately (see RELEASES.md).
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
from urllib.request import Request, urlopen

from catalog import validate_catalog, version_tuple

ROOT = Path(__file__).resolve().parents[1]


def merge_release(catalog, release, version, key, requirements, channel):
    version_tuple(version)
    if (not isinstance(release, dict) or release.get("draft") is not False
            or release.get("tag_name") != f"v{version}" or not release.get("published_at")):
        raise ValueError("Expected the exact published, non-draft application release.")
    if release.get("prerelease") and channel == "stable":
        raise ValueError("A GitHub prerelease cannot be advertised as stable.")
    published_at = datetime.fromisoformat(release["published_at"].replace("Z", "+00:00")).date().isoformat()
    from copy import deepcopy
    result = deepcopy(catalog)
    record = result["releases"].get(version)
    metadata = {"published_at": published_at, "channel": channel, "notes": release.get("body") or ""}
    if record is None:
        record = result["releases"][version] = {**metadata, "platforms": {}}
    elif any(record.get(field) != value for field, value in metadata.items()):
        raise ValueError("Existing release metadata differs. Review it before adding another platform.")
    formats = ("dmg",) if key.startswith("macos-") else ("deb", "AppImage")
    downloads = []
    for extension in formats:
        name = f"EIDORA-{version}-{key}.{extension}"
        for asset in release.get("assets", []):
            if asset.get("name") != name:
                continue
            digest = asset.get("digest") or ""
            if asset.get("state") != "uploaded" or not digest.startswith("sha256:"):
                raise ValueError(f"Missing uploaded state or GitHub SHA-256 digest for {name}.")
            downloads.append({"format": extension, "name": name, "url": asset.get("browser_download_url"),
                              "size": asset.get("size"), "sha256": digest.removeprefix("sha256:")})
    existing = record["platforms"].get(key)
    if existing is not None and existing.get("downloads") != downloads:
        raise ValueError("Published installer contents changed. Prepare a new version instead.")
    record["platforms"][key] = {"requirements": requirements, "downloads": downloads}
    result["latest"][key] = version
    return validate_catalog(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--platform", choices=("macos-arm64", "macos-x86_64", "linux-x86_64"), required=True)
    parser.add_argument("--requirements", required=True, help="Verified OS/runtime requirements for this build")
    parser.add_argument("--channel", choices=("prototype", "preview", "stable"), required=True)
    args = parser.parse_args()
    version_tuple(args.version)
    request = Request(f"https://api.github.com/repos/eidora-desktop/EIDORA/releases/tags/v{args.version}",
                      headers={"Accept": "application/vnd.github+json", "User-Agent": "EIDORA-website-release-preparation"})
    with urlopen(request, timeout=30) as response:
        release = json.load(response)
    path = ROOT / "updates.json"
    catalog = merge_release(json.loads(path.read_text()), release, args.version, args.platform, args.requirements, args.channel)
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)
    print("Prepared updates.json. Review the diff and run the site tests/build before committing.")


if __name__ == "__main__":
    main()
