#!/usr/bin/env python3
"""Generates the static truman-cho.com mirror from scraped _data/*.json into HTML files."""
import json, os, re, html
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "_data")
CDN = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f"

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

url_map = load("url_to_filename.json")
path_map = load("url_to_path.json")

def img(url, cls=""):
    path = path_map.get(url)
    if path:
        return f"/assets/img/{path}"
    name = url_map.get(url)
    if not name:
        return url
    return f"/assets/img/{name}"

_aspect_cache = {}
def aspect_ratio(local_src):
    """height/width for a locally-hosted image, from its file on disk. 0.75 fallback."""
    if local_src in _aspect_cache:
        return _aspect_cache[local_src]
    ratio = 0.75
    if local_src.startswith("/assets/img/"):
        path = os.path.join(ROOT, local_src.lstrip("/"))
        try:
            with Image.open(path) as im:
                ratio = im.height / im.width
        except Exception:
            pass
    _aspect_cache[local_src] = ratio
    return ratio

def masonry(items, cols=3, extra_class=""):
    """Balance figures across N flex columns by estimated rendered height (aspect ratio),
    always placing the next figure into the currently-shortest column."""
    columns = [[] for _ in range(cols)]
    heights = [0.0] * cols
    for it in items:
        src, fig_html = it
        shortest = heights.index(min(heights))
        columns[shortest].append(fig_html)
        heights[shortest] += aspect_ratio(src) + 0.08  # + gap/caption fudge factor
    col_html = "".join(
        f'<div class="masonry-col">{"".join(c)}</div>' for c in columns
    )
    cls = f"masonry {extra_class}".strip()
    return f'<div class="{cls}">{col_html}</div>'

ABOUT_DROPDOWN = [
    ("/about.html", "About"),
    ("/timeline.html", "Timeline"),
    ("/resume.html", "Resume"),
    ("/youtube.html", "YouTube"),
]

SOCIAL_ICONS = [
    ("https://www.instagram.com/thetrumancho", "Instagram",
     '<path d="M12 2.2c3.2 0 3.6 0 4.9.07 1.2.06 2.1.26 2.6.5.6.24 1.1.55 1.6 1.05.5.5.8 1 1.05 1.6.24.5.44 1.4.5 2.6.06 1.3.07 1.7.07 4.9s0 3.6-.07 4.9c-.06 1.2-.26 2.1-.5 2.6a4.4 4.4 0 0 1-1.05 1.6 4.4 4.4 0 0 1-1.6 1.05c-.5.24-1.4.44-2.6.5-1.3.06-1.7.07-4.9.07s-3.6 0-4.9-.07c-1.2-.06-2.1-.26-2.6-.5a4.4 4.4 0 0 1-1.6-1.05 4.4 4.4 0 0 1-1.05-1.6c-.24-.5-.44-1.4-.5-2.6C2.2 15.6 2.2 15.2 2.2 12s0-3.6.07-4.9c.06-1.2.26-2.1.5-2.6.24-.6.55-1.1 1.05-1.6.5-.5 1-.8 1.6-1.05.5-.24 1.4-.44 2.6-.5C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.15 0-3.52 0-4.76.07-1 .04-1.5.2-1.86.34-.47.18-.8.4-1.15.75-.35.35-.57.68-.75 1.15-.14.36-.3.87-.34 1.86C3.07 8.48 3.07 8.85 3.07 12s0 3.52.07 4.76c.04 1 .2 1.5.34 1.86.18.47.4.8.75 1.15.35.35.68.57 1.15.75.36.14.87.3 1.86.34 1.24.07 1.61.07 4.76.07s3.52 0 4.76-.07c1-.04 1.5-.2 1.86-.34.47-.18.8-.4 1.15-.75.35-.35.57-.68.75-1.15.14-.36.3-.87.34-1.86.07-1.24.07-1.61.07-4.76s0-3.52-.07-4.76c-.04-1-.2-1.5-.34-1.86a2.6 2.6 0 0 0-.75-1.15 2.6 2.6 0 0 0-1.15-.75c-.36-.14-.87-.3-1.86-.34C15.52 4 15.15 4 12 4zm0 3.16A4.84 4.84 0 1 1 7.16 12 4.84 4.84 0 0 1 12 7.16zm0 1.8A3.04 3.04 0 1 0 15.04 12 3.04 3.04 0 0 0 12 8.96zm5.03-1.98a1.13 1.13 0 1 1-1.13-1.13 1.13 1.13 0 0 1 1.13 1.13z"/>'),
    ("https://x.com/RandomUser1081", "X",
     '<path d="M18.24 3H21l-6.3 7.2L22 21h-6.13l-4.8-6.28L5.6 21H2.83l6.74-7.7L2.5 3h6.28l4.34 5.74L18.24 3zm-1.07 16.17h1.5L7.9 4.74H6.29l10.88 14.43z"/>'),
    ("https://idk1801.itch.io/", "itch.io games",
     '<path d="M2.5 6.2C3.6 4.9 5.2 3.1 6 3h12c.8.1 2.4 1.9 3.5 3.2 1 1.1 1 3.5-1.2 3.7-1.7.1-2.7-1-3-2-.3 1-1.5 2-3 2-1.4 0-2.6-1-2.9-2-.3 1-1.2 2-2.9 2-1.6 0-2.7-1-3-2-.3 1-1.3 2.1-3 2C1.5 9.7 1.5 7.3 2.5 6.2zM3 10.7c.6.3 1.3.5 2.1.4.9-.1 1.7-.5 2.3-1 .7.5 1.6 1 2.6 1s2-.4 2.6-.9c.6.5 1.6.9 2.6.9s1.9-.5 2.6-1c.6.5 1.4.9 2.3 1 .8.1 1.5-.1 2.1-.4l-.7 7.6c-.1 1.1-1 2-2.1 2.2-1.7.3-4.5.6-7.4.6s-5.7-.3-7.4-.6c-1.1-.2-2-1.1-2.1-2.2L3 10.7zm6.2 2.7c-1.6 0-3.3 1.3-3.3 3.4 0 .5.1.9.3 1.2.5-.1 1.7-.3 3-.3.3-.7.9-1.6 1.6-2.3-.3-1.1-1-2-1.6-2zm5.6 0c-.6 0-1.3.9-1.6 2 .7.7 1.3 1.6 1.6 2.3 1.3 0 2.5.2 3 .3.2-.3.3-.7.3-1.2 0-2.1-1.7-3.4-3.3-3.4z"/>'),
]

