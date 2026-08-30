# Aaron Delay Counseling · Brand & Playbooks

Warm, faith-friendly counseling resources for individuals, couples, and parents.
Editorial, grounded, and gender-neutral, built on one consistent brand system.

Start at [`index.html`](index.html) — it links to everything below.

## What's here

```
index.html              Hub page linking to every resource
brand-kit/              The brand field guide
playbooks/              The finished playbooks (HTML source + print-ready PDF)
coaching-instagram/     "Land the Plane" coaching deck
_archive/               Superseded versions, kept for reference only
```

### `brand-kit/`
An interactive **Brand Field Guide**: the visual and verbal identity system used
across every playbook. Open [`brand-kit/index.html`](brand-kit/index.html) in a browser.

- **Palette.** Ink `#262019` · Cream `#F7F2EA` · Sand `#E7DECF` · Clay `#B4694E`
- **Type.** *Fraunces* (display serif) and *Montserrat* (text), both free on Google Fonts
- Click any swatch to copy its hex, toggle light/dark, and preview the wordmark live

### `playbooks/01-you-didnt-marry-the-wrong-person/`
The first playbook, **"You Didn't Marry the Wrong Person,"** a 19-page marriage guide.

- **[You-Didnt-Marry-the-Wrong-Person.pdf](playbooks/01-you-didnt-marry-the-wrong-person/You-Didnt-Marry-the-Wrong-Person.pdf)** is the finished, print-ready guide (US Letter)
- `playbook.html` is the editable source
- `playbook.fonts.css` holds Fraunces and Montserrat, embedded so it renders identically anywhere

### `playbooks/02-five-minute-argument-reset/`
**"The 5-Minute Marriage Argument Reset,"** a 3-page practical tool, rebuilt on the
brand system from the earlier off-brand version.

- **[The-5-Minute-Marriage-Argument-Reset.pdf](playbooks/02-five-minute-argument-reset/The-5-Minute-Marriage-Argument-Reset.pdf)** is the finished, print-ready tool (US Letter)
- `playbook.html` is the editable source; same structure and font file as playbook 01
- Page 3 is a worksheet, so it is designed to be printed and written on
- The booking link is a placeholder. Drop the real URL into the `.js-booking` span,
  or preview one without editing via `playbook.html?book=https://…`

### `coaching-instagram/`
**"Land the Plane,"** the Instagram coaching deck (session 01, presented by Ben Forehand):
the method, roles, and recording-day plan for turning one hour of podcast conversation
into ten clips worth reposting. Open [`coaching-instagram/index.html`](coaching-instagram/index.html)
and use the arrow keys. It is marked `noindex`, so it is for sharing directly, not for search.

### `_archive/`
Superseded files, kept only so nothing is lost. Nothing here is current.

- `The-5-Minute-Marriage-Argument-Reset-v1-offbrand.pdf` — the original ReportLab-generated
  version of playbook 02, replaced by the on-brand rebuild

## Conventions

- **Each playbook folder is self-contained.** `playbook.fonts.css` is deliberately duplicated
  into every playbook so a folder can be zipped, moved, or hosted on its own and still
  render and print correctly. Don't factor it out into a shared file.
- **Finished PDFs live beside their source**, named for the title rather than the folder.

## Rendering a playbook to PDF

The source is a self-contained HTML file. To regenerate the PDF with headless Chrome,
run this from inside the playbook's folder:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="You-Didnt-Marry-the-Wrong-Person.pdf" \
  --virtual-time-budget=8000 "playbook.html"
```

---

*Fonts: [Fraunces](https://fonts.google.com/specimen/Fraunces) and [Montserrat](https://fonts.google.com/specimen/Montserrat), both under the SIL Open Font License.*
