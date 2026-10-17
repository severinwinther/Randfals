"""
RANDFALS — hent nye innlegg fra Instagram og lag prosjektutkast.

Kjøres automatisk av GitHub (se .github/workflows/instagram.yml), men kan også kjøres selv:

    INSTAGRAM_TOKEN=... python3 verktoy/instagram.py --mapper /tmp/mapper --rapport /tmp/rapport.md

Slik vet skriptet hvilket prosjekt et innlegg hører til:
  Første linje i bildeteksten er mappenavnet, samme format som på skrivebordet:
      2026_OSLO_PAUSEBORD_SA STEINSKULPTUR
      2026_OSLO_STUEBORD-PORTLAND
  Resten av bildeteksten blir prosjekttekst (hashtags fjernes).
  Flere innlegg med samme første linje samles i ett prosjekt.
  Har prosjektet allerede en side, legges bildene til i galleriet.
  Innlegg uten en slik første linje hoppes over (og listes i rapporten).

Innstillinger i verktoy/instagram.json:
  "fra":     innlegg eldre enn denne datoen hentes ikke
  "ignorer": lenker til innlegg som aldri skal hentes

Et innlegg regnes som ferdig når lenken til det står i et prosjekt i js/data.js
(feltet "instagram"), altså når utkastet er godkjent og flettet inn.
"""
import argparse, json, os, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importer  # noqa: E402

ROT = Path(__file__).resolve().parent.parent
OPPSETT = ROT / "verktoy" / "instagram.json"
API = "https://graph.instagram.com/me/media"
FELT = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,children{id,media_type,media_url,thumbnail_url}"
NAVN = re.compile(r"^\s*(\d{4}_[^_\n]+_.+?)\s*$")
BARE_TAGGER = re.compile(r"^[\s.·•\-–—_]*((#|@)[\w.]+[\s.·•]*)*$")


def hent_json(url):
    if url.startswith("/") or url.startswith("file:"):  # testdata
        return json.loads(Path(url.removeprefix("file://")).read_text(encoding="utf-8"))
    for forsok in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            melding = e.read().decode(errors="replace")
            if e.code < 500:
                sys.exit(f"Instagram svarte {e.code}: {melding}\n"
                         "Sjekk at INSTAGRAM_TOKEN er gyldig (den varer i 60 dager).")
        except urllib.error.URLError:
            pass
        time.sleep(5 * (forsok + 1))
    sys.exit("Fikk ikke kontakt med Instagram.")


def last_ned(url, mål):
    for forsok in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r, open(mål, "wb") as f:
                while blokk := r.read(1 << 16):
                    f.write(blokk)
            return True
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (forsok + 1))
    print(f"  Klarte ikke å laste ned {url}")
    return False


def alle_innlegg(token, fra):
    test = os.environ.get("INSTAGRAM_TEST_JSON")
    url = test or f"{API}?fields={urllib.parse.quote(FELT)}&limit=50&access_token={token}"
    while url:
        side = hent_json(url)
        for innlegg in side.get("data", []):
            if innlegg["timestamp"][:10] < fra:
                return  # nyeste først, så resten er eldre
            yield innlegg
        url = None if test else side.get("paging", {}).get("next")


def tolk_tekst(tekst):
    """-> (mappenavn eller None, [avsnitt])"""
    linjer = (tekst or "").splitlines()
    navn = None
    if linjer and (m := NAVN.match(linjer[0])):
        navn = re.sub(r'[/\\:*?"<>|]', "", m.group(1)).upper()
        navn = re.sub(r"\s+", " ", navn)
        linjer = linjer[1:]
    avsnitt = []
    for l in linjer:
        l = re.sub(r"(\s*#[\w.]+)+\s*$", "", l).strip()  # hashtags til slutt i linja
        if l and not BARE_TAGGER.match(l):
            avsnitt.append(l)
    return navn, avsnitt


def medier_i(innlegg):
    deler = innlegg.get("children", {}).get("data") or [innlegg]
    for d in deler:
        if d.get("media_url"):
            yield (".mp4" if d.get("media_type") == "VIDEO" else ".jpg"), d["media_url"]