def nav_html(current):
    links = [f'<a href="/" class="{"current" if current == "Home" else ""}">Home</a>']
    links.append(f'<a href="https://www.betrumaker.com" target="_blank" rel="noopener">Maker Resource</a>')
    about_current = "current" if current in ("About", "Timeline", "Resume", "YouTube") else ""
    dropdown_items = "".join(
        f'<a href="{href}">{label}</a>' for href, label in ABOUT_DROPDOWN
    )
    links.append(f'''<div class="nav-dropdown">
        <a href="/about.html" class="{about_current}">About</a>
        <div class="nav-dropdown-menu">{dropdown_items}</div>
      </div>''')
    links.append(f'<a href="/journal/" class="{"current" if current == "Journal" else ""}">Journal</a>')
    links.append(f'<a href="/game-dev.html" class="{"current" if current == "Game Dev" else ""}">Game Dev</a>')
    links.append(f'<a href="/projects.html" class="{"current" if current == "Projects" else ""}">Projects</a>')
    return "\n      ".join(links)

def social_icons_html():
    icons = "".join(
        f'<a href="{href}" target="_blank" rel="noopener" title="{label}" class="nav-icon">'
        f'<svg viewBox="0 0 24 24" width="17" height="17" fill="currentColor">{path}</svg></a>'
        for href, label, path in SOCIAL_ICONS
    )
    return f'<div class="nav-icons">{icons}<span class="nav-login">Login</span></div>'

def page(title, current, body, description="Truman Cho — artist, game developer, and maker."):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="stylesheet" href="/assets/css/style.css">
</head>
<body>
<header class="site-header">
  <a href="/" class="logo">Truman Cho</a>
  <nav class="nav-links">
      {nav_html(current)}
  </nav>
  {social_icons_html()}
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="foot-links">
    <a href="/projects.html">Projects</a> · <a href="/journal/">Journal</a> · <a href="/about.html">About</a> · <a href="https://contact">Contact</a>
  </div>
  <div>&copy; Truman Cho</div>
  <div style="margin-top:8px;">🎮 <a href="https://idk1801.itch.io/" target="_blank" rel="noopener">Games on itch.io</a> &nbsp;|&nbsp; 💬 <a href="https://x.com/RandomUser1081" target="_blank" rel="noopener">Dev updates on X</a> &nbsp;|&nbsp; 📸 <a href="https://www.instagram.com/thetrumancho" target="_blank" rel="noopener">Visual journal on Instagram</a></div>
</footer>
</body>
</html>
"""

def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("wrote", path)

# ---------- HOME ----------
hero_row = [
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/1751743318824-BOAU93KAIVFFU0AQL19M/IMG_0224.jpeg",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/f26d0100-f170-4451-8ffa-b54cd09b0f1a/17.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/1780108142202-BIHUBQN1IDLEP37RGE8J/IMG_0722.jpg",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/53f74df8-8c14-4568-b3f9-f888cd839f95/IMG_4270.jpg",
]
intro_photo = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/142f5e09-cc8c-4fb1-82ce-61540e97b2f3/IMG_4264.jpg"
process_strip = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/e24f0bbb-3194-4482-9a05-bca7e7b26250/3.png"
process_labels = ["CREATE", "DIGITIZE", "CODE", "PLAY!", "MAKE"]
process_panels = "".join(
    f'''<div class="process-panel">
      <div class="process-img" role="img" aria-label="{label}" style="background-image:url('{img(process_strip)}'); background-position:{p}% 0;"></div>
    </div>'''
    for p, label in zip([0, 25, 50, 75, 100], process_labels)
)
watch_videos = [
    ("eDjfnad-6zY", "betru maker presentation knollwood elementary"),
    ("Z-xL04PwuUQ", "A Midevial Fantasy Gameboy game"),
]
watch_html = "".join(
    f'''<div class="watch-embed">
      <iframe src="https://www.youtube.com/embed/{vid}" title="{html.escape(title)}" allowfullscreen></iframe>
    </div>'''
    for vid, title in watch_videos
)
home_body = f"""
<section class="hero">
  <div class="hero-intro">
  <p>I am an artist and game developer who loves bringing things to life through my game dev, small art business and teaching kids to be creators.</p>
  <p>My latest project: a free resource so any kid can cross from consumer to maker on their own terms.</p>
  <a class="cta" href="https://www.betrumaker.com" target="_blank" rel="noopener">visit betrumaker.com</a>
  </div>
  <div class="hero-collage">
    {''.join(f'<img src="{img(u)}" alt="">' for u in hero_row)}
  </div>
</section>
<div class="intro-split wrap">
  <img class="intro-photo" src="{img(intro_photo)}" alt="">
  <p class="intro-text">My parents wouldn't let me play Angry Birds, so I built my own version out of blocks. I wanted a Game Boy, so I made a cardboard version. That's still basically how I work. If something doesn't exist in the form I need, I figure out how to make it. I study computer science at Brooklyn Tech and publish my games on <a href="https://idk1801.itch.io/" target="_blank" rel="noopener" style="text-decoration:underline;">itch.io</a>. My current itch to create is figuring out what it takes to shift a kid from player to maker.</p>
</div>
<section class="featured-projects wrap">
  <h2 class="section-heading">FEATURED PROJECTS</h2>
  <div class="process-row">
    {process_panels}
  </div>
</section>
<section class="watch-section">
  <h2 class="section-heading watch-heading">watch</h2>
  <div class="watch-videos wrap">
    {watch_html}
  </div>
