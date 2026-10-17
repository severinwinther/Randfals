"""Bygger fonten «Randfals Modul» fra 4×5-rutenettet.

Hver glyf er beskrevet i moduler (1 modul = strektykkelse), y opp, grunnlinje = 0,
versalhøyde = 5. Operasjoner: ('+', form) legger til, ('-', form) trekker fra.
Form = rektangel (x0, y0, x1, y1) eller polygon [(x, y), ...].
"""
import pathops
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont

U = 140          # font units per modul
SB = 70          # sidespacing på hver side (½ modul)
UPM = 1000

TR = (3, 4, 4, 5)          # falsen: øvre høyre hjørne (4 bred glyf)
BLOCK = (0, 0, 4, 5)
LEG = [(2, 2), (3, 2), (4, 0), (3, 0)]   # R-ens skrå bein


def blk(w):
    return (0, 0, w, 5)


G = {}  # navn -> (bredde i moduler, ops, unicode-liste)


def g(name, w, ops, *cps):
    G[name] = (w, ops, list(cps))


# ---------- Versaler ----------
g("A", 4, [("+", BLOCK), ("-", (0, 4, 1, 5)), ("-", (1, 3, 3, 4)), ("-", (1, 0, 3, 2))], 0x41, 0x61)
g("B", 4, [("+", BLOCK), ("-", TR), ("-", (1, 3, 3, 4)), ("-", (1, 1, 3, 2))], 0x42, 0x62)
g("C", 4, [("+", BLOCK), ("-", (1, 1, 4, 4))], 0x43, 0x63)
g("D", 4, [("+", BLOCK), ("-", TR), ("-", (1, 1, 3, 4))], 0x44, 0x64)
g("E", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (1, 1, 4, 2)), ("-", (3, 2, 4, 3))], 0x45, 0x65)
g("F", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (3, 2, 4, 3)), ("-", (1, 0, 4, 2))], 0x46, 0x66)
g("G", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (1, 1, 2, 3)), ("-", (2, 1, 3, 2))], 0x47, 0x67)
g("H", 4, [("+", BLOCK), ("-", (1, 3, 3, 5)), ("-", (1, 0, 3, 2))], 0x48, 0x68)
g("I", 1, [("+", (0, 0, 1, 5))], 0x49, 0x69)
g("J", 4, [("+", BLOCK), ("-", (0, 2, 3, 5)), ("-", (1, 1, 3, 2))], 0x4A, 0x6A)
g("K", 4, [("+", (0, 0, 1, 5)), ("+", (1, 2, 3, 3)),
           ("+", [(2, 3), (3, 3), (4, 5), (3, 5)]), ("+", [(2, 2), (3, 2), (4, 0), (3, 0)])], 0x4B, 0x6B)
g("L", 4, [("+", (0, 0, 1, 5)), ("+", (0, 0, 4, 1))], 0x4C, 0x6C)
g("M", 5, [("+", blk(5)), ("-", (4, 4, 5, 5)), ("-", (1, 0, 2, 4)), ("-", (3, 0, 4, 4))], 0x4D, 0x6D)
g("N", 4, [("+", BLOCK), ("-", TR), ("-", (1, 0, 3, 4))], 0x4E, 0x6E)
g("O", 4, [("+", BLOCK), ("-", (1, 1, 3, 4))], 0x4F, 0x6F)
g("P", 4, [("+", BLOCK), ("-", TR), ("-", (1, 3, 3, 4)), ("-", (1, 0, 4, 2))], 0x50, 0x70)
g("Q", 4, [("+", BLOCK), ("-", (1, 1, 3, 4)), ("+", LEG)], 0x51, 0x71)
g("R", 4, [("+", (0, 2, 4, 5)), ("-", TR), ("-", (1, 3, 3, 4)), ("+", (0, 0, 1, 2)), ("+", LEG)], 0x52, 0x72)
g("S", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (0, 1, 3, 2))], 0x53, 0x73)
g("T", 4, [("+", (0, 4, 4, 5)), ("+", (1.5, 0, 2.5, 4))], 0x54, 0x74)
g("U", 4, [("+", BLOCK), ("-", (1, 1, 3, 5))], 0x55, 0x75)
g("V", 4, [("+", BLOCK), ("-", (1, 1, 3, 5)), ("-", (0, 0, 1, 1)), ("-", (3, 0, 4, 1))], 0x56, 0x76)
g("W", 5, [("+", blk(5)), ("-", (1, 1, 2, 5)), ("-", (3, 1, 4, 5)), ("-", (0, 0, 1, 1)), ("-", (4, 0, 5, 1))], 0x57, 0x77)
g("X", 4, [("+", (1, 2, 3, 3)),
           ("+", [(2, 3), (3, 3), (4, 5), (3, 5)]), ("+", [(1, 3), (2, 3), (1, 5), (0, 5)]),
           ("+", [(2, 2), (3, 2), (4, 0), (3, 0)]), ("+", [(1, 2), (2, 2), (1, 0), (0, 0)])], 0x58, 0x78)
