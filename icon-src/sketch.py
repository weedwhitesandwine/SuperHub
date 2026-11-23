"""Pencil-sketch icons for SuperHub, in the style of atelier.svg / keywords.svg.

    python sketch.py OUTDIR [name ...]

Each icon is a list of parts on a 1024 canvas: (shape svg, fill) where fill is
'dark' | 'mid' | 'light' | 'white' | None, plus optional stroke width. Every part
gets a hatched fill and a doubled, wobbly pencil outline. SVGs are written to
OUTDIR; build.sh turns them into the 280 px PNGs the plugin uses.
"""
import os, sys

DEFS = """<defs>
<pattern id="hD" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><line x1="0" y1="4" x2="9" y2="4" stroke="#2b2b2b" stroke-width="3.2"/></pattern>
<pattern id="hM" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><line x1="0" y1="6" x2="12" y2="6" stroke="#3a3a3a" stroke-width="2.4"/></pattern>
<pattern id="hL" width="15" height="15" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><line x1="0" y1="7" x2="15" y2="7" stroke="#8a8a8a" stroke-width="1.3"/></pattern>
<filter id="pA" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1124" height="1124"><feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="3" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="7" xChannelSelector="R" yChannelSelector="G" result="b"/><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="g"/><feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 1.55" result="a"/><feComposite in="b" in2="a" operator="in"/></filter>
<filter id="pB" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1124" height="1124"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="11" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="9" xChannelSelector="G" yChannelSelector="R" result="b"/><feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="2" result="g"/><feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2 1.7" result="a"/><feComposite in="b" in2="a" operator="in"/></filter>
<filter id="hF" filterUnits="userSpaceOnUse" x="-50" y="-50" width="1124" height="1124"><feTurbulence type="fractalNoise" baseFrequency="0.05" numOctaves="2" seed="5" result="w"/><feDisplacementMap in="SourceGraphic" in2="w" scale="4" xChannelSelector="R" yChannelSelector="G" result="b"/><feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="1" seed="9" result="g"/><feColorMatrix in="g" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.5" result="a"/><feComposite in="b" in2="a" operator="in"/></filter>
<clipPath id="ball"><circle cx="512" cy="512" r="322"/></clipPath>
</defs>"""
FILL = {'dark': 'url(#hD)', 'mid': 'url(#hM)', 'light': 'url(#hL)'}


def part(shape, fill=None, w=16, line=False):
    """One sketched part. `shape` is an SVG element string without fill/stroke.
    line=True: an open stroke only (no fill, no knock-out)."""
    out = []
    if not line:
        out.append(shape.replace('/>', ' fill="#fff"/>'))  # knock out what's behind
        if fill in FILL:
            out.append(f'<g filter="url(#hF)">{shape.replace("/>", f" fill=\"{FILL[fill]}\"/>")}</g>')
    out.append(f'<g fill="none" stroke="#222" stroke-linejoin="round" stroke-linecap="round">'
               f'<g filter="url(#pA)" stroke-width="{w}">{shape}</g>'
               f'<g filter="url(#pB)" stroke-width="{max(4, w * 0.5):.1f}" opacity="0.85" transform="translate(3,-2)">{shape}</g></g>')
    return ''.join(out)


def svg(parts):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">{DEFS}<rect width="1024" height="1024" fill="#fff"/>{"".join(parts)}</svg>'


def rect(x, y, w, h, r=16): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>'
def circ(cx, cy, r): return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
def path(d): return f'<path d="{d}"/>'
def line(x1, y1, x2, y2): return f'<path d="M{x1} {y1} L{x2} {y2}"/>'
SPARK = 'M0 -46 Q7 -7 46 0 Q7 7 0 46 Q-7 7 -46 0 Q-7 -7 0 -46 Z'
def spark(x, y, s=1.0):
    # scale the coordinates, not the shape, so the pencil line keeps its width
    import re
    d = re.sub(r'(-?\d+(?:\.\d+)?) (-?\d+(?:\.\d+)?)', lambda m: f'{x + float(m[1]) * s:.0f} {y + float(m[2]) * s:.0f}', SPARK)
    return f'<path d="{d}"/>'


