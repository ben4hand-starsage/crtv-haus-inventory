# aarondelaycounseling.com

Static site for Aaron Delay, LPC-MHSP. Plain HTML/CSS/JS, no build step, deployed on GitHub Pages.
Built on the Brand Field Guide v1.0 tokens (Fraunces + Montserrat, ink / cream / sand / clay).

---

## What's here

```
/                    Home — opt-in above the fold, approach, resources, churches, book
/reset/              Bare opt-in landing page. No nav, no exits, one form.
                     All Instagram DM traffic and church QR codes land here.
/thanks/             Post-opt-in confirmation. Asks for a reply (trains the inbox).
/playbooks/          The $19 playbook with Gumroad checkout + FAQ
/speaking/           For pastors: what a marriage night is, what the church provides, how to book
/book/               Saying "I Do" Everyday, with notify-me capture
/404.html            Soft landing for stale links
/assets/css/brand.css   All styling. One file.
/assets/js/site.js      All configuration. One file. See below.
CNAME                aarondelaycounseling.com
.nojekyll            Stops GitHub trying to run Jekyll over it
```

---

## Step 1 — Configure the three accounts

Everything that needs an account lives in **`assets/js/site.js`**. Open it, replace the remaining
`REPLACE_ME` values, commit. Nothing else in the site needs touching.

**Current state:** `INSTAGRAM_URL`, `CONTACT_EMAIL`, and `THANKS_URL` are set.
`KIT_FORM_ACTION` and `GUMROAD_PLAYBOOK_URL` are still placeholders, so the opt-in forms and the
buy button show a "not connected yet" message. The site is safe to deploy in this state.

| Value | Where to get it |
|---|---|
| `KIT_FORM_ACTION` | Kit → Grow → Landing Pages & Forms → your form → Embed → HTML. Copy the URL inside `action="..."`. Looks like `https://app.kit.com/forms/1234567/subscriptions` |
| `GUMROAD_PLAYBOOK_URL` | Gumroad → your product → Share → the product URL. Looks like `https://aarondelay.gumroad.com/l/playbook` |
| `CONTACT_EMAIL` | The address speaking enquiries should reach |
| `INSTAGRAM_URL` | Aaron's profile URL |
| `THANKS_URL` | Leave as `/thanks/` unless you build a different confirmation page |

Until they're set, forms and buy buttons show a clear "not connected yet" message instead of
failing silently. That's deliberate — you can push the site live before the accounts exist.

### Kit specifics

The forms post these fields, so create them in Kit before going live:

- `email_address` — standard
- `fields[first_name]` — standard
- `fields[source]` — **custom field, create it.** Values sent: `reset-landing`, `home-hero`,
  `home-book-notify`, `book-page`. This is what lets you tell church traffic from Instagram
  traffic later, which section 11 of the plan depends on.

In Kit, set the form's incentive email to deliver the Reset PDF, and set the form's redirect
to `https://aarondelaycounseling.com/thanks/`.

**Do not bulk-import the 3,500 client contacts.** See section 02 of the strategy document.

---

## Step 2 — Push to GitHub

```bash
cd site
git init
git add -A
git commit -m "Initial site"
git branch -M main
git remote add origin git@github.com:ben4hand-starsage/aarondelaycounseling-site.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from a branch → `main` / `root`**.

In the same panel, **Custom domain** → `aarondelaycounseling.com` → Save, then tick
**Enforce HTTPS** once the certificate provisions (up to an hour on first setup).

---

## Step 3 — DNS at GoDaddy

GoDaddy → Domain → Manage DNS. **Do not use domain forwarding** — it breaks SSL and search
indexing. Real DNS records only.

Delete any existing `A` record on `@` (GoDaddy parks one by default), then add:

| Type | Name | Value | TTL |
|---|---|---|---|
| A | @ | 185.199.108.153 | 1 hour |
| A | @ | 185.199.109.153 | 1 hour |
| A | @ | 185.199.110.153 | 1 hour |
| A | @ | 185.199.111.153 | 1 hour |
| CNAME | www | ben4hand-starsage.github.io | 1 hour |

Delete GoDaddy's default `CNAME www → @` if it's there, otherwise the new one won't save.

Propagation is usually minutes, occasionally an hour. Check with:

```bash
dig aarondelaycounseling.com +short
dig www.aarondelaycounseling.com +short
```

You want the four GitHub IPs back on the apex.

---

## Step 4 — ManyChat

The comment-to-DM trigger sends people to `https://aarondelaycounseling.com/reset/`.
Test it end to end on a real post before relying on it — comment the keyword from a second
account and confirm the DM arrives with a working link.

---

## Local preview

```bash
cd site
python3 -m http.server 8080
```

Then open `http://localhost:8080`. Pretty URLs (`/reset/`, `/playbooks/`) work because each is a
folder with an `index.html`.

---

## Notes on decisions made

- **No `/cohort` page.** Section 03 of the plan argues against a "coming soon" page for an offer
  that can't be filled yet, and that reasoning won over section 06's page list. It ships the week
  it's decided, not before.
- **`/reset` is `noindex`.** It's a paid-traffic-style landing page with no navigation; you don't
  want Google surfacing it instead of the home page. `/thanks/` is `noindex, nofollow`.
- **A compliance disclaimer sits in every footer** and on `/reset`, separating educational content
  from psychotherapy. This is placeholder wording written from a strategy perspective — section 02
  of the plan is right that it needs a real attorney and the practice's HIPAA advisor to approve
  the final text before launch.
- **`robots.txt` allows everything.** An earlier version disallowed `/reset/` and `/thanks/`, which
  cancelled out their `noindex` meta tags: a crawler blocked by robots.txt never fetches the page, so
  it never reads the `noindex`, and the URL can still be indexed bare if something links to it. The
  meta tags do the work now.
- **No logo file was provided**, so the wordmark is type-set per the brand guide: Fraunces 600 with
  a clay full stop. Drop a real logo in later without touching the layout.