g("Y", 4, [("+", (1, 2, 3, 3)), ("+", (1.5, 0, 2.5, 2)),
           ("+", [(2, 3), (3, 3), (4, 5), (3, 5)]), ("+", [(1, 3), (2, 3), (1, 5), (0, 5)])], 0x59, 0x79)
g("Z", 4, [("+", (0, 4, 4, 5)), ("+", (0, 0, 4, 1)), ("+", [(3, 4), (4, 4), (1, 1), (0, 1)])], 0x5A, 0x7A)
g("AE", 6, [("+", blk(6)), ("-", (0, 4, 1, 5)), ("-", (1, 3, 3, 4)), ("-", (1, 0, 3, 2)),
            ("-", (4, 3, 6, 4)), ("-", (5, 2, 6, 3)), ("-", (4, 1, 6, 2))], 0xC6, 0xE6)
g("Oslash", 4, [("+", BLOCK), ("-", (1, 1, 3, 4)), ("+", [(0.5, 0), (1.5, 0), (3.5, 5), (2.5, 5)])], 0xD8, 0xF8)
g("Aring", 4, [("+", BLOCK), ("-", (0, 4, 1, 5)), ("-", (1, 3, 3, 4)), ("-", (1, 0, 3, 2)),
               ("+", (1.5, 5.5, 2.5, 6.5))], 0xC5, 0xE5)
g("Adieresis", 4, [("+", BLOCK), ("-", (0, 4, 1, 5)), ("-", (1, 3, 3, 4)), ("-", (1, 0, 3, 2)),
                   ("+", (0.5, 5.5, 1.5, 6.5)), ("+", (2.5, 5.5, 3.5, 6.5))], 0xC4, 0xE4)
g("Odieresis", 4, [("+", BLOCK), ("-", (1, 1, 3, 4)),
                   ("+", (0.5, 5.5, 1.5, 6.5)), ("+", (2.5, 5.5, 3.5, 6.5))], 0xD6, 0xF6)
g("Udieresis", 4, [("+", BLOCK), ("-", (1, 1, 3, 5)),
                   ("+", (0.5, 5.5, 1.5, 6.5)), ("+", (2.5, 5.5, 3.5, 6.5))], 0xDC, 0xFC)
g("Eacute", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (1, 1, 4, 2)), ("-", (3, 2, 4, 3)),
                ("+", [(1.5, 5.5), (2.5, 5.5), (3.5, 6.5), (2.5, 6.5)])], 0xC9, 0xE9)

# ---------- Tall ----------
g("zero", 3, [("+", blk(3)), ("-", (1, 1, 2, 4))], 0x30)
g("one", 2, [("+", (1, 0, 2, 5)), ("+", (0, 4, 1, 5))], 0x31)
g("two", 4, [("+", BLOCK), ("-", (0, 3, 3, 4)), ("-", (1, 1, 4, 2))], 0x32)
g("three", 4, [("+", BLOCK), ("-", (0, 3, 3, 4)), ("-", (0, 1, 3, 2))], 0x33)
g("four", 4, [("+", (0, 2, 1, 5)), ("+", (0, 2, 4, 3)), ("+", (2, 0, 3, 5))], 0x34)
g("five", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (0, 1, 3, 2)), ("-", (3, 2, 4, 3))], 0x35)
g("six", 4, [("+", BLOCK), ("-", (1, 3, 4, 4)), ("-", (1, 1, 3, 2))], 0x36)
g("seven", 4, [("+", (0, 4, 4, 5)), ("+", [(3, 4), (4, 4), (2, 0), (1, 0)])], 0x37)
g("eight", 4, [("+", BLOCK), ("-", (1, 3, 3, 4)), ("-", (1, 1, 3, 2))], 0x38)
g("nine", 4, [("+", BLOCK), ("-", (1, 3, 3, 4)), ("-", (0, 1, 3, 2))], 0x39)

