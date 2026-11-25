# Rick Turner

Archive site for Richard (Rick) Turner, South African political philosopher (1941 - 1978), maintained by South African History Online. A Hugo static site on the same stack as the Franco Frescura and Dumile Feni archives.

## Layout

- `legacy-site/wayback/` - archived pages of the old subsite (Wayback Machine captures of the Drupal 7 site, plus a few 2008 static pages).
- `legacy-site/files/` - the old site's images, graphics and PDFs.
- `scripts/migrate_legacy.py` - rebuilds `hugo-site/content`, `hugo-site/static/images` and `hugo-site/static/pdfs` from the two folders above, and holds the legacy-to-new URL mapping. Re-running it overwrites manual edits to content.
- `hugo-site/` - the site. Theme: `themes/turner-press`.
- `scripts/check_links.py` - verifies internal links, images and PDFs in a build.

## Develop

```bash
docker compose -f docker-compose.dev.yml up     # http://localhost:1315
```

Build once:

```bash
docker run --rm -v "$(pwd)/hugo-site:/project" ghcr.io/gohugoio/hugo:v0.170.1 build --minify
python3 scripts/check_links.py hugo-site/public
```

## Design

The look follows the original banner: a sepia band, the name in heavy black grotesque, an italic subtitle. Titles use Archivo Black (SIL Open Font License, self-hosted); dates, captions and labels are set in a typewriter face.

## Known gaps

Two documents the old site linked to are no longer available anywhere we could find: "Rick Turner's Continuing Challenge" by Colin Gardner and "Elegy for Rick Turner" by Vortex.