ICONS = {}
def icon(f):
    ICONS[f.__name__] = f
    return f


@icon
def folder():
    return [part(path('M170 300 Q170 270 200 270 L400 270 L450 320 L824 320 Q854 320 854 350 L854 760 Q854 790 824 790 L200 790 Q170 790 170 760 Z'), 'mid'),
            part(path('M170 420 Q170 390 200 390 L824 390 Q854 390 854 420 L854 760 Q854 790 824 790 L200 790 Q170 790 170 760 Z'), 'light')]


@icon
def document():
    return [part(path('M260 150 L640 150 L780 290 L780 870 Q780 890 760 890 L280 890 Q260 890 260 870 Z'), 'light'),
            part(path('M640 150 L640 290 L780 290 Z'), 'mid', 9),
            part(line(340, 420, 700, 420), line=True, w=14), part(line(340, 510, 700, 510), line=True, w=14),
            part(line(340, 600, 700, 600), line=True, w=14), part(line(340, 690, 560, 690), line=True, w=14)]


@icon
def todo():
    p = [part(rect(250, 170, 524, 700, 26), 'light'), part(rect(400, 130, 224, 90, 22), 'dark')]
    for i, y in enumerate((330, 490, 650)):
        p.append(part(rect(320, y, 90, 90, 14), None, 10))
        if i < 2:
            p.append(part(path(f'M335 {y+45} L360 {y+75} L415 {y-5}'), line=True, w=16))
        p.append(part(line(460, y + 45, 700, y + 45), line=True, w=16))
    return p


import math


@icon
def settings():
    pts = []
    for i in range(8):
        a0 = i * math.pi / 4
        for da, r in ((-0.26, 300), (-0.17, 370), (0.17, 370), (0.26, 300)):
            a = a0 + da
            pts.append((512 + r * math.cos(a), 512 + r * math.sin(a)))
    d = 'M' + ' L'.join(f'{x:.0f} {y:.0f}' for x, y in pts) + ' Z'
    return [part(path(d), 'mid'), part(circ(512, 512, 120), 'white')]


@icon
def globe():
    return [part(circ(512, 512, 330), 'light'),
            part('<ellipse cx="512" cy="512" rx="140" ry="330"/>', line=True, w=12),
            part(line(512, 182, 512, 842), line=True, w=12),
            part(line(182, 512, 842, 512), line=True, w=12),
            part(path('M232 360 Q512 410 792 360'), line=True, w=12),
            part(path('M232 664 Q512 614 792 664'), line=True, w=12)]


@icon
def book():
    return [part(path('M512 300 Q380 230 170 250 L170 780 Q380 760 512 830 Z'), 'light'),
            part(path('M512 300 Q644 230 854 250 L854 780 Q644 760 512 830 Z'), 'light'),
            part(path('M240 370 Q350 360 450 400'), line=True, w=11), part(path('M240 470 Q350 460 450 500'), line=True, w=11),
            part(path('M240 570 Q350 560 450 600'), line=True, w=11), part(path('M784 370 Q674 360 574 400'), line=True, w=11),
            part(path('M784 470 Q674 460 574 500'), line=True, w=11), part(path('M784 570 Q674 560 574 600'), line=True, w=11)]


@icon
def bible():
    return [part(path('M300 180 L760 180 L760 800 L300 800 Q250 800 250 750 L250 230 Q250 180 300 180 Z'), 'dark'),
            part(path('M250 750 Q250 860 300 860 L760 860 L760 800 L300 800 Q250 800 250 750 Z'), 'white', 12),
            part(rect(470, 290, 70, 380, 10), 'white', 12), part(rect(380, 400, 250, 70, 10), 'white', 12)]


@icon
def inbox():
    return [part(path('M200 560 L310 330 L714 330 L824 560 L824 800 Q824 830 794 830 L230 830 Q200 830 200 800 Z'), 'light'),
            part(path('M200 560 L380 560 Q400 640 512 640 Q624 640 644 560 L824 560'), line=True, w=14),
            part(path('M512 130 L512 450'), line=True, w=20), part(path('M420 370 L512 460 L604 370'), line=True, w=20)]