# ---------- Tegnsetting ----------
g("space", 2, [], 0x20, 0xA0)
g("period", 1, [("+", (0, 0, 1, 1))], 0x2E)
g("comma", 1, [("+", (0, 0, 1, 1)), ("+", [(0.5, 0), (1, 0), (0.5, -0.75), (0, -0.75)])], 0x2C)
g("colon", 1, [("+", (0, 0, 1, 1)), ("+", (0, 3, 1, 4))], 0x3A)
g("semicolon", 1, [("+", (0, 0, 1, 1)), ("+", [(0.5, 0), (1, 0), (0.5, -0.75), (0, -0.75)]), ("+", (0, 3, 1, 4))], 0x3B)
g("exclam", 1, [("+", (0, 2, 1, 5)), ("+", (0, 0, 1, 1))], 0x21)
g("question", 4, [("+", (0, 4, 4, 5)), ("+", (3, 2, 4, 5)), ("+", (1.5, 2, 4, 3)), ("+", (1.5, 0, 2.5, 1))], 0x3F)
g("quotesingle", 1, [("+", (0, 3.5, 1, 5))], 0x27, 0x2019, 0x2018)
g("quotedbl", 3, [("+", (0, 3.5, 1, 5)), ("+", (2, 3.5, 3, 5))], 0x22, 0x201C, 0x201D)
g("hyphen", 2, [("+", (0, 2, 2, 3))], 0x2D, 0x2010)
g("endash", 3, [("+", (0, 2, 3, 3))], 0x2013)
g("emdash", 5, [("+", (0, 2, 5, 3))], 0x2014)
g("underscore", 4, [("+", (0, -1, 4, -0.5))], 0x5F)
g("slash", 3, [("+", [(0, 0), (1, 0), (3, 5), (2, 5)])], 0x2F)
g("periodcentered", 1, [("+", (0, 2, 1, 3))], 0xB7)
g("plus", 3, [("+", (1, 1, 2, 4)), ("+", (0, 2, 3, 3))], 0x2B)
g("multiply", 3, [("+", [(0, 1), (1, 1), (3, 4), (2, 4)]), ("+", [(2, 1), (3, 1), (1, 4), (0, 4)])], 0xD7)
g("equal", 3, [("+", (0, 1, 3, 2)), ("+", (0, 3, 3, 4))], 0x3D)
g("bracketleft", 2, [("+", (0, -0.5, 2, 5.5)), ("-", (1, 0.5, 2, 4.5))], 0x5B, 0x28)
g("bracketright", 2, [("+", (0, -0.5, 2, 5.5)), ("-", (0, 0.5, 1, 4.5))], 0x5D, 0x29)
g("guillemotleft", 3, [("+", [(1, 2), (2, 2), (3, 0.5), (2, 0.5)]), ("+", [(1, 3), (2, 3), (3, 4.5), (2, 4.5)]), ("+", (0, 2, 2, 3))], 0xAB)
g("guillemotright", 3, [("+", [(1, 2), (2, 2), (1, 0.5), (0, 0.5)]), ("+", [(1, 3), (2, 3), (1, 4.5), (0, 4.5)]), ("+", (1, 2, 3, 3))], 0xBB)
g("arrowright", 5, [("+", (0, 2, 4, 3)), ("+", [(3, 3), (4, 3), (2, 5), (1, 5)]), ("+", [(3, 2), (4, 2), (2, 0), (1, 0)]), ("+", (3, 2, 5, 3))], 0x2192)
g("numbersign", 4, [("+", (1, 0, 2, 5)), ("+", (2.5, 0, 3.5, 5)), ("+", (0, 1, 4, 2)), ("+", (0, 3, 4, 4))], 0x23)
g("percent", 4, [("+", (0, 3, 1, 5)), ("+", (3, 0, 4, 2)), ("+", [(0, 0), (1, 0), (4, 5), (3, 5)])], 0x25)
g("at", 5, [("+", (0, 4, 5, 5)), ("+", (0, 0, 1, 5)), ("+", (4, 1, 5, 5)), ("+", (0, 0, 4, 1)),
            ("+", (2, 1, 3, 3)), ("+", (2, 1, 5, 2))], 0x40)
