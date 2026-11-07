# Pinoy Mobile Mechanic website

Static site for pinoymobilemechanic.com. Pushing to `main` publishes it. No approval step.

- `index.html` — homepage (booking link and phone in the CONFIG block at the bottom)
- `content/articles/*.md` — blog articles (front matter + Markdown). Source of truth.
- `content/keywords.md` — article queue
- `scripts/build_blog.py` — builds `blog/`, `links/` (all guides + social links), `sitemap.xml`, `robots.txt`, `llms.txt`, and the newest-guides list between the GUIDES markers in `index.html`. Never hand-edit those outputs. Social accounts live in `SOCIALS` in the script.
- Menu on every page: Why us (`/why-us/`), Guides (`/blog/`), Reviews (`/reviews/`), all built by the script.
- `content/reviews.yml` — real reviews only, copied word for word with their source. Never write, invent or paraphrase a review or testimonial. The daily article run does not touch this file.
- `content/review-widget.html` — embed code for the review widget (Google/Facebook/Yelp sync). Shown at the top of `/reviews/` when it holds code; empty means hidden. The daily article run does not touch it.

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

   Structure, in this exact order (see `content/articles/2026-11-07-car-wont-start-clicking-noise.md` as the model):
   1. **Opening answer** (2–3 sentences, no heading): what the problem means in plain words, how common it is, and that only a proper diagnosis finds the cause. AI answers quote this.
   2. **Disclaimer** as a `>` blockquote: "This article explains what the problem means. It is general information, not repair instructions. [One line on the specific risk, e.g. electrical, brakes, hot coolant.] Leave testing and repairs to a licensed mechanic."
   3. **Pain points, heavy on data** (4–5 `##` question sections). Make the reader feel how common, costly and disruptive the problem is, backed by real numbers:
      - How common it is (a "By the numbers" table of 4–6 sourced stats).
      - When and where it hits (timing, being stranded, commute roads); safety line if relevant.
      - Why San Diego makes it worse (heat, salt air, hills, commuting, smog rules), with sourced numbers.
      - Why the cause is hard to pin down and how guessing wastes money (several parts give the same symptom; wrong-part pattern; AAA trust data is fine).
      - What putting it off costs (a table: tow costs, time without a car, rideshares, the problem getting worse).
      Aim for at least 8 sourced numbers per article. Every number links to the page it came from, opened in this run. Never invent or round up a statistic; if you can't source it, leave it out. Describe symptoms as "what it can feel like", never as a self-diagnosis guide (no "if X then it's part Y" tables).
   4. **The dream** (`##`, e.g. "What if…"): short picture of life with the problem gone: car works, fixed at home or work, no tow, no waiting room, price known before work.
   5. **Solution, kept vague** (`##`): 2–3 sentences only. A mobile mechanic comes to the car, finds what's actually wrong, gives a written quote first, and often fixes it on the same visit. No steps, no list of what gets tested, no parts, no procedure.
   6. **Call to action** (`##`): Pinoy comes to your home or work lot within 50 miles of Mira Mesa, finds the cause, written quote, fixes it where it's parked, Mon–Sat 8–5. Bold line: "Book a visit online in about a minute, or call or text 858-933-7045". Link to `/` and `/why-us/`.

   NO DIY, ever. Never tell readers how to test, check, repair, replace, adjust, top up, jump-start, tighten, clean or bypass anything, in the body or the FAQ. No tool lists, part numbers, torque values or step-by-step procedures. Describe symptoms and causes, never how to fix them. The only things readers are told to do themselves: stop driving when it's unsafe, get to safety, and call a professional.

   Other body rules:
   - 1,200–1,600 words, almost all of it on the problem. Short paragraphs, `##` headings phrased as the questions people search, two tables.
   - One San Diego angle where it's true and relevant (inland heat on batteries and cooling, coastal salt air, I-15/I-805/SR-52 commuting, hills, smog rules). Don't force it.
   - Link to 1–2 earlier articles where relevant (`/blog/<slug>/`) and to the homepage (`/`).
   - 3–4 FAQ items in front matter about meaning, urgency, cost ranges or whether a tow is needed, each answered in 1–3 sentences, never with how-to steps.
   - Plain English, no filler, no "In today's fast-paced world". Safety first: tell readers to stop driving when it's unsafe.
   - Written to be quoted by AI search (ChatGPT, Gemini, Perplexity, Google AI Overviews): each `##` section opens with a one- or two-sentence answer that makes sense on its own, then the detail. Use specific nouns ("a weak 12-volt battery") rather than "it" or "this". Name San Diego places in full. Prefer short lists and tables for data.
   - The build adds the "About Pinoy Mobile Mechanic" box, structured data, sitemap, robots.txt and llms.txt automatically; don't add them by hand.
5. Change that queue line from `[ ]` to `[x]`.
6. `python3 scripts/build_blog.py` — it must print the article count with no errors.
7. `git add -A && git commit -m "Add article: <title>" && git push origin main`.
8. If the queue is empty, add 20 new topics in the same format (real search phrases for car repair in San Diego, no duplicates), then continue.

Only tell the user when something needs a decision (a push fails twice, the build breaks and can't be fixed, the queue topics run out of good ideas).
