#!/usr/bin/env python3
"""Build the Pinoy Mobile Mechanic blog.

Reads content/articles/*.md (front matter + Markdown) and writes:
  blog/<slug>/index.html   one page per article
  blog/index.html          the article list
  sitemap.xml, robots.txt  for Google and Bing

Run from the repo root:  python3 scripts/build_blog.py
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys

try:
    import markdown
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
                           "--break-system-packages", "markdown", "pyyaml"])
    import markdown
    import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content", "articles")
OUT = os.path.join(ROOT, "blog")
SITE = "https://pinoymobilemechanic.com"
BOOK = "https://calendar.app.google/mxYcWMjDeqJaWwGKA"
PHONE = "+18589337045"
PHONE_TEXT = "858-933-7045"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800'
         '&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">')

BUSINESS = {
    "@type": "AutoRepair",
    "name": "Pinoy Mobile Mechanic LLC",
    "url": SITE + "/",
    "telephone": "+1-858-933-7045",
    "logo": SITE + "/logo.png",
    "image": SITE + "/og-image.png",
    "address": {"@type": "PostalAddress", "addressLocality": "San Diego",
                "addressRegion": "CA", "addressCountry": "US"},
}


def esc(s):
    return html.escape(str(s), quote=True)


def nice_date(d):
    return d.strftime("%B %-d, %Y")


def load_articles():
    arts = []
    for name in sorted(os.listdir(SRC)):
        if not name.endswith(".md"):
            continue
        raw = open(os.path.join(SRC, name), encoding="utf-8").read()
        if not raw.startswith("---"):
            sys.exit(f"{name}: missing front matter")
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm)
        for key in ("title", "slug", "description", "date"):
            if not meta.get(key):
                sys.exit(f"{name}: front matter needs '{key}'")
        d = meta["date"]
        if isinstance(d, str):
            d = datetime.date.fromisoformat(d)
        meta["date"] = d
        meta["body_html"] = markdown.markdown(body, extensions=["tables", "sane_lists"])
        arts.append(meta)
    today = datetime.date.today()
    arts = [a for a in arts if a["date"] <= today]  # future-dated drafts stay unpublished
    arts.sort(key=lambda a: (a["date"], a["slug"]), reverse=True)
    return arts


def head(title, description, url, extra_ld, current=None):
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>'
                 for x in extra_ld)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta name="theme-color" content="#C41E24">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Pinoy Mobile Mechanic">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
{FONTS}
<link rel="stylesheet" href="/blog/blog.css">
{ld}
</head>
<body>
<div class="wrap">
<a class="mast" href="/"><img src="/logo.png" width="48" height="48" alt="Pinoy Mobile Mechanic logo"><div><b>Pinoy Mobile Mechanic</b><span>We come to you &middot; San Diego</span></div></a>
{nav(current)}
"""


MENU = [("why-us", "Why us", "/why-us/"), ("guides", "Guides", "/blog/"), ("reviews", "Reviews", "/reviews/")]


def nav(current=None):
    links = "".join(
        f'<li><a href="{u}"{" aria-current=\"page\"" if k == current else ""}>{n}</a></li>'
        for k, n, u in MENU)
    return f'<nav aria-label="Main"><ul class="nav">{links}</ul></nav>'


def tail():
    return f"""<footer>
Pinoy Mobile Mechanic LLC &middot; Mobile auto repair within 50 miles of Mira Mesa, San Diego<br>
California Bureau of Automotive Repair &middot; ARD 315968<br>
<a href="/">Home</a> &middot; <a href="/why-us/">Why us</a> &middot; <a href="/blog/">Car repair guides</a> &middot; <a href="/reviews/">Reviews</a> &middot; <a href="tel:{PHONE}">{PHONE_TEXT}</a><br>
Follow us: {social_links()}
</footer>
</div>
<div class="dock"><div class="dock-inner">
<a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Book a visit</a>
<a class="btn btn-ghost" href="tel:{PHONE}">Call</a>
</div></div>
</body>
</html>
"""


def cta():
    return f"""<div class="cta">
<h2>Skip the tow. We come to you.</h2>
<p>Pinoy Mobile Mechanic fixes cars at your home or work anywhere within 50 miles of Mira Mesa, Mon&ndash;Sat 8&ndash;5. You get a written quote before any work starts.</p>
<p><a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Book a visit online</a></p>
<p style="margin:10px 0 0">Or call or text <a href="tel:{PHONE}">{PHONE_TEXT}</a> and describe what the car is doing.</p>
</div>
"""


