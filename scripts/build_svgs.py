#!/usr/bin/env python3
"""Generate the profile README's SVG assets in developersteve.com's palette.

Every image is a self-contained dark card (no external fonts or resources, which
GitHub's image proxy would block anyway). Motion is plain CSS so it respects
prefers-reduced-motion; the one exception is the title gradient drift (SMIL).

Run from anywhere:  python3 scripts/build_svgs.py
"""
from __future__ import annotations

import math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# developersteve.com palette (src/app/globals.css)
BG_DARKEST = "#00151F"
BG_FRAME = "#02162B"
BG_CARD = "#00283A"
TEXT = "#dedee0"
MUTED = "#919ca1"
WHITE = "#fcfcfe"
GREEN = "#70ba65"
GREEN_LIGHT = "#c2f59c"
TEAL = "#57e0c4"

SANS = "'Inter','Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

W = 840  # GitHub's profile README column is ~830px; everything scales down from here.

# Same roles as TYPED_ROLES on the site, lightly tidied.
ROLES = [
    "a Co-CEO",
    "a CTO",
    "a Company Director",
    "a CIO",
    "a Co-Founder",
    "a Mentor",
    "a Teacher",
    "a Public Speaker",
    "a Developer",
    "a Developer Evangelist",
    "an Author",
    "a Blogger",
    "an Event Organiser",
    "a Streamer",
    "an IoT-ist",
    "a Maker",
    "a 3D Printer Enthusiast",
    "an Open Source Contributor",
    "a Ruralite",
]

STATS = [
    ("30", "+", "Years", "Developer"),
    ("10", "+", "Years", "Developer Relations"),
    ("10", "+", "Years", "Data Analyst"),
    ("291", "", "Conference", "Talks Worldwide"),
    ("600", "+", "Articles", "Blogs & Tutorials"),
]

# Same titles as the site's Titles grid. A title with no url is still under wraps.
TITLES = [
    ("stealth-startup", "Co-CEO / CTO", "Stealth Startup", "Something new. Under wraps for now.", None),
    ("clermont-digital", "Technical Director", "Clermont Digital", "Digital agency. Built in Clermont.", "clermontdigital.com.au"),
    ("coochin-co", "Director", "The Coochin Co.", "Tech, digital & creative ventures", "thecoochin.co"),
    ("mysteryos", "Creator", "MysteryOS", "Puzzle-survival game, Steam & mobile", "mysteryos.app"),
    ("settlesound", "Creator", "Settle Sound", "Binaural beats & calm tones app", "settlesound.com"),
    ("plotplan", "Co-Founder", "PlotPlan.land", "Property layout on satellite imagery", "plotplan.land"),
    ("feedfinda", "Co-Founder", "FeedFinda", "Map-based hay & feed marketplace", "feedfinda.com.au"),
    ("stealth-podcast", "Co-Founder", "Stealth Podcast", "A new show. Still in stealth.", None),
    ("muster-learn", "Teacher", "Muster Learn", "Free short courses on your phone", "learn.muster.life"),
]

WORKED_WITH = [
    "PayPal", "Braintree", "Xero", "Telstra", "NGINX", "GitLab", "IBM", "Snyk",
    "UN Human Rights", "Australian Red Cross", "RMIT Online",
]

# The 200x200 circuit tile from src/components/CircuitBackground.
CIRCUIT_LINES = [
    (0, 40, 60, 40), (80, 40, 140, 40), (160, 40, 200, 40),
    (0, 100, 50, 100), (70, 100, 130, 100), (150, 100, 200, 100),
    (0, 160, 40, 160), (60, 160, 120, 160), (140, 160, 200, 160),
    (40, 0, 40, 40), (40, 40, 40, 100), (100, 0, 100, 40), (100, 100, 100, 160),
    (160, 40, 160, 100), (160, 100, 160, 160), (60, 40, 60, 80), (140, 60, 140, 100),
    (80, 120, 80, 160), (20, 160, 20, 200), (120, 160, 120, 200), (180, 40, 180, 80),
    (60, 80, 80, 100), (80, 100, 60, 120), (140, 100, 160, 120), (180, 80, 200, 100),
    (0, 120, 20, 100), (120, 40, 140, 60),
]
CIRCUIT_NODES = [
    (40, 40, 2.5), (60, 40, 2), (80, 40, 1.5), (100, 40, 2.5), (140, 40, 2), (160, 40, 2.5),
    (40, 100, 2), (60, 80, 1.5), (80, 100, 2), (100, 100, 2.5), (140, 100, 2), (160, 100, 2.5),
    (40, 160, 2), (80, 160, 1.5), (120, 160, 2), (160, 160, 2), (20, 160, 1.5), (180, 80, 1.5),
]