def ferdige_lenker():
    _, data = importer.les_data()
    return {l for p in data["prosjekter"] for l in p.get("instagram", [])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapper", required=True, help="hvor prosjektmappene skal lagres")
    ap.add_argument("--rapport", help="markdown-oppsummering (brukes som tekst i pull requesten)")
    a = ap.parse_args()

    oppsett = json.loads(OPPSETT.read_text(encoding="utf-8"))
    token = os.environ.get("INSTAGRAM_TOKEN", "")
    if not token and not os.environ.get("INSTAGRAM_TEST_JSON"):
        sys.exit("Mangler INSTAGRAM_TOKEN.")
    hopp = ferdige_lenker() | set(oppsett.get("ignorer", []))

    grupper, uten_navn = {}, []
    for innlegg in alle_innlegg(token, oppsett.get("fra", "2000-01-01")):
        if innlegg["permalink"] in hopp:
            continue
        navn, tekst = tolk_tekst(innlegg.get("caption"))
        if navn:
            grupper.setdefault(navn, []).append((innlegg, tekst))
        else:
            første = (innlegg.get("caption") or "").strip().splitlines()[:1]
            uten_navn.append((innlegg, første[0][:80] if første else "(ingen tekst)"))

    rot = Path(a.mapper); rot.mkdir(parents=True, exist_ok=True)
    mapper, ekstra = [], {}
    for navn, liste in grupper.items():
        liste.sort(key=lambda x: x[0]["timestamp"])  # eldste innlegg først
        mappe = rot / navn; mappe.mkdir(exist_ok=True)
        avsnitt = []
        for i, (innlegg, tekst) in enumerate(liste, 1):
            for j, (ext, url) in enumerate(medier_i(innlegg), 1):
                last_ned(url, mappe / f"{i:02d}-{j:02d}{ext}")
            avsnitt += [t for t in tekst if t not in avsnitt]
        if avsnitt:
            (mappe / "tekst.txt").write_text("\n\n".join(avsnitt) + "\n", encoding="utf-8")
        mapper.append(mappe)
        ekstra[navn] = {"fra": "instagram", "instagram": [x[0]["permalink"] for x in liste]}

    resultat = importer.legg_til(mapper, ekstra) if mapper else []

    if a.rapport:
        repo = os.environ.get("GITHUB_REPOSITORY", "severinwinther/randfals")
        r = ["Nye innlegg fra Instagram er klare som utkast. **Flett inn (merge) for å publisere.**", ""]
        for navn, slug, hva, vis in resultat:
            lenker = ", ".join(f"[innlegg]({x[0]['permalink']})" for x in grupper[navn])
            bilde = f"https://github.com/{repo}/blob/instagram/utkast/{vis}?raw=true"
            r += [f"### {navn}",
                  f"{'Nytt prosjekt' if hva == 'ny' else 'Bilder lagt til i eksisterende prosjekt'} · `{slug}` · {lenker}", "",
                  f'<img src="{bilde}" width="320">', ""]
        if uten_navn:
            r += ["---", "**Hoppet over (første linje er ikke et prosjektnavn som `2026_OSLO_BESKRIVELSE_KUNDE`):**", ""]
            r += [f"- [{tekst}]({inn['permalink']})" for inn, tekst in uten_navn]
            r += ["", "Rett første linje i bildeteksten på Instagram, så blir innlegget med neste gang."]
        r += ["", "---",
              "- Mappene med originalfilene ligger under **Artifacts → prosjektmapper** i kjøringen som laget dette utkastet. "
              "Legg dem i `RANDFALS.COM/Prosjekter` hvis du vil ha dem på skrivebordet.",
              "- Vil du ikke ha et innlegg på siden: legg lenken i `ignorer` i `verktoy/instagram.json`.",
              "- Lukker du dette utkastet uten å flette, kommer innleggene igjen ved neste kjøring."]
        Path(a.rapport).write_text("\n".join(r) + "\n", encoding="utf-8")

    print(f"{len(resultat)} prosjekt(er) laget/utvidet, {len(uten_navn)} innlegg uten prosjektnavn.")
    if (ut := os.environ.get("GITHUB_OUTPUT")):
        with open(ut, "a") as f:
            f.write(f"endret={'true' if resultat else 'false'}\n")


if __name__ == "__main__":
    main()
