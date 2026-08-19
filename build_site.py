#!/usr/bin/env python3
"""Generates the static truman-cho.com mirror from scraped _data/*.json into HTML files."""
import json, os, re, html
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "_data")

def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)

url_map = load("url_to_filename.json")

def img(url, cls=""):
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

NAV_ITEMS = [
    ("/", "Home", True),
    ("https://www.betrumaker.com", "Maker Resource", False),
    ("/about.html", "About", False),
    ("/journal/", "Journal", False),
    ("/game-dev.html", "Game Dev", False),
    ("/projects.html", "Projects", False),
]

ABOUT_DROPDOWN = [
    ("/about.html", "About"),
    ("/timeline.html", "Timeline"),
    ("/resume.html", "Resume"),
    ("/youtube.html", "YouTube"),
]

def nav_html(current):
    links = []
    for href, label, is_home in NAV_ITEMS:
        cls = " current" if (current == label) else ""
        target = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        links.append(f'<a href="{href}" class="{cls.strip()}"{target}>{label}</a>')
    return "\n      ".join(links)

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
</header>
<main>
{body}
</main>
<footer class="site-footer">
  <div class="foot-links">
    <a href="/projects.html">Projects</a> · <a href="/journal/">Journal</a> · <a href="/about.html">About</a>
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
hero_accent = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/142f5e09-cc8c-4fb1-82ce-61540e97b2f3/IMG_4264.jpg"
hero_banner = "https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/e24f0bbb-3194-4482-9a05-bca7e7b26250/3.png"
home_body = f"""
<section class="hero">
  <div class="hero-intro">
  <p>I am an artist and game developer who loves bringing things to life through my game dev, small art business and teaching kids to be creators.</p>
  <p>My latest project: a free resource so any kid can cross from consumer to maker on their own terms.</p>
  <a class="cta" href="https://www.betrumaker.com" target="_blank" rel="noopener">visit betrumaker.com</a>
  </div>
  <div class="hero-collage">
    {''.join(f'<img src="{img(u)}" alt="">' for u in hero_row)}
    <div class="accent"><img src="{img(hero_accent)}" alt=""></div>
  </div>
  <p style="max-width:720px;margin:0 auto 50px;">My parents wouldn't let me play Angry Birds, so I built my own version out of blocks. I wanted a Game Boy, so I made a cardboard version. That's still basically how I work. If something doesn't exist in the form I need, I figure out how to make it. I study computer science at Brooklyn Tech and publish my games on itch.io. My current itch to create is figuring out what it takes to shift a kid from player to maker.</p>
</section>
<a class="hero-banner" href="/projects.html">
  <img src="{img(hero_banner)}" alt="Featured Projects">
</a>
"""
write("index.html", page("Truman Cho", "Home", home_body))

# ---------- ABOUT ----------
about_imgs = [
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/9ff6ec98-1db8-4d43-a7b8-29450a153674/Screenshot+2025-06-23+at+6.47.47%E2%80%AFPM.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/73f927f2-ef23-4909-a002-d965289c32ea/14.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/cc6d7c41-2a7b-4c85-ad5f-9f7903aa28ca/16.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/f1b2c854-df7c-40e8-ba75-c6d51c1e4ce6/557711349_17857829103518335_7504760071234781922_n.jpg",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/a24b8567-c689-427a-bf99-d3af20b36ef1/657740688_17880431190515204_2166118040848615964_n.jpg",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/6c4516f9-f021-46c4-bb89-5b84d8798972/Screenshot+2025-06-28+at+2.36.23%E2%80%AFPM.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/9e6482d0-5a55-454c-9ade-21988b631e1f/Screenshot+2025-06-29+at+8.47.39%E2%80%AFPM.png",
"https://images.squarespace-cdn.com/content/v1/6851fcf232cff511a449134f/e9266336-b6b7-48b9-9772-c0968d6219b3/maker-demo-classroom1.jpg",
]
about_body = f"""
<h1 class="page-title">About Me</h1>
<div class="post-body">
<p>I'm Truman Cho, a junior at Brooklyn Technical High School in New York.</p>
<p>I've been making things my whole life &mdash; not because anyone told me to, but because I couldn't help it. Games, comics, cardboard consoles, merch, businesses. Most of it started with a question I couldn't answer any other way except by building something.</p>
<p>I publish original games on itch.io, press them onto Game Boy cartridges, and sell my own character art at markets and pop-up events. Since I was ten I've worked at a boutique hotel in Washington State &mdash; starting in the kitchen and eventually designing the merchandise still sold in their gift shop.</p>
<p>My current itch to create is figuring out what it takes to shift a kid from player to maker.</p>
<p>All started with a comic book I bought for $1 from a kid at the park.</p>
</div>
{masonry([(img(u), f'<figure><img src="{img(u)}" alt=""></figure>') for u in about_imgs])}
"""
write("about.html", page("About — Truman Cho", "About", about_body))