def svg(width: float, height: float, title: str, body: str, style: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" height="{height:g}" '
        f'viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{escape(title)}">\n'
        f"<title>{escape(title)}</title>\n"
        f"<style>{style}{REDUCED_MOTION}</style>\n{body}\n</svg>\n"
    )


def circuit_pattern(pid: str) -> str:
    lines = "".join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>' for a, b, c, d in CIRCUIT_LINES)
    nodes = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in CIRCUIT_NODES)
    return (
        f'<pattern id="{pid}" width="200" height="200" patternUnits="userSpaceOnUse">'
        f'<g stroke="{GREEN}" stroke-opacity=".15" stroke-width="1" stroke-linecap="round">{lines}</g>'
        f'<g fill="{GREEN}" fill-opacity=".18">{nodes}</g></pattern>'
    )


def polyline_length(points: list[tuple[float, float]]) -> float:
    return sum(math.dist(points[i], points[i + 1]) for i in range(len(points) - 1))


# --------------------------------------------------------------------------- header

def build_header() -> str:
    H = 300
    cx, cy, half = 724, 150, 46  # the "chip" on the right

    # PCB routes leaving the chip, as offsets from (cx, cy). Pulses run outward.
    routes = [
        [(-28, -52), (-28, -80), (-48, -100), (-48, -150)],
        [(0, -52), (0, -150)],
        [(14, -52), (14, -76), (44, -106), (116, -106)],
        [(-14, 52), (-14, 84), (-44, 114), (-150, 114)],
        [(14, 52), (14, 150)],
        [(28, 52), (28, 74), (58, 104), (116, 104)],
        [(52, -28), (86, -28), (106, -48), (116, -48)],
        [(52, 0), (116, 0)],
        [(52, 28), (74, 28), (94, 48), (94, 150)],
        [(-52, -14), (-92, -14), (-112, -34), (-150, -34)],
        [(-52, 14), (-96, 14), (-116, 34), (-150, 34)],
    ]
    route_svg, pulse_svg, vias, css = [], [], [], []
    for i, rel in enumerate(routes):
        pts = [(cx + dx, cy + dy) for dx, dy in rel]
        d = "M" + " L".join(f"{x:g} {y:g}" for x, y in pts)
        length = polyline_length(pts)
        route_svg.append(f'<path d="{d}"/>')
        dur = length / 55 / 0.6
        css.append(
            f"@keyframes p{i}{{0%{{stroke-dashoffset:18}}60%,100%{{stroke-dashoffset:-{length:.1f}}}}}"
            f".p{i}{{stroke-dasharray:18 {length + 18:.1f};stroke-dashoffset:18;"
            f"animation:p{i} {dur:.2f}s linear {(i * 0.73) % 4:.2f}s infinite}}"
        )
        pulse_svg.append(f'<path class="p{i}" d="{d}"/>')
        ex, ey = pts[-1]
        if 0 < ex < W and 0 < ey < H:  # only routes that stop inside the frame get a via
            vias.append(f'<circle cx="{ex:g}" cy="{ey:g}" r="3.5"/>')

    pins = []
    for k in (-28, -14, 0, 14, 28):
        pins.append(f'<rect x="{cx + k - 2:g}" y="{cy - half - 6:g}" width="4" height="6"/>')
        pins.append(f'<rect x="{cx + k - 2:g}" y="{cy + half:g}" width="4" height="6"/>')
        pins.append(f'<rect x="{cx - half - 6:g}" y="{cy + k - 2:g}" width="6" height="4"/>')
        pins.append(f'<rect x="{cx + half:g}" y="{cy + k - 2:g}" width="6" height="4"/>')

    # Title: fixed rendered width so the trace underneath always lines up.
    title_x, title_y, title_w = 46, 146, 492

    # Typed-role pill. Monospace with textLength pins each character to a fixed
    # advance, so the cover/cursor steps land exactly on character boundaries.
    fs = 17
    cw = fs * 0.6
    pill_x, pill_y, pill_h = 48, 188, 44
    base_y = pill_y + 28
    prompt_x = pill_x + 18
    im_x = prompt_x + 2 * cw
    role_x = im_x + 4 * cw
    longest = max(len(r) for r in ROLES)
    pill_w = role_x - pill_x + longest * cw + cw + 22
    slot = 3.2
    total = slot * len(ROLES)
    pct = 100 / len(ROLES)

    role_svg = []
    for i, role in enumerate(ROLES):
        n = len(role)
        w = n * cw
        s = i * pct
        a, b, c, e = s + 0.38 * pct, s + 0.80 * pct, s + 0.93 * pct, (i + 1) * pct
        start = "0%" if i == 0 else f"0%,{s:.3f}%"
        css.append(
            f"@keyframes g{i}{{0%{{opacity:{1 if i == 0 else 0}}}"
            + ("" if i == 0 else f"{s:.3f}%{{opacity:1}}")
            + f"{e:.3f}%,100%{{opacity:0}}}}"
            f".g{i}{{opacity:{1 if i == 0 else 0};animation:g{i} {total:.1f}s step-end infinite}}"
            f"@keyframes c{i}{{{start}{{transform:translateX(0);animation-timing-function:steps({n},end)}}"
            f"{a:.3f}%,{b:.3f}%{{transform:translateX({w:.1f}px);animation-timing-function:steps({n},end)}}"
            f"{c:.3f}%,100%{{transform:translateX(0)}}}}"
            f".c{i}{{{'transform:translateX(%.1fpx);' % w if i == 0 else ''}animation:c{i} {total:.1f}s linear infinite}}"
        )
        role_svg.append(
            f'<g class="g{i}">'
            f'<text x="{role_x:.1f}" y="{base_y}" textLength="{w:.1f}" lengthAdjust="spacing" fill="{WHITE}">{escape(role)}</text>'
            f'<g class="c{i}"><rect x="{role_x:.1f}" y="{pill_y + 2}" width="{pill_w:.1f}" height="{pill_h - 4}" fill="{BG_CARD}"/>'
            f'<rect class="cur" x="{role_x + 1:.1f}" y="{base_y - 15}" width="{cw - 1:.1f}" height="19" fill="{GREEN}"/></g></g>'
        )

    css.append(
        "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:blink 1.05s step-end infinite}"
        "@keyframes glow{0%,100%{opacity:.35}50%{opacity:.7}}.glow{animation:glow 3.6s ease-in-out infinite}"
        f"@keyframes node{{from{{transform:translateX(0)}}to{{transform:translateX({title_w - 4}px)}}}}"
        ".node{animation:node 3.4s cubic-bezier(.45,0,.55,1) infinite alternate}"
        "@keyframes chip{0%,100%{stroke-opacity:.45}50%{stroke-opacity:.9}}.chip{animation:chip 3.6s ease-in-out infinite}"
    )

    body = f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG_DARKEST}"/><stop offset=".55" stop-color="{BG_FRAME}"/><stop offset="1" stop-color="{BG_CARD}"/></linearGradient>