</section>
"""
write("index.html", page("Truman Cho", "Home", home_body))

# ---------- ABOUT ----------
about_portrait = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/a24b8567-c689-427a-bf99-d3af20b36ef1/657740688_17880431190515204_2166118040848615964_n.jpg"
started_row = [
    "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/9ff6ec98-1db8-4d43-a7b8-29450a153674/Screenshot+2025-06-23+at+6.47.47%E2%80%AFPM.png",
    "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/6c4516f9-f021-46c4-bb89-5b84d8798972/Screenshot+2025-06-28+at+2.36.23%E2%80%AFPM.png",
    "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/9e6482d0-5a55-454c-9ade-21988b631e1f/Screenshot+2025-06-29+at+8.47.39%E2%80%AFPM.png",
]
journey_grid = [
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/73f927f2-ef23-4909-a002-d965289c32ea/14.png", "AGE 6, first scratch games"),
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/1759785791906-YXEOWL5S3VTDU93KP0UG/29403639_1893697284255305_3740429998100578304_n.jpg", "making consoles"),
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/f26d0100-f170-4451-8ffa-b54cd09b0f1a/17.png", "designing games"),
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/cc6d7c41-2a7b-4c85-ad5f-9f7903aa28ca/16.png", "developing games"),
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/f1b2c854-df7c-40e8-ba75-c6d51c1e4ce6/557711349_17857829103518335_7504760071234781922_n.jpg", "selling my products"),
    ("https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/e9266336-b6b7-48b9-9772-c0968d6219b3/maker-demo-classroom1.jpg", "sharing what I love"),
]
about_body = f"""
<div class="about-intro wrap">
  <img class="about-photo" src="{img(about_portrait)}" alt="">
  <div class="about-intro-text">
    <h1>About Me</h1>
    <p>I'm Truman Cho, a junior at Brooklyn Technical High School in New York.</p>
    <p>I've been making things my whole life &mdash; not because anyone told me to, but because I couldn't help it. Games, comics, cardboard consoles, merch, businesses. Most of it started with a question I couldn't answer any other way except by building something.</p>
    <p>I publish original games on itch.io, press them onto Game Boy cartridges, and sell my own character art at markets and pop-up events. Since I was ten I've worked at a boutique hotel in Washington State &mdash; starting in the kitchen and eventually designing the merchandise still sold in their gift shop.</p>
    <p>My current itch to create is figuring out what it takes to shift a kid from player to maker.</p>
  </div>
</div>
<section class="about-section wrap">
  <div class="about-section-header">
    <h3>How it started</h3>
    <p>All started with a comic book I bought for $1 from a kid at the park.</p>
  </div>
  <div class="about-photo-row">
    {''.join(f'<img src="{img(u)}" alt="">' for u in started_row)}
  </div>
</section>
<section class="about-section wrap">
  <div class="about-section-header">
    <h3>My journey</h3>
    <p>I Taught myself the things I wanted to learn and make and now giving back to encourage kids like me.</p>
  </div>
  <div class="journey-grid">
    {''.join(f'<div class="journey-tile"><img src="{img(u)}" alt=""><div class="journey-caption">{html.escape(cap)}</div></div>' for u, cap in journey_grid)}
  </div>
</section>
"""
write("about.html", page("About — Truman Cho", "About", about_body))

# ---------- TIMELINE (curated: one photo per year) ----------
# Curation lives in _data/timeline_curated.json (editable via the local admin
# tool at admin_server.py) rather than hardcoded here, so picks/captions can
# change without touching this script.
timeline = load("timeline_images.json")
tl_curated = load("timeline_curated.json")
tl_cards = ""
for entry in tl_curated:
    i = entry["index"]
    t = timeline[i]
    year = entry["label"]
    caption = entry.get("caption_override") or t.get("caption", "")
    tl_cards += f'''<figure class="timeline-card">
      <img src="{img(t["src"])}" alt="{html.escape(caption)}">
      <div class="timeline-year">{year}</div>
      <figcaption>{html.escape(caption)}</figcaption>
    </figure>'''
timeline_body = f"""
<h1 class="page-title">Timeline</h1>
<p class="page-subtitle">Twelve years of making, in order &mdash; from cardboard consoles to published games to a hotel gift shop to markets across three cities.</p>
<div class="timeline-grid wrap">
{tl_cards}
</div>
"""
write("timeline.html", page("Timeline — Truman Cho", "Timeline", timeline_body,
      "A photo timeline of twelve years of making, from cardboard game consoles to published games and merchandise."))

# ---------- RESUME ----------
resume_body = """
<div class="resume">
<h1>Truman Cho</h1>
<p class="tagline">Computer Science Student &middot; Game Developer &middot; Creator</p>
<p class="meta">Brooklyn Technical High School, Software Engineering Major &middot; Class of 2027</p>
<p class="meta">SAT: 1540 (740 ELA, 800 Math)</p>
<p class="meta">📍 Brooklyn, NY</p>

<h2>Profile</h2>
<p>I build games and make things. I've been doing it since I was four. I study CS at Brooklyn Tech, publish games on itch.io, run a custom charm and merch business out of Brooklyn, and show up every week for younger kids in my church community.</p>

<h2>Key Work</h2>
<h3>BeTru Maker Project (2025&ndash;Present)</h3>
<ul>
<li>Self-directed maker workshop project studying what it takes to shift a kid from player to maker</li>
<li>Ran structured game demos for 80+ kids at Knollwood Elementary school in New Jersey</li>
<li>Ran charm bar activation for 70+ graduating 5th graders at PS38 in Brooklyn</li>
<li>Built and ran a 5-day maker workshop for 6 kids, each taking a character from sketch to playable game to printed shirt</li>
<li>Ran a condensed 2-hour session for a 5-year-old to test the curriculum with younger kids</li>
<li>Built and launched betrumaker.com, a free public resource site for kids who want to start making things, including a gallery of student work</li>
</ul>

<h2>Game Development</h2>
<ul>
<li>Blood Moon (2023), my first game jam entry</li>
<li>Retro-style Game Boy games built in GB Studio and published on itch.io (idk1801):
  <ul>
    <li>Mount Rock (2024), GB Compo 2024 entry</li>
    <li>OverDose (2025)</li>
    <li>Archaea (2025), GB Compo 2025 entry</li>
    <li>Dragon 0 (2026, in development), a medieval fantasy Game Boy game with all art drawn in my own style</li>
  </ul>
