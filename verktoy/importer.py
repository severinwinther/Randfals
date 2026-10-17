"""
RANDFALS — importer prosjekter fra mappestrukturen på skrivebordet.

Bruk:  python3 verktoy/importer.py <sti til RANDFALS.COM/Prosjekter>

Mappenavn (alt på ett nivå):
  ÅR_STED_BESKRIVELSE_KUNDE        f.eks. 2026_OSLO_PAUSEBORD_SA STEINSKULPTUR
  ÅR_STED_BESKRIVELSE-VERKNAVN     f.eks. 2026_OSLO_STUEBORD-PORTLAND

I hver mappe (undermapper leses også):
  JPEG/PNG  -> bilder (filnavn-rekkefølge; en fil som heter "forside" blir forsidebilde)
  MP4/MOV   -> video i galleriet (lydløs, går i loop)
  PDF       -> hver side blir et bilde
  TXT       -> prosjekttekst (tom linje = nytt avsnitt)

Skriver img/<slug>/ og js/data.js. Om-teksten, ingressen osv. i data.js beholdes.
"""
import hashlib, json, re, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path
from PIL import Image, ImageOps
try:  # HEIC-bilder fra iPhone
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

ROT = Path(__file__).resolve().parent.parent
IMG = ROT / "img"
DATA = ROT / "js" / "data.js"
MAKS = 2000          # lengste side på bilder (px)
KVALITET = 82
BILDE = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}
VIDEO = {".mp4", ".mov", ".m4v", ".webm"}


def slugify(s):
    s = s.lower().replace("æ", "ae").replace("ø", "o").replace("å", "a")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def tittelcase(s):
    return s.strip().capitalize()  # vises uansett med STORE BOKSTAVER


def tolk_navn(navn):
    aar, sted, rest = (navn.split("_", 2) + ["", "", ""])[:3]
    if "_" in rest:                       # BESKRIVELSE_KUNDE
        beskr, kunde = rest.split("_", 1)
        return dict(aar=aar, sted=sted, tittel=beskr, undertittel=kunde, kategori=beskr, kunde=kunde, verk="")
    if "-" in rest:                       # BESKRIVELSE-VERKNAVN
        beskr, verk = rest.split("-", 1)
        return dict(aar=aar, sted=sted, tittel=verk, undertittel=beskr, kategori=beskr, kunde="", verk=verk)
    return dict(aar=aar, sted=sted, tittel=rest, undertittel="", kategori=rest, kunde="", verk="")


def lagre_bilde(kilde, mål):
    with Image.open(kilde) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((MAKS, MAKS), Image.LANCZOS)
        im.save(mål, "JPEG", quality=KVALITET, progressive=True, optimize=True)
        return im.size


def lagre_video(kilde, mål, plakat):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(kilde), "-an",
                    "-vf", "scale='min(1280,iw)':-2", "-c:v", "libx264", "-crf", "26", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mål)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.3", "-i", str(mål), "-frames:v", "1",
                    "-q:v", "4", str(plakat)], check=True)
    with Image.open(plakat) as im:
        return im.size


def les_tekst(filer):
    avsnitt = []
    for f in filer:
        rå = f.read_bytes()
        for kod in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                t = rå.decode(kod); break
            except UnicodeDecodeError:
                continue
        avsnitt += [re.sub(r"\s+", " ", a).strip() for a in t.splitlines() if a.strip()]
    return avsnitt


def sett_format(medier):
    """Rytme: full bredde, så par, så full ... Stående bilder i par.
    Små bilder (under 1400 px brede) og enslige stående/videoer blir smale."""
    staaende = lambda m: m["h"] > m["w"] * 1.05
    i, forrige = 0, None
    while i < len(medier):
        m = medier[i]
        n = medier[i + 1] if i + 1 < len(medier) else None
        liten = m["w"] < 1400
        if n and staaende(m) == staaende(n) and (staaende(m) or forrige == "full" or liten):
            m["format"] = n["format"] = "halv"; forrige = "halv"; i += 2; continue
        m["format"] = "smal" if staaende(m) or liten or m.get("type") == "video" else "full"
        forrige = m["format"]; i += 1