<radialGradient id="halo" cx="{cx / W:.3f}" cy=".5" r=".45"><stop offset="0" stop-color="{GREEN}" stop-opacity=".16"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset=".55" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff"/></linearGradient>
<mask id="fadeMask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
{circuit_pattern("circuit")}
<linearGradient id="steve" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="240" y2="0" spreadMethod="repeat">
<stop offset="0" stop-color="{GREEN}"/><stop offset=".35" stop-color="{GREEN_LIGHT}"/><stop offset=".65" stop-color="{TEAL}"/><stop offset="1" stop-color="{GREEN}"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="240 0" dur="7s" repeatCount="indefinite"/></linearGradient>
<linearGradient id="trace" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".12" stop-color="{GREEN}" stop-opacity=".35"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".6"/><stop offset=".88" stop-color="{GREEN}" stop-opacity=".35"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<filter id="blur" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<clipPath id="pill"><rect x="{pill_x + 1}" y="{pill_y + 1}" width="{pill_w - 2:.1f}" height="{pill_h - 2}" rx="9"/></clipPath>
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#circuit)" mask="url(#fadeMask)"/>
<rect width="{W}" height="{H}" fill="url(#halo)"/>
<g fill="none" stroke="{GREEN}" stroke-opacity=".32" stroke-width="1.5" stroke-linejoin="round">{"".join(route_svg)}</g>
<g fill="none" stroke="{GREEN_LIGHT}" stroke-width="2.4" stroke-linecap="round" filter="url(#soft)">{"".join(pulse_svg)}</g>
<g fill="{BG_DARKEST}" stroke="{GREEN}" stroke-opacity=".7" stroke-width="1.5">{"".join(vias)}</g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="17.5" fill="none" stroke="{GREEN}" stroke-opacity=".22"/>