</li>
<li>Pressed Mount Rock onto a physical Game Boy cartridge (2024): sourced the parts, flashed the chip, and designed the box and instruction manual</li>
<li>Built a solo Roblox game as a school final, and a collaborative Roblox game since 2025 with peers from the CIEE Kyoto program, working across Brooklyn and Tokyo time zones</li>
<li>Started on Scratch at six and made 10+ projects through elementary school (idkalt)</li>
<li>Post build devlogs on YouTube (2 published)</li>
</ul>

<h2>Merch &amp; Product Design</h2>
<ul>
<li>Founded BeTru (2023&ndash;Present), an original character brand. Launched June 2023 with 10 original characters printed on apparel, stickers, mugs, bottles, notebooks, and pouches</li>
<li>Created exclusive merchandise line for Friday Harbor Suites
  <ul>
    <li>First collection, July 2023: 12 original artworks on apparel, mugs, bottles, postcards, and totes</li>
    <li>Second collection, April 2025: 6 additional artworks</li>
  </ul>
</li>
<li>Sold products through Philz Coffee (July 2024, December 2025), CorePower Yoga (December 2025), FAD Market Brooklyn (September 2025), Lululemon pop-ups (July 2024), and Friday Harbor Suites (summer 2023, first pop-up)</li>
<li>Commissioned work: Brooklyn/Korean-themed party charm bar (May 2026), reptile-themed party charm bar (April 2026), CorePower Yoga animal designs (December 2025), Philz Coffee California-themed pieces (December 2025), a 3-day pop-up in Korea (November 2025), Redeemer Church activation (June 2025), Paper Cup Design Mother's Day hand lettering (April 2025), VOX Media holiday gifting illustration (March 2024), private holiday gift illustrations (December 2023), CorePower Yoga custom water bottle art for the Brea, CA location (September 2023)</li>
</ul>

<h2>Experience &amp; Leadership</h2>
<h3>Youth Game &amp; Community Lead, Redeemer Presbyterian Church Brooklyn (Spring 2025&ndash;Present)</h3>
<ul>
<li>Assistant teacher for elementary youth class, twice monthly</li>
<li>Founded informal post-service hangout and monthly lunch outings for middle schoolers</li>
<li>VBS team lead</li>
</ul>
<h3>Friday Harbor Suites, WA (2020&ndash;Present)</h3>
<ul>
<li>Cafe service, kitchen prep, and guest hospitality</li>
<li>Designed and managed in-lobby merchandise; assisted with store layout and product curation</li>
<li>Returning August 2026 as barista and to run a souvenir gift customization bar</li>
</ul>

<h2>Skills</h2>
<p><strong>Technical:</strong> Java &middot; SQL &middot; C++ &middot; BASH &middot; LUA &middot; GB Studio (self-taught) &middot; Unity (basic)</p>
<p><strong>Creative:</strong> Procreate &middot; CapCut &middot; Cricut (since 2023) &middot; Heat Press &middot; Hand Lettering &middot; DTF/UV-DTF Printing</p>
<p><strong>Business / Other:</strong> Branding &amp; Packaging &middot; Pop-up Planning &middot; Customer Engagement &middot; Self-taught Piano (since 2021)</p>

<h2>Press &amp; Partnerships</h2>
<ul>
<li>Featured in &ldquo;The New York Teen at Home&rdquo; by Adriane Quinlan, Curbed / New York Magazine, July 2026 &mdash; part of Curbed's Teen Week coverage</li>
<li>Creating 13 pieces of content for xTool through Paper Cup Design (August 2026)</li>
</ul>

<h2>Competitions &amp; Recognition</h2>
<ul>
<li>3rd Place, Game Design Project, CIEE Kyoto (2025), out of 12 teams</li>
<li>GB Compo entrant, 2024 (Mount Rock) and 2025 (Archaea)</li>
</ul>

<h2>For Fun</h2>
<ul>
<li>Making videos with friends for over five years, directed and edited in CapCut</li>
<li>Plays guitar, and taught himself piano in 2021 on a free upright</li>
<li>Bakes with friends and turns it into YouTube shorts</li>
<li>Collects retro handhelds, including a 1989 Game Boy</li>
</ul>
</div>
"""
write("resume.html", page("Resume — Truman Cho", "Resume", resume_body,
      "Truman Cho's resume: game development, merch and product design, and community leadership."))

# ---------- YOUTUBE ----------
youtube_imgs = [
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/5fb76878-05d0-4f97-872d-b66f54cbb0aa/Screenshot+2025-07-03+at+10.58.24%E2%80%AFAM.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/7533714a-3af0-4c90-b895-8b4cacf3db05/Screenshot+2025-07-03+at+10.59.28%E2%80%AFAM.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/31e94566-7f3d-4bf9-ab7f-559f8eeeb533/Screenshot+2025-07-03+at+6.10.21%E2%80%AFPM.png",
]
youtube_body = f"""
<h1 class="page-title">YouTube</h1>
<div class="video-embed">
  <iframe src="https://www.youtube.com/embed/eKwmt9syNm0" title="Truman Cho devlog" allowfullscreen></iframe>