# ---------- TIMELINE ----------
timeline = load("timeline_images.json")
tl_figures = [
    (img(t["src"]), f'<figure><img src="{img(t["src"])}" alt="{html.escape(t.get("caption",""))}"><figcaption>{html.escape(t.get("caption",""))}</figcaption></figure>')
    for t in timeline
]
timeline_body = f"""
<h1 class="page-title">Timeline</h1>
<p class="page-subtitle">Twelve years of making, in order &mdash; from cardboard consoles to published games to a hotel gift shop to markets across three cities.</p>
{masonry(tl_figures)}
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
projects_body = """
<h1 class="page-title">Projects</h1>
<div class="project-cats">
  <a class="project-cat" href="https://www.betrumaker.com" target="_blank" rel="noopener">
    <img src="/assets/img/IMG_4270.jpg" alt="Maker Project">
    <span class="label">MAKER PROJECT</span>
  </a>
  <a class="project-cat" href="/portfolio/client-work.html">
    <img src="/assets/img/IMG_9565.jpg" alt="Client Work">
    <span class="label">CLIENT WORK</span>
  </a>
  <a class="project-cat" href="/portfolio/tru-merch.html">
    <img src="/assets/img/503040689_1896533771159955_6325911197630627969_n.jpg" alt="Tru Merch">
    <span class="label">TRU MERCH</span>
  </a>
  <a class="project-cat" href="/portfolio/events-projects.html">
    <img src="/assets/img/IMG_4999.jpg" alt="Events + Projects">
    <span class="label">EVENTS + PROJECTS</span>
  </a>
</div>
"""
write("projects.html", page("Projects — Truman Cho", "Projects", projects_body))

# ---------- PORTFOLIO GALLERIES ----------
def gallery_page(fname, title, images_file, subtitle):
    imgs = load(images_file)
    figures = [
        (img(it["src"]), f'<figure><img src="{img(it["src"])}" alt="{html.escape(it.get("caption",""))}">'
        + (f'<figcaption>{html.escape(it["caption"])}</figcaption>' if it.get("caption") else "")
        + '</figure>')
        for it in imgs
    ]
    body = f"""
<h1 class="page-title">{title}</h1>
<p class="page-subtitle">{subtitle}</p>
{masonry(figures)}
"""
    write(f"portfolio/{fname}.html", page(f"{title} — Truman Cho", "Projects", body))

gallery_page("client-work", "Client Work", "client_work_images.json",
             "Commissioned illustration and product work for clients since 2021.")
gallery_page("tru-merch", "Tru Merch", "tru_merch_images.json",
             "Original character brand BeTru, founded 2023 &mdash; apparel, stickers, and accessories.")
gallery_page("events-projects", "Events + Projects", "events_projects_images.json",
             "Maker demos, pop-ups, and markets from Brooklyn to Seoul.")

# ---------- JOURNAL ----------
posts = load("posts_extracted.json")
# Dev Log 1 is a direct YouTube link, not a page
dev_log = {"title": "DEV LOG 1", "date": "1/25/26", "youtube": "https://youtu.be/S-4ASV5tQos"}

journal_list_items = f'<div class="journal-item"><span class="date">{dev_log["date"]}</span><a class="title" href="{dev_log["youtube"]}" target="_blank" rel="noopener">{dev_log["title"]} (YouTube)</a></div>\n'
for p in posts:
    slug = p["slug"]
    journal_list_items += f'<div class="journal-item"><span class="date">{p["date"]}</span><a class="title" href="/journal/{slug}.html">{html.escape(p["title"])}</a></div>\n'

journal_index_body = f"""
<h1 class="page-title">Journal</h1>
<div class="journal-list">
{journal_list_items}
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
