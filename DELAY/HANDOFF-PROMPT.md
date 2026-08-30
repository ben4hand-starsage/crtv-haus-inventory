# Handoff prompt

Paste everything below the line into a fresh Claude desktop session with the `CLAUDE` folder
connected.

---

I'm picking up a project mid-stream. Everything you need is in the connected folder at `CLAUDE/DELAY/`. Read `DELAY/launch-kit/00-START-HERE.md` and `DELAY/site/README.md` first — they're the source of truth. Don't rebuild anything that's already there.

## Context

I'm Ben. I'm doing platform and revenue strategy for **Aaron Delay, LPC-MHSP** — a licensed professional counselor and mental health service provider in Tennessee, credentialed minister, founder of a counseling practice running ~10,000 sessions a year. He has a finished 45,000-word manuscript, *Saying "I Do" Everyday*, with a foreword by Gary Chapman, and no publisher and no launch date.

The strategy is **platform before publisher**. Starting point is 72 Instagram followers (maybe 30 real), 0 email subscribers, and two Reels at ~3,000 views each — meaning reach is already working but there's nothing capturing it. The whole plan exists to turn Instagram attention into an owned email list and a countable record of people paying for his ideas, over 12–18 months. Instagram's only job is producing email addresses.

The offer ladder: free 3-page "5-Minute Marriage Argument Reset" (built), a $19 19-page playbook "You Didn't Marry the Wrong Person" (built), a $149 course and a $2,400 cohort both parked until the audience exists. The fastest growth channel is his ministry network — ~40,000 people across churches where he counsels pastors and staff — via free marriage nights that capture 100–300 emails an evening.

## What's already been done (days 1–14 of the plan)

**The website** — `DELAY/site/`. Static HTML/CSS/JS, no build step, ready to push to GitHub Pages. Built on his existing brand kit: Fraunces + Montserrat, ink `#262019` / cream `#F7F2EA` / sand `#E7DECF` / clay `#B4694E`.

Pages: `/` (home, opt-in above the fold, approach, about with photo, resources, churches, book notify), `/reset/` (bare opt-in landing, no nav, no exits, `noindex` — all Instagram DM and church QR traffic lands here), `/playbooks/` ($19 product + FAQ + Gumroad checkout), `/speaking/` (for pastors), `/book/`, `/thanks/`, `404.html`. Plus `CNAME`, `.nojekyll`, `robots.txt`, `sitemap.xml`, and two photos in `assets/img/`.

All configuration is centralized in **`site/assets/js/site.js`** — five `REPLACE_ME` values (Kit form action, Gumroad URL, contact email, Instagram URL, thanks URL). Until they're set, forms and buy buttons show a clear "not connected yet" message instead of failing silently, so the site can go live before the accounts exist.

**The launch kit** — `DELAY/launch-kit/`:
- `01-welcome-sequence.md` — all five welcome emails (day 0/1/3/5/8), written in full, ready to paste into Kit
- `02-gumroad-listing.md` — product name, price, description, receipt message, settings checklist
- `03-manychat-flow.md` — the comment-to-DM trigger ("Comment RESET"), DM copy, follow-up, and an end-to-end test script
- `04-compliance-outreach.md` — two notes to send today, plus the hard rules

## Two decisions already made — don't reverse them without telling me why

1. **No `/cohort` page.** An empty "coming soon" page for an offer that can't be filled tells every visitor nothing is happening. It ships the week we decide to sell it.
2. **The `/speaking` page says the marriage nights are free *and says why*** — that Aaron would rather have the room than the fee because he's building an audience for a book. Pastors spot unstated trades; naming it reads as respect.

## Two compliance constraints — these are hard rules

1. **Do not import Aaron's ~3,500 client contacts into any email tool.** The fact of someone being his counseling client is protected health information; using that list for marketing generally requires written authorization. Clients must opt in by their own action through practice touchpoints. This isn't negotiable, and it isn't a thing to work around cleverly.
2. **The coaching offer must be visibly separate from the therapy practice** — separate brand and probably separate entity, a written agreement stating coaching is not psychotherapy, an intake screen that refers clinical need to care, and no current or former counseling client in the program.

The disclaimer wording currently in the site footers is a **strategy placeholder written by an AI, not approved language**. It needs a real attorney and the practice's HIPAA advisor to review and replace it. Flag that rather than treating it as settled.

## What I need next

1. **Push the site to GitHub Pages** and set the DNS at GoDaddy — four A records to `185.199.108-111.153` on the apex plus a `www` CNAME to `USERNAME.github.io`. **Real DNS records, never GoDaddy domain forwarding** — forwarding breaks SSL and search indexing. Full steps are in `site/README.md`. The domain `aarondelaycounseling.com` is already registered at GoDaddy.
2. **Set up Kit** — create the form, create a `source` custom field (values: `reset-landing`, `home-hero`, `home-book-notify`, `book-page` — this is what lets us tell church traffic from Instagram traffic later), load the welcome sequence, set the incentive email to deliver the Reset PDF, set the redirect to `/thanks/`.
3. **Set up Gumroad** from the listing file, upload the 19-page PDF.
4. **Build the ManyChat flow** and test it end to end from a second account.
5. Paste the resulting URLs into `site/assets/js/site.js` and push.

Nothing in days 15–45 starts until the full round trip works: comment the keyword → DM arrives → land on `/reset/` → submit → PDF arrives → subscriber appears in Kit tagged correctly → day-8 email offers the playbook → buy → receipt.

## Still open — ask me if it matters to what you're doing

- Aaron's Instagram handle, contact email, and my GitHub username (needed for the `www` CNAME)
- Which two Reels hit 3,000 views and what they had in common — the most actionable data in the account
- Whether Aaron will actually run live group calls, since the whole high-ticket rung rests on it
- Any price points he's already committed to out loud
- How many of the 72 followers are current clients
- Whether there's a budget — ManyChat and a scheduler run ~$50/month past the free tiers

## How to work with me

Ask before you rebuild something that already exists. Push back if a decision looks wrong. Keep the writing plain and unhurried — the brand voice is steady, plain-spoken, shame-free, and on the reader's side, and it should never sound like marketing copy.

Start by reading the folder and telling me what you found and what you'd do first.
