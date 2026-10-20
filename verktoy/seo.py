#!/usr/bin/env python3
"""RANDFALS — bygger sidene ferdig for søkemotorer (SEO).

Leser js/data.js og skriver:
  index.html, liste.html, om.html, 404.html, prosjekt.html
  prosjekt/<slug>/index.html   (én ekte side per prosjekt: randfals.com/prosjekt/<slug>/)
  sitemap.xml, robots.txt

Hver side får tittel, beskrivelse, kanonisk adresse, delingsbilde (Open Graph),
strukturerte data (JSON-LD) og innholdet ferdig skrevet i HTML, slik at Google
ser tekst og bilder uten å kjøre JavaScript. Utseendet styres fortsatt av js/app.js.

Kjøres automatisk av importer.py, instagram.py og GitHub (se .github/workflows/seo.yml).
Manuelt:  python3 verktoy/seo.py
"""
import html
import json
import re
import subprocess
from datetime import date
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent
DATA = ROT / "js" / "data.js"
VERSJON = "6"  # øk når css/js endres, så nettlesere henter nye filer
DELINGSBILDE = {"src": "del.png", "w": 1200, "h": 630}
LOGO = "logo.png"
LAT = ' loading="lazy"'


def les_data():
    t = DATA.read_text(encoding="utf-8")
    return json.loads(t[t.index("=", t.index("window.RANDFALS")) + 1:].strip().rstrip(";"))


def nettadresse():
    cname = ROT / "CNAME"
    domene = cname.read_text().strip() if cname.exists() else "randfals.com"
    return f"https://{domene}/"


e = lambda s: html.escape(str(s if s is not None else ""), quote=True)
nr = lambda i: str(i + 1).zfill(2)


def kort_tekst(s, maks=155):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= maks:
        return s
    kutt = s[: maks - 1].rsplit(" ", 1)[0].rstrip(",.;:—–- ")
    return kutt + "…"


def under(p):
    u = p.get("undertittel") or ""
    return u if u and u.lower() != str(p.get("tittel", "")).lower() else ""


def alt_for(p, b, n=None):
    """Alt-tekst: egen tekst om den finnes, ellers prosjektnavn (+ nummer)."""
    if b.get("alt"):
        return b["alt"]
    navn = ", ".join(x for x in [p["tittel"], under(p)] if x)
    return f"{navn} — bilde {n}" if n else navn


def lenke(p):
    return f"prosjekt/{p['slug']}/"


def sist_endret(*stier):
    try:
        d = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *stier], cwd=ROT,
                           capture_output=True, text=True, timeout=20).stdout.strip()
        return d or None
    except Exception:
        return None


# ---------------------------------------------------------------- deler

def hode(D, url, *, tittel, beskrivelse, sti, bilde=None, og_type="website", jsonld=(), robots=None, side, slug=None):
    kanonisk = url + sti
    b = bilde or DELINGSBILDE
    ld = "".join("\n<script type=\"application/ld+json\">" + json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
                 for x in jsonld)
    rob = f'\n<meta name="robots" content="{robots}">' if robots else ""
    kan = "" if robots else f'\n<link rel="canonical" href="{e(kanonisk)}">'
    stoerrelse = f'\n<meta property="og:image:width" content="{b["w"]}">\n<meta property="og:image:height" content="{b["h"]}">' if b.get("w") else ""
    return f"""<!doctype html>
<html lang="nb">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<base href="/">
<title>{e(tittel)}</title>
<meta name="description" content="{e(beskrivelse)}">{rob}{kan}
<meta property="og:site_name" content="{e(D['navn'])}">
<meta property="og:locale" content="nb_NO">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(tittel)}">
<meta property="og:description" content="{e(beskrivelse)}">
<meta property="og:url" content="{e(kanonisk)}">
<meta property="og:image" content="{e(url + b['src'])}">{stoerrelse}
<meta property="og:image:alt" content="{e(b.get('alt') or D['navn'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="favicon.ico" sizes="32x32">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="sitemap" type="application/xml" href="sitemap.xml">
<link rel="preload" href="fonts/archivo.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="css/stil.css?v={VERSJON}">
<script>try{{var t=localStorage.getItem("randfals-tema");if(t)document.documentElement.dataset.tema=t}}catch(e){{}}</script>
<script>try{{if(!sessionStorage.getItem("randfals-besok"))document.documentElement.classList.add("laster")}}catch(e){{}}</script>{ld}
</head>
<body data-side="{side}"{f' data-slug="{e(slug)}"' if slug else ""}>
<script src="js/laster.js?v={VERSJON}"></script>"""


