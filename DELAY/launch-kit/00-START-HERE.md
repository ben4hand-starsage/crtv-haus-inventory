# Days 1–14: the machine, standing

Everything in this folder is the "get the machine standing" block from section 10 of the strategy.
The site is built. The copy is written. What's left is account setup, which needs your logins.

---

## The order to do it in

**Today: start the clocks that aren't yours**

1. Send both notes in `04-compliance-outreach.md`. They gate nothing on the free side, but they gate
   the coaching offer entirely, and advisors answer on their own schedule.

**This week: the site goes live**

2. Unzip the site folder and push it to GitHub. Steps are in the site's own `README.md`.
3. Set the five DNS records at GoDaddy. Records are in the README. **Do not use domain forwarding.** It breaks SSL and search indexing both.
4. Turn on GitHub Pages with the custom domain, tick Enforce HTTPS.

At this point aarondelaycounseling.com is live with the forms showing a polite "not connected yet"
message. That's fine. You can push before the accounts exist.

**This week: the accounts**

5. **Kit.** Create the form, create the `source` custom field, load the welcome sequence from
   `01-welcome-sequence.md`, set the incentive email to deliver the Reset PDF, set the redirect to
   `/thanks/`. Paste the form action URL into `assets/js/site.js`.
6. **Gumroad.** Create the product from `02-gumroad-listing.md`, upload the 19-page PDF, paste the
   product URL into `assets/js/site.js`.
7. **ManyChat.** Build the flow from `03-manychat-flow.md` and test it end to end from a second
   account. Step 6 of that test is the one that matters.

**Then**

8. Commit the updated `site.js`, push, and run the whole funnel yourself once: comment the keyword →
   DM arrives → land on `/reset/` → submit → PDF arrives → subscriber appears in Kit tagged
   `reset-landing` → day-8 email offers the playbook → buy it → receipt arrives.

Nothing in days 15–45 should start until that round trip works.

---

## What's in this folder

| File | What it is |
|---|---|
| `01-welcome-sequence.md` | The five welcome emails, written and ready to paste into Kit |
| `02-gumroad-listing.md` | Product name, price, description, receipt message, settings checklist |
| `03-manychat-flow.md` | The comment-to-DM trigger, DM copy, follow-up, and the test script |
| `04-compliance-outreach.md` | Two notes to send today, and the one hard rule until they come back |
| `../site/` | The website. Its own README has GitHub + DNS instructions. |

---

## Two decisions I made that you should sanity-check

**No `/cohort` page.** Section 03 argues against advertising an offer that can't be filled, and I let
that win over section 06's page list. An empty "coming soon" page that sits unchanged for eight months
tells every visitor nothing here is happening. It ships the week you decide to sell it.

**The site says the marriage nights are free, and says why.** The `/speaking` page states plainly that
Aaron would rather have the room than the fee because he's building an audience for a book. Pastors
are asked for favours constantly and are good at spotting an unstated trade; naming it is disarming
rather than costly.

---

## Still open, from section 12

These affect what gets built next, not what's here:

- Which two Reels hit three thousand views, and what they had in common. That's the most actionable data in the account and it should shape the content pillars.
- Whether Aaron will actually run live group calls, since the whole high-ticket rung rests on it.
- Any price points he's already said out loud, so nothing here argues with a number he's committed to.
- How many of the 72 followers are current clients, which affects what he can safely post.
- Whether there's a budget. ManyChat and a scheduler run about $50/month past the free tiers.