@icon
def export():
    return [part(path('M200 520 L200 800 Q200 830 230 830 L794 830 Q824 830 824 800 L824 520'), line=True, w=16),
            part(rect(300, 560, 424, 180, 20), 'mid'),
            part(path('M512 470 L512 140'), line=True, w=20), part(path('M420 230 L512 140 L604 230'), line=True, w=20)]


@icon
def heart():
    return [part(path('M512 830 Q250 640 190 480 Q140 300 300 240 Q440 200 512 340 Q584 200 724 240 Q884 300 834 480 Q774 640 512 830 Z'), 'mid')]


@icon
def sports():
    pent = lambda cx, cy, r, rot=-90: 'M' + ' L'.join(f'{cx + r * math.cos(math.radians(rot + 72 * k)):.0f} {cy + r * math.sin(math.radians(rot + 72 * k)):.0f}' for k in range(5)) + ' Z'
    p = [part(circ(512, 512, 330), 'light'), part(path(pent(512, 512, 110)), 'dark', 12)]
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        x1, y1 = 512 + 110 * math.cos(a), 512 + 110 * math.sin(a)
        x2, y2 = 512 + 235 * math.cos(a), 512 + 235 * math.sin(a)
        p.append(part(line(f'{x1:.0f}', f'{y1:.0f}', f'{x2:.0f}', f'{y2:.0f}'), line=True, w=12))
        p.append('<g clip-path="url(#ball)">' + part(path(pent(512 + 300 * math.cos(a), 512 + 300 * math.sin(a), 70, -90 + 72 * k + 36)), 'dark', 10) + '</g>')
    p.append(part(circ(512, 512, 330), line=True, w=16))
    return p


@icon
def flag():
    return [part(rect(230, 150, 34, 740, 14), 'dark', 10),
            part(path('M264 200 Q420 150 560 210 Q700 270 830 210 L830 600 Q700 660 560 600 Q420 540 264 590 Z'), 'light'),
            part(circ(550, 400, 100), 'dark', 12)]


@icon
def palette():
    return [part(path('M512 180 Q820 180 850 440 Q870 600 720 600 Q620 600 640 690 Q660 820 520 840 Q220 840 180 560 Q160 200 512 180 Z'), 'light'),
            part(circ(390, 360, 50), 'dark', 10), part(circ(560, 300, 50), 'mid', 10), part(circ(720, 400, 50), 'dark', 10),
            part(circ(330, 560, 50), 'mid', 10), part(circ(500, 690, 60), 'white', 10)]


@icon
def lists():
    p = [part(rect(250, 150, 524, 730, 22), 'light')]
    for y in (300, 430, 560, 690):
        p.append(part(circ(340, y, 26), 'dark', 9))
        p.append(part(line(400, y, 690, y), line=True, w=14))
    return p


@icon
def clock():
    return [part(circ(512, 520, 320), 'light'), part(circ(512, 520, 250), 'white', 10),
            part(path('M512 520 L512 360'), line=True, w=20), part(path('M512 520 L630 590'), line=True, w=20),
            part(circ(512, 520, 22), 'dark', 8)]



@icon
def clips():
    """Note Clips: a lassoed scrap of handwriting and scissors."""
    return [part(path('M200 300 Q180 170 400 180 Q700 170 760 280 Q820 420 640 470 Q420 520 260 470 Q170 430 200 300 Z'), 'light'),
            part(path('M270 330 Q320 280 360 330 Q400 380 440 320 Q480 270 520 330 Q560 380 600 320 Q640 280 680 330'), line=True, w=12),
            part(circ(340, 760, 80), 'white', 14), part(circ(560, 800, 80), 'white', 14),
            part(path('M395 700 L700 470'), line=True, w=18), part(path('M500 740 L470 470'), line=True, w=18)]


STAR = 'M0 -150 L44 -48 L150 -46 L68 22 L96 130 L0 68 L-96 130 L-68 22 L-150 -46 L-44 -48 Z'