def build_article(a, arts):
    url = f"{SITE}/blog/{a['slug']}/"
    ld = [
        {"@context": "https://schema.org", "@type": "BlogPosting",
         "headline": a["title"], "description": a["description"],
         "datePublished": a["date"].isoformat(),
         "dateModified": str(a.get("updated") or a["date"].isoformat()),
         "mainEntityOfPage": url, "image": SITE + "/og-image.png",
         "author": {"@type": "Organization", "name": "Pinoy Mobile Mechanic"},
         "publisher": BUSINESS},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Car repair guides", "item": SITE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": url}]},
    ]
    faq = a.get("faq") or []
    faq_html = ""
    if faq:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]})
        faq_html = "<h2>Frequently asked questions</h2>\n" + "".join(
            f"<h3>{esc(f['q'])}</h3>\n<p>{esc(f['a'])}</p>\n" for f in faq)
    others = [o for o in arts if o["slug"] != a["slug"]][:3]
    related = ""
    if others:
        related = '<div class="related"><h2>More car repair guides</h2><ul class="list">' + "".join(
            f'<li><a href="/blog/{o["slug"]}/">{esc(o["title"])}</a></li>' for o in others) + "</ul></div>"
    page = head(f"{a['title']} | Pinoy Mobile Mechanic", a["description"], url, ld, "guides")
    page += f"""<p class="crumbs"><a href="/">Home</a> / <a href="/blog/">Car repair guides</a></p>
<article>
<h1>{esc(a['title'])}</h1>
<p class="meta">{nice_date(a['date'])} &middot; Pinoy Mobile Mechanic, San Diego</p>
{a['body_html']}
{faq_html}
<h2>About Pinoy Mobile Mechanic</h2>
<p>Pinoy Mobile Mechanic is a mobile auto repair business based in Mira Mesa, San Diego. It repairs cars at the customer's home or work lot anywhere within 50 miles, Monday to Saturday, 8 AM to 5 PM, and is licensed by the California Bureau of Automotive Repair (ARD 315968). Call or text {PHONE_TEXT}.</p>
</article>
{cta()}
{related}
"""
    page += tail()
    path = os.path.join(OUT, a["slug"])
    os.makedirs(path, exist_ok=True)
    open(os.path.join(path, "index.html"), "w", encoding="utf-8").write(page)


def build_index(arts):
    url = SITE + "/blog/"
    title = "Car Repair Guides for San Diego Drivers"
    desc = ("Straight answers on car problems, repair costs and maintenance from a San Diego "
            "mobile mechanic. Symptoms, prices and when to call a pro.")
    ld = [{"@context": "https://schema.org", "@type": "Blog", "name": title, "url": url,
           "publisher": BUSINESS}]
    items = "".join(
        f'<li><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a>'
        f'<p>{esc(a["description"])}</p><p class="meta">{nice_date(a["date"])}</p></li>'
        for a in arts)
    page = head(f"{title} | Pinoy Mobile Mechanic", desc, url, ld, "guides")
    page += f"""<p class="crumbs"><a href="/">Home</a> / Car repair guides</p>
<h1>{title}</h1>
<p class="lede">Plain-English answers from a mobile mechanic who works on cars in driveways across San Diego County every day.</p>
<div class="hazard" aria-hidden="true"></div>
<ul class="list">{items}</ul>
{cta()}
"""
    page += tail()
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)


def build_sitemap(arts):
    today = datetime.date.today().isoformat()
    urls = [(SITE + "/", today), (SITE + "/why-us/", today), (SITE + "/blog/", today),
            (SITE + "/reviews/", today)]
    urls += [(f"{SITE}/blog/{a['slug']}/", a["date"].isoformat()) for a in arts]
    body = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n')
    bots = ["*", "Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "GPTBot",
            "Google-Extended", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Applebot"]
    robots = "# Search engines and AI assistants are welcome to read and cite this site.\n"
    robots += "".join(f"\nUser-agent: {b}\nAllow: /\n" for b in bots)
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots + f"\nSitemap: {SITE}/sitemap.xml\n")


# Paste the Google Business Profile link (Share > copy link, or the Maps URL) once it's verified.
GOOGLE_PROFILE_URL = "https://www.google.com/maps/place/PINOY+MOBILE+MECHANIC/@32.924324,-117.1217935,17z/data=!3m1!4b1!4m6!3m5!1s0x80dbf9764482941b:0xc0eb98c3f1605d2f!8m2!3d32.9243195!4d-117.1192186!16s%2Fg%2F11p2llr00w"

SOCIALS = [
    ("Facebook", "https://www.facebook.com/Pinoymobilemechanic"),
    ("Instagram", "https://instagram.com/pinoy_mobile_mechanic"),
] + ([("Google", GOOGLE_PROFILE_URL)] if GOOGLE_PROFILE_URL else [])


