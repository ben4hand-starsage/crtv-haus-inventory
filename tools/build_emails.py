#!/usr/bin/env python3
"""
Build the Aaron Delay welcome-sequence emails as paste-ready HTML.

Source of truth for the copy is DELAY/launch-kit/01-welcome-sequence.md.
This script holds the same copy marked up for email, plus the brand shell,
and writes one file per email into DELAY/emails/ along with a preview page.

Run:  python3 tools/build_emails.py

Email-client constraints this file deliberately respects:
  - Every style is inline. Gmail strips <style> blocks in forwarded mail.
  - No web fonts. Gmail and Outlook drop @font-face, so Fraunces and
    Montserrat are declared with Georgia and Helvetica as the real faces.
  - Tables for the button. Padding on an <a> collapses in Outlook.
  - No background images, no external assets, nothing to block.
  - 600px, single column, which every client handles.
"""

import os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "DELAY", "emails")

# ── brand tokens ────────────────────────────────────────────────────────────
CREAM   = "#F7F2EA"
INK     = "#262019"
BODY    = "#3D352C"
STONE   = "#8A7C6C"
SAND    = "#E7DECF"
CLAY    = "#B4694E"
CLAYDK  = "#9A5238"

SERIF = "Georgia,'Times New Roman',serif"          # stands in for Fraunces
SANS  = ("-apple-system,BlinkMacSystemFont,'Segoe UI',"
         "Helvetica,Arial,sans-serif")             # stands in for Montserrat

P    = f"margin:0 0 20px;font-family:{SANS};font-size:17px;line-height:1.7;color:{BODY};"
A    = f"color:{CLAYDK};text-decoration:underline;"
STRONG = f"color:{INK};font-weight:600;"

# Live destinations. The free reset is hosted on the site; the paid playbook
# is the Gumroad product. Both are checked with curl before shipping.
RESET_PDF_URL = ("https://aarondelaycounseling.com/downloads/"
                 "The-5-Minute-Marriage-Argument-Reset.pdf")
GUMROAD_URL   = "https://shop.aarondelaycounseling.com/l/wrong-person"


def p(text):
    return f'<p style="{P}">{text}</p>'


def link(text, href="LINK"):
    return f'<a href="{href}" style="{A}"><strong style="{STRONG}">{text}</strong></a>'


def button(label, href="LINK"):
    """Table-based so Outlook keeps the padding."""
    return (
        '<table role="presentation" cellpadding="0" cellspacing="0" border="0" '
        'style="margin:4px 0 24px;"><tr><td '
        f'style="background:{CLAY};border-radius:4px;">'
        f'<a href="{href}" style="display:inline-block;padding:15px 30px;'
        f'font-family:{SANS};font-size:14px;font-weight:600;letter-spacing:.06em;'
        f'text-transform:uppercase;color:{CREAM};text-decoration:none;">'
        f'{label}</a></td></tr></table>'
    )


def rule():
    return (f'<div style="height:1px;line-height:1px;font-size:0;'
            f'background:{SAND};margin:34px 0 26px;">&nbsp;</div>')


def signoff():
    return (f'<p style="margin:28px 0 0;font-family:{SERIF};font-size:20px;'
            f'color:{INK};">Aaron</p>')