@icon
def starpage():
    """Starred pages: a page with a drawn star."""
    return [part(path('M260 150 L640 150 L780 290 L780 870 Q780 890 760 890 L280 890 Q260 890 260 870 Z'), 'light'),
            part(path('M640 150 L640 290 L780 290 Z'), 'mid', 9),
            part(f'<path transform="translate(520,560) scale(1.35)" d="{STAR}"/>', 'dark', 14)]


@icon
def sparkle():
    return [part(spark(470, 560, 6.0), 'light', 14), part(spark(770, 250, 2.4), 'mid', 11), part(spark(250, 230, 1.6), 'light', 9)]



def plus_badge(cx, cy, r=120):
    """A round badge with a plus, drawn over the corner of a page."""
    return [part(circ(cx, cy, r), 'white', 16),
            part(line(cx, cy - r * 0.55, cx, cy + r * 0.55), line=True, w=22),
            part(line(cx - r * 0.55, cy, cx + r * 0.55, cy), line=True, w=22)]


@icon
def newnote():
    """New note: a spiral notebook with a plus."""
    p = [part(rect(250, 170, 470, 650, 26), 'light')]
    for y in (250, 360, 470, 580, 690):
        p.append(part(f'<ellipse cx="250" cy="{y}" rx="44" ry="22"/>', line=True, w=12))
    for y in (300, 390, 480):
        p.append(part(line(340, y, 620, y), line=True, w=12))
    return p + plus_badge(690, 770)


@icon
def newdoc():
    """New document: a page with a folded corner and a plus."""
    return [part(path('M260 150 L600 150 L740 290 L740 850 Q740 870 720 870 L280 870 Q260 870 260 850 Z'), 'light'),
            part(path('M600 150 L600 290 L740 290 Z'), 'mid', 9),
            part(line(340, 400, 640, 400), line=True, w=12), part(line(340, 490, 640, 490), line=True, w=12),
            part(line(340, 580, 540, 580), line=True, w=12)] + plus_badge(700, 790)


@icon
def plus():
    return [part(path('M400 170 L624 170 L624 400 L854 400 L854 624 L624 624 L624 854 L400 854 L400 624 L170 624 L170 400 L400 400 Z'), 'mid')]

def frame(w=1720, h=600, b=46, m=26, hatch="hM", ow=14, iw=10):
    """Picture frame for the clock: a hatched band between two pencil outlines."""
    band = (f'M{m} {m + 28} Q{m} {m} {m + 28} {m} L{w - m - 28} {m} Q{w - m} {m} {w - m} {m + 28} L{w - m} {h - m - 28} '
            f'Q{w - m} {h - m} {w - m - 28} {h - m} L{m + 28} {h - m} Q{m} {h - m} {m} {h - m - 28} Z '
            f'M{m + b} {m + b} L{m + b} {h - m - b} L{w - m - b} {h - m - b} L{w - m - b} {m + b} Z')
    parts = [f'<path d="{band}" fill="#fff" fill-rule="evenodd"/>',
             f'<g filter="url(#hF)"><path d="{band}" fill="url(#{hatch})" fill-rule="evenodd"/></g>',
             part(rect(m, m, w - 2 * m, h - 2 * m, 28), line=True, w=ow),
             part(rect(m + b, m + b, w - 2 * (m + b), h - 2 * (m + b), 8), line=True, w=iw)]
    body = "".join(parts).replace('width="1124" height="1124"', f'width="{w + 100}" height="{h + 100}"')
    defs = DEFS.replace('width="1124" height="1124"', f'width="{w + 100}" height="{h + 100}"')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs}{body}</svg>'


SVG_ORDER = list(ICONS)

if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    # pframe: the light frame round each recent-page preview (3:4 page inside a 26 px band)
    frames = {'frame': lambda: frame(), 'pframe': lambda: frame(400, 520, 30, 12, 'hL', 5, 3.5)}
    for name in sys.argv[2:] or list(ICONS) + list(frames):
        open(os.path.join(out, name + '.svg'), 'w').write(frames[name]() if name in frames else svg(ICONS[name]()))
        print(name)