def fot():
    return f"""
<script src="js/data.js?v={VERSJON}"></script>
<script src="js/app.js?v={VERSJON}"></script>
</body>
</html>
"""


def nav(D):
    return f"""<header class="nav"><a href="./" class="logo">{e(D['navn'])}<i></i></a> <a href="liste.html" class="strek">Index</a> <a href="om.html" class="strek">Om</a> <div class="nav-h"><a href="om.html#kontakt" class="strek">Kontakt</a></div></header>"""


def bunn(D):
    return f"""<footer class="bunn"><span>© {date.today().year} {e(D['navn'])}</span> <span>{e(D.get('sted', ''))}</span></footer>"""


def img(b, alt, lat=True):
    if not b:
        return ""
    st = f' width="{b["w"]}" height="{b["h"]}"' if b.get("w") else ""
    return f'<img src="{e(b["src"])}" alt="{e(alt)}"{st}{LAT if lat else ""} decoding="async">'


def tekst_under(b):
    return "<figcaption>" + e(b["tekst"]) + "</figcaption>" if b.get("tekst") else ""


def media(p, b, n):
    if b.get("type") == "video":
        st = f' width="{b["w"]}" height="{b["h"]}"' if b.get("w") else ""
        plakat = f' poster="{e(b["plakat"])}"' if b.get("plakat") else ""
        return f'<video src="{e(b["src"])}"{plakat}{st} muted loop playsinline preload="none" aria-label="{e(alt_for(p, b, n))}"></video>'
    return img(b, alt_for(p, b, n))


# ---------------------------------------------------------------- strukturerte data

def organisasjon(D, url):
    o = D.get("om", {})
    org = {
        "@type": "Organization",
        "@id": url + "#org",
        "name": D["navn"],
        "url": url,
        "logo": url + LOGO,
        "image": url + DELINGSBILDE["src"],
        "description": o.get("tekst", ""),
        "address": {"@type": "PostalAddress", "addressLocality": D.get("sted", "Oslo"), "addressCountry": "NO"},
        "areaServed": "NO",
        "knowsAbout": o.get("tjenester", []),
        "sameAs": [l["url"] for l in o.get("lenker", []) if l.get("url")],
    }
    if o.get("epost"):
        org["email"] = o["epost"]
    if o.get("telefon"):
        org["telephone"] = o["telefon"]
    return org


def smuler(url, *ledd):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url + s} for i, (n, s) in enumerate(ledd)]}


# ---------------------------------------------------------------- sider

def seo_tekst(D):
    s = D.get("seo", {})
    t = [x.lower() for x in D["om"]["tjenester"][:3]]
    tittel = s.get("tittel") or f"{D['navn']} — {', '.join(t[:-1])} og {t[-1]} i {D.get('sted', 'Oslo')}"
    beskrivelse = s.get("beskrivelse") or kort_tekst(D["om"]["tekst"])
    return tittel, beskrivelse