# ── the shell ───────────────────────────────────────────────────────────────
def shell(subject, preheader, body):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<title>{html.escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:{CREAM};">

<!-- preview text. Leave MailerLite's preview-text field blank if you keep this. -->
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">
{html.escape(preheader)}
&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;
</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:{CREAM};">
<tr><td align="center" style="padding:36px 20px 56px;">

<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;">
<tr><td style="padding:0 4px;">

<p style="margin:0 0 30px;font-family:{SANS};font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:{STONE};font-weight:600;">
Aaron&nbsp;Delay <span style="color:{CLAY};">&middot;</span> LPC-MHSP
</p>

{body}

{rule()}

<p style="margin:0 0 14px;font-family:{SANS};font-size:13px;line-height:1.6;color:{STONE};">
<strong style="color:{BODY};font-weight:600;">Aaron Delay, LPC-MHSP</strong><br>
Licensed professional counselor and credentialed minister
</p>

<p style="margin:0 0 14px;font-family:{SANS};font-size:11.5px;line-height:1.6;color:{STONE};">
These emails are educational and are not psychotherapy, diagnosis, or treatment, and reading them
does not create a therapist&#8211;client relationship. If you are in crisis or need clinical care,
please contact a licensed provider in your state or call or text 988.
</p>

<!-- MailerLite requires an unsubscribe link in the HTML itself. -->
<p style="margin:0;font-family:{SANS};font-size:11.5px;line-height:1.6;color:{STONE};">
Don't want these? <a href="{{$unsubscribe}}" style="color:{STONE};text-decoration:underline;">Unsubscribe</a>,
no hard feelings.
</p>

</td></tr>
</table>
<!--[if mso]></td></tr></table><![endif]-->

</td></tr>
</table>
</body>
</html>
"""


# MailerLite personalization. Syntax is {$field|default('value')} and is
# case-sensitive. The exact tag for any field is in Subscribers > Fields > Tag.
NAME = "{$name|default('there')}"
GREET = p(f'Hi {NAME},')

# ── the five emails ─────────────────────────────────────────────────────────
EMAILS = [
 dict(
  slug="01-heres-your-reset",
  day="Day 0",
  subject="Here's your reset",
  preheader="And one thing to do with it tonight.",
  body=GREET
   + p("Here it is: " + link("The 5-Minute Marriage Argument Reset &rarr;", RESET_PDF_URL))
   + p("Three pages. Read it now if you have five minutes, or print it and stick it somewhere "
       "you'll see it when you need it, which, if you're anything like the couples I sit with, "
       "will be sooner than you'd like.")
   + p("One thing to do tonight, before anything gets heated: read page two out loud to each "
       "other. Not as a negotiation. Just so the words are already in the room before you need them.")
   + p("And plenty of people who use this aren't in the middle of anything. They just want "
       "communication around difficult topics to be a little easier, and they'd rather have the "
       "words ready than go looking for them mid-argument. That's most of what this is for.")
   + p("Then hit reply and tell me the fight you keep having, or the conversation you keep putting "
       "off. Not the big dramatic one. The small one that keeps coming back wearing different "
       "clothes. I read every reply, and they decide what I write next.")
   + signoff(),
 ),
 dict(
  slug="02-why-a-counselor-wrote-this",
  day="Day 1",
  subject="Why a counselor wrote this",
  preheader="Ten thousand sessions a year, and the same thing kept showing up.",
  body=GREET
   + p("Quick context, so you know whose advice you're holding.")
   + p("I'm a licensed professional counselor and mental health service provider in Tennessee, and "
       "a credentialed minister. I founded a counseling practice that now runs somewhere around ten "
       "thousand sessions a year. A lot of those hours have been spent with married couples.")
   + p("Here's what changed how I work.")
   + p("Early on I assumed marriages ended because of the big things. An affair. An addiction. Some "
       "single catastrophic betrayal you could point at.")
   + p("That's not what I found. Most of the marriages that came apart in front of me didn't have "
       "one big thing. They had a hundred small ones nobody named. A comment let go. A conversation "
       "avoided because it was late and everyone was tired. A pattern that got a little more worn "
       "every month for six years, until one day two people who genuinely loved each other couldn't "
       "figure out how to be in a kitchen together.")
   + p("That's the good news, oddly. Nobody knows how to undo an affair in five minutes. But a "
       f'pattern? A pattern you can interrupt. That\'s most of what I do now, and it\'s what '
       "everything I send you is about.")
   + signoff(),
 ),
 dict(
  slug="03-the-mistake-in-conflict",
  day="Day 3",
  subject="The mistake almost every couple makes in conflict",
  preheader="It happens in the first ninety seconds, before the actual argument starts.",
  body=GREET
   + p("Most arguments are lost before they begin.")
   + p("Not because of what the fight is about, whether that's money, in-laws, the dishes, or the "
       "thing that happened at your sister's, but because of what happens in the first ninety seconds.")
   + p("Here's the pattern. One person raises something. They're nervous, so it comes out sharper "
       "than they meant. The other person hears the sharpness, not the content, and their body "
       "responds before their brain does: heart rate up, jaw tight, and now they're not listening, "
       "they're preparing.")
   + p("From that point on you're both defending. Nobody is describing anything. And the actual "
       "problem, the real one, the one that could have been solved in four minutes, never gets said "
       "out loud at all.")
   + p("The mistake is thinking the fix is <em>staying calm</em>. It isn't. Nobody stays calm on "
       "command, and telling a flooded person to relax reliably makes it worse.")
   + p(f'The fix is much smaller: <strong style="{STRONG}">name the state, not the story.</strong>')
   + p("&ldquo;I'm getting heated and I don't want to be&rdquo; is a sentence about you. It's almost "
       "impossible to argue with, and it doesn't require your spouse to agree about anything. It buys "
       "you the twenty seconds where someone's nervous system can come back down.")
   + p("That's it. That's the whole move. It's page two of the reset, and if you take nothing else "
       "from anything I ever send you, take that one.")
   + p("Try it once this week. It'll feel deeply unnatural the first time.")
   + signoff(),
 ),
 dict(
  slug="04-the-couple-who-almost-quit",
  day="Day 5",
  subject="The couple who almost quit",
  preheader="They'd already picked which weekends the kids would be where.",
  body=GREET
   + p("A story. The details are changed and blended across several couples, so nothing here "
       "identifies anybody, but the shape of it is one I've watched more times than I can count.")
   + p("They came in having already decided. Not officially. But they'd had the conversation about "
       "which weekends the kids would be where, and once a couple has had that conversation out "
       "loud, they're usually just looking for someone to confirm it.")
   + p("Sixteen years. No affair. No addiction. Nothing you could put on a form. They described "
       "their marriage as having &ldquo;just run out,&rdquo; which is the phrase I hear most and "
       "trust least.")
   + p("So I asked them to walk me through their last fight. Not the topic. The mechanics. Who said "
       "what, in what order, and where each of them was standing.")
   + p("It took about eleven minutes to find it. She would raise something small. He would hear it "
       "as an indictment of him as a husband, because it usually had been at some point in the past. "
       "He'd go quiet, not cruel, just gone, and she'd read the quiet as contempt, so she'd escalate "
       "to get any reaction at all, and then he'd have proof that raising things led to fights, so "
       "he'd avoid the next one even harder.")
   + p("Sixteen years of two people being decent to each other inside a pattern that made them both "
       "awful.")
   + p("Neither of them was the problem. The loop was the problem. And a loop, unlike a person, will "
       "actually change when you interrupt it in the same place a few dozen times in a row.")
   + p("They're still married. It wasn't fast and it wasn't dramatic. It was mostly them learning to "
       "say one sentence differently, over and over, on ordinary evenings, until the sentence stopped "
       "being a performance and started being how they talked.")
   + p("That's what the work actually looks like.")
   + signoff(),
 ),
 dict(
  slug="05-the-full-playbook",
  day="Day 8",
  subject="The full playbook",
  preheader="The longer version of everything I've sent you this week. $19.",
  body=GREET
   + p("This is the only thing I'll ever sell you in this sequence, so let me be plain about what "
       "it is.")
   + p("The reset you downloaded solves one moment, the ninety seconds where a conversation turns. "
       "It's genuinely useful and it's genuinely free, and if that's all you ever take from me, "
       "that's fine.")
   + p(link("You Didn't Marry the Wrong Person", GUMROAD_URL) + " is the longer version. Nineteen pages on the "
       "patterns underneath the moments: the four shapes that account for most recurring fights, the "
       "exact sentences that move each one, a repair sequence for the morning after an argument went "
       "badly, and the small daily version that makes the big conversations rare.")
   + p("It's $19. It's a PDF, it's yours immediately, and it's built to be worked through by two "
       "people in one sitting rather than read alone and admired.")
   + button("Get the playbook &middot; $19", GUMROAD_URL)
   + p("The title is the sentence I say most often in my office, and the one people take longest to "
       "believe. Almost nobody married the wrong person. Most people just never got taught the "
       "handful of moves that make the right one workable on a Tuesday.")
   + p("If it's not for you, that's honestly fine. The weekly email keeps coming either way, free, "
       "one idea at a time.")
   + signoff()
   + f'<p style="margin:22px 0 0;font-family:{SANS};font-size:15px;line-height:1.6;color:{STONE};'
     f'font-style:italic;">If money is the reason you\'re hesitating, reply and say so. '
     f'I\'d rather you have it.</p>',
 ),
]


# ── the weekly ──────────────────────────────────────────────────────────────
# Same engine as the Reels: Tension, Truth, Tool. Around 200 words. The closing
# question is deliberate: replies are the strongest deliverability signal there
# is while the list is small.
WEEKLY = dict(
  slug="weekly-template",
  day="Weekly",
  subject="[THE LINE, six to ten words]",
  preheader="[One line. What they get if they read it. Never a summary.]",
  body=p(f'Hi {NAME},')
   + p('<span style="background:#F2E4D8;">[TENSION. Two or three sentences naming a situation they '
       'recognise from their own house. Concrete, not abstract. If they do not see themselves here, '
       'nothing below matters.]</span>')
   + p('<span style="background:#F2E4D8;">[TRUTH. Two or three sentences. The thing underneath the '
       'situation that they have felt but never had words for. This is the part only a counselor '
       'can write.]</span>')
   + p(f'<strong style="{STRONG}">[THE LINE. One sentence with teeth. The one they would screenshot '
       'or send to their spouse. Write this first, before anything else.]</strong>')
   + p('<span style="background:#F2E4D8;">[TOOL. What they actually do tonight. A script, a '
       'question, a boundary. Specific enough to act on without deciding anything.]</span>')
   + p('<span style="background:#F2E4D8;">[QUESTION. One short question, and ask them to hit reply. '
       'Change it weekly.]</span>')
   + signoff(),
)


def main():
    os.makedirs(OUT, exist_ok=True)
    built = []
    for e in EMAILS + [WEEKLY]:
        doc = shell(e["subject"], e["preheader"], e["body"])
        path = os.path.join(OUT, e["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc)
        built.append((e, doc))
        print("wrote", os.path.relpath(path, ROOT))

    # preview page: all five stacked in iframes, with subject lines above each
    cards = []
    for e, doc in built:
        cards.append(f"""
  <section style="margin:0 0 44px;">
    <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:baseline;margin-bottom:10px;">
      <span style="font:600 11px/1 {SANS};letter-spacing:.16em;text-transform:uppercase;color:{CLAYDK};">{e['day']}</span>
      <strong style="font:600 16px/1.3 {SANS};color:{INK};">{html.escape(e['subject'])}</strong>
    </div>
    <div style="font:400 13px/1.5 {SANS};color:{STONE};margin-bottom:12px;">
      Preview text: {html.escape(e['preheader'])}
    </div>
    <iframe srcdoc="{html.escape(doc, quote=True)}" title="{html.escape(e['subject'])}"
      style="width:100%;height:760px;border:1px solid {SAND};border-radius:4px;background:{CREAM};"></iframe>
  </section>""")

    preview = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Welcome sequence preview</title></head>
<body style="margin:0;background:#FDFBF6;padding:40px 20px 80px;">
<div style="max-width:680px;margin:0 auto;">
  <h1 style="font:400 30px/1.15 {SERIF};color:{INK};margin:0 0 8px;">Welcome sequence</h1>
  <p style="font:400 15px/1.6 {SANS};color:{BODY};margin:0 0 34px;max-width:60ch;">
    Five emails over eight days. Rendered exactly as they will arrive. Every link still says
    <code style="background:{SAND};padding:1px 5px;border-radius:2px;">LINK</code> and must be
    replaced before the sequence is switched on.
  </p>
  {''.join(cards)}
</div>
</body></html>
"""
    ppath = os.path.join(OUT, "preview.html")
    with open(ppath, "w", encoding="utf-8") as f:
        f.write(preview)
    print("wrote", os.path.relpath(ppath, ROOT))

    # guard: no em-dashes anywhere in the output
    bad = []
    for e, doc in built:
        if "—" in doc:
            bad.append(e["slug"])
    print("em-dash check:", "clean" if not bad else f"FOUND IN {bad}")


if __name__ == "__main__":
    main()
