# Pinoy Mobile Mechanic website

Static site for pinoymobilemechanic.com. Pushing to `main` publishes it. No approval step.

- `index.html` — homepage (booking link and phone in the CONFIG block at the bottom)
- `content/articles/*.md` — blog articles (front matter + Markdown). Source of truth.
- `content/keywords.md` — article queue
- `scripts/build_blog.py` — builds `blog/`, `sitemap.xml`, `robots.txt` from the articles. Never hand-edit `blog/*/index.html` or `sitemap.xml`.

## Business facts (use only these)

- Pinoy Mobile Mechanic LLC, mobile auto repair, based in Mira Mesa (92126), travels up to 50 miles: all of San Diego County.
- Mon–Sat 8:00–5:00, Sunday closed. Phone/text 858-933-7045. Book online (button on every page).
- Licensed with the California Bureau of Automotive Repair, ARD 315968. Written quote before any work starts.
- Services: hybrid service and repair, brakes, oil changes and fluids, diagnostics (check engine, electrical, no-start, warning lights), A/C service, starters, alternators, belts, suspension, tune-ups.
- Do NOT state Pinoy prices (not approved yet), warranty terms, certifications (e.g. ASE), years of experience, review counts, or customer stories. Do not invent any of these.

## Daily article workflow

1. `git pull` on `main`.
2. Open `content/keywords.md`, take the first unchecked line. Skip it if `content/articles/` already has that slug.
3. Research with web search: what people actually ask about the phrase, and current price ranges if it's a cost topic. Open the pages you use. Cite numbers with a link to the page they came from.
4. Write `content/articles/YYYY-MM-DD-<slug>.md` (date = today in America/Los_Angeles):

   ```
   ---
   title: "Car Won't Start but Clicks? 6 Causes and What to Do"   # under 65 characters, main phrase near the front
   slug: car-wont-start-clicking-noise
   description: "..."   # 140–155 characters, answers the question, mentions San Diego
   date: 2026-11-07
   keyword: car won't start clicking noise
   faq:
     - q: "..."
       a: "..."
   ---
   ```

   Body rules:
   - 900–1,400 words. First paragraph answers the question directly in 2–3 sentences (AI answers quote this).
   - `##` headings phrased as the questions people search. Short paragraphs, lists and one table where it helps.
   - Genuinely useful: specific checks the reader can do, what each cause sounds or looks like, what's urgent vs can wait, honest about when a job needs a shop with a lift.
   - One San Diego angle where it's true and relevant (inland heat on batteries and cooling, coastal salt air, I-15/I-805 commuting, hills, smog rules). Don't force it.
   - A "When to call a mechanic" section that mentions Pinoy comes to your home or work lot and quotes before work. One or two mentions, not salesy.
   - Link to 1–2 earlier articles where relevant (`/blog/<slug>/`) and to the homepage (`/`).
   - 3–4 FAQ items in front matter, each answered in 1–3 sentences, not repeating the body word for word.
   - Plain English, no filler, no "In today's fast-paced world". Safety first: tell readers to stop driving when it's unsafe.
   - Written to be quoted by AI search (ChatGPT, Gemini, Perplexity, Google AI Overviews): each `##` section opens with a one- or two-sentence answer that makes sense on its own, then the detail. Use specific nouns ("a weak 12-volt battery") rather than "it" or "this". Name San Diego places in full. Prefer a short list or table for symptoms, causes and steps.
   - The build adds the "About Pinoy Mobile Mechanic" box, structured data, sitemap, robots.txt and llms.txt automatically; don't add them by hand.
5. Change that queue line from `[ ]` to `[x]`.
6. `python3 scripts/build_blog.py` — it must print the article count with no errors.
7. `git add -A && git commit -m "Add article: <title>" && git push origin main`.
8. If the queue is empty, add 20 new topics in the same format (real search phrases for car repair in San Diego, no duplicates), then continue.

Only tell the user when something needs a decision (a push fails twice, the build breaks and can't be fixed, the queue topics run out of good ideas).