</div>
{masonry([(img(u), f'<figure><img src="{img(u)}" alt=""></figure>') for u in youtube_imgs])}
"""
write("youtube.html", page("YouTube — Truman Cho", "YouTube", youtube_body))

# ---------- GAME DEV ----------
games = [
    {"title": "Archaea", "img": "https://img.itch.zone/aW1nLzIyOTY1MTgzLnBuZw==/original/kacoij.png",
     "desc": "You are a space ranger who was abandoned by his crew, left all alone on planet Archaea. Your one goal: to survive and find a way off of the planet. Archaea's resources are scarce, and the creatures living on the planet are hostile.",
     "meta": "GB Compo 2025 entry &middot; Released", "link": "https://idk1801.itch.io/archaea"},
    {"title": "OverDose", "img": "https://img.itch.zone/aW1nLzIzMzExMTIxLnBuZw==/original/azPXw9.png",
     "desc": "An endless runner where the goal is to get the highest score. Dodge obstacles and grab pills, but after a certain amount the medicine has an increasing chance to hurt you. Survive as long as you can and try not to overdose.",
     "meta": "2025 &middot; Released", "link": "https://idk1801.itch.io/overdose"},
    {"title": "Mount Rock", "img": "https://img.itch.zone/aW1nLzE4NzU2NzkwLnBuZw==/original/cGmv8H.png",
     "desc": "A really hard and unforgiving Game Boy homebrew. Pressed onto a physical Game Boy cartridge in 2024 &mdash; parts sourced, chip flashed, box and manual designed by hand.",
     "meta": "GB Compo 2024 entry &middot; Also on cartridge", "link": "https://idk1801.itch.io/mountrock"},
    {"title": "Adventure of the Sea", "img": "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/12488323-acd2-46ae-a484-2110ad670803/Screenshot+2025-06-23+at+9.26.31%E2%80%AFPM.png",
     "desc": "A highly ambitious RPG started at age 10: explore the world across the seas, battling and defeating enemies. In development, not yet published.",
     "meta": "2020&ndash;2021 &middot; In development", "link": None},
    {"title": "Backrooms", "img": "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/026f9425-094b-418b-b451-a27fd8b7cba4/Screenshot%2B2025-02-22%2B152811.png",
     "desc": "In development, not yet published.",
     "meta": "In development", "link": None},
]
cards = ""
for g in games:
    link_html = f'<a class="card-link" href="{g["link"]}" target="_blank" rel="noopener">Play on itch.io &rarr;</a>' if g["link"] else '<span class="card-link" style="opacity:0.5;">In development</span>'
    cards += f"""<div class="card">
      <img src="{img(g['img'])}" alt="{html.escape(g['title'])}">
      <div class="card-body">
        <h3>{html.escape(g['title'])}</h3>
        <div class="card-meta">{g['meta']}</div>
        <p>{html.escape(g['desc'])}</p>
        {link_html}
      </div>
    </div>
    """
game_dev_body = f"""
<h1 class="page-title">Game Dev</h1>
<p class="page-subtitle">Retro-style games built in GB Studio, published on <a href="https://idk1801.itch.io/" target="_blank" rel="noopener">itch.io</a> and pressed onto real Game Boy cartridges.</p>
<div class="card-grid">
{cards}
</div>
"""
write("game-dev.html", page("Game Dev — Truman Cho", "Game Dev", game_dev_body,
      "Truman Cho's GB Studio games: Archaea, OverDose, Mount Rock, and more, published on itch.io."))

# ---------- PROJECTS LANDING ----------
_projects_maker_img = f"{CDN}/53f74df8-8c14-4568-b3f9-f888cd839f95/IMG_4270.jpg"
_projects_client_img = f"{CDN}/0603dfde-9759-4264-8013-14ae48a8158d/IMG_9565.jpg"
_projects_merch_img = f"{CDN}/4185538d-9bb0-46ab-b3b3-5cf3907e771d/503040689_1896533771159955_6325911197630627969_n.jpg"
_projects_events_img = f"{CDN}/02012e93-8fcc-48e4-bc66-85e20ea4537a/IMG_4999.jpg"
projects_body = f"""
<h1 class="page-title">Projects</h1>
<div class="project-cats">
  <a class="project-cat" href="https://www.betrumaker.com" target="_blank" rel="noopener">
    <img src="{img(_projects_maker_img)}" alt="Maker Project">
    <span class="label">MAKER PROJECT</span>
  </a>
  <a class="project-cat" href="/portfolio/client-work.html">
    <img src="{img(_projects_client_img)}" alt="Client Work">
    <span class="label">CLIENT WORK</span>
  </a>
  <a class="project-cat" href="/portfolio/tru-merch.html">
    <img src="{img(_projects_merch_img)}" alt="Tru Merch">
    <span class="label">TRU MERCH</span>
  </a>
  <a class="project-cat" href="/portfolio/events-projects.html">
    <img src="{img(_projects_events_img)}" alt="Events + Projects">
    <span class="label">EVENTS + PROJECTS</span>
  </a>
</div>
"""
write("projects.html", page("Projects — Truman Cho", "Projects", projects_body))

# ---------- PORTFOLIO PAGES (real section structure, not flat galleries) ----------

def photo_row(urls, max_cols=4):
    """A row of cropped, uniformly-sized photos. Uses exactly len(urls) columns (all in
    one row) when that's small; caps at max_cols and wraps for larger sets."""
    if not urls:
        return ""
    cols = min(len(urls), max_cols)
    out = "".join(f'<img src="{img(u)}" alt="">' for u in urls)
    return f'<div class="project-photos" style="grid-template-columns:repeat({cols}, 1fr);">{out}</div>'

def illustration(url):
    """A single uncropped, full-width graphic (character sheets, sticker collages)."""
    return f'<img class="project-illustration" src="{img(url)}" alt="">'

def portfolio_page(fname, title, subtitle, body_html):
    body = f"""
<h1 class="page-title">{title}</h1>
<p class="page-subtitle">{subtitle}</p>
{body_html}
"""
    write(f"portfolio/{fname}.html", page(f"{title} — Truman Cho", "Projects", body))