g("asterisk", 3, [("+", (1, 2.5, 2, 5)), ("+", [(0, 3), (1, 3), (3, 4.5), (2, 4.5)]), ("+", [(2, 3), (3, 3), (1, 4.5), (0, 4.5)])], 0x2A)
g("notdef", 4, [("+", BLOCK), ("-", (1, 1, 3, 4))])


def shape_path(shape):
    p = pathops.Path()
    pen = p.getPen()
    if isinstance(shape, tuple):
        x0, y0, x1, y1 = shape
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    else:
        pts = shape
    pts = [(SB + x * U, y * U) for x, y in pts]
    pen.moveTo(pts[0])
    for pt in pts[1:]:
        pen.lineTo(pt)
    pen.closePath()
    return p


def glyph_path(ops):
    acc = pathops.Path()
    for op, shape in ops:
        sp = shape_path(shape)
        acc = pathops.op(acc, sp, pathops.PathOp.UNION if op == "+" else pathops.PathOp.DIFFERENCE)
    return acc


def build(flavor_cff=False):
    order = [".notdef"] + [n for n in G if n != "notdef"]
    cmap, advs, outlines = {}, {}, {}
    for name in order:
        key = "notdef" if name == ".notdef" else name
        w, ops, cps = G[key]
        for cp in cps:
            cmap[cp] = name
        advs[name] = int(w * U + 2 * SB)
        path = glyph_path(ops)
        path.simplify(fix_winding=True, clockwise=not flavor_cff)
        outlines[name] = path

    fb = FontBuilder(UPM, isTTF=not flavor_cff)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    if flavor_cff:
        cs = {}
        for name in order:
            pen = T2CharStringPen(advs[name], None)
            outlines[name].draw(pen)
            cs[name] = pen.getCharString()
        fb.setupCFF("RandfalsModul-Regular", {"FullName": "Randfals Modul"}, cs, {})
    else:
        glyphs = {}
        for name in order:
            pen = TTGlyphPen(None)
            outlines[name].draw(pen)
            glyphs[name] = pen.glyph()
        fb.setupGlyf(glyphs)
    metrics = {}
    for name in order:
        lsb = 0
        if not outlines[name].bounds is None:
            try:
                lsb = int(outlines[name].bounds[0])
            except Exception:
                lsb = 0
        metrics[name] = (advs[name], lsb)
    fb.setupHorizontalMetrics(metrics)
    asc, desc = 920, -220
    fb.setupHorizontalHeader(ascent=asc, descent=desc, lineGap=120)
    fb.setupNameTable({
        "familyName": "Randfals Modul",
        "styleName": "Regular",
        "uniqueFontIdentifier": "RandfalsModul-Regular-1.0",
        "fullName": "Randfals Modul",
        "psName": "RandfalsModul-Regular",
        "version": "Version 1.000",
        "copyright": "© 2026 RANDFALS",
        "designer": "RANDFALS",
    })
    fb.setupOS2(sTypoAscender=asc, sTypoDescender=desc, sTypoLineGap=120,
                usWinAscent=asc, usWinDescent=-desc, sCapHeight=700, sxHeight=700,
                achVendID="RNDF", fsType=0)
    fb.setupPost()
    if not flavor_cff:
        pass
    return fb.font


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "font")
    os.makedirs(out, exist_ok=True)
    ttf = build(False)
    ttf.save(f"{out}/RandfalsModul-Regular.ttf")
    otf = build(True)
    otf.save(f"{out}/RandfalsModul-Regular.otf")
    for flav in ("woff2", "woff"):
        f = TTFont(f"{out}/RandfalsModul-Regular.ttf")
        f.flavor = flav
        f.save(f"{out}/RandfalsModul-Regular.{flav}")
    print("glyfer:", len(G), "->", os.listdir(out))