def naturlig(f):
    """1, 2, ... 10 i stedet for 1, 10, 2"""
    return [int(d) if d.isdigit() else d for d in re.split(r"(\d+)", f.name.lower())]


def les_data():
    gammel = DATA.read_text(encoding="utf-8")
    hode = gammel[: gammel.index("window.RANDFALS")]
    data = json.loads(gammel[gammel.index("=", gammel.index("window.RANDFALS")) + 1:].strip().rstrip(";"))
    return hode, data


def skriv_data(hode, data):
    DATA.write_text(hode + "window.RANDFALS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")


def slug_for(navn):
    info = tolk_navn(navn)
    return slugify(f"{info['tittel']}-{info['undertittel']}" if info["kunde"] else info["tittel"])


def lagre_medier(kilder, slug, start=0):
    """Lagrer bilder/video/PDF-sider i img/<slug>/ fra nummer start+1. Returnerer medieliste."""
    ut = IMG / slug
    ut.mkdir(parents=True, exist_ok=True)
    sett, medier, n = set(), [], start
    with tempfile.TemporaryDirectory() as tmp:
        for f in kilder:  # samme rekkefølge som i mappen (naturlig sortert)
            h = hashlib.md5(f.read_bytes()).hexdigest()
            if h in sett: continue
            sett.add(h)
            ext = f.suffix.lower()
            if ext in VIDEO:
                n += 1
                w, hh = lagre_video(f, ut / f"{n:02d}.mp4", ut / f"{n:02d}-plakat.jpg")
                medier.append({"type": "video", "src": f"img/{slug}/{n:02d}.mp4", "plakat": f"img/{slug}/{n:02d}-plakat.jpg", "w": w, "h": hh, "alt": ""})
                continue
            sider = [f]
            if ext == ".pdf":
                subprocess.run(["pdftoppm", "-r", "150", "-jpeg", str(f), str(Path(tmp) / f"{h}")], check=True)
                sider = sorted(Path(tmp).glob(f"{h}*.jpg"), key=naturlig)
            for side in sider:
                n += 1
                navn = f"{n:02d}.jpg"
                w, hh = lagre_bilde(side, ut / navn)
                medier.append({"src": f"img/{slug}/{navn}", "w": w, "h": hh, "alt": ""})
    return medier


def finn_kilder(mappe):
    filer = sorted((f for f in mappe.rglob("*") if f.is_file()), key=naturlig)
    kilder = [f for f in filer if f.suffix.lower() in BILDE | VIDEO | {".pdf"}]
    tekst = les_tekst([f for f in filer if f.suffix.lower() == ".txt"])
    forside = [f for f in kilder if f.suffix.lower() in BILDE and f.stem.lower().startswith("forside")]
    return forside + [f for f in kilder if f not in forside], tekst, bool(forside)


def bygg_prosjekt(mappe):
    """Bygger ett prosjekt fra en mappe (sletter og lager img/<slug>/ på nytt). None hvis ingen medier."""
    info = tolk_navn(mappe.name)
    kilder, tekst, har_forside = finn_kilder(mappe)
    if not kilder:
        return None
    slug = slug_for(mappe.name)
    shutil.rmtree(IMG / slug, ignore_errors=True)
    medier = lagre_medier(kilder, slug)

    stille = [m for m in medier if m.get("type") != "video"]
    if har_forside:  # en fil som heter "forside" vinner alltid
        forsidebilde = stille[0]
    elif stille:  # ellers første bilde som er stort nok, ev. det største
        forsidebilde = next((m for m in stille if max(m["w"], m["h"]) >= 1000), max(stille, key=lambda m: m["w"] * m["h"]))
    else:
        forsidebilde = {**medier[0], "src": medier[0]["plakat"]}
    galleri = [m for m in medier if m is not forsidebilde]
    sett_format(galleri)
    fakta = {"Kunde": tittelcase(info["kunde"])} if info["kunde"] else {}
    print(f"  {mappe.name}: {len(medier)} medier, {len(tekst)} avsnitt")
    return {
        "slug": slug,
        "tittel": tittelcase(info["tittel"]),
        "undertittel": tittelcase(info["undertittel"]),
        "kategori": tittelcase(info["kategori"]),
        "aar": int(info["aar"]) if info["aar"].isdigit() else info["aar"],
        "sted": tittelcase(info["sted"]),
        "forside": {"src": forsidebilde["src"], "w": forsidebilde["w"], "h": forsidebilde["h"], "alt": tittelcase(info["tittel"])},
        "tekst": tekst,
        "fakta": fakta,
        "bilder": galleri,
        "kilde": mappe.name,
    }