# --- Client Work ---
vox_imgs = [
    f"{CDN}/b33d8b32-e479-4735-a219-fcefdc125ce2/TRU-CUSTOM+WORK.png",
    f"{CDN}/7793692c-8852-4185-82c0-661b1b675dd4/IMG_6607.jpg",
    f"{CDN}/96fc17dd-092c-45bf-a77b-10f26bcd1aac/IMG_6622.JPG",
    f"{CDN}/6deeaa44-5b53-45d7-a676-184bb132266b/IMG_6551.JPG",
    f"{CDN}/72635480-c2eb-4d75-8bd3-5646c49ae63e/IMG_6459.JPG",
]
fhs_imgs = [
    f"{CDN}/4bd445ee-6d6e-410f-89ce-ee2beba9bbf9/TRU-CUSTOM+WORK+%281%29.png",
    f"{CDN}/8882e33b-bcee-455c-b273-21f9e08506c4/IMG_9565.jpg",
    f"{CDN}/e4f4ebd9-b7e9-4272-b2e9-409fe9b4eb43/Screenshot+2025-06-30+at+11.50.40%E2%80%AFPM.png",
    f"{CDN}/0777067e-7df8-412b-8774-cd191822b974/26B22AE5-9810-451A-9002-6BDBF391877B.jpg",
]
fhs_collection_imgs = [
    f"{CDN}/361e4f7b-f84d-43d2-8c41-0b42c2bb4ebc/IMG_0734.JPG",
    f"{CDN}/5759942a-f73c-4306-a100-f3fd3f5e1aa9/fhs-merch-2025.png",
    f"{CDN}/4b5f1ad9-0fdc-4dec-a392-7d145867cf00/IMG_0722.jpg",
]
commissions = [
    (f"{CDN}/e29107e0-ae2e-4699-94e4-9e3cf796047f/IMG_6966.JPG", "Client party · Birthday party commission · 2026"),
    (f"{CDN}/c14a8a81-7ccb-4523-ad7d-bce981b2ddcd/IMG_6953.JPG", "Client party · Birthday party commission · 2026"),
    (f"{CDN}/e458766f-6984-416c-81f0-99239f530ddf/kiah-reptile-party-1.JPG", "Client party · Reptile party commission · 2025"),
    (f"{CDN}/ba785ce4-bc33-43fb-a400-3fd52fd84492/kiah-reptile-party-2.JPG", "Client party · Reptile party commission · 2025"),
    (f"{CDN}/ae67a86a-d76b-494c-a393-7c5b44e109c4/IMG_5460.png", "Client gift · Onitsuka Tiger commission · 2025"),
    (f"{CDN}/906062e5-992d-4e0e-877e-d8a91183df9e/IMG_5564.png", "Client gift · Onitsuka Tiger commission · 2025"),
    (f"{CDN}/771540c1-cfec-4ded-bcfb-76e95898335e/475730640_18483425812017687_1268968030103333545_n.jpg", "Client gift · Baby Nike commission · 2025"),
    (f"{CDN}/7effe316-ce39-433a-9b17-896e29b240fe/Screenshot+2025-06-21+at+3.02.23%E2%80%AFPM.png", "Client order · custom art commission · 2023"),
    (f"{CDN}/9d58d83d-65d1-4a32-9664-e75f23e29ae3/Screenshot+2025-07-01+at+12.01.53%E2%80%AFAM.png", "Client order · custom art commission · 2021"),
    (f"{CDN}/8bd2b8ae-933b-4ffb-bb0d-836d9fbfec87/Obi-dog-dec-2023.jpeg", "Dog portrait 2023"),
    (f"{CDN}/cbe83bc5-faa7-45ba-bf2c-e6e900c35741/05-Events-philz-popup-give-away-keychains-for-employee-gifts-2025-age16.jpg", "Philz coffee dude 2024"),
    (f"{CDN}/1786244066755-B848NX11LGKOTEJDZXL9/yoga-tlc.png", "Corepower Yoga Animals 2024"),
    (f"{CDN}/c101acaa-36ff-491c-b9d7-affbdb318f9b/496856393_18400623109107632_2139766122613354719_n.jpg", "Client gift · Yoga art commission · 2023"),
]
client_work_body = f"""
<section class="project-block wrap">
  <h2 class="project-title">VOX MEDIA</h2>
  <p class="project-meta">Vox Media &middot; Custom illustrations &middot; Holiday gifting 2024</p>
  {illustration(vox_imgs[0])}
  {photo_row(vox_imgs[1:])}
</section>
<section class="project-block wrap">
  <h2 class="project-title">FRIDAY HARBOR SUITES</h2>
  <p class="project-meta">Friday Harbor Suites &middot; Gift shop merch design &middot; 2023&ndash;present</p>
  <p class="project-desc">Custom illustrations on procreate, heat-pressed and decaled on site<br>launched first collection with a one day popup event</p>
  {illustration(fhs_imgs[0])}
  {photo_row(fhs_imgs[1:])}
  <h3 class="project-subtitle">Friday Harbor Suites&ndash; Collection 2025</h3>
  <p class="project-desc">New collection and art direction by managing director of FHS.</p>
  {photo_row(fhs_collection_imgs)}
</section>
<section class="project-block wrap">
  <h2 class="project-title">Custom Commissions</h2>
  <p class="project-meta">Custom work &middot; Various clients &middot; 2021&ndash;present</p>
  <div class="journey-grid cols-4">
    {''.join(f'<div class="journey-tile"><img src="{img(u)}" alt=""><div class="journey-caption">{html.escape(cap)}</div></div>' for u, cap in commissions)}
  </div>
</section>
"""
portfolio_page("client-work", "Client Work",
    "Commissioned illustration and product work for clients since 2021.", client_work_body)

# --- Tru Merch ---
tru_merch_cover = f"{CDN}/ea4e85a6-6572-4a78-a5b0-bf8b9d337de6/Screenshot+2026-05-15+at+7.02.44%E2%80%AFPM.png"
tlc_imgs = load("tru_merch_images.json")[1:]  # skip cover, already shown separately
tru_merch_body = f"""
<img class="project-cover wrap" src="{img(tru_merch_cover)}" alt="">
<section class="project-block wrap">
  <h2 class="project-title">TLC Collection</h2>
  <p class="project-meta">started 2023</p>
  {masonry([(img(it["src"]), f'<figure><img src="{img(it["src"])}" alt=""></figure>') for it in tlc_imgs])}
</section>
"""
portfolio_page("tru-merch", "Tru Merch",
    "Original character brand BeTru, founded 2023 &mdash; apparel, stickers, and accessories.", tru_merch_body)

