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
        avsnitt += [re.sub(r"\s+", " ", a).strip() for a in re.split(r"\n\s*\n", t) if a.strip()]
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


def importer(kildemappe):
    gammel = DATA.read_text(encoding="utf-8")
    hode = gammel[: gammel.index("window.RANDFALS")]
    data = json.loads(gammel[gammel.index("=", gammel.index("window.RANDFALS")) + 1:].strip().rstrip(";"))

    prosjekter, hoppet = [], []
    for mappe in sorted(p for p in Path(kildemappe).iterdir() if p.is_dir()):
        info = tolk_navn(mappe.name)
        filer = sorted((f for f in mappe.rglob("*") if f.is_file()), key=lambda f: f.name.lower())
        bilder = [f for f in filer if f.suffix.lower() in BILDE]
        videoer = [f for f in filer if f.suffix.lower() in VIDEO]
        pdfer = [f for f in filer if f.suffix.lower() == ".pdf"]
        tekst = les_tekst([f for f in filer if f.suffix.lower() == ".txt"])
        if not (bilder or videoer or pdfer):
            hoppet.append(mappe.name); continue

        forside = [f for f in bilder if f.stem.lower().startswith("forside")]
        bilder = forside + [f for f in bilder if f not in forside]
        slug = slugify(f"{info['tittel']}-{info['undertittel']}" if info["kunde"] else info["tittel"])
        ut = IMG / slug
        shutil.rmtree(ut, ignore_errors=True); ut.mkdir(parents=True)

        sett, medier, n = set(), [], 0
        with tempfile.TemporaryDirectory() as tmp:
            for pdf in pdfer:
                subprocess.run(["pdftoppm", "-r", "150", "-jpeg", str(pdf), str(Path(tmp) / pdf.stem)], check=True)
            pdfsider = sorted(Path(tmp).glob("*.jpg"))
            for f in bilder + pdfsider:
                h = hashlib.md5(f.read_bytes()).hexdigest()
                if h in sett: continue
                sett.add(h); n += 1
                navn = f"{n:02d}.jpg"
                w, hh = lagre_bilde(f, ut / navn)
                medier.append({"src": f"img/{slug}/{navn}", "w": w, "h": hh, "alt": ""})
        for f in videoer:
            h = hashlib.md5(f.read_bytes()).hexdigest()
            if h in sett: continue
            sett.add(h); n += 1
            w, hh = lagre_video(f, ut / f"{n:02d}.mp4", ut / f"{n:02d}-plakat.jpg")
            medier.append({"type": "video", "src": f"img/{slug}/{n:02d}.mp4", "plakat": f"img/{slug}/{n:02d}-plakat.jpg", "w": w, "h": hh, "alt": ""})

        stille = [m for m in medier if m.get("type") != "video"]
        if forside:  # en fil som heter "forside" vinner alltid
            forsidebilde = stille[0]
        elif stille:  # ellers første bilde som er stort nok, ev. det største
            forsidebilde = next((m for m in stille if max(m["w"], m["h"]) >= 1000), max(stille, key=lambda m: m["w"] * m["h"]))
        else:
            forsidebilde = {**medier[0], "src": medier[0]["plakat"]}
        galleri = [m for m in medier if m is not forsidebilde]
        sett_format(galleri)
        fakta = {"Kunde": tittelcase(info["kunde"])} if info["kunde"] else {}
        prosjekter.append({
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
        })
        print(f"  {mappe.name}: {len(medier)} medier, {len(tekst)} avsnitt")

    # nyeste år først, ellers mappenavn
    prosjekter.sort(key=lambda p: (-int(p["aar"]) if str(p["aar"]).isdigit() else 0, p["kilde"]))
    gyldige = {p["slug"] for p in prosjekter}
    for d in IMG.iterdir():  # fjern bildemapper for prosjekter som ikke finnes lenger
        if d.is_dir() and d.name not in gyldige:
            shutil.rmtree(d)
    data["prosjekter"] = prosjekter
    om_bilde = data.get("om", {}).get("bilde")
    if om_bilde and not (ROT / om_bilde["src"]).exists():
        data["om"]["bilde"] = prosjekter[0]["forside"] if prosjekter else None
    DATA.write_text(hode + "window.RANDFALS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    if hoppet:
        print("Hoppet over (ingen bilder):", ", ".join(hoppet))


if __name__ == "__main__":
    importer(sys.argv[1])
