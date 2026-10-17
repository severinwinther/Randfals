"""Tre gjentakbare mønstre fra modulrutenettet. Hver fil er én sømløs rapport (tile)."""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "monster"
R_D = re.search(r' d="([^"]+)"', (ROOT / "logo/randfals-R-kull.svg").read_text()).group(1)
KULL, KALK = "#0B0B0B", "#F4F3EF"
M = 20  # px per modul i rapporten


def falsfelt(fg, bg):
    # 2×2 celler à 6 moduler; 4×4-blokk med fals, rotert så falsene møtes i midten
    c = 6 * M
    parts = [f'<rect width="{2*c}" height="{2*c}" fill="{bg}"/>']
    blk = f"M{M} {M}H{4*M}V{2*M}H{5*M}V{5*M}H{M}Z"  # fals øverst til høyre
    for i, (ox, oy, rot) in enumerate([(0, 0, 90), (c, 0, 180), (0, c, 0), (c, c, 270)]):
        parts.append(f'<path fill="{fg}" transform="translate({ox},{oy}) rotate({rot} {c/2} {c/2})" d="{blk}"/>')
    return 2 * c, 2 * c, "".join(parts)


def trapp(fg, bg):
    # linjer med en fals (spor) som flytter seg én modul for hver rad — sømløs i begge retninger
    rows, gap, w = 12, 1.5 * M, 12 * M
    parts = [f'<rect width="{w}" height="{rows*gap}" fill="{bg}"/>']
    for i in range(rows):
        y, s = i * gap + 0.25 * M, i * M
        parts.append(f'<path fill="none" stroke="{fg}" stroke-width="1.5" stroke-linejoin="miter" d="M0 {y}H{s}V{y+0.75*M}H{s+M}V{y}H{w}"/>')
    return w, rows * gap, "".join(parts)


def rfelt(fg, bg):
    # R-merket i halvforskjøvet rapport
    sc = (2 * M) / 560  # R = 2 moduler bred i rapporten
    w, h = 6 * M, 8 * M
    r = lambda x, y: f'<path fill="{fg}" transform="translate({x},{y}) scale({sc})" d="{R_D}"/>'
    return w, h, f'<rect width="{w}" height="{h}" fill="{bg}"/>' + r(M, M) + r(4 * M, 5 * M)


SETT = {"falsfelt": falsfelt, "trapp": trapp, "r-felt": rfelt}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(device_scale_factor=2)
    for navn, fn in SETT.items():
        for farge, (fg, bg) in {"kull-paa-kalk": (KULL, KALK), "kalk-paa-kull": (KALK, KULL)}.items():
            w, h, body = fn(fg, bg)
            tile = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
            (OUT / f"randfals-monster-{navn}-{farge}.svg").write_text(tile)
            # flate til visning og bruk: 1600 × 1000 px
            uri = "data:image/svg+xml;utf8," + tile.replace("#", "%23").replace('"', "'")
            pg.set_viewport_size({"width": 1600, "height": 1000})
            pg.set_content(f'<body style="margin:0;width:1600px;height:1000px;background:url(&quot;{uri}&quot;)"></body>')
            pg.screenshot(path=str(OUT / f"randfals-monster-{navn}-{farge}.png"))
    b.close()
print("ok")
