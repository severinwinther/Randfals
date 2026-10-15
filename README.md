# RANDFALS — nettside

Statisk nettside (HTML/CSS/JS, ingen byggesteg) laget for **GitHub Pages**.
Sort/hvitt, STORE BOKSTAVER, horisontal prosjektstripe på forsiden og vertikal prosjektside ved klikk.

## Sider

| Fil | Innhold |
|---|---|
| `index.html` | Forside: uendelig horisontal stripe med prosjekter øverst, stort RANDFALS-ordmerke, ingress, klokke |
| `prosjekt.html?p=<slug>` | Ett prosjekt: tittel, toppbilde, tekst, bildegalleri, fakta, «neste prosjekt» |
| `liste.html` | Index: alle prosjekter i liste, med bilde som følger musepekeren |
| `om.html` | Om, tjenester, lenker og kontakt |
| `404.html` | Feilside |

## Importere prosjekter fra mapper

Prosjektene hentes fra `RANDFALS.COM/Prosjekter` på skrivebordet med `verktoy/importer.py`:

```bash
python3 verktoy/importer.py "<sti>/RANDFALS.COM/Prosjekter"
```

- Mappenavn: `ÅR_STED_BESKRIVELSE_KUNDE` (tittel = beskrivelse, undertittel = kunde) eller `ÅR_STED_BESKRIVELSE-VERKNAVN` (tittel = verknavn, undertittel = beskrivelse).
- Bilder (JPEG/PNG), video (MP4/MOV) og PDF-sider blir galleri. Bilder skaleres til maks 2000 px, duplikater fjernes.
- Første store bilde blir forsidebilde. Gi en fil navnet `forside.jpg` for å velge selv.
- `.txt` blir prosjekttekst (tom linje = nytt avsnitt).
- Om-teksten og ingressen i `data.js` røres ikke.

## Oppdatere innhold manuelt

**All tekst og alle prosjekter ligger i `js/data.js`.** Du trenger ikke røre noe annet.

1. Legg bildene i `img/<prosjekt-slug>/` (f.eks. `img/kant/01.jpg`). Anbefalt: JPG, ca. 2000 px på lengste side, under 400 KB.
2. Kopier en prosjektblokk i `data.js` og endre `slug`, `tittel`, `kategori`, `aar`, `sted`, `tekst` og `bilder`.
3. Bildeformat i galleriet: `full`, `halv` (to etter hverandre = par), `smal` eller `hoyre`.
4. Rekkefølgen i `data.js` er rekkefølgen på siden.

> Alt innhold nå er **plassholdere** (prosjektnavn, tekster, e-post og bilder). Bytt ut før lansering.

## Design-justeringer (i `css/stil.css`, øverst)

- `--kort` — bredden på kortene i stripen
- `--mellom` — luft mellom kortene (sett `0` for helt kant-i-kant)
- `--bildefilter: grayscale(1)` — alle bilder i sort/hvitt. Sett `none` for farge.
- Fonter: Archivo (overskrifter) og IBM Plex Mono (små tekster), lagret lokalt i `fonts/`. Ingen kall til Google.

## Funksjoner

- Hjul, trackpad, dra med mus og piltaster scroller stripen horisontalt. Den glir rolig av seg selv og stopper ved hover.
- Mobil: vanlig sveip i stripen.
- Klikk på et prosjekt: bildet «flyr» inn i prosjektsiden og siden glir opp vertikalt (View Transitions; Chrome, Edge og Safari 18+. Andre nettlesere får vanlig sideskift).
- Bryter øverst til høyre bytter mellom hvit og sort side (huskes).
- Respekterer «redusert bevegelse» i operativsystemet.

## Publisere på GitHub Pages

1. Lag et nytt repo på GitHub, f.eks. `randfals`.
2. Last opp filene. Enten dra hele mappen inn på «Add file → Upload files», eller:
   ```bash
   git remote add origin https://github.com/<bruker>/randfals.git
   git push -u origin main
   ```
3. I repoet: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`** → Save.
4. Siden blir tilgjengelig på `https://<bruker>.github.io/randfals/` etter et minutt.

### Eget domene (f.eks. randfals.no)

1. Settings → Pages → Custom domain: `randfals.no` → Save (GitHub lager filen `CNAME`).
2. Hos domeneleverandøren: fire A-poster for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`, og en CNAME for `www` → `<bruker>.github.io`.
3. Huk av «Enforce HTTPS» når sertifikatet er klart.

## Teste lokalt

Åpne `index.html` direkte i nettleseren, eller kjør `python3 -m http.server` i mappen og gå til `http://localhost:8000`.

## Videre (valgfritt)

- Bildeoptimalisering: lag WebP-versjoner og `srcset` når de ekte bildene er klare.
- Video i stripen (MP4 som spiller lydløst i loop) i stedet for stillbilde.
- Om dere vil redigere uten å røre kode: koble på et enkelt CMS (f.eks. Decap CMS eller Pages CMS) som skriver til `data.js`/JSON i repoet.
