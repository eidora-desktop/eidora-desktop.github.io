from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import END, START, build, catalog_for_channels, download_details, experimental_downloads, render_landing_downloads, update_feed
from catalog import PLATFORMS, REPOSITORY, validate_catalog
from prepare_release import merge_release


def sample():
    key, version = "macos-arm64", "0.2.0"
    name = f"EIDORA-{version}-{key}.dmg"
    return {"schema_version": 1, "latest": {**dict.fromkeys(PLATFORMS), key: version}, "releases": {
        version: {"channel": "prototype", "published_at": "2026-01-01", "notes": "First release <script>alert(1)</script>",
                  "platforms": {key: {"requirements": "Verified test requirement", "downloads": [{
                      "format": "dmg", "name": name, "url": f"{REPOSITORY}/releases/download/v{version}/{name}",
                      "size": 1000000, "sha256": "a" * 64,
                  }]}}}}}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls, self.ids = [], set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.urls.append(attrs[key])


class SiteTests(unittest.TestCase):
    def test_markdown_release_notes_render_safe_html(self):
        from build_site import release_notes_html
        notes = 'Intro\n\n### Changes\n\n- **GPU support**\n- [Store](https://apps.microsoft.com/detail/TEST)\n\n<script>alert(1)</script> [unsafe](javascript:alert(1))'
        rendered = release_notes_html(notes)
        self.assertIn('<h3>Changes</h3>', rendered)
        self.assertIn('<ul><li><strong>GPU support</strong></li>', rendered)
        self.assertIn('href="https://apps.microsoft.com/detail/TEST"', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('href="javascript:', rendered)
        catalog = json.loads((ROOT / 'updates.json').read_text())
        old = 'Plain-text release notes\n\nChanges\n\n- A fix with <escaped> text.'
        from html import escape
        self.assertEqual(release_notes_html(old), f'<p class="release-notes">{escape(old)}</p>')
        current = release_notes_html(catalog['releases']['0.2.6']['notes'])
        self.assertNotIn('### ', current)
        self.assertNotIn('**', current)
        self.assertIn('<h3>Validation</h3>', current)

    def test_optional_download_section_and_marker_validation(self):
        plain_page = '<main><a href="/download/">Downloads</a></main>'
        self.assertEqual(render_landing_downloads(plain_page, sample()), plain_page)
        landing = f'<main>{START}<p>Old download cards</p>{END}</main>'
        rendered = render_landing_downloads(landing, sample())
        self.assertNotIn("Old download cards", rendered)
        self.assertIn("Version 0.2.0", rendered)
        self.assertEqual(rendered.count('<article class="download-card">'), 3)
        for heading in ("macOS", "Windows", "Linux"):
            self.assertIn(f'<h3>{heading}</h3>', rendered)
        self.assertIn('>Apple Silicon (M-Series)<svg class="action-icon action-icon-download"', rendered)
        self.assertTrue(rendered.startswith("<main>" + START))
        self.assertTrue(rendered.endswith(END + "</main>"))
        for malformed in (START, END, END + START, START + START + END):
            with self.subTest(markers=malformed), self.assertRaises(ValueError):
                render_landing_downloads(malformed, sample())

    def test_empty_catalog_does_not_claim_a_release(self):
        validate_catalog(json.loads((ROOT / "updates.json").read_text()))

    def test_bad_catalogs_cannot_publish(self):
        mutations = [
            lambda c: c.update(schema_version=True),
            lambda c: c["latest"].update({"linux-x86_64": "0.3.0"}),
            lambda c: c["releases"]["0.2.0"].update(published_at="2099-01-01"),
            lambda c: c["releases"]["0.2.0"]["platforms"]["macos-arm64"]["downloads"][0].update(url="https://example.org/download"),
            lambda c: c["releases"]["0.2.0"]["platforms"]["macos-arm64"]["downloads"][0].update(sha256="bad"),
        ]
        for mutate in mutations:
            data = sample()
            mutate(data)
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_catalog(data)

    def test_store_publication_is_independent(self):
        data = sample()
        data["releases"]["0.1.0"] = {"channel": "prototype", "published_at": "2025-12-01", "notes": "Previous release", "platforms": {
            "windows-x86_64": {"requirements": "Test requirement", "store_url": "https://apps.microsoft.com/detail/TEST123"},
        }}
        data["latest"]["windows-x86_64"] = "0.1.0"
        validate_catalog(data)
        data["releases"]["0.1.0"]["platforms"]["windows-x86_64"]["downloads"] = []
        with self.assertRaises(ValueError):
            validate_catalog(data)

    def test_store_links_preserve_website_and_offer_native_windows_app(self):
        data = sample()
        platform = {"requirements": "Windows x64", "store_url": "https://apps.microsoft.com/detail/9P0WFNT5DZS5"}
        data["latest"]["windows-x86_64"] = "0.2.0"
        data["releases"]["0.2.0"]["platforms"]["windows-x86_64"] = platform
        for rendered in (experimental_downloads(data), download_details(platform), render_landing_downloads(START + END, data)):
            self.assertIn('href="https://apps.microsoft.com/detail/9P0WFNT5DZS5" target="_blank" rel="noopener noreferrer"', rendered)
            self.assertIn('href="ms-windows-store://pdp/?ProductId=9P0WFNT5DZS5"', rendered)
            self.assertIn('Microsoft Store', rendered)
            self.assertIn('open in browser</a>', rendered)
            self.assertIn('href="https://get.microsoft.com/installer/download/9P0WFNT5DZS5"', rendered)
            self.assertIn('Download installer (.exe)<svg class="action-icon action-icon-download"', rendered)
            self.assertNotIn('href="ms-windows-store://pdp/?ProductId=9P0WFNT5DZS5" target="_blank"', rendered)
        mac_only = experimental_downloads(sample())
        self.assertNotIn('open in browser', mac_only)
        self.assertNotIn('ms-windows-store:', mac_only)
        self.assertNotIn('get.microsoft.com/installer/download/', mac_only)

    def test_import_accepts_published_prototype_but_rejects_drafts(self):
        data = sample()
        asset = data["releases"]["0.2.0"]["platforms"]["macos-arm64"]["downloads"][0]
        release = {"tag_name": "v0.2.0", "draft": False, "prerelease": True,
                   "published_at": "2026-01-01T12:00:00Z", "body": "Notes", "assets": [{
                       "name": asset["name"], "state": "uploaded", "digest": "sha256:" + asset["sha256"],
                       "browser_download_url": asset["url"], "size": asset["size"],
                   }]}
        empty = {"schema_version": 1, "latest": dict.fromkeys(PLATFORMS), "releases": {}}
        merged = merge_release(empty, release, "0.2.0", "macos-arm64", "Test requirement", "prototype")
        self.assertEqual(merged["latest"]["macos-arm64"], "0.2.0")
        self.assertIsNone(merged["latest"]["windows-x86_64"])
        self.assertEqual(empty["releases"], {})
        release["assets"][0]["digest"] = "sha256:" + "b" * 64
        with self.assertRaisesRegex(ValueError, "contents changed"):
            merge_release(merged, release, "0.2.0", "macos-arm64", "Test requirement", "prototype")
        release["draft"] = True
        with self.assertRaises(ValueError):
            merge_release(empty, release, "0.2.0", "macos-arm64", "Test requirement", "prototype")

    def test_generated_pages_and_local_links(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            for name in ("index.html", "styles.css", "release-pages.css", "CNAME", "EIDORA_logo.svg"):
                shutil.copyfile(ROOT / name, source / name)
            shutil.copytree(ROOT / "assets", source / "assets")
            (source / "updates.json").write_text(json.dumps(sample()))
            output = build(source)
            self.assertEqual(json.loads((output / "updates.json").read_text()), sample())
            landing = (output / "index.html").read_text()
            self.assertIn("· Prototype</p>", landing)
            self.assertIn('href="/releases/#v0.2.0"', landing)
            self.assertIn(sample()["releases"]["0.2.0"]["platforms"]["macos-arm64"]["downloads"][0]["url"], landing)
            self.assertNotIn("0.2.0", (output / "download/index.html").read_text())
            history = (output / "releases/index.html").read_text()
            self.assertIn("EIDORA 0.2.0", history)
            self.assertIn("Prototype", history)
            self.assertIn("&lt;script&gt;", history)
            self.assertNotIn("<script>", history)
            self.assertIn('id="installation"', history)
            redirect = (output / "download/index.html").read_text()
            self.assertIn('http-equiv="refresh" content="0; url=/#downloads"', redirect)
            self.assertFalse((output / "request-access.html").exists())
            experimental = (output / "experimental/index.html").read_text()
            self.assertIn("&lt;script&gt;", experimental)
            self.assertNotIn("<script>", experimental)
            self.assertIn("untested prototype software", experimental)
            self.assertIn('<meta name="robots" content="noindex, nofollow">', experimental)
            self.assertIn('href="/experimental/#v0.2.0"', experimental)
            self.assertIn('href="/experimental/"', (output / "index.html").read_text())
            self.assertNotIn("scripts", [p.name for p in output.iterdir()])
            for path in output.rglob("*.html"):
                document = Links()
                document.feed(path.read_text())
                for url in document.urls:
                    parsed = urlsplit(url)
                    if parsed.scheme or parsed.netloc:
                        continue
                    target = (output / parsed.path.lstrip("/") if parsed.path.startswith("/") else path.parent / parsed.path) if parsed.path else path
                    if target.is_dir():
                        target /= "index.html"
                    self.assertTrue(target.is_file(), f"{path}: missing {url}")
                    if parsed.fragment and target.suffix == ".html":
                        other = Links()
                        other.feed(target.read_text())
                        self.assertIn(parsed.fragment, other.ids, f"{path}: missing anchor {url}")
            initial = (output / "index.html").read_bytes()
            build(source)
            self.assertEqual(initial, (output / "index.html").read_bytes())

    def test_linux_patch_keeps_mac_version_and_displays_matching_downloads(self):
        original = sample()
        assets = []
        for extension in ("deb", "AppImage"):
            name = f"EIDORA-0.2.1-linux-x86_64.{extension}"
            assets.append({"name": name, "state": "uploaded", "digest": "sha256:" + "b" * 64,
                           "size": 2000000, "browser_download_url": f"{REPOSITORY}/releases/download/v0.2.1/{name}"})
        release = {"tag_name": "v0.2.1", "draft": False, "prerelease": True,
                   "published_at": "2026-01-02T12:00:00Z", "body": "Linux patch", "assets": assets}
        catalog = merge_release(original, release, "0.2.1", "linux-x86_64", "Linux test requirement", "prototype")
        self.assertEqual(catalog["latest"]["macos-arm64"], "0.2.0")
        self.assertEqual(catalog["latest"]["linux-x86_64"], "0.2.1")
        self.assertEqual(catalog["releases"]["0.2.0"], original["releases"]["0.2.0"])
        rendered = experimental_downloads(catalog)
        self.assertIn('class="prototype-badge">Experimental</span>', rendered)
        self.assertIn('0.2 series', rendered)
        self.assertIn('href="/experimental/#v0.2.1"', rendered)
        self.assertIn(' · v0.2.0', rendered)
        self.assertIn('aria-label="Download EIDORA 0.2.0 — Apple Silicon (M-Series)"', rendered)
        self.assertIn('aria-label="Download EIDORA 0.2.1 — AppImage"', rendered)
        self.assertIn('aria-label="Download EIDORA 0.2.1 — DEB package"', rendered)
        linux = rendered.split('id="linux-x86_64"', 1)[1].split('</article>', 1)[0]
        self.assertEqual(linux.count(' · v0.2.1'), 2)
        self.assertNotIn('v0.2.0', linux)
        for asset in assets:
            self.assertIn(asset["browser_download_url"], linux)
        self.assertNotIn('0.2.1', json.dumps(catalog_for_channels(catalog, {"stable"})))

    def test_update_feed_uses_explicit_recommendations_independently_of_homepage(self):
        data = sample()
        for version, channel in (("0.1.0", "stable"), ("0.3.0", "preview")):
            record = json.loads(json.dumps(data["releases"]["0.2.0"]).replace("0.2.0", version))
            record.update(channel=channel, notes=f"Notes for {version}")
            data["releases"][version] = record
        data["latest"]["macos-arm64"] = "0.3.0"
        validate_catalog(data)
        public = catalog_for_channels(data, {"stable"})
        experimental = catalog_for_channels(data, {"prototype", "preview"})
        self.assertEqual(public["latest"]["macos-arm64"], "0.1.0")
        self.assertEqual(set(public["releases"]), {"0.1.0"})
        self.assertEqual(experimental["latest"]["macos-arm64"], "0.3.0")
        self.assertEqual(set(experimental["releases"]), {"0.2.0", "0.3.0"})
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            for name in ("index.html", "styles.css", "release-pages.css", "CNAME", "EIDORA_logo.svg"):
                shutil.copyfile(ROOT / name, source / name)
            shutil.copytree(ROOT / "assets", source / "assets")
            (source / "updates.json").write_text(json.dumps(data))
            output = build(source)
            for name in ("index.html",):
                rendered = (output / name).read_text()
                self.assertIn("0.1.0", rendered)
                self.assertNotIn("0.2.0", rendered)
                self.assertNotIn("0.3.0", rendered)
            releases = (output / "releases/index.html").read_text()
            for version in ("0.1.0", "0.2.0", "0.3.0"):
                self.assertIn(f'id="v{version}"', releases)
            self.assertIn("Prototype", releases)
            self.assertIn("Preview", releases)
            feed = json.loads((output / "updates.json").read_text())
            self.assertEqual(feed, update_feed(data))
            self.assertEqual(feed["latest"]["macos-arm64"], "0.3.0")
            self.assertEqual(set(feed["releases"]), {"0.3.0"})
            data["latest"]["macos-arm64"] = "0.2.0"
            self.assertEqual(set(update_feed(data)["releases"]), {"0.2.0"})
            rendered = (output / "experimental/index.html").read_text()
            self.assertIn("0.2.0", rendered)
            self.assertIn("0.3.0", rendered)
            self.assertNotIn("0.1.0", rendered)

    def test_published_feed_recommends_027_for_every_platform(self):
        catalog = validate_catalog(json.loads((ROOT / "updates.json").read_text()))
        feed = validate_catalog(update_feed(catalog))
        self.assertEqual(feed["latest"], dict.fromkeys(PLATFORMS, "0.2.7"))
        self.assertEqual(set(catalog["releases"]), {"0.2.6", "0.2.7"})
        self.assertEqual(set(feed["releases"]), {"0.2.7"})
        self.assertEqual(feed["releases"]["0.2.7"]["channel"], "prototype")
        self.assertEqual(set(feed["releases"]["0.2.7"]["platforms"]), set(PLATFORMS))
        self.assertEqual(set(catalog["releases"]["0.2.6"]["platforms"]), set(PLATFORMS))

    def test_website_history_starts_at_026(self):
        from build_site import history
        catalog = validate_catalog(json.loads((ROOT / "updates.json").read_text()))
        for experimental in (False, True):
            page = history(catalog, experimental=experimental)
            for version in ("0.2.4", "0.2.5"):
                self.assertNotIn(f"/download/v{version}/", page)
                self.assertNotIn(f"EIDORA-{version}-", page)
                self.assertNotIn(f'id="v{version}"', page)
        self.assertNotIn("EIDORA-0.2.4-", (ROOT / "index.html").read_text())

    def test_empty_experimental_catalog_is_explicit(self):
        from build_site import cards, history
        empty = {"schema_version": 1, "latest": dict.fromkeys(PLATFORMS), "releases": {}}
        self.assertIn("No experimental installers have been posted yet", history(empty, experimental=True))
        rendered = cards(empty, experimental=True)
        self.assertEqual(rendered.count("No experimental build available yet"), len(PLATFORMS))
        self.assertNotIn('class="download-link"', rendered)


if __name__ == "__main__":
    unittest.main()