def social_links(color="var(--ink-3)"):
    return " &middot; ".join(
        f'<a href="{u}" target="_blank" rel="noopener" style="color:{color}">{n}</a>' for n, u in SOCIALS)


# Paste the Google "Ask for reviews" short link here once the Google Business Profile is verified.
GOOGLE_REVIEW_LINK = ""


def build_why_us():
    url = SITE + "/why-us/"
    title = "Why San Diego Drivers Trust Pinoy Mobile Mechanic"
    desc = ("Licensed by the California Bureau of Automotive Repair, a written quote before any work, "
            "and repairs at your home or work lot anywhere in San Diego County.")
    ld = [{"@context": "https://schema.org", "@type": "AboutPage", "name": title, "url": url,
           "about": BUSINESS}]
    page = head(f"{title} | Pinoy Mobile Mechanic", desc, url, ld, "why-us")
    page += f"""<p class="crumbs"><a href="/">Home</a> / Why us</p>
<h1>Why San Diego drivers trust us</h1>
<p class="lede">Pinoy Mobile Mechanic is a local, family-run mobile auto repair business based in Mira Mesa. We bring the shop to your driveway or work lot, tell you what's wrong in plain words, and put the price in writing before we touch anything.</p>
<div class="hazard" aria-hidden="true"></div>
<ul class="facts">
<li><b>Licensed in California</b>Pinoy Mobile Mechanic LLC is registered with the California Bureau of Automotive Repair, license ARD 315968. You can look it up on the <a href="https://www.bar.ca.gov/" target="_blank" rel="noopener">Bureau of Automotive Repair</a> website.</li>
<li><b>A written quote before any work</b>You see the price in writing and approve it before a repair starts. If something else comes up, we ask again first. Nothing gets done without your OK.</li>
<li><b>Straight answers</b>We explain what's wrong without the jargon. If a job really needs a shop with a lift, we tell you so instead of guessing in your driveway.</li>
<li><b>We come to you</b>Home, apartment lot or office parking lot, anywhere within 50 miles of Mira Mesa. That covers all of San Diego County, Monday to Saturday, 8 AM to 5 PM.</li>
<li><b>A real person answers</b>Call or text <a href="tel:{PHONE}">{PHONE_TEXT}</a> and you talk to the mechanic, not a call center.</li>
<li><b>Free, honest guides</b>Our <a href="/blog/">car repair guides</a> explain what common problems mean, so you know what you're dealing with before you book anyone.</li>
</ul>
<h2>How a visit works</h2>
<ol>
<li><b>Book online or call.</b> Tell us the address, the vehicle and what it's doing.</li>
<li><b>We find the cause.</b> The van arrives equipped, and we diagnose the problem where the car is parked.</li>
<li><b>You approve a written quote.</b> No surprises.</li>
<li><b>We fix it on the spot.</b> Most jobs are done right there while you keep working.</li>
</ol>
<p>See what customers say on our <a href="/reviews/">reviews page</a>.</p>
{cta()}
"""
    page += tail()
    os.makedirs(os.path.join(ROOT, "why-us"), exist_ok=True)
    open(os.path.join(ROOT, "why-us", "index.html"), "w", encoding="utf-8").write(page)