def sorter(prosjekter):
    # nyeste år først, ellers mappenavn
    prosjekter.sort(key=lambda p: (-int(p["aar"]) if str(p["aar"]).isdigit() else 0, p["kilde"]))


def importer(kildemappe):
    """Full import fra skrivebordsmappen. Prosjekter som bare finnes fra Instagram beholdes."""
    hode, data = les_data()
    prosjekter, hoppet = [], []
    for mappe in sorted(p for p in Path(kildemappe).iterdir() if p.is_dir()):
        p = bygg_prosjekt(mappe)
        if p: prosjekter.append(p)
        else: hoppet.append(mappe.name)

    fra_mappe = {p["slug"] for p in prosjekter}
    beholdt = [p for p in data.get("prosjekter", []) if p.get("fra") == "instagram" and p["slug"] not in fra_mappe]
    prosjekter += beholdt
    sorter(prosjekter)
    gyldige = {p["slug"] for p in prosjekter}
    for d in IMG.iterdir():  # fjern bildemapper for prosjekter som ikke finnes lenger
        if d.is_dir() and d.name not in gyldige:
            shutil.rmtree(d)
    data["prosjekter"] = prosjekter
    om_bilde = data.get("om", {}).get("bilde")
    if om_bilde and not (ROT / om_bilde["src"]).exists():
        data["om"]["bilde"] = prosjekter[0]["forside"] if prosjekter else None
    skriv_data(hode, data)
    if beholdt:
        print("Beholdt fra Instagram:", ", ".join(p["kilde"] for p in beholdt))
    if hoppet:
        print("Hoppet over (ingen bilder):", ", ".join(hoppet))


def legg_til(mapper, ekstra=None):
    """Legger til prosjekter uten å røre de andre. Finnes prosjektet fra før,
    legges bildene til sist i galleriet og teksten beholdes.
    ekstra: {mappenavn: {felt: verdi}} som flettes inn i prosjektet (f.eks. Instagram-ID-er).
    Returnerer [(mappenavn, slug, "ny"/"utvidet", bilde å vise)]."""
    hode, data = les_data()
    ekstra = ekstra or {}
    finnes = {p["slug"]: p for p in data["prosjekter"]}
    resultat = []
    for mappe in mapper:
        slug = slug_for(mappe.name)
        tillegg = ekstra.get(mappe.name, {})
        if slug in finnes:
            p = finnes[slug]
            kilder, tekst, _ = finn_kilder(mappe)
            brukt = [int(m.group(1)) for f in (IMG / slug).glob("*") if (m := re.match(r"(\d+)", f.name))]
            nye = lagre_medier(kilder, slug, start=max(brukt, default=0))
            sett_format(nye)
            p["bilder"] += nye
            if not p.get("tekst"):
                p["tekst"] = tekst
            for k, v in tillegg.items():
                if k == "fra": continue  # prosjektet kommer fortsatt fra skrivebordet
                p[k] = (p.get(k) or []) + v if isinstance(v, list) else v
            resultat.append((mappe.name, slug, "utvidet", nye[0].get("plakat", nye[0]["src"]) if nye else p["forside"]["src"]))
            print(f"  {mappe.name}: {len(nye)} medier lagt til i eksisterende prosjekt")
        else:
            p = bygg_prosjekt(mappe)
            if not p: continue
            p.update(tillegg)
            data["prosjekter"].append(p)
            finnes[slug] = p
            resultat.append((mappe.name, slug, "ny", p["forside"]["src"]))
    sorter(data["prosjekter"])
    skriv_data(hode, data)
    return resultat


if __name__ == "__main__":
    importer(sys.argv[1])
