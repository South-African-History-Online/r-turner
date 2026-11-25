# Preservation record

## Subject

Richard Albert David (Rick) Turner (1941 - 1978), South African political philosopher, lecturer at the University of Natal and author of *The Eye of the Needle*. Banned in 1973 and assassinated at his home in Durban on 8 January 1978.

## Original site

- Published at `https://www.sahistory.org.za/r-turner/` by South African History Online.
- First version: a static site (captures from 2008).
- Later version: a Drupal 7 site at the same address (that codebase is kept in a separate private archive). Drupal 7 reached end of life and the site was not maintained.

## Decision

In November 2026 the site was rebuilt as a static Hugo archive, on the same stack as the Franco Frescura and Dumile Feni archives, to be served at a subdomain of sahistory.org.za. A Drupal 11 migration was rejected because the content never changes and would carry a permanent security-update burden; retiring the site was rejected because the content would be lost from the web.

## Scope of what is preserved

- `legacy-site/wayback/` - Wayback Machine captures of the old pages, the source for all page text. No database dump was used. Email addresses and the old server's file path, which appeared in the captures, have been blanked.
- `legacy-site/files/` - the old site's images, graphics and PDFs.
- `hugo-site/` - generated from both by `scripts/migrate_legacy.py`: biography, chronology, bibliography, quotes from *The Eye of the Needle*, articles by Jann Turner, the poem by Peter Sacks, and galleries of portraits, family photographs, the funeral, press headlines and letters.

## Document inventory

Scanned documents served from `hugo-site/static/pdfs/`. All are image scans or exports taken from the old site; none has been checked for an embedded text layer.

| File | Title | Author | Source noted on the old site |
| --- | --- | --- | --- |
| `what-is-political-philosophy.pdf` | What is political philosophy? | Richard Turner | - |
| `sartre-and-ryle-on-the-imagination.pdf` | Sartre and Ryle on the imagination | Richard Turner | 8 p. typescript |
| `south-african-outlook-june-1978.pdf` | Letter to parliament | Richard Turner | South African Outlook, June 1978: 84-87 |
| `human-models-and-economic-systems.pdf` | Human models and economic systems | Richard Turner | Reality, vol. 2 no. 5, Nov 1970 |
| `the-east-london-strikes.pdf` | The East London strikes | Richard Turner, as G. Maré | South African Labour Bulletin, 1 (5), Aug 1974 |
| `dialectical-reason.pdf` | Dialectical Reason | Richard Turner | Radical Philosophy, no. 4, Spring 1973 |
| `memorandum-to-schlebusch-commission.pdf` | Memorandum to the Schlebusch Commission | Richard Turner | 6 pp. typescript |
| `tony-morphet-the-eye-of-the-needle-ravan-1980.pdf` | Biographical introduction to The Eye of the Needle | Tony Morphet | Ravan Press, 1980 |
| `turner-by-nash.pdf` | The Moment of Western Marxism in South Africa | Andrew Nash | - |
| `turner-by-fluxman-and-vale.pdf` | Re-reading Rick Turner in the New South Africa | Tony Fluxman and Peter Vale | - |
| `heywood-is-the-continuation-of-the-present-a-possible-future.pdf` | Is the continuation of the present a possible future? | Mark Heywood | Daily Maverick, 4 August 2014 |

Not recovered: "Rick Turner's Continuing Challenge" by Colin Gardner and "Elegy for Rick Turner" by Vortex. The old site linked to both; the files are gone from sahistory.org.za and were not in the old site's files.

## Still to do for the documents

- Confirm rights for each document, in particular the 2014 Daily Maverick article and the published essays by Morphet, Nash, and Fluxman and Vale.
- Run OCR so the scans are searchable, and produce PDF/A copies.
- Deposit the set with the Internet Archive.
- Fill in publication details for the three documents with no source noted.

## Known limits

- Page text is converted as-is from the archived pages and only spot-checked.
- Photographs are the old web versions.
- Accessibility: the templates use semantic landmarks, alt text, visible focus and a keyboard-operable lightbox. A formal WCAG 2.1 audit has not been done.

## Backups

- This repository (content, files and the archived pages).
- SAHO's own backups of the 2018 web server, which hold the original Drupal 7 tree and files.
- The Internet Archive's captures of `sahistory.org.za/r-turner/`.

## Earlier codebase

This repository's history starts with the 2026 rebuild. The Drupal 7 codebase that served the site before it is kept in a separate private archive repository at South African History Online and is not part of this one.