def forside(D, url):
    tittel, beskrivelse = seo_tekst(D)
    ld = [{"@context": "https://schema.org", "@graph": [
        organisasjon(D, url),
        {"@type": "WebSite", "@id": url + "#nettsted", "url": url, "name": D["navn"], "inLanguage": "nb", "publisher": {"@id": url + "#org"}},
    ]}]
    kort = "".join(
        f'<a class="kort" href="{lenke(p)}">{img(p.get("forside"), alt_for(p, p.get("forside") or {}), lat=i > 2)}<span class="bt"><b>{e(p["tittel"])}</b><br>{e(p.get("undertittel") or p.get("kategori"))}</span></a>'
        for i, p in enumerate(D["prosjekter"]))
    innhold = f"""{nav(D)}
<main class="hjem">
<section class="stripe" aria-label="Prosjekter"><div class="spor">{kort}</div></section>
<div class="ordmerke-boks"><h1 class="ordmerke"><span>{e(D['navn'])}</span></h1></div>
<p class="ingress">{e(D.get('ingress', ''))}</p>
{bunn(D)}
</main>"""
    return hode(D, url, tittel=tittel, beskrivelse=beskrivelse, sti="", jsonld=ld, side="hjem") + f'\n<div id="app">{innhold}</div>' + fot()


def listeside(D, url):
    tittel = f"Prosjekter — {D['navn']}"
    beskrivelse = kort_tekst(f"Alle prosjekter fra {D['navn']}: " + ", ".join(
        f"{p['tittel']} ({p.get('aar')})" for p in D["prosjekter"]) + ".")
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": tittel, "url": url + "liste.html",
           "isPartOf": {"@id": url + "#nettsted"},
           "mainEntity": {"@type": "ItemList", "itemListElement": [
               {"@type": "ListItem", "position": i + 1, "url": url + lenke(p), "name": p["tittel"]} for i, p in enumerate(D["prosjekter"])]}},
          smuler(url, (D["navn"], ""), ("Index", "liste.html"))]
    rader = "".join(
        f'<a class="rad" href="{lenke(p)}"><span>{nr(i)}</span> <span class="navn">{e(p["tittel"])}</span> <span class="kat">{e(p.get("kategori"))}</span> <span class="sted">{e(p.get("sted"))}</span> <span class="aar">{e(p.get("aar"))}</span></a>'
        for i, p in enumerate(D["prosjekter"]))
    innhold = f"""{nav(D)}
<main class="liste">
<h1 class="usynlig">Prosjekter — {e(D['navn'])}</h1>
<div class="liste-rader">{rader}</div>
</main>
{bunn(D)}"""
    return hode(D, url, tittel=tittel, beskrivelse=beskrivelse, sti="liste.html", jsonld=ld, side="liste") + f'\n<div id="app">{innhold}</div>' + fot()


def omside(D, url):
    o = D["om"]
    tittel = f"Om og kontakt — {D['navn']}"
    beskrivelse = kort_tekst(o["tekst"] + (f" Kontakt: {o['epost']}" if o.get("epost") else ""))
    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": tittel, "url": url + "om.html",
           "mainEntity": organisasjon(D, url)},
          smuler(url, (D["navn"], ""), ("Om", "om.html"))]
    kontakt = "".join(x for x in [
        f'<li><a href="mailto:{e(o["epost"])}">{e(o["epost"])}</a></li>' if o.get("epost") else "",
        f'<li><a href="tel:{e(o["telefon"].replace(" ", ""))}">{e(o["telefon"])}</a></li>' if o.get("telefon") else ""])
    innhold = f"""{nav(D)}
<main class="om">
<h1 class="usynlig">Om {e(D['navn'])}</h1>
<p class="om-tekst">{e(o['tekst'])}</p>
<div class="om-blokk"><h2 class="etikett">Tjenester</h2><ul>{''.join(f'<li>{e(t)}</li>' for t in o.get('tjenester', []))}</ul></div>
<div class="om-blokk"><h2 class="etikett">Finn oss</h2><ul>{''.join(f'<li><a href="{e(l["url"])}" rel="noopener">{e(l["navn"])}</a></li>' for l in o.get('lenker', []))}</ul></div>
<div class="om-blokk" id="kontakt"><h2 class="etikett">Kontakt</h2><ul>{kontakt}</ul></div>
</main>
{bunn(D)}"""
    return hode(D, url, tittel=tittel, beskrivelse=beskrivelse, sti="om.html", jsonld=ld, side="om") + f'\n<div id="app">{innhold}</div>' + fot()