<g fill="{GREEN}" fill-opacity=".75">{"".join(pins)}</g>
<rect x="{cx - half}" y="{cy - half}" width="{half * 2}" height="{half * 2}" rx="10" fill="{BG_CARD}"/>
<rect class="chip" x="{cx - half}" y="{cy - half}" width="{half * 2}" height="{half * 2}" rx="10" fill="none" stroke="{GREEN}" stroke-width="1.5"/>
<rect x="{cx - half + 9}" y="{cy - half + 9}" width="{half * 2 - 18}" height="{half * 2 - 18}" rx="6" fill="none" stroke="{GREEN}" stroke-opacity=".2"/>
<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="900" textLength="52" lengthAdjust="spacingAndGlyphs"><tspan fill="{TEXT}">D</tspan><tspan fill="{GREEN}">S</tspan></text>

<text x="{title_x + 2}" y="78" font-family="{MONO}" font-size="13" letter-spacing="4.5" fill="{MUTED}"><tspan fill="{GREEN}">//</tspan> STEVEN COOCHIN</text>
<text class="glow" x="{title_x}" y="{title_y}" font-family="{SANS}" font-size="62" font-weight="800" textLength="{title_w}" lengthAdjust="spacingAndGlyphs" filter="url(#blur)"><tspan fill="none">Developer</tspan><tspan fill="{GREEN}">Steve</tspan></text>
<text x="{title_x}" y="{title_y}" font-family="{SANS}" font-size="62" font-weight="800" textLength="{title_w}" lengthAdjust="spacingAndGlyphs"><tspan fill="{WHITE}">Developer</tspan><tspan fill="url(#steve)">Steve</tspan></text>
<rect x="{title_x + 2}" y="{title_y + 16}" width="{title_w}" height="2" rx="1" fill="url(#trace)"/>
<circle class="node" cx="{title_x + 4}" cy="{title_y + 17}" r="3" fill="{GREEN_LIGHT}" filter="url(#soft)"/>

<rect x="{pill_x}" y="{pill_y}" width="{pill_w:.1f}" height="{pill_h}" rx="10" fill="{BG_CARD}" stroke="{GREEN}" stroke-opacity=".3"/>
<g font-family="{MONO}" font-size="{fs}">
<text x="{prompt_x}" y="{base_y}" fill="{GREEN}">›</text>
<text x="{im_x:.1f}" y="{base_y}" textLength="{3 * cw:.1f}" lengthAdjust="spacing" fill="{MUTED}">I'm</text>
<g clip-path="url(#pill)">{"".join(role_svg)}</g>
</g>

