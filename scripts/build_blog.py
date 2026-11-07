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


def head(title, description, url, extra_ld):
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
"""


def tail():
    return f"""<footer>
Pinoy Mobile Mechanic LLC &middot; Mobile auto repair within 50 miles of Mira Mesa, San Diego<br>
California Bureau of Automotive Repair &middot; ARD 315968<br>
<a href="/">Home</a> &middot; <a href="/blog/">Car repair guides</a> &middot; <a href="tel:{PHONE}">{PHONE_TEXT}</a>
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
    page = head(f"{a['title']} | Pinoy Mobile Mechanic", a["description"], url, ld)
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
    page = head(f"{title} | Pinoy Mobile Mechanic", desc, url, ld)
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
    urls = [(SITE + "/", today), (SITE + "/blog/", today), (SITE + "/links/", today)]
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


SOCIALS = [
    ("Instagram", "@pinoy_mobile_mechanic", "https://instagram.com/pinoy_mobile_mechanic"),
    ("Facebook", "Pinoy Mobile Mechanic", "https://www.facebook.com/Pinoymobilemechanic"),
]


def build_links_page(arts):
    """/links/: every guide plus social accounts. Also works as a link-in-bio page."""
    url = SITE + "/links/"
    title = "Guides, Articles and Social Links"
    desc = ("Every Pinoy Mobile Mechanic car repair guide in one place, plus our Instagram and "
            "Facebook. Mobile auto repair across San Diego County.")
    ld = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": title, "url": url,
           "publisher": BUSINESS}]
    socials = "".join(
        f'<li><a href="{u}" target="_blank" rel="noopener">{esc(n)}</a><p>{esc(h)}</p></li>'
        for n, h, u in SOCIALS)
    guides = "".join(
        f'<li><a href="/blog/{a["slug"]}/">{esc(a["title"])}</a><p class="meta">{nice_date(a["date"])}</p></li>'
        for a in arts)
    page = head(f"{title} | Pinoy Mobile Mechanic", desc, url, ld)
    page += f"""<p class="crumbs"><a href="/">Home</a> / Links</p>
<h1>Guides, articles and social links</h1>
<p><a class="btn btn-primary" href="{BOOK}" target="_blank" rel="noopener">Book a visit</a></p>
<p style="margin:10px 0 0"><a class="btn btn-ghost" href="tel:{PHONE}">Call or text {PHONE_TEXT}</a></p>
<h2>Follow us</h2>
<ul class="list">{socials}</ul>
<h2>All car repair guides ({len(arts)})</h2>
<ul class="list">{guides}</ul>
"""
    page += tail()
    os.makedirs(os.path.join(ROOT, "links"), exist_ok=True)
    open(os.path.join(ROOT, "links", "index.html"), "w", encoding="utf-8").write(page)


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
    build_links_page(arts)
    update_homepage(arts)
    print(f"built {len(arts)} article(s)")


if __name__ == "__main__":
    main()
