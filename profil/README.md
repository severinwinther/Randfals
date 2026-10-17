# RANDFALS — grafisk profil

Alt her ligger klart til bruk, men er ikke lenket fra nettsiden. Det eneste som er aktivt på siden, er det animerte ordmerket på forsiden (`js/ordmerke.js`).

## Innhold

| Mappe | Hva |
|---|---|
| `font/` | **Randfals Modul** — egen versalskrift på 4 × 5-rutenettet. OTF/TTF til installering, WOFF/WOFF2 til nett. `partner/` har Archivo og IBM Plex Mono (brukt i visittkortet). |
| `logo/` | R-merket og ordmerket som SVG (kull og kalk), og PNG: merke 1024 px, profilbilde 1080 px, ordmerke 2400 px. |
| `epost/` | E-postmal, signatur og kort hilsen. Bildene i `epost/bilder/` hentes fra `https://randfals.com/profil/epost/bilder/`. Felter i [hakeparentes] byttes ut. |
| `visittkort/` | Trykkfil 85 × 55 mm med 3 mm utfallende (`randfals-visittkort-trykk.pdf`) og forhåndsvisning. |
| `monster/` | Tre sømløse mønstre (falsfelt, trapp, R-felt) i to fargeveier, SVG-rapport + PNG. |
| `animasjon/` | Ordmerket bygget av ruter på tilfeldige steder. HTML (spilles én gang) og MP4 1080 × 1080 til Instagram. |
| `fontprove/` | Fontprøve med alle tegn og prøvefelt. Åpnes på `randfals.com/profil/fontprove/`. |
| `kilde/` | Skriptene som lager alt over. |

## Farger

| Navn | Hex |
|---|---|
| Kull | `#0B0B0B` |
| Kalk | `#F4F3EF` |
| Betong | `#B9B6AE` |
| Skifer | `#6B6A66` |

## Typografi

- **Randfals Modul** — titler, merke, skilt. Alltid versaler. Ikke brødtekst. Minste størrelse ca. 14 px / 8 pt.
- **Archivo** — brødtekst.
- **IBM Plex Mono** — metadata, i samme rekkefølge som mappenavnene: `ÅR — STED — BESKRIVELSE — KUNDE`.

## Lage filene på nytt

Krever Python med `fonttools`, `skia-pathops`, `brotli` og `playwright`.

```bash
cd profil/kilde
python3 lag_font.py                       # font/  (glyfene er definert øverst i filen)
python3 lag_logoer.py                     # logo/*.svg fra fonten
python3 lag_monster.py                    # monster/
python3 lag_visittkort.py "NAVN" "TITTEL" "+47 000 00 000"   # visittkort/
```
