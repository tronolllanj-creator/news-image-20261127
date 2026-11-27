"""generate_image.py — draws a deterministic 1024x1024 PNG of the
world news of Friday 27 November 2026, using only stdlib + PIL.
Three variants; main() renders the one named on the command line."""


import sys
from PIL import Image, ImageDraw, ImageFont

# Canonical width/height for every variant.
CANVAS = 1024

# Palette (hex -> RGB tuples).
PAPER = (0xF7, 0xF1, 0xE3)
INK = (0x14, 0x21, 0x3D)
RED = (0xC1, 0x27, 0x2D)
NAVY = (0x1B, 0x2A, 0x4A)
TEAL = (0x0E, 0x7C, 0x7B)
GOLD = (0xD9, 0xA4, 0x41)
WHITE = (0xFF, 0xFF, 0xFF)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_bold(size):
    """Return a bold truetype font at the given pixel size."""
    return ImageFont.truetype(FONT_BOLD, int(size))


def load_reg(size):
    """Return a regular truetype font at the given pixel size."""
    return ImageFont.truetype(FONT_REG, int(size))


def wrap_text(draw, text, font, max_width):
    """Greedy word wrap of text to max_width pixels using font for measure.

    Returns a list of lines. An empty max_width or a single token that cannot
    split yields that token on its own line.
    """
    words = text.split()
    lines = []
    current = []
    for word in words:
        trial = " ".join(current + [word]) if current else word
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines or [""]


def draw_wrapped(draw, xy, lines, font, fill, leading=6):
    """Draw a list of lines starting at xy, each stacked `leading` px apart.

    Returns the y coordinate just below the last line (baseline + descent)."""
    x, y = xy
    for i, line in enumerate(lines):
        if i:
            y += leading
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y = bbox[3] + leading
    return y


def rounded_rect(draw, box, radius, fill):
    """Draw a filled rounded rectangle (int coords)."""
    x0, y0, x1, y1 = [int(v) for v in box]
    r = int(radius)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill)


def icon_chess(draw, cx, cy, size, ink=INK):
    """Geometric knight-less chess rook / pawn pictogram drawn from primitives."""
    s = int(size)
    # Simple pawn: disc head, tapered body, base.
    head_r = int(s * 0.26)
    draw.ellipse([cx - head_r, cy - int(s * 0.42), cx + head_r, cy - int(s * 0.42) + 2 * head_r], fill=ink)
    # Neck.
    draw.rectangle([cx - int(s * 0.06), cy - int(s * 0.14), cx + int(s * 0.06), cy + int(s * 0.04)], fill=ink)
    # Body trapezoid.
    draw.polygon(
        [
            (cx - int(s * 0.08), cy + int(s * 0.04)),
            (cx + int(s * 0.08), cy + int(s * 0.04)),
            (cx + int(s * 0.20), cy + int(s * 0.34)),
            (cx - int(s * 0.20), cy + int(s * 0.34)),
        ],
        fill=ink,
    )
    # Base bar.
    draw.rectangle([cx - int(s * 0.28), cy + int(s * 0.34), cx + int(s * 0.28), cy + int(s * 0.44)], fill=ink)


def chip(draw, x, y, label, color, font):
    """Draw a category chip: rounded rect + white bold label. Returns (w, h)."""
    pad_x = int(12)
    pad_y = int(7)
    tw = draw.textlength(label, font=font)
    w = int(tw) + pad_x * 2
    h = int(font.size) + pad_y * 2
    rounded_rect(draw, [x, y, x + w, y + h], radius=int(h * 0.28), fill=color)
    tx = x + pad_x
    ty = y + pad_y + max(0, int((h - font.size) * 0.5))
    draw.text((tx, ty), label, font=font, fill=WHITE)
    return w, h