# --- Events + Projects ---
events = [
    ("June 2026 - PS38 Graduating 5th graders charm bar", [
        "91d32516-1298-49da-80c9-eeea981995fb/PS38-5-girls-lined-up-papercup-gazebo.jpg",
        "e2d54e18-806c-4b90-b1db-1f9705741eff/PS38-6-be-tru-charm-bar-display-board.jpg",
        "c2b744af-0c7f-49d8-b6e0-045593271245/PS38-7-school-exterior-sign-pacific-street.jpeg",
        "4a07ceb2-0dd6-4a9c-912b-30da26a51979/PS38-25-kid-yellow-checkered-top-holding-motel-keychain.jpeg",
        "31c780ea-cd7d-41be-b1b3-42499eda167e/PS38-9-truman-helping-kids-charm-table.jpeg",
        "fba11f70-d6dc-4588-9c31-b4f29e1be8b9/PS38-12-ps38-kids-blue-shirts-charm-table-dup.jpg",
        "b3dd75e1-2e27-4edd-8f2e-aa3809f055cc/PS38-20-woman-blue-hair-browsing-charm-wall.jpeg",
        "ae8a2a2e-f288-422f-af55-f771099bfd82/PS38-22-truman-woman-bending-over-charm-display.jpeg",
        "3bfd9ef2-3861-4cc6-adfe-e321d43a22c9/PS38-28-overhead-orange-motel-keychain-pliers-charm-grid.jpeg",
        "dd432a2d-55df-4c17-91df-b925f136d62d/PS38-30-be-tru-charm-bar-sign-blue-keychain-on-table.jpeg",
        "ceaf5368-5cda-4f04-8eeb-bc5c2ed7ca25/PS38-37-tray-packaged-named-keychains-closer.jpeg",
        "3deaf375-7107-49dc-8dd8-7352f7d92e5e/PS38-35-boy-glasses-cap-holding-hotdog-motel-keychain.jpg",
    ]),
    ("June 2026 - Knollwood Elementary Maker Presentation", [
        "b5b7946a-ba15-47f0-8125-abbc837c55d8/KNOLLWOOD-40-knollwood-school-sign-exterior.jpeg",
        "f4e68ad6-528d-4014-bf3a-64f3572edc16/KNOLLWOOD-19-truman-presenting-rise-up-kids-raising-hands-2.jpg",
        "50574196-9f85-4a11-a8b2-755a4d95e8b1/KNOLLWOOD-22-truman-presenting-program-it-hotdog-run-slide.jpg",
        "7b2f0db7-5577-42fb-bba3-af12c1217008/KNOLLWOOD-8-kids-around-laptop-rise-game-dup.jpeg",
        "e0007672-627d-40f5-a770-c20db3ab2cbc/KNOLLWOOD-26-kids-playing-games-on-laptops.jpeg",
        "36682173-3993-42e9-b20c-02f44f95105e/KNOLLWOOD-25-two-boys-crowded-over-laptop.jpeg",
        "e47cbcf8-8704-4ef9-a538-00d63d8162fb/KNOLLWOOD-36-girls-at-laptop-smiling.jpeg",
        "3732ae32-0a6c-4364-bf24-77bae4957228/KNOLLWOOD-10-truman-girl-looking-at-sketchbook.jpg",
        "33892d58-212e-4ba4-8c75-a7e551491e47/KNOLLWOOD-4-closeup-cowboy-horse-keychains.jpeg",
        "84d9460b-9a4a-4f70-8269-75862bb30c3f/KNOLLWOOD-13-group-photo-whole-class.jpeg",
        "e1aed51e-f307-466b-bc59-f0053546c8d2/KNOLLWOOD-39-truman-teacher-posing-rise-up-slide.jpeg",
    ]),
    ("April 2026 - Dawn's Til Dusk Dumbo, Brooklyn", [
        "cec40a39-6280-475c-bf03-169b00c4c981/06-RealWorld-Dawns-Popup-2025-truman.JPG",
        "1a8ad89a-6a57-4102-b29b-ac6a719f75f9/06-RealWorld-Dawns-Popup-2025-customer-keychain.JPG",
        "99120fe4-17ec-4971-9fee-ecc49f390988/06-RealWorld-Dawns-Popup-2025-booth.JPG",
        "8b8dc8e5-1c9a-449d-bf4d-ccf26bf26d0d/06-RealWorld-Dawns-Popup-2025-customers.JPG",
    ]),
    ("April 2026 - FAD Market, TimeOut Dumbo, Brooklyn", [
        "e617e76e-78c8-40e1-918c-171951171833/06-RealWorld-Fad-Timeout-popup-family-customers-2025.JPG",
        "e9babd73-8d20-4ffb-8083-2c8d4ee0e7b6/06-RealWorld-Fad-Timeout-popup-motelkeychain-display-2025.jpg",
        "5c74c8e4-ad59-4a6c-95dc-4c0c03f36bb2/06-RealWorld-Fad-Timeout-popup-truman-at-booth-2025.JPG",
        "d605ef09-d323-471f-8c4d-d3800582f9c0/06-RealWorld-Fad-TimeOut-Popup-customers-at-booth.JPG",
    ]),
    ("December 2025 - CorePower Yoga Huntington Beach, California", [
        "fb76fe0d-7877-4caa-8add-7fa23392a387/06-Realworld-corepower-2025-popup-truman-tablesetup.jpg",
        "df11f6d5-f9cf-4fd0-bea0-e059d56fe118/06-Realworld-corepower-2025-popup-truman-helping-customer.jpg",
        "ee979ef6-5ee7-4e7e-8435-c2cc059a47d7/06-Realworld-corepower-2025-popup-truman-working.jpg",
        "a260fd74-8111-42b1-94db-23a9a12c8062/06-Realworld-corepower-2025-popup-customer2.jpg",
        "3c7ca4c4-e7e7-489b-8ad4-0acde2ed59af/06-Realworld-corepower-2025-popup-customer1.jpg",
    ]),
    ("December 2025 - Philz Coffee Huntington Beach, California", [
        "22702d16-58e3-4403-94cc-f5c4b2f5fb6d/06-RealWorld-Philz-2025-Popup-Customer-Sally-Pink-Keychain.jpg",
        "2d174073-41f9-49df-8508-8023cfb38148/06-RealWorld-Philz-2025-Popup-with-customers-little-kids.jpg",
        "ddc9dec2-3a7b-4cb1-904e-51195a7bd9d7/06-Realworld-Philz-2025-popup-with-daniel-young-friend-and-thomas-manager.jpg",
        "3d96cb8a-5ed3-4c11-b1bd-ebfc36ce07d2/06-Realworld-philz-2025-popup-give-away-keychains-for-employee-gifts.jpg",
    ]),
    ("November 2025 - Seongsu Seoul, Korea (remote)", [
        "b41b2439-1eec-46b2-85a6-08beef49dca7/06-Realworld-seongsu-popup-sign.jpg",
        "1a7e9055-effa-4281-a364-984adf8c4109/06-Realworld-seongsu-popup-customers2.jpg",
        "e9cb8696-a07b-4130-9717-ff78e395db30/06-Realworld-seongsu-popup-setup2.jpg",
        "1413a8dc-7161-49e3-828d-3b7294197391/06-Realworld-seongsu-popup-customers.jpg",
    ]),
    ("September 2025 - Fad Market/Montague Street Brooklyn", [
        "d6bd962d-6a97-48c7-824b-f493fb9a21c2/557711349_17857829103518335_7504760071234781922_n.jpg",
        "f4b4d960-6e67-49c0-bf22-103b672c5e4c/3EDE648F-513B-48A9-95E8-61BC26A395C9.jpg",
        "7b904cdb-e6d5-40c0-aafd-f7d5a16c59f1/559260950_17857829094518335_1742727309389999358_n.jpg",
        "02012e93-8fcc-48e4-bc66-85e20ea4537a/IMG_4999.jpg",
        "65fdf1da-4b6e-4d8b-9778-d31e826eedfd/IMG_1440.jpg",
        "11e64187-96e4-4601-a00b-fe6d1773b182/IMG_2152.jpg",
    ]),
    ("April 2025 - Redeemer Presbyterian Church Volunteer Appreciation Event", [
        "2baea238-b787-4224-b675-e508eecff17d/IMG_5311.jpg",
        "c4026d7b-2a77-4262-85fa-ebf6354f53ea/IMG_5318.jpg",
        "7b76b2c4-f278-4f29-b66d-0787cf6e4de5/IMG_5352.jpg",
        "765a4810-4f36-4d28-b28f-d45d232ac275/IMG_5328.jpg",
        "262cdda4-0658-42dc-b1b9-a930cbc46efe/IMG_5335.jpg",
        "f0ca57f6-68fb-4bd9-b2c8-d492d6841ea8/IMG_5384.jpg",
        "0191b737-0604-432a-bf42-75ad36416c17/IMG_5304.jpg",
    ]),
    ("July 2024 - Philz Coffee Huntington Beach, California", [
        "072973f3-be6d-4961-bf9b-0d5b5837e020/IMG_7453.jpg",
        "af572067-8f4a-44ba-adfb-3f3af2fa6795/IMG_7467.jpg",
        "99376093-5046-4215-a68d-9f122b3cee4c/IMG_7494.JPG",
        "d891f508-d1bd-4999-a8ec-e99c5d003403/IMG_7483.jpg",
    ]),
    ("July 2024 - Lululemon Brea, California", [
        "1750374648728-98KX8W9BI4QY3AC9S4IX/90125621_1743994491165041_r.jpg",
        "f242a218-d96a-40b9-81f8-ec5497c09a3a/IMG_7741.jpg",
        "fc813ae2-85a7-4336-968d-e85d37a08ab8/IMG_7731.jpg",
        "e317d795-0558-466e-863d-e112b9331b5c/IMG_7739.jpg",
    ]),
]
events_body = '<section class="project-block wrap"><h2 class="project-title">EVENTS</h2>'
for name, imgs_list in events:
    events_body += f'<h3 class="project-subtitle">{html.escape(name)}</h3>{photo_row([f"{CDN}/{u}" for u in imgs_list])}'