def build_reviews():
    url = SITE + "/reviews/"
    title = "Customer Reviews"
    desc = ("Reviews and testimonials from Pinoy Mobile Mechanic customers across San Diego County, "
            "copied word for word from Google, Facebook and Yelp.")
    data = yaml.safe_load(open(os.path.join(ROOT, "content", "reviews.yml"), encoding="utf-8")) or {}
    reviews = data.get("reviews") or []
    reviews.sort(key=lambda r: str(r.get("date", "")), reverse=True)
    cards = ""
    for r in reviews:
        stars = "&#9733;" * int(r.get("rating", 5))
        where = f" &middot; {esc(r['area'])}" if r.get("area") else ""
        src = esc(r.get("source", ""))
        if r.get("link"):
            src = f'<a href="{esc(r["link"])}" target="_blank" rel="noopener">{src}</a>'
        cards += (f'<div class="review"><p aria-label="{int(r.get("rating", 5))} out of 5 stars" '
                  f'style="color:var(--accent-text)">{stars}</p><p>&ldquo;{esc(r["text"])}&rdquo;</p>'
                  f'<p class="meta">{esc(r["name"])}{where} &middot; {src} &middot; {esc(r.get("date", ""))}</p></div>')
    if not cards:
        cards = ("<p>We're a new business collecting our first online reviews. Every review shown here "
                 "will be a real one, copied word for word from where the customer posted it.</p>")
    widget = open(os.path.join(ROOT, "content", "review-widget.html"), encoding="utf-8").read()
    widget = re.sub(r"<!--.*?-->", "", widget, flags=re.S).strip()
    if widget:
        cards = f'<div class="review-widget">{widget}</div>\n' + (cards if reviews else "")
    leave = ""
    if GOOGLE_REVIEW_LINK:
        leave = (f'<p><a class="btn btn-primary" href="{GOOGLE_REVIEW_LINK}" target="_blank" '
                 f'rel="noopener">Leave a Google review</a></p>')
    page = head(f"{title} | Pinoy Mobile Mechanic", desc, url, [], "reviews")
    page += f"""<p class="crumbs"><a href="/">Home</a> / Reviews</p>
<h1>What customers say</h1>
<p class="lede">Real reviews from drivers we've helped across San Diego County.</p>
<div class="hazard" aria-hidden="true"></div>
{cards}
<h2>Had us out recently?</h2>
<p>A short review helps other San Diego drivers find a mechanic they can trust.</p>
{leave}
<p><a class="btn btn-ghost" href="https://www.facebook.com/Pinoymobilemechanic" target="_blank" rel="noopener">See us on Facebook</a></p>
{cta()}
"""
    page += tail()
    os.makedirs(os.path.join(ROOT, "reviews"), exist_ok=True)
    open(os.path.join(ROOT, "reviews", "index.html"), "w", encoding="utf-8").write(page)


def update_homepage(arts):
    """Fill the newest guides between the GUIDES markers on the homepage."""
    path = os.path.join(ROOT, "index.html")
    s = open(path, encoding="utf-8").read()
    start, end = "<!-- GUIDES:START -->", "<!-- GUIDES:END -->"
    if start not in s or end not in s:
        sys.exit("index.html is missing the GUIDES markers")
    items = "".join(
        f'<li><a href="/blog/{a["slug"]}/" style="color:var(--ink);text-decoration:none">{esc(a["title"])}</a></li>'
        for a in arts[:5])
    block = f'{start}\n    <ul class="svc">{items}</ul>\n    {end}'
    s = s[:s.index(start)] + block + s[s.index(end) + len(end):]
    s0, s1 = "<!-- SOCIAL:START -->", "<!-- SOCIAL:END -->"
    if s0 not in s or s1 not in s:
        sys.exit("index.html is missing the SOCIAL markers")
    s = s[:s.index(s0)] + f"{s0}Follow us: {social_links()}{s1}" + s[s.index(s1) + len(s1):]
    open(path, "w", encoding="utf-8").write(s)


def build_llms_txt(arts):
    """llms.txt: a plain summary AI assistants can read in one fetch."""
    lines = [
        "# Pinoy Mobile Mechanic",
        "",
        "> Mobile auto repair in San Diego County, California. Pinoy Mobile Mechanic LLC is based in "
        "Mira Mesa (92126) and fixes cars at the customer's home or work lot anywhere within 50 miles: "
        "San Diego, Poway, Escondido, San Marcos, Carlsbad, Oceanside, Vista, Encinitas, Del Mar, "
        "La Mesa, El Cajon, Santee, Chula Vista, National City and nearby.",
        "",
        "- Services: hybrid service and repair, brakes, oil changes and fluids, diagnostics "
        "(check engine light, electrical, no-start, warning lights), A/C service, starters, "
        "alternators, belts, suspension, tune-ups.",
        "- Hours: Monday to Saturday 8:00 AM to 5:00 PM Pacific. Closed Sunday.",
        f"- Phone and text: {PHONE_TEXT}. Book online: {BOOK}",
        "- Licensed by the California Bureau of Automotive Repair, ARD 315968. "
        "Customers get a written quote before any work starts.",
        "",
        "## Pages",
        f"- [Home]({SITE}/): services, service area, hours, booking",
        f"- [Car repair guides]({SITE}/blog/): answers to common car problems and repair costs",
        "",
        "## Car repair guides",
    ]
    lines += [f"- [{a['title']}]({SITE}/blog/{a['slug']}/): {a['description']}" for a in arts]
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")


def main():
    arts = load_articles()
    slugs = [a["slug"] for a in arts]
    if len(slugs) != len(set(slugs)):
        sys.exit("duplicate slug in content/articles")
    for a in arts:
        build_article(a, arts)
    build_index(arts)
    build_sitemap(arts)
    build_llms_txt(arts)
    build_why_us()
    build_reviews()
    update_homepage(arts)
    print(f"built {len(arts)} article(s)")


if __name__ == "__main__":
    main()
