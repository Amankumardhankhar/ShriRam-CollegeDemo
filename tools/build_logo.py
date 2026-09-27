#!/usr/bin/env python3
"""Build the SRGI logo as a self-contained SVG (text converted to outlines).

Clean vector redraw of the college's SRGI badge: yellow disc, red/black rings,
red "S-J" monogram + "RGI" with white/dark outline, "HARYANA" curved along the bottom.
Needs fontTools and Montserrat (Fedora: julietaula-montserrat-fonts).
Output: wp-content/themes/shriram-college/assets/images/srgi-logo.svg
"""
import math
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "wp-content", "themes", "shriram-college", "assets", "images", "srgi-logo.svg")
FONTS = "/usr/share/fonts/julietaula-montserrat-fonts"

YELLOW, RED, INK, WHITE = "#FFE10A", "#E1161C", "#161616", "#FFFFFF"
C = 100  # centre of the 200x200 canvas


class Font:
    def __init__(self, name):
        self.f = TTFont(os.path.join(FONTS, name))
        self.gs = self.f.getGlyphSet()
        self.cmap = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm

    def advance(self, ch, size):
        return self.f["hmtx"][self.cmap[ord(ch)]][0] * size / self.upm

    def glyph(self, ch, size, a, b, c, d, e, f):
        """Glyph outline under the affine (a b c d e f), font units scaled to `size`, y flipped."""
        s = size / self.upm
        pen = SVGPathPen(self.gs)
        # compose: font units -> scaled, y-down -> caller's transform
        self.gs[self.cmap[ord(ch)]].draw(TransformPen(pen, (a * s, b * s, -c * s, -d * s, e, f)))
        return pen.getCommands()

    def text(self, s, size, x, y, tracking=0.0):
        out = []
        for ch in s:
            out.append(self.glyph(ch, size, 1, 0, 0, 1, x, y))
            x += self.advance(ch, size) + tracking
        return "".join(out)

    def width(self, s, size, tracking=0.0):
        return sum(self.advance(ch, size) for ch in s) + tracking * (len(s) - 1)


def arc(r, a0, a1):
    """Clockwise arc (SVG angles, degrees; 0 = right, 90 = down)."""
    p = lambda a: (C + r * math.cos(math.radians(a)), C + r * math.sin(math.radians(a)))
    (x0, y0), (x1, y1) = p(a0), p(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.2f} {y0:.2f}A{r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}"


black = Font("Montserrat-Black.otf")
bold = Font("Montserrat-Bold.otf")

# --- Monogram: "S" whose lower half drops into a "J" stem with a hook (stroke centreline) ---
SW = 11.5  # stroke width of the monogram
k = 0.9    # scale of the centreline drawing below
monogram_d = (
    "M42 17A11 11 0 0 0 31 6H14A8 8 0 0 0 6 14V26A8 8 0 0 0 14 34H26A8 8 0 0 1 34 42"
    "V73A11 11 0 0 1 23 84H17A9 9 0 0 1 8 75V72"
)
mono_w = (34 + SW / 2) * k  # right edge of the stem

# --- "RGI" set right of the stem ---
RGI_SIZE = 46
gap = 3.5
rgi_w = black.width("RGI", RGI_SIZE, tracking=-0.5)
group_w = mono_w + gap + rgi_w
mx = C - group_w / 2 - 2  # optical nudge: the S hangs lower-left
my = 46
rgi_x = mx + mono_w + gap
rgi_base = my + 84 * k - 6
rgi_d = black.text("RGI", RGI_SIZE, rgi_x, rgi_base, tracking=-0.5)

# --- "HARYANA" around the bottom, letters upright (tops toward the centre) ---
HR, HSIZE, HTRACK = 72, 11.5, 2.2
total = bold.width("HARYANA", HSIZE, HTRACK)
theta = 90 + math.degrees(total / 2 / HR)  # start angle (left end), walk anticlockwise
haryana = []
for ch in "HARYANA":
    adv = bold.advance(ch, HSIZE)
    mid = theta - math.degrees(adv / 2 / HR)
    rot = math.radians(mid - 90)
    px, py = C + HR * math.cos(math.radians(mid)), C + HR * math.sin(math.radians(mid))
    cos, sin = math.cos(rot), math.sin(rot)
    # local glyph origin sits adv/2 left of the arc point, on the baseline
    ox, oy = px - cos * adv / 2, py - sin * adv / 2
    haryana.append(bold.glyph(ch, HSIZE, cos, sin, -sin, cos, ox, oy))
    theta -= math.degrees((adv + HTRACK) / HR)
haryana_d = "".join(haryana)

mono_tf = f'transform="translate({mx:.2f} {my}) scale({k})"'
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" role="img" aria-labelledby="t">
  <title id="t">SRGI Haryana logo</title>
  <circle cx="100" cy="100" r="96" fill="{YELLOW}"/>
  <!-- rings -->
  <path d="{arc(90, -78, 104)}" fill="none" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  <path d="{arc(83, 112, 290)}" fill="none" stroke="{RED}" stroke-width="8" stroke-linecap="round"/>
  <path d="{arc(82.5, -62, 70)}" fill="none" stroke="{RED}" stroke-width="2.2" stroke-linecap="round"/>
  <path d="{arc(76, 128, 258)}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round"/>
  <!-- monogram: dark keyline, white outline, red fill -->
  <g fill="none" stroke-linejoin="round" stroke-linecap="square" {mono_tf}>
    <path d="{monogram_d}" stroke="{INK}" stroke-width="{SW + 9.5 / k:.2f}"/>
    <path d="{monogram_d}" stroke="{WHITE}" stroke-width="{SW + 5.5 / k:.2f}"/>
  </g>
  <path d="{rgi_d}" fill="none" stroke="{INK}" stroke-width="9.5" stroke-linejoin="round"/>
  <path d="{rgi_d}" fill="{WHITE}" stroke="{WHITE}" stroke-width="5.5" stroke-linejoin="round"/>
  <g fill="none" stroke-linejoin="round" stroke-linecap="square" {mono_tf}>
    <path d="{monogram_d}" stroke="{RED}" stroke-width="{SW}"/>
  </g>
  <path d="{rgi_d}" fill="{RED}"/>
  <path d="{haryana_d}" fill="{INK}"/>
</svg>
"""
with open(OUT, "w") as fh:
    fh.write(svg)
print(f"wrote {OUT} ({len(svg)} bytes)")