<text x="{title_x + 2}" y="270" font-family="{MONO}" font-size="12" letter-spacing="1.6" fill="{MUTED}">CENTRAL QLD, AUSTRALIA <tspan fill="{GREEN}">/</tspan> GMT+10 <tspan fill="{GREEN}">/</tspan> OFF-GRID <tspan fill="{GREEN}">/</tspan> SOLAR POWERED</text>"""
    return svg(W, H, "DeveloperSteve: Steven Coochin, technology leader, company director and developer advocate", body, "".join(css))


# --------------------------------------------------------------------------- stats

def build_stats() -> str:
    H, gap = 138, 14
    n = len(STATS)
    cw = (W - gap * (n - 1)) / n
    css = [
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
        f"@keyframes shine{{0%{{transform:translateX(-90px) skewX(-20deg)}}35%,100%{{transform:translateX({cw + 60:.0f}px) skewX(-20deg)}}}}",
    ]
    cards, clips = [], []
    for i, (num, sym, label, sub) in enumerate(STATS):
        x = i * (cw + gap)
        css.append(f".s{i}{{animation:rise .7s cubic-bezier(.2,.7,.2,1) {i * 0.09:.2f}s both}}"
                   f".h{i}{{animation:shine 7s ease-in-out {1.2 + i * 0.35:.2f}s infinite;transform:translateX(-90px)}}")
        clips.append(f'<clipPath id="k{i}"><rect x="{x:.1f}" y="0" width="{cw:.1f}" height="{H}" rx="12"/></clipPath>')
        mid = x + cw / 2
        cards.append(
            f'<g class="s{i}"><rect x="{x + .5:.1f}" y=".5" width="{cw - 1:.1f}" height="{H - 1}" rx="12" fill="{BG_CARD}" stroke="{GREEN}" stroke-opacity=".2"/>'
            f'<g clip-path="url(#k{i})"><rect x="{x:.1f}" y="0" width="{cw:.1f}" height="3" fill="url(#top)"/>'
            f'<rect class="h{i}" x="{x:.1f}" y="-20" width="50" height="{H + 40}" fill="url(#sheen)"/></g>'
            f'<text x="{mid:.1f}" y="62" text-anchor="middle" font-family="{MONO}" font-size="38" font-weight="700" fill="{WHITE}">{num}<tspan fill="{GREEN}">{sym}</tspan></text>'
            f'<text x="{mid:.1f}" y="90" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="2.4" fill="{MUTED}">{label.upper()}</text>'
            f'<text x="{mid:.1f}" y="111" text-anchor="middle" font-family="{SANS}" font-size="13.5" font-weight="600" fill="{TEXT}">{escape(sub)}</text></g>'
        )
    body = f"""<defs>
<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="top" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".8"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
{"".join(clips)}
</defs>
{"".join(cards)}"""
    alt = "; ".join(f"{a}{b} {c.lower()} {d.lower()}" for a, b, c, d in STATS)
    return svg(W, H, alt, body, "".join(css))


# --------------------------------------------------------------------------- title badges

def build_title(role: str, name: str, tagline: str, url: str | None, index: int) -> str:
    BW, BH = 272, 124
    c = 14  # corner accent length
    corners = (
        f"M1.5 {c + 1.5}V1.5H{c + 1.5}M{BW - c - 1.5} 1.5H{BW - 1.5}V{c + 1.5}"
        f"M{BW - 1.5} {BH - c - 1.5}V{BH - 1.5}H{BW - c - 1.5}M{c + 1.5} {BH - 1.5}H1.5V{BH - c - 1.5}"
    )
    css = (
        "@keyframes shine{0%{transform:translateX(-80px) skewX(-20deg)}30%,100%{transform:translateX(360px) skewX(-20deg)}}"
        f".sh{{animation:shine 8s ease-in-out {1.5 + index * 0.45:.2f}s infinite;transform:translateX(-80px)}}"
    )
    body = f"""<defs>