def prosjektside(D, url, i):
    p = D["prosjekter"][i]
    neste = D["prosjekter"][(i + 1) % len(D["prosjekter"])]
    u = under(p)
    tittel = " — ".join(x for x in [p["tittel"], u, D["navn"]] if x)
    tekst = " ".join(t.strip() + ("" if t.strip()[-1:] in ".!?…:" else ".") for t in (p.get("tekst") or []) if t.strip())
    sted_aar = ", ".join(str(x) for x in [p.get("sted"), p.get("aar")] if x)
    navn = p["tittel"] + (" — " + u if u else "")
    beskrivelse = kort_tekst(f"{navn}. {sted_aar}. {tekst}" if tekst
                             else f"{navn}. {p.get('kategori', '')} av {D['navn']}, {sted_aar}.")
    forsideb = p.get("forside") or {}
    bilder = [b for b in [forsideb] + (p.get("bilder") or []) if b.get("src") and b.get("type") != "video"]
    delb = dict(forsideb, alt=alt_for(p, forsideb)) if forsideb.get("src") else None

    verk = {"@type": "CreativeWork", "@id": url + lenke(p) + "#verk", "name": p["tittel"], "headline": tittel.rsplit(" — ", 1)[0],
            "description": kort_tekst(tekst, 500) if tekst else beskrivelse, "url": url + lenke(p), "inLanguage": "nb",
            "image": [url + b["src"] for b in bilder[:12]],
            "creator": {"@id": url + "#org"}, "publisher": organisasjon(D, url),
            "genre": p.get("kategori")}
    if p.get("aar"):
        verk["dateCreated"] = str(p["aar"])
    if p.get("sted"):
        verk["locationCreated"] = {"@type": "Place", "name": p["sted"], "address": {"@type": "PostalAddress", "addressLocality": p["sted"], "addressCountry": "NO"}}
    kunde = (p.get("fakta") or {}).get("Kunde")
    if kunde:
        verk["funder"] = {"@type": "Organization", "name": kunde}
    ld = [{"@context": "https://schema.org", **verk},
          smuler(url, (D["navn"], ""), ("Index", "liste.html"), (p["tittel"], lenke(p)))]

    fakta = {"År": p.get("aar"), "Sted": p.get("sted"), "Kategori": p.get("kategori"), **(p.get("fakta") or {})}
    galleri = "".join(f'<figure>{media(p, b, n + 2)}{tekst_under(b)}</figure>'
                      for n, b in enumerate(p.get("bilder") or []))
    innhold = f"""{nav(D)}
<main class="prosjekt">
<section class="p-topp"><h1 class="p-tittel">{e(p['tittel'])}</h1>
<p class="meta"><span>{nr(i)} / {nr(len(D['prosjekter']) - 1)}</span> <span>{e(p.get('kategori'))}</span> <span>{e(p.get('sted'))}</span> <span>{e(p.get('aar'))}</span></p></section>
<figure class="hero">{img(forsideb, alt_for(p, forsideb), lat=False)}</figure>
{f'<section class="p-tekst"><h2 class="etikett">Om prosjektet</h2><div class="avsnitt">' + "".join(f"<p>{e(t)}</p>" for t in p["tekst"]) + "</div></section>" if p.get("tekst") else ""}
<section class="galleri" aria-label="Bilder">{galleri}</section>
<section class="fakta"><h2 class="etikett">Fakta</h2><dl>{''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in fakta.items() if v not in ("", None))}</dl></section>
<a class="neste" href="{lenke(neste)}"><span class="etikett">Neste prosjekt →</span> <span class="stor">{e(neste['tittel'])}</span></a>
{bunn(D)}
</main>"""
    return hode(D, url, tittel=tittel, beskrivelse=beskrivelse, sti=lenke(p), bilde=delb, og_type="article",
                jsonld=ld, side="prosjekt", slug=p["slug"]) + f'\n<div id="app">{innhold}</div>' + fot()