def draw_variant1(width=1024, height=1024):
    """FRONT PAGE: masthead, lead story, 2x2 grid, ticker, footer."""
    img = Image.new("RGB", (int(width), int(height)), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead band -------------------------------------------------------
    mast_h = 132
    d.rectangle([0, 0, width, int(mast_h)], fill=NAVY)
    f_mast = load_bold(40)
    mast_text = "THE WORLD IN ONE IMAGE"
    mw = d.textlength(mast_text, font=f_mast)
    d.text(((width - mw) / 2, int(mast_h * 0.16)), mast_text, font=f_mast, fill=WHITE)
    f_date = load_reg(26)
    date_text = "FRIDAY 27 NOVEMBER 2026"
    dw = d.textlength(date_text, font=f_date)
    d.text(((width - dw) / 2, int(mast_h * 0.60)), date_text, font=f_date, fill=GOLD)
    # thin gold rule under masthead
    d.rectangle([0, int(mast_h), width, int(mast_h) + 4], fill=GOLD)

    pad = 40
    top = int(mast_h) + 24

    # ---- lead story (full width) --------------------------------------------
    lead_h = 190
    d.rectangle([pad, top, width - pad, top + lead_h], fill=WHITE)
    d.rectangle([pad, top, int(pad) + 8, top + lead_h], fill=RED)  # left accent bar
    ix, iy = pad + 8 + 54, top + lead_h // 2
    icon_chess(d, ix, iy, 96, ink=NAVY)
    text_x = ix + 84
    text_right = width - pad - 24
    max_w = text_right - text_x
    f_leadh = load_bold(34)
    headline = "Gukesh and Sindarov marathon draw in Gene a Game 3".replace("Gene a", "Geneva")
    headline = "Gukesh and Sindarov draw as Game 3 runs longest yet in Geneva title match"
    h_lines = wrap_text(d, headline, f_leadh, max_w)[:2]
    hy = draw_wrapped(d, (text_x, top + 30), h_lines, f_leadh, INK, leading=5)
    f_leadp = load_reg(21)
    summary = "After three games nothing separates the two at the World Championship in Geneva."
    s_lines = wrap_text(d, summary, f_leadp, max_w)[:2]
    draw_wrapped(d, (text_x, hy + 12), s_lines, f_leadp, INK, leading=3)

    # ---- 2x2 grid of stories 2-5 --------------------------------------------
    grid_top = top + lead_h + 20
    gap = 16
    cell_w = (width - pad * 2 - gap) // 2
    cell_h = 190
    chips = [
        ("NEW ZEALAND", TEAL, "Coalition keeps slim 67/131 seat majority", "Final count after special votes could force a deal with the Opportunity Party or a hung parliament."),
        ("USA", RED, "Trump unveils new tariffs on excess capacity", "Undeterred by midterms; considering fresh tariffs on goods from India, China and the EU."),
        ("WAR", GOLD, "Missiles hit Kyiv; Saudi Arabia intercepts", "Mayor reports ballistic strikes on the capital; two Houthi missiles stopped toward Riyadh."),
        ("SOUTH AFRICA", NAVY, "Ramaphosa wins bid to overturn impeachment", "Chief justice rules in favour of the president, scuttling the impeachment report."),
    ]
    f_chip = load_bold(16)
    f_head = load_bold(20)
    f_sum = load_reg(15)
    for idx, (label, color, headline, summary) in enumerate(chips):
        col = idx % 2
        row = idx // 2
        x0 = pad + col * (cell_w + gap)
        y0 = grid_top + row * (cell_h + gap)
        x1 = x0 + cell_w
        y1 = y0 + cell_h
        d.rectangle([x0, y0, x1, y1], fill=WHITE)
        d.line([x0, y0, x1, y0], fill=color, width=4)
        cx, cy = x0 + 14, y0 + 14
        cw, chh = chip(d, cx, cy, label, color, f_chip)
        # headline (max 2 lines)
        hx = x0 + 14
        hy = cy + chh + 10
        hmax = x1 - hx - 12
        hlines = wrap_text(d, headline, f_head, hmax)[:2]
        hy = draw_wrapped(d, (hx, hy), hlines, f_head, INK, leading=2)
        # summary (max 2 lines) right under headline
        smax = x1 - hx - 12
        slines = wrap_text(d, summary, f_sum, smax)[:2]
        draw_wrapped(d, (hx, hy + 2), slines, f_sum, INK, leading=1)

    # ---- ticker strip ---------------------------------------------------------
    tick_top = grid_top + 2 * cell_h + gap + 18
    tick_h = 66
    d.rectangle([pad, tick_top, width - pad, tick_top + tick_h], fill=NAVY)
    f_tickh = load_bold(17)
    f_tick = load_reg(17)
    ticklabel_w, _ = chip(d, pad + 12, tick_top + tick_h // 2 - 16, "LIVE", RED, f_tickh)
    tx = pad + 12 + ticklabel_w + 14
    tick_items = [
        "KIM: North Korea vows more nuclear weapons after ignoring Trump\u2019s overture.",
        "EU: Leaders weigh ~1.6 trillion euro 2028\u201334 budget and Ukraine funding.",
        "AU OPEN: Sinner out of 2027 with a knee injury.",
    ]
    right = width - pad - 12
    for item in tick_items:
        # single-line clamp within strip
        tlines = wrap_text(d, item, f_tick, right - tx) if right - tx > 20 else [item]
        line = (" ".join(tlines) if tlines else item)
        if d.textlength(line, font=f_tick) > right - tx:
            # ellipsize at last space
            while line and d.textlength(line + "\u2026", font=f_tick) > right - tx:
                line = line[:-1].rstrip()
            line = line + "\u2026"
        d.text((tx, tick_top + tick_h // 2 - 12), line, font=f_tick, fill=WHITE)
        tx += d.textlength(line, font=f_tick) + 22

    # ---- footer ---------------------------------------------------------------
    f_foot = load_reg(16)
    foot = "All stories first reported 27 November 2026"
    fw = d.textlength(foot, font=f_foot)
    d.text(((width - fw) / 2, height - 34), foot, font=f_foot, fill=INK)
    return img


def main():
    variant = sys.argv[1] if len(sys.argv) > 1 else "1"
    draw = globals().get("draw_variant" + variant)
    if draw is None:
        print("unknown variant: " + variant)
        return 1
    img = draw(CANVAS, CANVAS)
    out = "variant_" + variant + ".png"
    img.save(out)
    import os
    n = os.path.getsize(out)
    print("wrote " + out + " 1024x1024 bytes " + str(n))
    return 0


def draw_variant2(width=1024, height=1024):
    """SIX PANELS: date banner, then a 2x3 grid of six equal story panels."""
    img = Image.new("RGB", (int(width), int(height)), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top date banner -----------------------------------------------------
    banner_h = 100
    d.rectangle([0, 0, width, int(banner_h)], fill=NAVY)
    f_ban = load_bold(38)
    ban_text = "FRIDAY 27 NOVEMBER 2026"
    bw = d.textlength(ban_text, font=f_ban)
    d.text(((width - bw) / 2, int(banner_h * 0.22)), ban_text, font=f_ban, fill=WHITE)
    d.rectangle([0, int(banner_h), width, int(banner_h) + 4], fill=GOLD)

    pad = 40
    gap = 16
    top = int(banner_h) + 24
    grid_h = height - top - 42  # leave room for footer
    cell_w = (width - pad * 2 - gap) // 2
    cell_h = (grid_h - 2 * gap) // 3

    stories = [
        ("CHESS", TEAL, "Gukesh and Sindarov marathon draw", "Geneva match's Game 3 was the longest yet; after three games nothing separates the two."),
        ("NEW ZEALAND", TEAL, "Coalition keeps slim 67/131 majority", "Final count after special votes could force a deal with the Opportunity Party or a hung parliament."),
        ("USA", RED, "Trump unveils new tariffs on excess capacity", "Undeterred by midterms; considering fresh tariffs on goods from India, China and the EU."),
        ("WAR", GOLD, "Missiles hit Kyiv; Saudi Arabia intercepts", "Mayor reports ballistic strikes on the capital; two Houthi missiles stopped toward Riyadh."),
        ("SOUTH AFRICA", NAVY, "Ramaphosa wins bid to overturn impeachment", "Chief justice rules in favour of the president, scuttling the impeachment report."),
        ("SPORT", TEAL, "Sinner out of Australian Open 2027", "Knee injury rules him out; Barrett to captain All Blacks; NZ-INDIA Test 2 starts in Christchurch."),
    ]

    f_chip = load_bold(15)
    f_head = load_bold(19)
    f_sum = load_reg(14)
    for idx, (label, color, headline, summary) in enumerate(stories):
        col = idx % 2
        row = idx // 2
        x0 = pad + col * (cell_w + gap)
        y0 = top + row * (cell_h + gap)
        x1 = x0 + cell_w
        y1 = y0 + cell_h
        d.rectangle([x0, y0, x1, y1], fill=WHITE)
        d.line([x0, y0, x1, y0], fill=color, width=4)

        # header chip top-left
        cx, cy = x0 + 12, y0 + 12
        cw, chh = chip(d, cx, cy, label, color, f_chip)

        # small geometric icon top-right (diamond + dot), tinted with panel colour
        icx = x1 - 26
        icy = y0 + 12 + chh // 2
        iris = int(chh * 0.55)
        d.polygon([(icx, icy - iris), (icx + iris, icy), (icx, icy + iris), (icx - iris, icy)], fill=color)
        drad = int(chh * 0.14)
        d.ellipse([icx - drad, icy - drad, icx + drad, icy + drad], fill=WHITE)

        # headline (max 2 lines) below chip
        hx = x0 + 12
        hmax = x1 - hx - 12
        hy = cy + chh + 10
        hlines = wrap_text(d, headline, f_head, hmax)[:2]
        hy = draw_wrapped(d, (hx, hy), hlines, f_head, INK, leading=2)

        # one-line summary right under headline
        slines = wrap_text(d, summary, f_sum, hmax)[:1]
        draw_wrapped(d, (hx, hy + 2), slines, f_sum, INK, leading=1)

    # ---- footer ---------------------------------------------------------------
    f_foot = load_reg(16)
    foot = "All stories first reported 27 November 2026"
    fw = d.textlength(foot, font=f_foot)
    d.text(((width - fw) / 2, height - 34), foot, font=f_foot, fill=INK)
    return img


def draw_variant3(width=1024, height=1024):
    """HEADLINE + BRIEFS: huge lead headline, red rule, five brief rows, ticker strip."""
    img = Image.new("RGB", (int(width), int(height)), PAPER)
    d = ImageDraw.Draw(img)

    pad = 40
    top = 34

    # ---- date line ------------------------------------------------------------
    f_date = load_reg(22)
    date_text = "FRIDAY 27 NOVEMBER 2026"
    dw = d.textlength(date_text, font=f_date)
    d.text(((width - dw) / 2, top), date_text, font=f_date, fill=NAVY)

    # ---- huge lead headline (story 1) across the top --------------------------
    f_lead = load_bold(40)
    lead_text = "Gukesh and Sindarov marathon draw in Geneva"
    lead_lines = wrap_text(d, lead_text, f_lead, width - pad * 2)[:2]
    ly = draw_wrapped(d, (pad, top + 34), lead_lines, f_lead, INK, leading=4)
    f_leadp = load_reg(20)
    lead_sub = "Game 3 was the match's longest yet; after three games nothing separates the two at the World Championship."
    sub_lines = wrap_text(d, lead_sub, f_leadp, width - pad * 2)[:1]
    ly = draw_wrapped(d, (pad, ly + 6), sub_lines, f_leadp, INK, leading=2)

    # red rule under the lead
    rule_y = ly + 10
    d.rectangle([0, rule_y, width, rule_y + 5], fill=RED)

    # ---- five horizontal brief rows (stories 2-6) -----------------------------
    f_chip = load_bold(15)
    f_head = load_bold(19)
    f_sum = load_reg(15)
    briefs = [
        ("NEW ZEALAND", TEAL, "Coalition keeps slim 67/131 majority", "Final count after special votes could force a deal with the Opportunity Party or a hung parliament."),
        ("USA", RED, "Trump unveils new tariffs on excess capacity", "Undeterred by midterms; considering fresh tariffs on goods from India, China and the EU."),
        ("WAR", GOLD, "Missiles hit Kyiv; Saudi Arabia intercepts", "Mayor reports ballistic strikes on the capital; two Houthi missiles stopped toward Riyadh."),
        ("SOUTH AFRICA", NAVY, "Ramaphosa wins bid to overturn impeachment", "Chief justice rules in favour of the president, scuttling the impeachment report."),
        ("SPORT", TEAL, "Sinner out of Australian Open 2027", "Knee injury rules him out; Barrett to captain All Blacks; NZ-INDIA Test 2 starts in Christchurch."),
    ]
    rows_top = rule_y + 22
    row_gap = 12
    row_h = 78
    for idx, (label, color, headline, summary) in enumerate(briefs):
        y0 = rows_top + idx * (row_h + row_gap)
        y1 = y0 + row_h
        d.rectangle([pad, y0, width - pad, y1], fill=WHITE)
        d.rectangle([pad, y0, int(pad) + 7, y1], fill=color)
        # chip
        cx, cy = pad + 20, y0 + 12
        cw, chh = chip(d, cx, cy, label, color, f_chip)
        tx = cx + cw + 14
        tmax = width - pad - tx - 12
        # headline (max 1 line, ellipsize)
        hlines = wrap_text(d, headline, f_head, tmax)[:1]
        hline = hlines[0] if hlines else headline
        if d.textlength(hline, font=f_head) > tmax:
            while hline and d.textlength(hline + "\u2026", font=f_head) > tmax:
                hline = hline[:-1].rstrip()
            hline = hline + "\u2026"
        hh = d.textbbox((0, 0), hline, font=f_head)
        d.text((tx, y0 + 12), hline, font=f_head, fill=INK)
        # one-liner below
        slines = wrap_text(d, summary, f_sum, tmax)[:1]
        slin = slines[0] if slines else summary
        if d.textlength(slin, font=f_sum) > tmax:
            while slin and d.textlength(slin + "\u2026", font=f_sum) > tmax:
                slin = slin[:-1].rstrip()
            slin = slin + "\u2026"
        d.text((tx, y0 + 44), slin, font=f_sum, fill=INK)

    # ---- bottom ticker strip with two items -----------------------------------
    strip_top = rows_top + 5 * (row_h + row_gap) + 6
    strip_h = 58
    sy1 = min(strip_top + strip_h, height - 42)
    d.rectangle([pad, strip_top, width - pad, sy1], fill=NAVY)
    f_tickh = load_bold(16)
    f_tick = load_reg(16)
    tx = pad + 12
    ty = strip_top + strip_h // 2 - 12
    _, _chh = chip(d, tx, ty - 4, "TICKER", RED, f_tickh)
    tx += 96
    tick_items = [
        "N. KOREA: Kim vows more nuclear weapons after ignoring Trump's overture.",
        "EU: Leaders weigh ~1.6 trillion euro 2028-2034 budget and Ukraine funding.",
    ]
    seg_w = (width - pad - tx - 40) // 2
    for item in tick_items:
        tlines = wrap_text(d, item, f_tick, seg_w)
        seg = " " + item.replace("\u2019", "'")
        txt = tlines[0] if tlines else item
        if d.textlength(txt, font=f_tick) > seg_w:
            while txt and d.textlength(txt + "\u2026", font=f_tick) > seg_w:
                txt = txt[:-1].rstrip()
            txt = txt + "\u2026"
        d.text((tx, ty), txt, font=f_tick, fill=WHITE)
        tx += seg_w

    # ---- footer ---------------------------------------------------------------
    f_foot = load_reg(16)
    foot = "All stories first reported 27 November 2026"
    fw = d.textlength(foot, font=f_foot)
    d.text(((width - fw) / 2, height - 34), foot, font=f_foot, fill=INK)
    return img
if __name__ == "__main__":
    sys.exit(main())