events_body += '</section>'
portfolio_page("events-projects", "Events + Projects",
    "Maker demos, pop-ups, and markets from Brooklyn to Seoul.", events_body)

# ---------- JOURNAL ----------
posts = load("posts_extracted.json")
journal_thumbs = load("journal_thumbs.json")
# Dev Log 1 is a direct YouTube link, not a page
dev_log = {"title": "DEV LOG 1", "date": "1/25/26", "youtube": "https://youtu.be/S-4ASV5tQos",
           "slug": "jo13sztq8wc9j4t6r3l25ybbjowy8k"}

def journal_card(href, thumb_url, date, title, external=False):
    target = ' target="_blank" rel="noopener"' if external else ""
    return f"""<a class="journal-card" href="{href}"{target}>
      <img src="{img(thumb_url)}" alt="">
      <div class="journal-card-date">{date}</div>
      <div class="journal-card-title">{html.escape(title)}</div>
      <div class="journal-card-more">Read More</div>
    </a>"""

journal_cards = journal_card(dev_log["youtube"], journal_thumbs[dev_log["slug"]], dev_log["date"], dev_log["title"], external=True)
for p in posts:
    slug = p["slug"]
    journal_cards += journal_card(f"/journal/{slug}.html", journal_thumbs[slug], p["date"], p["title"])

journal_index_body = f"""
<h1 class="page-title">Journal</h1>
<div class="journal-grid wrap">
{journal_cards}
</div>
"""
write("journal/index.html", page("Journal — Truman Cho", "Journal", journal_index_body,
      "Truman Cho's journal: a dated record of games, merch, and events since 2023."))

for i, p in enumerate(posts):
    slug = p["slug"]
    gallery_imgs = masonry([(img(u), f'<figure><img src="{img(u)}" alt=""></figure>') for u in p["images"]], cols=2, extra_class="post-gallery")
    paragraphs = "".join(f"<p>{html.escape(t)}</p>" for t in p["text"].split("\n") if t.strip())
    prev_link = f'<a href="/journal/{posts[i-1]["slug"]}.html">&larr; {html.escape(posts[i-1]["title"])}</a>' if i > 0 else '<span></span>'
    next_link = f'<a href="/journal/{posts[i+1]["slug"]}.html">{html.escape(posts[i+1]["title"])} &rarr;</a>' if i < len(posts)-1 else '<span></span>'
    post_body = f"""
<div class="post-header">
  <div class="date">{p["date"]}</div>
  <h1>{html.escape(p["title"])}</h1>
</div>
<div class="post-body">
{paragraphs}
</div>
{gallery_imgs}
<div class="post-nav">{prev_link}{next_link}</div>
"""
    write(f"journal/{slug}.html", page(f"{p['title']} — Truman Cho", "Journal", post_body))

print("\nBUILD COMPLETE")