def gammel_prosjektside(D, url):
    """prosjekt.html?p=<slug> (gamle lenker, f.eks. delt på Instagram) sendes videre til den nye adressen."""
    s = hode(D, url, tittel=f"Prosjekt — {D['navn']}", beskrivelse=f"Prosjekt fra {D['navn']}.", sti="prosjekt.html",
             robots="noindex, follow", side="prosjekt")
    s = s.replace("</head>", '<script>var p=new URLSearchParams(location.search).get("p");if(p)location.replace("prosjekt/"+encodeURIComponent(p)+"/"+location.hash)</script>\n</head>')
    return s + f'\n<div id="app">{nav(D)}<main class="p-topp"><p><a href="liste.html">Se alle prosjekter</a></p></main></div>' + fot()


def ikke_funnet(D, url):
    return hode(D, url, tittel=f"Fant ikke siden — {D['navn']}", beskrivelse="Siden finnes ikke.", sti="404.html",
                robots="noindex", side="ikkefunnet") + f'\n<div id="app">{nav(D)}<main class="p-topp"><h1 class="p-tittel">Fant ikke siden</h1><p class="meta"><a class="strek" href="./">Tilbake til forsiden</a></p></main></div>' + fot()


def sitemap(D, url):
    def post(sti, endret=None, bilder=()):
        lm = f"<lastmod>{endret}</lastmod>" if endret else ""
        bi = "".join(f"<image:image><image:loc>{e(url + b)}</image:loc></image:image>" for b in bilder)
        return f"<url><loc>{e(url + sti)}</loc>{lm}{bi}</url>"
    data_endret = sist_endret("js/data.js")
    rader = [post("", data_endret), post("liste.html", data_endret), post("om.html", data_endret)]
    for p in D["prosjekter"]:
        bilder = [b["src"] for b in [p.get("forside") or {}] + (p.get("bilder") or []) if b.get("src") and b.get("type") != "video"]
        rader.append(post(lenke(p), sist_endret(f"img/{p['slug']}", "js/data.js"), list(dict.fromkeys(bilder))))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(rader) + "\n</urlset>\n")


def robots(url):
    return f"User-agent: *\nAllow: /\nDisallow: /profil/\nDisallow: /verktoy/\n\nSitemap: {url}sitemap.xml\n"


def skriv(sti, tekst):
    sti.parent.mkdir(parents=True, exist_ok=True)
    if not sti.exists() or sti.read_text(encoding="utf-8") != tekst:
        sti.write_text(tekst, encoding="utf-8")
        return True
    return False


def bygg():
    D = les_data()
    url = nettadresse()
    filer = {
        "index.html": forside(D, url),
        "liste.html": listeside(D, url),
        "om.html": omside(D, url),
        "prosjekt.html": gammel_prosjektside(D, url),
        "404.html": ikke_funnet(D, url),
        "robots.txt": robots(url),
    }
    for i, p in enumerate(D["prosjekter"]):
        filer[f"prosjekt/{p['slug']}/index.html"] = prosjektside(D, url, i)
    # fjern sider for prosjekter som ikke finnes lenger
    gyldige = {p["slug"] for p in D["prosjekter"]}
    mappe = ROT / "prosjekt"
    if mappe.is_dir():
        for d in mappe.iterdir():
            if d.is_dir() and d.name not in gyldige:
                for f in d.iterdir():
                    f.unlink()
                d.rmdir()
    endret = [n for n, t in filer.items() if skriv(ROT / n, t)]
    # sitemap til slutt (lastmod hentes fra git)
    if skriv(ROT / "sitemap.xml", sitemap(D, url)):
        endret.append("sitemap.xml")
    print(f"SEO: {len(filer) + 1} filer bygget, {len(endret)} endret.")
    return endret


if __name__ == "__main__":
    bygg()
