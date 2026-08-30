#!/usr/bin/env python3
"""
Local, one-shot token capture.

Serves a small page on 127.0.0.1 only. Paste a secret, press Save, and it is
written straight to .env with the correct KEY= prefix, then the server stops.

The value never passes through the chat transcript, never gets echoed to a
terminal, and is never logged here.

Usage:
    python3 tools/token_capture.py [KEY_NAME] [PORT]

Defaults to MAILERLITE_API_TOKEN on port 8777.
"""

import http.server
import os
import re
import socketserver
import sys
import urllib.parse

KEY = sys.argv[1] if len(sys.argv) > 1 else "MAILERLITE_API_TOKEN"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8777

ENV_PATH = "/Users/benjaminforehand/Desktop/CLAUDE/.env"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Save %(key)s</title>
<style>
  :root{
    --bg:#F7F2EA; --surface:#FFFDFA; --ink:#241F1A; --ink-2:#5B534A;
    --ink-3:#8A8076; --line:#E4DACB; --clay:#A65B3E; --ok:#3F7A55;
  }
  @media (prefers-color-scheme:dark){
    :root:not([data-theme=light]){
      --bg:#17140F; --surface:#211C16; --ink:#F2EBE1; --ink-2:#BCB2A5;
      --ink-3:#8A8076; --line:#332C23; --clay:#D08A66; --ok:#78B48F;
    }
  }
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:grid;place-items:center;
    background:var(--bg);color:var(--ink);
    font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
    padding:28px}
  .card{width:100%%;max-width:560px;background:var(--surface);
    border:1px solid var(--line);border-radius:10px;padding:34px 34px 30px}
  h1{margin:0 0 6px;font-size:1.32rem;letter-spacing:-.01em}
  .sub{margin:0 0 22px;color:var(--ink-2);font-size:.94rem}
  code{background:var(--bg);border:1px solid var(--line);border-radius:4px;
    padding:1px 6px;font-size:.86em}
  label{display:block;font-size:.74rem;font-weight:600;letter-spacing:.09em;
    text-transform:uppercase;color:var(--ink-3);margin-bottom:8px}
  textarea{width:100%%;min-height:120px;padding:13px 14px;border-radius:7px;
    border:1px solid var(--line);background:var(--bg);color:var(--ink);
    font:13px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;resize:vertical}
  textarea:focus{outline:2px solid var(--clay);outline-offset:1px;border-color:transparent}
  button{margin-top:16px;width:100%%;padding:13px;border:0;border-radius:7px;
    background:var(--clay);color:#fff;font-size:.82rem;font-weight:600;
    letter-spacing:.09em;text-transform:uppercase;cursor:pointer}
  button:hover{filter:brightness(1.07)}
  .note{margin-top:18px;font-size:.82rem;color:var(--ink-3);line-height:1.5}
  .ok{color:var(--ok);font-weight:600}
</style></head><body>
<div class="card">
  <h1>Save your %(key)s</h1>
  <p class="sub">Paste the token below. It is written straight to
    <code>.env</code> on this machine and never leaves it.</p>
  <form method="POST" action="/save">
    <label for="v">Token</label>
    <textarea id="v" name="value" autofocus spellcheck="false"
      placeholder="eyJ0eXAiOiJKV1Qi..."></textarea>
    <button type="submit">Save to .env</button>
  </form>
  <p class="note">Served on <strong>127.0.0.1</strong> only — nothing else on
    your network can reach this page. The server stops itself once saved.</p>
</div></body></html>
"""

DONE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Saved</title>
<style>
  :root{--bg:#F7F2EA;--surface:#FFFDFA;--ink:#241F1A;--ink-2:#5B534A;
    --line:#E4DACB;--ok:#3F7A55}
  @media (prefers-color-scheme:dark){:root:not([data-theme=light]){
    --bg:#17140F;--surface:#211C16;--ink:#F2EBE1;--ink-2:#BCB2A5;
    --line:#332C23;--ok:#78B48F}}
  body{margin:0;min-height:100vh;display:grid;place-items:center;
    background:var(--bg);color:var(--ink);padding:28px;
    font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
  .card{max-width:520px;background:var(--surface);border:1px solid var(--line);
    border-radius:10px;padding:34px;text-align:center}
  h1{margin:0 0 10px;font-size:1.3rem;color:var(--ok)}
  p{margin:0;color:var(--ink-2);font-size:.95rem}
</style></head><body>
<div class="card">
  <h1>Saved</h1>
  <p>%(detail)s<br><br>You can close this tab and tell Claude it's done.</p>
</div></body></html>
"""


def write_env(key, value):
    """Upsert KEY=value in .env, leaving every other line untouched."""
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as fh:
            lines = fh.read().split("\n")

    pat = re.compile(r"^\s*" + re.escape(key) + r"\s*=")
    replaced = False
    out = []
    for ln in lines:
        if pat.match(ln):
            out.append(f"{key}={value}")
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        if out and out[-1].strip() != "":
            out.append("")
        out.append(f"{key}={value}")

    with open(ENV_PATH, "w") as fh:
        fh.write("\n".join(out).rstrip("\n") + "\n")
    os.chmod(ENV_PATH, 0o600)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        """Silence the access log so the value can never reach stdout."""
        return

    def _send(self, html, code=200):
        body = html.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(PAGE % {"key": KEY})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n).decode()
        value = urllib.parse.parse_qs(raw).get("value", [""])[0].strip()

        if not value:
            self._send(PAGE % {"key": KEY}, 400)
            return

        write_env(KEY, value)
        detail = (
            f"{KEY} written to .env "
            f"({len(value)} characters, ending &hellip;{value[-4:]})."
        )
        self._send(DONE % {"detail": detail})
        print(f"{KEY} saved: {len(value)} chars, ends ...{value[-4:]}", flush=True)

        # One-shot: stop once we have it.
        import threading
        threading.Thread(target=self.server.shutdown, daemon=True).start()


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"open http://127.0.0.1:{PORT}", flush=True)
    httpd.serve_forever()
print("server stopped", flush=True)
