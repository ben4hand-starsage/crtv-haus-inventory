#!/usr/bin/env python3
"""
Pull Cloudflare Web Analytics into a static JSON snapshot for the dashboard.

Why a snapshot rather than a live fetch from the page: the site is a public
GitHub Pages repo, so anything the page can read, anyone can read. A Cloudflare
API token in that JavaScript would hand out account access. The token stays here
in .env and never ships; the dashboard reads the JSON this writes.

Usage:
    python3 tools/fetch_cloudflare_analytics.py            # 30 days
    python3 tools/fetch_cloudflare_analytics.py --days 7
    python3 tools/fetch_cloudflare_analytics.py --probe    # check credentials only
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(ROOT, ".env")
# The snapshot is generated, not authored, so it lives only in the deploy repo
# - the same file the Actions workflow writes. Keeping a copy in DELAY/site
# would be a second source of truth that sync_site.sh deliberately excludes.
OUT = "/Users/benjaminforehand/Desktop/aarondelaycounseling-site/siteanalytics/data.json"

ACCOUNT_TAG = "9452bc58f548c7b6593d7fd4945f2971"
SITE_TAG = "99a9f55959984d91b395f573fabb3fe6"
# NOT the beacon token. Web Analytics issues a separate site tag; the beacon
# token in the page HTML is a different value and returns zero rows here.
# Recover it by grouping rumPageloadEventsAdaptiveGroups on dimension siteTag
# with no siteTag filter.
ENDPOINT = "https://api.cloudflare.com/client/v4/graphql"

# Paths we care about naming nicely in the UI.
PAGE_LABELS = {
    "/": "Home",
    "/reset/": "Free reset (opt-in)",
    "/thanks/": "Reset delivered",
    "/counseling/": "Counseling & coaching",
    "/playbooks/": "Playbooks ($19)",
    "/speaking/": "For churches",
    "/book/": "The book",
    "/coaching-thanks/": "Coaching enquiry sent",
    "/speaking-thanks/": "Speaking enquiry sent",
}


def read_env(key):
    """Read a secret from the environment, else parse .env.

    CI sets it as an env var; locally it lives in .env. Never source the file -
    a malformed line would execute as a shell command.
    """
    if os.environ.get(key):
        return os.environ[key].strip()
    if not os.path.exists(ENV):
        return None
    pat = re.compile(r"^\s*" + re.escape(key) + r"\s*=\s*(.*)$")
    with open(ENV) as fh:
        for line in fh:
            m = pat.match(line)
            if m:
                return m.group(1).strip().strip('"').strip("'")
    return None


def gql(token, query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            payload = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        sys.exit(f"HTTP {e.code} from Cloudflare.\n{detail}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach Cloudflare: {e.reason}")

    if payload.get("errors"):
        msgs = "\n".join("  - " + str(e.get("message")) for e in payload["errors"])
        sys.exit(f"Cloudflare returned errors:\n{msgs}")
    return payload["data"]


# One request, several aliased groupings.
QUERY = """
query Dash($account: String!, $site: String!, $start: Time!, $end: Time!,
           $prevStart: Time!, $prevEnd: Time!) {
  viewer {
    accounts(filter: {accountTag: $account}) {

      totals: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 1
      ) { count sum { visits } }

      previous: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $prevStart, datetime_leq: $prevEnd}
        limit: 1
      ) { count sum { visits } }

      byDate: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 400
        orderBy: [date_ASC]
      ) { count sum { visits } dimensions { date } }

      pages: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 100
        orderBy: [count_DESC]
      ) { count sum { visits } dimensions { requestPath } }

      referers: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 100
        orderBy: [count_DESC]
      ) { count sum { visits } dimensions { refererHost } }

      countries: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 100
        orderBy: [count_DESC]
      ) { count sum { visits } dimensions { countryName } }

      devices: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 20
        orderBy: [count_DESC]
      ) { count sum { visits } dimensions { deviceType } }

      browsers: rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 20
        orderBy: [count_DESC]
      ) { count sum { visits } dimensions { userAgentBrowser } }
    }
  }
}
"""

PROBE = """
query Probe($account: String!, $site: String!, $start: Time!, $end: Time!) {
  viewer {
    accounts(filter: {accountTag: $account}) {
      rumPageloadEventsAdaptiveGroups(
        filter: {siteTag: $site, datetime_geq: $start, datetime_leq: $end}
        limit: 1
      ) { count sum { visits } }
    }
  }
}
"""


def rows(acct, key):
    return acct.get(key) or []


def one(acct, key):
    r = rows(acct, key)
    if not r:
        return {"pageviews": 0, "visits": 0}
    return {"pageviews": r[0].get("count", 0),
            "visits": (r[0].get("sum") or {}).get("visits", 0)}


def group(acct, key, dim, label=None, drop_empty=True):
    out = []
    for r in rows(acct, key):
        name = (r.get("dimensions") or {}).get(dim) or ""
        if drop_empty and not name:
            name = "(direct)" if dim == "refererHost" else "(unknown)"
        out.append({
            "name": name,
            "label": (label or {}).get(name, name),
            "pageviews": r.get("count", 0),
            "visits": (r.get("sum") or {}).get("visits", 0),
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()

    token = read_env("CLOUDFLARE_API_TOKEN")
    if not token and os.environ.get("CI"):
        sys.exit(
            "No CLOUDFLARE_API_TOKEN in the environment.\n"
            "Add it under Settings > Secrets and variables > Actions."
        )
    if not token:
        sys.exit(
            "No CLOUDFLARE_API_TOKEN in .env.\n\n"
            "Create one at dash.cloudflare.com > My Profile > API Tokens:\n"
            "  Create Token > Custom token\n"
            "  Permission:  Account | Account Analytics | Read\n"
            "  Account:     Ben4hand@gmail.com's Account\n\n"
            "Then save it without it touching the terminal:\n"
            "  python3 tools/token_capture.py CLOUDFLARE_API_TOKEN"
        )

    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    start = now - dt.timedelta(days=a.days)
    variables = {
        "account": ACCOUNT_TAG,
        "site": SITE_TAG,
        "start": start.isoformat().replace("+00:00", "Z"),
        "end": now.isoformat().replace("+00:00", "Z"),
        "prevStart": (start - dt.timedelta(days=a.days)).isoformat().replace("+00:00", "Z"),
        "prevEnd": start.isoformat().replace("+00:00", "Z"),
    }

    if a.probe:
        d = gql(token, PROBE, {k: variables[k] for k in ("account", "site", "start", "end")})
        accts = d["viewer"]["accounts"]
        if not accts:
            sys.exit("Token works, but no account matched that accountTag.")
        r = accts[0]["rumPageloadEventsAdaptiveGroups"]
        n = r[0]["count"] if r else 0
        print(f"  credentials OK - {n} page views in the last {a.days} days")
        return

    data = gql(token, QUERY, variables)
    accts = data["viewer"]["accounts"]
    if not accts:
        sys.exit("No account matched that accountTag - check ACCOUNT_TAG.")
    acct = accts[0]

    pages = group(acct, "pages", "requestPath", PAGE_LABELS)
    by_path = {p["name"]: p for p in pages}

    reset_v = by_path.get("/reset/", {}).get("pageviews", 0)
    thanks_v = by_path.get("/thanks/", {}).get("pageviews", 0)

    snapshot = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_days": a.days,
        "site": "aarondelaycounseling.com",
        "totals": one(acct, "totals"),
        "previous": one(acct, "previous"),
        "by_date": [
            {"date": (r.get("dimensions") or {}).get("date"),
             "pageviews": r.get("count", 0),
             "visits": (r.get("sum") or {}).get("visits", 0)}
            for r in rows(acct, "byDate")
        ],
        "pages": pages,
        "referrers": group(acct, "referers", "refererHost"),
        "countries": group(acct, "countries", "countryName"),
        "devices": group(acct, "devices", "deviceType"),
        "browsers": group(acct, "browsers", "userAgentBrowser"),
        # The one number that says whether the funnel works: of the people who
        # saw the opt-in page, how many reached the page you only reach by
        # submitting it.
        "funnel": {
            "reset_views": reset_v,
            "thanks_views": thanks_v,
            "rate": round(thanks_v / reset_v, 4) if reset_v else None,
        },
    }

    t = snapshot["totals"]
    summary = (f"{a.days}d: {t['pageviews']} page views, {t['visits']} visits, "
               f"{len(snapshot['by_date'])} days with data")

    # generated_at moves on every run, so a naive write makes the file differ
    # even when nothing happened - which would commit and rebuild the site daily
    # forever. Compare everything except the timestamp and leave the file alone
    # when the numbers have not moved.
    if os.path.exists(a.out):
        try:
            with open(a.out) as fh:
                previous = json.load(fh)
            a_cmp = {k: v for k, v in snapshot.items() if k != "generated_at"}
            b_cmp = {k: v for k, v in previous.items() if k != "generated_at"}
            if a_cmp == b_cmp:
                print(f"  unchanged - left {a.out} alone")
                print(f"  {summary}")
                return
        except (ValueError, OSError):
            pass  # unreadable or corrupt: fall through and rewrite it

    d = os.path.dirname(a.out)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(snapshot, fh, indent=2)

    print(f"  wrote {a.out}")
    print(f"  {summary}")


if __name__ == "__main__":
    main()