<radialGradient id="g" cx=".5" cy="0" r="1" gradientTransform="matrix(1.2 0 0 .8 -.1 0)"><stop offset="0" stop-color="{GREEN}" stop-opacity=".16"/><stop offset=".62" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="k"><rect width="{BW}" height="{BH}" rx="12"/></clipPath>
</defs>
<g clip-path="url(#k)"><rect width="{BW}" height="{BH}" fill="{BG_FRAME}"/><rect width="{BW}" height="{BH}" fill="url(#g)"/>
<rect class="sh" x="0" y="-20" width="46" height="{BH + 40}" fill="url(#sheen)"/></g>
<rect x=".5" y=".5" width="{BW - 1}" height="{BH - 1}" rx="11.5" fill="none" stroke="{GREEN}" stroke-opacity=".25"/>
<path d="{corners}" fill="none" stroke="{GREEN}" stroke-opacity=".75" stroke-width="2" stroke-linecap="round"/>
<text x="22" y="34" font-family="{MONO}" font-size="10.5" letter-spacing="2.4" fill="{GREEN}">{escape(role.upper())}</text>
<text x="22" y="64" font-family="{SANS}" font-size="22" font-weight="800" fill="{WHITE}">{escape(name)}</text>
<text x="22" y="87" font-family="{SANS}" font-size="12.5" fill="{MUTED}">{escape(tagline)}</text>
{f'<text x="22" y="108" font-family="{MONO}" font-size="11" fill="{GREEN}" fill-opacity=".85">↗ {escape(url)}</text>' if url else f'<text x="22" y="108" font-family="{MONO}" font-size="11" fill="{MUTED}" fill-opacity=".85">● in stealth</text>'}"""
    return svg(BW, BH, f"{role}, {name}: {tagline}", body, css)


# --------------------------------------------------------------------------- worked with

def build_worked_with() -> str:
    H, chip_h, gap = 68, 38, 12
    chips, x = [], 0.0
    for name in WORKED_WITH:
        cw = len(name) * 8.3 + 46
        chips.append((x, cw, name))
        x += cw + gap
    seq = x

    def row(offset: float) -> str:
        out = []
        for cx, cw, name in chips:
            left = offset + cx
            out.append(
                f'<rect x="{left:.1f}" y="{(H - chip_h) / 2}" width="{cw:.1f}" height="{chip_h}" rx="{chip_h / 2}" fill="{BG_CARD}" stroke="{GREEN}" stroke-opacity=".22"/>'
                f'<circle cx="{left + 17:.1f}" cy="{H / 2}" r="3" fill="{GREEN}"/>'
                f'<text x="{left + 29:.1f}" y="{H / 2 + 5}">{escape(name)}</text>'
            )
        return "".join(out)

    css = (
        f"@keyframes run{{from{{transform:translateX(0)}}to{{transform:translateX(-{seq:.1f}px)}}}}"
        f".run{{animation:run {seq / 38:.1f}s linear infinite}}"
    )
    body = f"""<defs>
<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect width="{W}" height="{H}" fill="url(#edge)"/></mask>
<clipPath id="k"><rect width="{W}" height="{H}" rx="14"/></clipPath>
</defs>
<g clip-path="url(#k)"><rect width="{W}" height="{H}" fill="{BG_FRAME}"/>
<g mask="url(#m)"><g class="run" font-family="{SANS}" font-size="14.5" font-weight="600" fill="{TEXT}">{row(16)}{row(16 + seq)}</g></g></g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" fill="none" stroke="{GREEN}" stroke-opacity=".18"/>"""
    return svg(W, H, "Worked with: " + ", ".join(WORKED_WITH), body, css)


# --------------------------------------------------------------------------- footer

def build_footer() -> str:
    H = 58
    css = (
        f"@keyframes node{{from{{transform:translateX(0)}}to{{transform:translateX({W - 80}px)}}}}"
        ".node{animation:node 6s cubic-bezier(.45,0,.55,1) infinite alternate}"
    )
    body = f"""<defs>
<linearGradient id="trace" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".5" stop-color="{GREEN}" stop-opacity=".45"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></linearGradient>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="{BG_FRAME}"/>
<rect x="40" y="12" width="{W - 80}" height="1.5" fill="url(#trace)"/>
<circle class="node" cx="40" cy="12.75" r="2.6" fill="{GREEN_LIGHT}" filter="url(#soft)"/>
<text x="{W / 2}" y="39" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{MUTED}">BUILT IN CLERMONT, QLD <tspan fill="{GREEN}">/</tspan> POWERED BY SOLAR, CURIOSITY &amp; OPEN SOURCE</text>"""
    return svg(W, H, "Built in Clermont, QLD. Powered by solar, curiosity and open source.", body, css)


def main() -> None:
    (ASSETS / "titles").mkdir(parents=True, exist_ok=True)
    out = {
        "header.svg": build_header(),
        "stats.svg": build_stats(),
        "worked-with.svg": build_worked_with(),
        "footer.svg": build_footer(),
    }
    for i, (slug, role, name, tagline, url) in enumerate(TITLES):
        out[f"titles/{slug}.svg"] = build_title(role, name, tagline, url, i)
    for rel, content in out.items():
        (ASSETS / rel).write_text(content, encoding="utf-8")
        print(f"wrote assets/{rel} ({len(content):,} bytes)")


if __name__ == "__main__":
    main()
