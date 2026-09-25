"""Offline Pillow banner. Run with Python + Pillow 11; no network required."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, S = 1200, 675, 3
NAVY, YELLOW, RED, CREAM, DARK = '#0B4F8A', '#F6B92B', '#E8553F', '#FFF8EC', '#1D2B3A'
FONT = next((Path('C:/Windows/Fonts') / name for name in
             ('meiryob.ttc', 'YuGothB.ttc', 'msgothic.ttc')
             if (Path('C:/Windows/Fonts') / name).is_file()), None)
if FONT is None:
    raise FileNotFoundError('No specified Japanese font found')
im = Image.new('RGB', (W*S, H*S), NAVY)
d = ImageDraw.Draw(im)

def ellipse(box, fill, outline=None, width=1):
    d.ellipse(tuple(round(v*S) for v in box), fill=fill, outline=outline, width=width*S)

# Six enamel-like badges, grouped left and across the lower edge.
badges = [(116, 142, 62, CREAM), (168, 348, 100, RED),
          (96, 560, 61, '#F29BB5'), (314, 544, 78, YELLOW),
          (510, 570, 54, '#FFE3A3'), (687, 514, 68, '#F29BB5')]
shadow = Image.new('RGBA', im.size)
sd = ImageDraw.Draw(shadow)
for x, y, r, color in badges:
    sd.ellipse(((x-r+5)*S, (y-r+12)*S, (x+r+5)*S, (y+r+12)*S), fill=(10, 29, 47, 105))
im.paste(shadow.filter(ImageFilter.GaussianBlur(9*S)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(9*S)))
d = ImageDraw.Draw(im)
for x, y, r, color in badges:
    ellipse((x-r, y-r, x+r, y+r), DARK)
    ellipse((x-r+2, y-r+1, x+r-2, y+r-6), color)
    rim = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    rim = tuple(round(v*.70) for v in rim)
    d.arc(((x-r+8)*S, (y-r+7)*S, (x+r-8)*S, (y+r-9)*S), 25, 135, fill=rim, width=2*S)
    hr = r*.115
    hx, hy = x-r*.36, y-r*.40
    ellipse((hx-hr, hy-hr, hx+hr, hy+hr), '#FFFFFF')

# Short rounded accent and generous clear space around type.
d.rounded_rectangle((300*S, 110*S, 375*S, 121*S), radius=5*S, fill=RED)
TEXT = [('色で、推せる。', (300, 177), 106, YELLOW),
        ('国産カラー缶バッジパーツ', (306, 321), 38, CREAM),
        ('badge-koi.com', (934, 578), 24, CREAM)]
report = []
for text, (x, y), size, color in TEXT:
    font = ImageFont.truetype(str(FONT), size*S, index=0)
    # FreeType's unsupported code point produces the font's missing glyph.
    missing = font.getmask(chr(0x10FFFF))
    missing_signature = (missing.size, bytes(missing))
    for char in text:
        mask = font.getmask(char)
        assert mask.getbbox() is not None, f'Empty glyph: {char!r}'
        assert (mask.size, bytes(mask)) != missing_signature, f'Missing glyph: {char!r}'
    box = d.textbbox((x*S, y*S), text, font=font, anchor='lt')
    assert box[0] >= 60*S and box[1] >= 60*S
    assert box[2] <= (W-60)*S and box[3] <= (H-60)*S
    for bx, by, br, _ in badges:
        nx = max(box[0]/S, min(bx, box[2]/S))
        ny = max(box[1]/S, min(by, box[3]/S))
        assert (nx-bx)**2 + (ny-by)**2 > (br+8)**2, 'Text overlaps badge'
    d.text((x*S, y*S), text, font=font, fill=color, anchor='lt')
    report.append({'text': text, 'top_left': [x, y]})

out = Path(__file__).with_suffix('.png')
im.resize((W, H), Image.Resampling.LANCZOS).save(out, format='PNG')
with Image.open(out) as check:
    assert check.size == (1200, 675) and check.mode == 'RGB' and check.format == 'PNG'
print(json.dumps({'path': str(out), 'size': [W,H], 'mode': 'RGB',
                  'font': str(FONT), 'glyph_check': 'passed', 'text': report}, ensure_ascii=False))
