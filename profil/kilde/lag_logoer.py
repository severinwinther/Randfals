import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
f=TTFont('font/RandfalsModul-Regular.ttf'); gs=f.getGlyphSet(); cmap=f.getBestCmap(); hm=f['hmtx']
def path(text, gap=0):
    pen=SVGPathPen(gs); x=0
    for ch in text:
        n=cmap[ord(ch)]
        gs[n].draw(TransformPen(pen,(1,0,0,-1,x-70,700)))
        x+=hm[n][0]+gap
    return pen.getCommands(), x-gap-140
def svg(text,fill,name,gap=0,pad=0,bg=None):
    d,w=path(text,gap); W=w+2*pad; H=700+2*pad
    bgr=f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ''
    open(f'logo/{name}.svg','w').write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}">{bgr}<path transform="translate({pad},{pad})" fill="{fill}" d="{d}"/></svg>')
for col,suf in (('#0B0B0B','kull'),('#F4F3EF','kalk')):
    svg('R',col,f'randfals-R-{suf}')
    svg('RANDFALS',col,f'randfals-ordmerke-{suf}')
print(open('logo/randfals-R-kull.svg').read()[:300])
