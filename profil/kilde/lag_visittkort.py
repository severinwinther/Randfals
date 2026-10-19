"""Visittkort 85 × 55 mm, 3 mm utfallende (91 × 61 mm). Side 1 forside, side 2 bakside."""
import re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
def d_of(name):
    s = (ROOT / f"logo/{name}.svg").read_text()
    return re.search(r'viewBox="([^"]+)"', s).group(1), re.search(r' d="([^"]+)"', s).group(1)

R_VB, R_D = d_of("randfals-R-kull")
TEKSTLOGO = (ROOT / "logo/randfals-tekstlogo-kull.svg").read_text().replace("<svg ", '<svg class="ord" ', 1)
FONT = (ROOT / "font/RandfalsModul-Regular.woff2").as_uri()
ARCH = (ROOT / "font/partner/Archivo-wdth.woff2").as_uri()
PLEX = (ROOT / "font/partner/IBMPlexMono-Regular.woff2").as_uri()

NAVN = sys.argv[1] if len(sys.argv) > 1 else "[FORNAVN ETTERNAVN]"
TITTEL = sys.argv[2] if len(sys.argv) > 2 else "[ARKITEKT MNAL]"
TLF = sys.argv[3] if len(sys.argv) > 3 else "[+47 000 00 000]"

html = f"""<!doctype html><html><head><meta charset="utf-8">
<style>
@font-face{{font-family:Archivo;src:url({ARCH}) format("woff2");font-weight:100 900;font-stretch:62% 125%}}
@font-face{{font-family:'IBM Plex Mono';src:url({PLEX}) format("woff2");font-weight:400}}
@font-face{{font-family:Modul;src:url({FONT}) format("woff2")}}
@page{{size:91mm 61mm;margin:0}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.side{{width:91mm;height:61mm;position:relative;overflow:hidden;page-break-after:always}}
/* sikker sone: 3 mm utfall + 5 mm marg = 8 mm fra papirkant */
.forside{{background:#0B0B0B}}
.forside .r{{position:absolute;left:8mm;bottom:8mm;height:22mm}}
.forside .m{{position:absolute;right:8mm;top:8mm;font-family:'IBM Plex Mono','Courier New',monospace;font-size:5.5pt;letter-spacing:.08em;color:#B9B6AE;text-transform:uppercase}}
.bakside{{background:#F4F3EF;color:#0B0B0B}}
.bakside .ord{{position:absolute;left:8mm;top:7.4mm;height:4.1mm}}
.fals{{position:absolute;left:8mm;right:8mm;top:14.5mm;height:1.6mm}}
.fals i{{position:absolute;left:0;top:0;width:78%;height:100%;border-top:.25mm solid #0B0B0B;border-right:.25mm solid #0B0B0B}}
.fals b{{position:absolute;left:78%;right:0;bottom:0;border-bottom:.25mm solid #0B0B0B}}
.navn{{position:absolute;left:8mm;bottom:8mm}}
.navn p:first-child{{font-family:Archivo,Arial,sans-serif;font-stretch:112%;font-weight:500;font-size:7.5pt;letter-spacing:.16em;text-transform:uppercase}}
.navn p+p{{font-family:'IBM Plex Mono','Courier New',monospace;font-size:5.5pt;letter-spacing:.06em;text-transform:uppercase;color:#6B6A66;margin-top:.8mm}}
.kontakt{{position:absolute;right:8mm;bottom:8mm;text-align:right;font-family:'IBM Plex Mono','Courier New',monospace;font-size:6pt;line-height:1.65;letter-spacing:.03em}}
</style></head><body>
<section class="side forside">
  <svg class="r" viewBox="{R_VB}"><path fill="#F4F3EF" d="{R_D}"/></svg>
  <div class="m">Arkitekter</div>
</section>
<section class="side bakside">
  {TEKSTLOGO}
  <div class="fals"><i></i><b></b></div>
  <div class="navn"><p>{NAVN}</p><p>{TITTEL}</p></div>
  <div class="kontakt">{TLF}<br>post@randfals.com<br>randfals.com</div>
</section>
</body></html>"""

out = ROOT / "visittkort"
(out / "visittkort.html").write_text(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(device_scale_factor=4)
    pg.goto((out / "visittkort.html").as_uri()); pg.wait_for_timeout(1200)
    pg.pdf(path=str(out / "randfals-visittkort-trykk.pdf"), width="91mm", height="61mm", print_background=True)
    # forhåndsvisning (beskåret til 85×55)
    pg.set_viewport_size({"width": 1200, "height": 900})
    pg.emulate_media(media="screen")
    for i, sel in enumerate([".forside", ".bakside"]):
        el = pg.locator(sel)
        bb = el.bounding_box(); bleed = bb["width"] * 3 / 91
        pg.screenshot(path=str(out / f"forhandsvisning-{i+1}.png"),
                      clip={"x": bb["x"] + bleed, "y": bb["y"] + bleed, "width": bb["width"] - 2 * bleed, "height": bb["height"] - 2 * bleed},
                      scale="device")
    b.close()
print("ok")
