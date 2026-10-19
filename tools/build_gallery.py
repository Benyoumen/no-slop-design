#!/usr/bin/env python3
"""Build the no-slop-design gallery (site/) from the Acme Realty snapshot and the token file.

Standard library only. The HTML is never edited by hand: change this file or the data, run it again.

    python tools/build_gallery.py

Inputs:  examples/acme-realty/data-snapshot.json, templates/tokens.css
Outputs: site/index.html, six screen pages (three built with the rules, three generic twins),
         site/tokens.css, site/screens.css, site/gallery.css, site/og.svg

The three screens are an operator product a broker opens all day: a left navigation on the
canvas, a sheet with a top bar, and the work in white cards on the sheet. Every number shows
where it comes from. The assistant proposes; the broker approves; every write shows Undo.
"""
import datetime as dt
import html
import json
import os
import shutil
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "acme-realty", "data-snapshot.json")
TOKENS = os.path.join(ROOT, "templates", "tokens.css")
SITE = os.path.join(ROOT, "site")
BASE_URL = "https://benyoumen.github.io/no-slop-design/"
REPO_URL = "https://github.com/Benyoumen/no-slop-design"
FOOTER = "Fictional brokerage, people and numbers."
OLD_PAGES = [
    "daily-list.html", "daily-list-generic.html", "proposal-review.html",
    "proposal-review-generic.html", "weekly-summary.html", "weekly-summary-generic.html",
]

with open(DATA, encoding="utf-8") as fh:
    D = json.load(fh)

SNAPSHOT = dt.date.fromisoformat(D["snapshot_date"])
RUN = dt.datetime.fromisoformat(D["last_assistant_run"]).strftime("%H:%M")
BROKER = D["broker"]
BUYERS = {b["id"]: b for b in D["buyers"]}
LISTINGS = {l["id"]: l for l in D["listings"]}
SUGG = {s["id"]: s for s in D["suggestions"]}
SOURCES = {s["ref"]: s for s in D["sources"]}
EXPLORE = {q["id"]: q for q in D["explore"]}


# ---------------------------------------------------------------- helpers


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def nodata(text="no data"):
    return f'<span class="na">{e(text)}</span>'


def money(amount):
    if amount is None:
        return nodata()
    return f'<span class="num">${amount:,.0f}</span>'


def short_money(amount):
    if amount is None:
        return "no data"
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    return f"${amount / 1000:.0f}k"


def day(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%d %b").lstrip("0")


def days_since(iso):
    return (SNAPSHOT - dt.date.fromisoformat(iso)).days


def days_bucket(n):
    if n <= 2:
        return "0-2"
    if n <= 7:
        return "3-7"
    if n <= 13:
        return "8-13"
    return "14+"


def long_date(d):
    return d.strftime("%A, %d %B %Y").replace(" 0", " ")


def greeting():
    h = int(D["snapshot_time"].split(":")[0])
    return "Good morning" if h < 12 else ("Good afternoon" if h < 18 else "Good evening")


def stage_chip(stage):
    cls = {"lead": "ch-neu", "visit": "ch-info", "proposal": "ch-warn", "reservation": "ch-ok",
           "signed": "ch-ok", "owner": "ch-neu"}.get(stage, "ch-neu")
    return f'<span class="ch {cls}">{e(stage)}</span>'


# Icons: small stroke drawings on a 24 grid, hidden from screen readers, always next to a label.
ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
    "home": '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
    "list": '<path d="M4 6h16M4 12h16M4 18h10"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14.5a5 5 0 0 1 6 5"/>',
    "building": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M8 7h3M13 7h3M8 11h3M13 11h3M8 15h3M13 15h3M10 21v-3h4v3"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 13h6M9 17h6"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "check": '<path d="M5 12l5 5L20 7"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "arrow-up": '<path d="M12 19V5M5 12l7-7 7 7"/>',
    "chevron-right": '<path d="M9 6l6 6-6 6"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    "paperclip": '<path d="M21 11l-9 9a5.5 5.5 0 0 1-8-8l9-9a3.5 3.5 0 0 1 5 5l-9 9a1.5 1.5 0 0 1-2-2l8-8"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3M13 10l3 3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "map": '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
}


def ico(name, size=16):
    return (f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def logo(name):
    """A monogram square before every listing or developer name, hidden from screen readers."""
    letter = name.strip()[0].upper()
    tone = (sum(ord(c) for c in name) % 6) + 1
    return f'<span class="lg lg-{tone}" aria-hidden="true">{e(letter)}</span>'


# ---------------------------------------------------------------- document shell


def document(path, title, description, body, extra_css=(), script="", kind="screen", twin=None, label=None):
    """kind: 'screen' (built with the rules), 'generic' (the twin) or 'gallery'."""
    css = ['<link rel="stylesheet" href="tokens.css">'] + [f'<link rel="stylesheet" href="{c}">' for c in extra_css]
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">'
    )
    frame = ""
    if kind != "gallery":
        side = "Built with the rules" if kind == "screen" else "The generic version"
        other = "See the generic version" if kind == "screen" else "See it built with the rules"
        frame = (
            '<div class="frame" role="region" aria-label="Gallery frame">'
            '<a class="frame-home" href="index.html">No-slop design</a>'
            f'<span class="frame-label">{e(label or "")}: {side}</span>'
            f'<a class="frame-twin" href="{twin}">{other}</a>'
            f'<a class="frame-repo" href="{REPO_URL}">GitHub</a>'
            "</div>"
        )
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{BASE_URL}{path}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{BASE_URL}{path}">
<meta property="og:image" content="{BASE_URL}og.svg">
<meta name="twitter:card" content="summary_large_image">
{fonts}
{''.join(css)}
</head>
<body class="{kind}">
{frame}
{body}
<footer class="site-footer"><p>{FOOTER}</p><p><a href="index.html">Gallery</a> · <a href="{REPO_URL}">GitHub repository</a></p></footer>
{('<script>' + script + '</script>') if script else ''}
</body>
</html>
"""
    with open(os.path.join(SITE, path), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)


# ---------------------------------------------------------------- operator shell (sidebar, top bar, sheet)

NAV = [
    ("group", "Today"),
    ("item", "Home", "home", "home.html"),
    ("item", "Priorities", "list", "home.html#priorities"),
    ("item", "Tasks", "check", "home.html#tasks"),
    ("group", "Portfolio"),
    ("item", "Portfolio", "users", "portfolio-explore.html"),
    ("item", "Buyers", "key", None),
    ("item", "Listings", "building", None),
    ("item", "Visits", "calendar", None),
    ("item", "Proposals", "file", None),
    ("item", "Forecast", "chart", None),
]


def nav_html(active):
    out = []
    for row in NAV:
        if row[0] == "group":
            out.append(f'<div class="nav-g">{e(row[1])}</div>')
            continue
        _, label, icon, href = row
        on = " on" if label == active else ""
        if href:
            cur = ' aria-current="page"' if label == active else ""
            out.append(f'<a class="nav-i{on}" href="{href}"{cur}>{ico(icon)}<span class="lb">{e(label)}</span></a>')
        else:
            out.append(f'<span class="nav-i is-mock" title="Not in this mockup">{ico(icon)}<span class="lb">{e(label)}</span><span class="nav-n">mock</span></span>')
    return "".join(out)


def shell(active, main, ctx="", job_title="Portfolio read", job_state=f"done today at {RUN}"):
    return f"""
<div class="app">
  <aside class="side">
    <div class="side-top">
      <div class="ws"><span class="ws-mk" aria-hidden="true"></span><span class="ws-t"><b>{e(D["brokerage"])}</b><span class="who">{e(BROKER["name"])}</span></span></div>
      <form class="acct" role="search" aria-label="Find a person or a listing">
        <label class="sr" for="find">Find a person or a listing</label>
        <div class="acct-b">{ico("search", 14)}<input id="find" class="acct-in" type="search" placeholder="Find a person or a listing" autocomplete="off"><kbd aria-hidden="true">/</kbd></div>
      </form>
    </div>
    <nav class="nav" aria-label="Sections">
      {nav_html(active)}
      <div class="nav-foot">
        <span class="nav-i is-mock" title="Not in this mockup">{ico("file")}<span class="lb">Sources</span></span>
        <span class="nav-i is-mock" title="Not in this mockup">{ico("settings")}<span class="lb">Settings</span></span>
      </div>
    </nav>
  </aside>
  <div class="sheet">
    <header class="hd">
      <div class="hd-in">
        <div class="job" role="status" aria-live="polite" id="job">{ico("check", 14)}<span class="job-t">{e(job_title)}</span><span class="job-s">{e(job_state)}</span></div>
        <span class="grow"></span>
        <button type="button" class="b b-p" id="log-visit">{ico("calendar")}Log a visit</button>
        <div class="umenu" id="umenu">
          <button type="button" class="uav" id="umenubtn" aria-expanded="false" aria-controls="umenu-l" aria-label="Account of {e(BROKER["name"])}">{e(BROKER["initials"])}</button>
          <div class="pop" id="umenu-l" hidden>
            <div class="pop-id"><span class="uav" aria-hidden="true">{e(BROKER["initials"])}</span><span class="pop-idt"><span class="pop-nm">{e(BROKER["name"])}</span><span class="pop-org">{e(BROKER["role"])}</span></span></div>
            <button type="button" class="pi">Preferences<span class="sub">channel, daily summary, quiet hours</span></button>
            <button type="button" class="pi">Sources<span class="sub">where every number on this screen comes from</span></button>
          </div>
        </div>
      </div>
    </header>
    <main class="mn" id="main">
      {ctx}
      {main}
    </main>
  </div>
</div>
"""


SHELL_JS = r"""
(function(){
  var btn=document.getElementById('umenubtn'), pop=document.getElementById('umenu-l'), menu=document.getElementById('umenu');
  if(btn&&pop){
    function close(){pop.hidden=true;btn.setAttribute('aria-expanded','false');menu.classList.remove('open');}
    btn.addEventListener('click',function(){var open=pop.hidden;pop.hidden=!open;btn.setAttribute('aria-expanded',open?'true':'false');menu.classList.toggle('open',open);if(open){pop.querySelector('button').focus();}});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&!pop.hidden){close();btn.focus();}});
    document.addEventListener('click',function(ev){if(!menu.contains(ev.target))close();});
    pop.querySelectorAll('.pi').forEach(function(p){p.addEventListener('click',function(){close();receipt('Not in this mockup','Preferences and Sources are described in the brief.');btn.focus();});});
  }
  var lv=document.getElementById('log-visit'); if(lv){lv.addEventListener('click',function(){receipt('Not in this mockup','Logging a visit is a drawer in the next round.');});}
  var find=document.getElementById('find'); if(find){document.addEventListener('keydown',function(ev){if(ev.key==='/'&&document.activeElement!==find&&!/INPUT|TEXTAREA/.test(document.activeElement.tagName)){ev.preventDefault();find.focus();}});}
  var toastTimer=null;
  window.receipt=function(title,detail,undo){
    var t=document.getElementById('toast'); if(!t){t=document.createElement('div');t.id='toast';t.className='toast';t.setAttribute('role','status');t.setAttribute('aria-live','polite');document.body.appendChild(t);}
    t.innerHTML='<span class="tk" aria-hidden="true">&#10003;</span><span class="tx"><b></b><i></i></span>'+(undo?'<button type="button" class="tu">Undo</button>':'')+'<button type="button" class="tx-x" aria-label="Close">&times;</button>';
    t.querySelector('b').textContent=title; t.querySelector('i').textContent=detail||'';
    t.classList.add('on'); clearTimeout(toastTimer);
    var hide=function(){t.classList.remove('on');};
    t.querySelector('.tx-x').addEventListener('click',hide);
    if(undo){t.querySelector('.tu').addEventListener('click',function(){undo();hide();});}
    toastTimer=setTimeout(hide,undo?12000:5000);
  };
})();
"""


# ---------------------------------------------------------------- portfolio, explore view (built with the rules)


def suggestion_cell(b):
    s = SUGG.get(b["suggestion"] or "")
    if not s:
        if b["kind"] == "owner":
            return '<span class="na">nothing to propose</span>'
        if b["next_step"]:
            return f'<span class="t3">Next step set: {e(b["next_step"]["text"])}</span>'
        return '<span class="na">nothing to propose</span>'
    ev = s["evidence"][0]
    writes = "; ".join(f'{w["object"]}: {w["fields"]}' for w in s["writes"])
    bid = e(b["id"])
    return (
        f'<div class="prop" id="prop-{bid}">'
        f'<span class="ch ch-prop">Assistant proposes</span>'
        f'<p class="prop-t">{e(s["title"])}</p>'
        f'<p class="prop-ev">"{e(ev["quote"])}" <span class="src">{e(ev["source"])} [{ev["ref"]}]</span></p>'
        f'<p class="prop-w"><span class="t3">Writes:</span> {e(writes)}</p>'
        f'<div class="acts"><button type="button" class="b b-p b-sm" data-approve="{bid}" data-task="{e(s["writes"][0]["fields"])}">Create the task</button>'
        f'<button type="button" class="b b-t b-sm" data-later="{bid}">Not now</button>'
        f'<a class="b b-l b-sm" href="buyer-record.html">Open</a></div>'
        f'</div><div class="result" id="result-{bid}" hidden></div>'
    )


def person_row(b):
    listing = LISTINGS.get(b["interested_in"][0]) if b["interested_in"] else None
    looking = f'{e(b["looking_for"])}'
    if listing:
        looking += f'<span class="sub">{logo(listing["name"])}{e(listing["name"])} · {money(listing["price"])}</span>'
    n = days_since(b["last_contact"])
    last = f'<span class="num">{e(day(b["last_contact"]))}</span><span class="sub">{e(b["last_contact_kind"])} · {n} d ago</span>'
    if b["kind"] == "buyer" and n >= 14:
        last = f'<span class="ch ch-bad">{n} d without contact</span><span class="sub">{e(b["last_contact_kind"])}</span>'
    nxt = nodata("none set") if not b["next_step"] else (
        f'{e(b["next_step"]["text"])}<span class="sub">{e(day(b["next_step"]["date"])) if b["next_step"]["date"] else "no date"}</span>')
    budget = money(b["budget"]) if b["kind"] == "buyer" else nodata("owner")
    return (
        f'<tr id="row-{e(b["id"])}" data-stage="{e(b["stage"])}" data-district="{e(b["district"])}" data-days="{days_bucket(n)}" data-source="{e(b["source"])}" data-kind="{e(b["kind"])}">'
        f'<th scope="row"><a class="lkn" href="buyer-record.html">{e(b["name"])}</a><span class="sub">{e("owner, " + b["looking_for"] if b["kind"] == "owner" else b["source"] + " · since " + day(b["since"]))}</span></th>'
        f'<td>{stage_chip(b["stage"])}</td>'
        f'<td class="looking">{looking}</td>'
        f'<td class="num">{budget}</td>'
        f'<td>{last}</td>'
        f'<td>{nxt}</td>'
        f'<td class="col-prop">{suggestion_cell(b)}</td>'
        "</tr>"
    )


def explore_answer(q, hidden=True):
    qid = q["id"]
    findings = "".join(
        f'<li>{e(f["text"])} {" ".join(f"<a class=\"ref\" href=\"#src-{qid}-{r}\">[{r}]</a>" for r in f["refs"])}</li>'
        for f in q["findings"]
    )
    conf = ""
    if q.get("confidence"):
        conf = f'<p class="ex-conf"><span class="ch ch-warn">confidence {e(q["confidence"])}</span> <span class="t2">{e(q["confidence_reason"])}</span></p>'
    refs = sorted({r for f in q["findings"] for r in f["refs"]})
    srcs = "".join(f'<li id="src-{qid}-{r}">[{r}] {e(SOURCES[r]["name"])} · {e(SOURCES[r]["detail"])}</li>' for r in refs)
    acts = "".join(
        f'<button type="button" class="b {"b-p" if a["primary"] else "b-s"}" data-mockact="{e(a["label"])}">{e(a["label"])}</button>'
        for q_a in [q["actions"]] for a in q_a
    )
    return (
        f'<article class="ex-ans" id="ans-{e(q["id"])}" data-q="{e(q["question"])}"{" hidden" if hidden else ""}>'
        f'<p class="ex-q"><span class="t3">You asked</span> {e(q["question"])}</p>'
        f'<p class="ex-v">{e(q["verdict"])}</p>'
        f'<ol class="ex-f">{findings}</ol>'
        f'<p class="ex-o"><b>What is not settled:</b> {e(q["open"])}</p>'
        f'{conf}'
        f'<ul class="ex-src">{srcs}</ul>'
        f'<div class="acts">{acts}</div>'
        "</article>"
    )


def portfolio_explore():
    people = D["buyers"]
    buyers = [b for b in people if b["kind"] == "buyer"]
    no_contact = [b for b in buyers if days_since(b["last_contact"]) >= 14]
    open_props = [p for p in D["proposals"] if p["status"] not in ("signed 8 April",)]
    open_value = sum(p["amount"] for p in open_props)
    visits_today = sum(1 for a in D["agenda"] if a["kind"] == "visit")
    rows = "".join(person_row(b) for b in people)
    districts = sorted({b["district"] for b in people})
    stage_counts = {}
    for b in people:
        stage_counts[b["stage"]] = stage_counts.get(b["stage"], 0) + 1

    def chips(group, options, label):
        out = [f'<span class="fl">{e(label)}</span>', f'<button type="button" class="fchip on" data-f="{group}" data-v="all" aria-pressed="true">All<span class="n">{len(people)}</span></button>']
        for v, n in options:
            out.append(f'<button type="button" class="fchip" data-f="{group}" data-v="{e(v)}" aria-pressed="false">{e(v)}<span class="n">{n}</span></button>')
        return "".join(out)

    days_opts = [("0-2", sum(1 for b in people if days_bucket(days_since(b["last_contact"])) == "0-2")),
                 ("3-7", sum(1 for b in people if days_bucket(days_since(b["last_contact"])) == "3-7")),
                 ("8-13", sum(1 for b in people if days_bucket(days_since(b["last_contact"])) == "8-13")),
                 ("14+", sum(1 for b in people if days_bucket(days_since(b["last_contact"])) == "14+"))]
    source_opts = [(s, sum(1 for b in people if b["source"] == s)) for s in sorted({b["source"] for b in people})]
    answers = "".join(explore_answer(q) for q in D["explore"])
    main = f"""
<div class="ph"><div class="ph-t"><h1>Portfolio</h1><span class="ph-s">{e(long_date(SNAPSHOT))} · snapshot of {e(D["snapshot_time"])}</span></div></div>
<nav class="subnav" aria-label="Portfolio sections">
  <a class="sn" href="buyer-record.html">People<span class="n">{len(people)}</span></a>
  <span class="sn is-mock" title="Not in this mockup">Listings<span class="n">{len(D["listings"])}</span></span>
  <span class="sn on" aria-current="page">Explore</span>
  <span class="sx"><span class="t3">Route</span> <code>#/portfolio/explore</code></span>
</nav>

<div class="strip" role="group" aria-label="The portfolio in numbers">
  <div class="st"><span class="v">{len(buyers)}</span><span class="l">buyers · <b>{len(people) - len(buyers)}</b> owners</span></div>
  <div class="st"><span class="v">{len(D["listings"])}</span><span class="l">listings · {sum(1 for l in D["listings"] if l["kind"] == "launch")} launches, {sum(1 for l in D["listings"] if l["kind"] == "resale")} resale</span></div>
  <div class="st wide"><span class="v">{e(short_money(open_value))}</span><span class="l">in {len(open_props)} open proposals · 1 countered, 1 accepted</span></div>
  <div class="st"><span class="v">{visits_today}</span><span class="l">visits today · {sum(1 for a in D["agenda"] if a["kind"] == "visit" and a["status"] == "done")} done</span></div>
  <button type="button" class="st act" data-filter-days="14+"><span class="v hot">{len(no_contact)}</span><span class="l">buyers without contact for 14 days or more</span><span class="go">filter the list</span></button>
  <div class="st"><span class="v na">no target</span><span class="l">April target not set in the CRM</span></div>
</div>

<div class="switcher" role="group" aria-label="Mockup state">
  <span class="switcher-label">Mockup state</span>
  <button type="button" class="fchip on" data-state="normal" aria-pressed="true">Normal</button>
  <button type="button" class="fchip" data-state="empty" aria-pressed="false">Empty</button>
  <button type="button" class="fchip" data-state="loading" aria-pressed="false">Loading</button>
  <button type="button" class="fchip" data-state="error" aria-pressed="false">Error</button>
</div>

<div id="app" data-state="normal">
<div class="only-error notice-bad" role="alert"><b>The CRM did not answer at {RUN}.</b> The list shows yesterday's read. The assistant retries at 08:10, or <button type="button" class="lk-b" data-state="normal">retry now</button>.</div>

<section class="pn only-normal only-error" aria-labelledby="h-people">
  <div class="pn-h">
    <h2 id="h-people">People</h2><span class="pn-n" id="count">{len(people)}</span>
    <span class="pn-x"><span class="t3" id="live" aria-live="polite">{len(people)} of {len(people)} shown</span></span>
  </div>
  <div class="filters">
    <div class="fgroup" role="group" aria-label="Stage">{chips("stage", sorted(stage_counts.items()), "Stage")}</div>
    <div class="fgroup" role="group" aria-label="District">{chips("district", [(d, sum(1 for b in people if b["district"] == d)) for d in districts], "District")}</div>
    <div class="fgroup" role="group" aria-label="Days since contact">{chips("days", days_opts, "Days since contact")}</div>
    <div class="fgroup" role="group" aria-label="Source">{chips("source", source_opts, "Source")}</div>
  </div>
  <div class="tbw">
    <table class="tb" id="people">
      <thead><tr><th scope="col">Person</th><th scope="col">Stage</th><th scope="col">Looking for, listing</th><th scope="col" class="num">Budget, recorded</th><th scope="col">Last contact</th><th scope="col">Next step</th><th scope="col">Assistant proposes</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <div class="tb-foot"><span>Order: without contact first, then by last contact. Budget and next step as recorded in the CRM; "no data" means the field is empty.</span></div>
  </div>
  <div class="empty" id="people-empty" hidden><b>Nobody matches these filters.</b> <button type="button" class="b b-s b-sm" id="clear-filters">Clear filters</button></div>
</section>

<section class="pn only-empty" aria-label="Empty portfolio" hidden>
  <div class="pn-b"><div class="empty soft"><b>No people yet.</b><p>Your portfolio fills from three places: the CRM, the visits you log, and the portal leads. Connect the CRM in Sources, or log the first visit.</p><a class="b b-s" href="home.html">Open today</a></div></div>
</section>

<section class="pn only-loading" aria-label="Loading" aria-busy="true" hidden>
  <div class="pn-b"><p class="t3">Reading the CRM, started {RUN}.</p><div class="skeleton-rows"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></div>
</section>

<section class="pn ex-card only-normal only-error" aria-labelledby="h-explore">
  <div class="pn-h"><h2 id="h-explore">Explore</h2><span class="t3">answers only from the snapshot of {e(day(D["snapshot_date"]))}, with the source of each fact</span></div>
  <div class="pn-b">
    <form class="cmp" id="ex-cmp">
      <label class="sr" for="ex-in">Ask about the portfolio</label>
      <textarea id="ex-in" rows="2" placeholder="Which buyers visited but have no proposal?"></textarea>
      <div class="cmp-b">
        <span class="cmp-ctx" role="group" aria-label="Context"><button type="button" class="cmp-ctx-b">{ico("users", 14)}Whole portfolio</button></span>
        <button type="button" class="cmp-ic" aria-label="Attach a document (not in this mockup)">{ico("paperclip")}</button>
        <button type="button" class="cmp-ic" aria-label="Dictate (not in this mockup)">{ico("mic")}</button>
        <span class="grow"></span>
        <button type="submit" class="cmp-env" aria-label="Ask">{ico("arrow-up")}</button>
      </div>
    </form>
    <p class="ex-sgt t3">Questions this snapshot can answer</p>
    <ul class="sg-l">
      {''.join(f'<li><button type="button" class="sg" data-q="{e(q["id"])}">{ico("chevron-right", 14)}<span class="sg-t">{e(q["question"])}</span></button></li>' for q in D["explore"])}
    </ul>
    {answers}
    <article class="ex-ans" id="ans-none" hidden>
      <p class="ex-q"><span class="t3">You asked</span> <span id="ans-none-q"></span></p>
      <p class="ex-v">That question is not in this snapshot.</p>
      <p class="ex-o">The assistant answers only from the visit log, the CRM buyer records, the portal leads export and the listings file of 13 April. It does not estimate, and it does not search outside them.</p>
    </article>
  </div>
</section>
</div>
"""
    script = SHELL_JS + r"""
(function(){
  var rows=Array.prototype.slice.call(document.querySelectorAll('#people tbody tr'));
  var state={stage:'all',district:'all',days:'all',source:'all'};
  var total=rows.length, count=document.getElementById('count'), live=document.getElementById('live'), empty=document.getElementById('people-empty');
  function apply(){
    var shown=0;
    rows.forEach(function(r){
      var ok=(state.stage==='all'||r.getAttribute('data-stage')===state.stage)&&(state.district==='all'||r.getAttribute('data-district')===state.district)&&(state.days==='all'||r.getAttribute('data-days')===state.days)&&(state.source==='all'||r.getAttribute('data-source')===state.source);
      r.classList.toggle('is-out',!ok); if(ok)shown++;
    });
    count.textContent=shown; live.textContent=shown+' of '+total+' shown'; empty.hidden=shown!==0;
    document.querySelector('#people').hidden=shown===0;
  }
  function setChip(group,value){
    state[group]=value;
    document.querySelectorAll('.fchip[data-f="'+group+'"]').forEach(function(c){var on=c.getAttribute('data-v')===value;c.classList.toggle('on',on);c.setAttribute('aria-pressed',on?'true':'false');});
    apply();
  }
  document.querySelectorAll('.fchip[data-f]').forEach(function(c){c.addEventListener('click',function(){setChip(c.getAttribute('data-f'),c.getAttribute('data-v'));});});
  document.getElementById('clear-filters').addEventListener('click',function(){['stage','district','days','source'].forEach(function(g){setChip(g,'all');});document.querySelector('.fchip[data-f="stage"]').focus();});
  document.querySelectorAll('[data-filter-days]').forEach(function(b){b.addEventListener('click',function(){setChip('days',b.getAttribute('data-filter-days'));document.getElementById('h-people').scrollIntoView({block:'start'});});});
  var app=document.getElementById('app');
  document.querySelectorAll('[data-state]').forEach(function(b){b.addEventListener('click',function(){var s=b.getAttribute('data-state');app.setAttribute('data-state',s);document.querySelectorAll('.switcher [data-state]').forEach(function(x){var on=x.getAttribute('data-state')===s;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on?'true':'false');});});});
  function pad(n){return (n<10?'0':'')+n;}
  document.querySelectorAll('[data-approve]').forEach(function(b){
    b.addEventListener('click',function(){
      var id=b.getAttribute('data-approve'), prop=document.getElementById('prop-'+id), res=document.getElementById('result-'+id);
      var d=new Date(), t=pad(d.getHours())+':'+pad(d.getMinutes());
      prop.hidden=true; res.hidden=false; res.className='result notice-ok';
      res.innerHTML='<b>Task created at '+t+'.</b> '+b.getAttribute('data-task')+'. Nothing was sent to the buyer.';
      receipt('Done · Task created in the CRM',b.getAttribute('data-task'),function(){res.hidden=true;prop.hidden=false;b.focus();});
    });
  });
  document.querySelectorAll('[data-later]').forEach(function(b){
    b.addEventListener('click',function(){
      var id=b.getAttribute('data-later'), prop=document.getElementById('prop-'+id), res=document.getElementById('result-'+id);
      prop.hidden=true; res.hidden=false; res.className='result notice-neu';
      res.innerHTML='Kept for tomorrow. The proposal returns in tomorrow\'s read.';
      receipt('Kept for tomorrow','The proposal returns in tomorrow\'s read.',function(){res.hidden=true;prop.hidden=false;b.focus();});
    });
  });
  var form=document.getElementById('ex-cmp'), input=document.getElementById('ex-in');
  var canned=Array.prototype.slice.call(document.querySelectorAll('.ex-ans[data-q]'));
  function norm(s){return s.toLowerCase().replace(/[^a-z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();}
  function show(id,q){
    canned.forEach(function(a){a.hidden=true;}); document.getElementById('ans-none').hidden=true;
    var el=id?document.getElementById('ans-'+id):null;
    if(el){el.hidden=false;el.setAttribute('tabindex','-1');el.focus();}
    else{var n=document.getElementById('ans-none');document.getElementById('ans-none-q').textContent=q;n.hidden=false;n.setAttribute('tabindex','-1');n.focus();}
    var job=document.getElementById('job'); if(job){job.querySelector('.job-t').textContent='Assistant answered';job.querySelector('.job-s').textContent='from the snapshot, just now';}
  }
  form.addEventListener('submit',function(ev){ev.preventDefault();var q=input.value.trim()||input.placeholder;var hit=canned.filter(function(a){return norm(a.getAttribute('data-q'))===norm(q);})[0];show(hit?hit.id.replace('ans-',''):null,q);});
  input.addEventListener('keydown',function(ev){if(ev.key==='Enter'&&!ev.shiftKey){ev.preventDefault();form.requestSubmit?form.requestSubmit():form.dispatchEvent(new Event('submit',{cancelable:true}));}});
  document.querySelectorAll('.sg[data-q]').forEach(function(b){b.addEventListener('click',function(){input.value=b.querySelector('.sg-t').textContent;show(b.getAttribute('data-q'),input.value);});});
  document.querySelectorAll('[data-mockact]').forEach(function(b){b.addEventListener('click',function(){receipt('Not in this mockup',b.getAttribute('data-mockact')+' is a drawer in the next round.');});});
  var m=/q=([a-z0-9]+)/.exec(location.hash), tm=/t=([^&]+)/.exec(location.hash);
  if(m){var sg=document.querySelector('.sg[data-q="'+m[1]+'"]');
    if(sg&&document.getElementById('ans-'+m[1])){input.value=sg.querySelector('.sg-t').textContent;show(m[1],input.value);}
    else if(tm){input.value=decodeURIComponent(tm[1]);show(null,input.value);}}
  apply();
})();
"""
    body = shell("Portfolio", main)
    document("portfolio-explore.html", "Portfolio, explore view, built with the rules",
             "A broker's portfolio as a dense operator screen: every person with stage, budget as recorded, last contact and next step, the assistant's proposals with their evidence, and an explore box that answers only from the snapshot, with the source of each fact.",
             body, ["screens.css"], script, "screen", "portfolio-explore-generic.html", "Portfolio")


# ---------------------------------------------------------------- generic twins (literal values on purpose)


def portfolio_explore_generic():
    cards = []
    for b in D["buyers"]:
        if b["kind"] != "buyer":
            continue
        amt = "$" + f"{round((b['budget'] or 0) / 50000) * 50000 or 500000:,}"
        hot = b["stage"] in ("proposal", "reservation")
        cards.append(
            f'<div class="g-card"><div class="g-card-top"><span class="g-badge">✨ AI insight</span>{" <span class=\"g-badge g-badge-hot\">🔥 Hot lead</span>" if hot else ""}</div>'
            f'<h3>{e(b["name"])}</h3><p class="g-sub">{e(b["stage"].title())} · {amt} · {e(b["district"])}</p>'
            f'<p class="g-text">Our AI recommends reaching out today to maximize your conversion potential.</p>'
            f'<div class="g-actions"><button type="button" class="g-btn g-btn-primary">Reach out ✅</button><button type="button" class="g-btn g-btn-secondary">View profile</button></div></div>'
        )
    body = f"""
<header class="g-hero">
  <div class="g-hero-inner">
    <span class="g-pill">✨ AI-powered</span>
    <h1>Welcome back, {e(BROKER["first_name"])}! 👋</h1>
    <p class="g-lead">Unlock your real estate superpowers. Your personalized buyer insights are ready to supercharge your pipeline.</p>
    <div class="g-hero-actions"><button type="button" class="g-btn g-btn-light">Get started</button><button type="button" class="g-btn g-btn-ghost">Learn more</button></div>
  </div>
</header>
<main class="g-main">
  <section class="g-stats">
    <div class="g-stat"><p class="g-stat-value">100+</p><p class="g-stat-label">Leads analyzed</p></div>
    <div class="g-stat"><p class="g-stat-value">$5M</p><p class="g-stat-label">Pipeline value</p></div>
    <div class="g-stat"><p class="g-stat-value">98%</p><p class="g-stat-label">Match accuracy</p></div>
  </section>
  <section class="g-features">
    <div class="g-feature"><div class="g-icon">🏠</div><h3>Smart Matching</h3><p>Next-gen AI pairs every buyer with their dream home.</p></div>
    <div class="g-feature"><div class="g-icon">📈</div><h3>Lead Scoring</h3><p>Effortlessly prioritize the leads most likely to close.</p></div>
    <div class="g-feature"><div class="g-icon">⚡</div><h3>Instant Insights</h3><p>Real-time recommendations, powered by AI.</p></div>
  </section>
  <section class="g-list">
    <h2>Your buyers 🗂️</h2>
    <div class="g-grid">{''.join(cards)}</div>
  </section>
</main>
"""
    document("portfolio-explore-generic.html", "Portfolio, the generic version",
             "The same broker's portfolio as a typical generated page: gradient hero, three icon cards, centered copy, round numbers, no sources, no states.",
             body, ["screens.css"], "", "generic", "portfolio-explore.html", "Portfolio")


# ---------------------------------------------------------------- buyer record (built with the rules)


def buyer_record():
    b = BUYERS["B-01"]
    s = SUGG[b["suggestion"]]
    listing = LISTINGS["L-101"]
    visits = [v for v in D["visits"] if v["buyer"] == b["id"]]
    first_visit = min(v["date"] for v in visits)
    open_tasks = [t for t in D["tasks"] if t["buyer"] == b["id"]]
    trail_rows = "".join(
        f'<tr><td class="num mono">{e(t["when"])}</td><td>{e(t["what"])}</td><td>{e(t["buyer"])}</td><td>{e(t["approved_by"])}</td>'
        f'<td>{"<span class=\"ch ch-neu\">undone</span>" if t["undone"] else ("<span class=\"ch ch-warn\">waiting</span>" if "not approved" in t["approved_by"] else "<span class=\"ch ch-ok\">in the CRM</span>")}</td></tr>'
        for t in D["trail"]
    )
    visit_rows = "".join(
        f'<li class="vrow"><span class="wh"><b>{e(day(v["date"]))}</b><small>{e(v["time"])}</small></span>'
        f'<span><span class="tt">{logo(LISTINGS[v["listing"]]["name"])}{e(LISTINGS[v["listing"]]["name"])} <span class="ch {"ch-ok" if v["outcome"] == "liked" else "ch-warn"}">{e(v["outcome"])}</span></span>'
        f'<span class="ds">"{e(v["feedback"])}" <span class="src">visit log [1]</span></span>'
        f'<span class="ds">{"Follow-up sent" if v["follow_up_sent"] else "<span class=\"ch ch-bad\">no follow-up sent</span>"}</span></span></li>'
        for v in sorted(visits, key=lambda v: v["date"], reverse=True)
    )
    writes = "".join(f'<li><b>{e(w["object"])}</b> {e(w["fields"])}</li>' for w in s["writes"])
    evidence = "".join(f'<li>"{e(x["quote"])}" <span class="src">{e(x["source"])} [{x["ref"]}]</span></li>' for x in s["evidence"])
    missing = ", ".join(b["missing_fields"])
    ctx = f"""
<div class="ctx" id="ctx">
  <span class="ctx-tr"><a class="ctx-all" href="portfolio-explore.html">{ico("users")}All people</a><span class="sep" aria-hidden="true">{ico("chevron-right", 14)}</span><span class="cn">{e(b["name"])}</span></span>
  <span class="cf"><span class="kf"><b>{stage_chip(b["stage"])}</b></span><span class="kf"><b>{e(b["source"])}</b><i>source</i></span><span class="kf"><b>{e(day(b["since"]))}</b><i>since</i></span></span>
  <span class="ca"><span class="seg-g" role="group" aria-label="View"><span class="seg on">Record</span><a class="seg" href="home.html#priorities">Priorities</a></span><span class="b b-l b-sm is-mock" title="Not in this mockup">Record in the CRM</span></span>
</div>
"""
    main = f"""
<section class="fid" aria-labelledby="h-id">
  <div class="fid-id"><h1 id="h-id">{e(b["name"])}</h1>
    <div class="chs">{stage_chip(b["stage"])}<span class="ch ch-dk">{e(b["source"])}</span><span class="ch ch-dk">since {e(day(b["since"]))}</span><span class="ch ch-dk">{e(b["looking_for"])}</span></div>
  </div>
  <div class="facts">
    <div class="fact"><span class="l">Budget</span><span class="v">{e(short_money(b["budget"]))}</span><span class="r">recorded 2 March · CRM [2]</span></div>
    <div class="fact"><span class="l">Visits</span><span class="v">{len(visits)}</span><span class="r">6 and 10 April · unit 1204 [1]</span></div>
    <div class="fact"><span class="l">Open proposals</span><span class="v hot">0</span><span class="r">none, {days_since(first_visit)} days after the first visit [2]</span></div>
    <div class="fact"><span class="l">Last contact</span><span class="v">{e(day(b["last_contact"]))}</span><span class="r">{e(b["last_contact_kind"])} [1]</span></div>
  </div>
</section>

<div class="ftabs" role="tablist" aria-label="Record sections">
  <button type="button" class="ft on" role="tab" id="tab-overview" aria-selected="true" aria-controls="panel-overview">Overview</button>
  <button type="button" class="ft" role="tab" id="tab-visits" aria-selected="false" aria-controls="panel-visits" tabindex="-1">Visits<span class="n">{len(visits)}</span></button>
  <button type="button" class="ft" role="tab" id="tab-proposals" aria-selected="false" aria-controls="panel-proposals" tabindex="-1">Proposals<span class="n">0</span></button>
  <button type="button" class="ft" role="tab" id="tab-docs" aria-selected="false" aria-controls="panel-docs" tabindex="-1">Documents<span class="n">1</span></button>
</div>

<div class="kpanel" id="panel-overview" role="tabpanel" aria-labelledby="tab-overview">
  <section class="blk hnc" aria-labelledby="h-today">
    <div class="blk-h"><h2 id="h-today">Today for this buyer</h2><span class="src">visit log [1] · CRM read {RUN} [2]</span></div>
    <div class="hnc-f">
      <div class="pf-i"><b>{days_since(first_visit)}</b><span>days since the first visit</span></div>
      <div class="pf-i"><b>2</b><span>visits, both "liked"</span></div>
      <div class="pf-i"><b>{len(open_tasks)}</b><span>open task for this buyer</span></div>
      <div class="pf-i"><b class="na">none</b><span>financing simulation on record</span></div>
    </div>
    <article class="prop-card" id="prop-card">
      <span class="ch ch-prop">Assistant proposes</span>
      <h3>{e(s["title"])}</h3>
      <p class="t3">Based on</p>
      <ul class="ev">{evidence}</ul>
      <p class="t3">What it writes, if you approve</p>
      <ul class="writes" id="writes">{writes}</ul>
      <div class="acts" id="prop-actions">
        <button type="button" class="b b-p" id="approve">Create the task and the note</button>
        <button type="button" class="b b-s" id="edit">Edit what it writes</button>
        <button type="button" class="b b-t" id="later">Not now</button>
      </div>
      <div class="result" id="result" hidden></div>
      <p class="never"><b>The assistant will not:</b> {e(s["never"])}.</p>
    </article>
  </section>

  <div class="gr2">
    <section class="blk" aria-labelledby="h-sum">
      <div class="blk-h"><h2 id="h-sum">Summary</h2><span class="src">written from [1] and [2], not from memory</span></div>
      <div class="exec">
        <p class="exec-l">Who</p><p>Buyer from Portal A since 2 March, looking for a two-bedroom launch unit in Northgate with delivery in 2027. Budget recorded at $650,000, which covers unit 1204 at $620,000.</p>
        <p class="exec-l">Where it stands</p><p>Two visits to unit 1204, the second with her partner. On both she asked about the financing simulation, and none is on record. No proposal nine days after the first visit.</p>
        <p class="exec-l">What is missing</p><p>Financing pre-approval and a decision date. The CRM has neither; the assistant does not estimate them.</p>
      </div>
    </section>
    <section class="blk" aria-labelledby="h-signals">
      <div class="blk-h"><h2 id="h-signals">Signals</h2><span class="src">[1] [2]</span></div>
      <ul class="signals">
        <li><b>Asked about financing twice</b><span>6 and 10 April [1]</span></li>
        <li><b>Visited with her partner</b><span>10 April [1]</span></li>
        <li><b>Budget covers the unit</b><span>$650,000 against $620,000 [2] [4]</span></li>
        <li><b>No follow-up sent after either visit</b><span>visit log [1]</span></li>
        <li><b>Portal lead on the same unit this morning</b><span>name withheld by the portal [3]</span></li>
      </ul>
      <div class="cov"><span class="t3">Profile coverage</span><span class="pb" aria-label="6 of 8 fields filled"><span class="tr"><i class="ok" style="width:75%"></i></span><span class="pl"><b>6</b> of 8 fields</span></span><p class="t3">missing: {e(missing)}</p></div>
    </section>
  </div>

  <section class="blk" aria-labelledby="h-props">
    <div class="blk-h"><h2 id="h-props">Open proposals</h2><span class="src">CRM [2]</span></div>
    <div class="empty soft"><b>No proposal yet.</b><p>The assistant proposes one after the financing simulation is sent and answered. The unit is {logo(listing["name"])}{e(listing["name"])}, {money(listing["price"])}, {listing["visits"]} visits and {listing["proposals"]} proposals from other buyers [4].</p></div>
  </section>

  <section class="blk" aria-labelledby="h-visits">
    <div class="blk-h"><h2 id="h-visits">Visits</h2><span class="src">visit log [1]</span></div>
    <ul class="ag">{visit_rows}</ul>
  </section>

  <section class="blk" aria-labelledby="h-trail">
    <div class="blk-h"><h2 id="h-trail">What the assistant did, and who approved it</h2><span class="src">assistant log, all people</span></div>
    <div class="tbw"><table class="tb"><thead><tr><th scope="col">When</th><th scope="col">What</th><th scope="col">Person</th><th scope="col">Approved by</th><th scope="col">Status</th></tr></thead><tbody id="trail-rows">{trail_rows}</tbody></table></div>
  </section>
</div>

<div class="kpanel" id="panel-visits" role="tabpanel" aria-labelledby="tab-visits" hidden>
  <section class="blk"><div class="blk-h"><h2>Visits</h2><span class="src">visit log [1]</span></div><ul class="ag">{visit_rows}</ul></section>
</div>
<div class="kpanel" id="panel-proposals" role="tabpanel" aria-labelledby="tab-proposals" hidden>
  <section class="blk"><div class="blk-h"><h2>Proposals</h2><span class="src">CRM [2]</span></div><div class="empty soft"><b>No proposal yet.</b><p>Nothing to show. The proposal, when it exists, appears here with its status and the developer's answer.</p></div></section>
</div>
<div class="kpanel" id="panel-docs" role="tabpanel" aria-labelledby="tab-docs" hidden>
  <section class="blk"><div class="blk-h"><h2>Documents</h2><span class="src">CRM [2]</span></div><ul class="ag"><li class="vrow"><span class="wh"><b>2 Mar</b></span><span><span class="tt">{ico("file")}Identity document, copy</span><span class="ds">uploaded by the broker on the first contact</span></span></li></ul><p class="t3 pad">Missing for a proposal: proof of income and the financing pre-approval. The assistant lists them; it does not request them from the buyer.</p></section>
</div>
"""
    script = SHELL_JS + r"""
(function(){
  var tabs=Array.prototype.slice.call(document.querySelectorAll('.ft[role="tab"]'));
  function select(t){tabs.forEach(function(x){var on=x===t;x.classList.toggle('on',on);x.setAttribute('aria-selected',on?'true':'false');x.setAttribute('tabindex',on?'0':'-1');document.getElementById(x.getAttribute('aria-controls')).hidden=!on;});}
  tabs.forEach(function(t,i){t.addEventListener('click',function(){select(t);});t.addEventListener('keydown',function(ev){var j=null;if(ev.key==='ArrowRight')j=(i+1)%tabs.length;if(ev.key==='ArrowLeft')j=(i-1+tabs.length)%tabs.length;if(ev.key==='Home')j=0;if(ev.key==='End')j=tabs.length-1;if(j!==null){ev.preventDefault();select(tabs[j]);tabs[j].focus();}});});
  function pad(n){return (n<10?'0':'')+n;}
  var approve=document.getElementById('approve'), edit=document.getElementById('edit'), later=document.getElementById('later'), actions=document.getElementById('prop-actions'), res=document.getElementById('result'), rows=document.getElementById('trail-rows');
  var added=null;
  approve.addEventListener('click',function(){
    var d=new Date(), t=pad(d.getHours())+':'+pad(d.getMinutes());
    actions.hidden=true; res.hidden=false; res.className='result notice-ok';
    res.innerHTML='<b>Created at '+t+':</b> the task and the note shown above. Nothing was sent to the buyer.';
    added=document.createElement('tr');
    added.innerHTML='<td class="num mono">'+d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())+' '+t+'</td><td>Task and note created: financing simulation, unit 1204</td><td>Helena Marques</td><td>Marina Costa</td><td><span class="ch ch-ok">in the CRM</span></td>';
    rows.insertBefore(added,rows.firstChild);
    receipt('Done · Task and note in the CRM','Financing simulation, unit 1204, due 14 April',function(){res.hidden=true;actions.hidden=false;if(added){added.querySelector('td:last-child').innerHTML='<span class="ch ch-neu">undone</span>';}approve.focus();});
    res.setAttribute('tabindex','-1'); res.focus();
  });
  edit.addEventListener('click',function(){
    var items=document.querySelectorAll('#writes li'); items.forEach(function(li){if(li.getAttribute('contenteditable'))return;li.setAttribute('contenteditable','true');li.classList.add('editing');});
    edit.textContent='Editing: change the text, then create'; if(items[0]){items[0].focus();}
  });
  later.addEventListener('click',function(){actions.hidden=true;res.hidden=false;res.className='result notice-neu';res.innerHTML='Kept for tomorrow. The proposal returns in tomorrow\'s read.';receipt('Kept for tomorrow','',function(){res.hidden=true;actions.hidden=false;later.focus();});});
})();
"""
    body = shell("Portfolio", main, ctx, "Portfolio read", f"done today at {RUN}")
    document("buyer-record.html", "Buyer record, built with the rules",
             "One buyer's record: the facts in a banner with their sources, the assistant's suggestion with its evidence and what it writes, approval with undo, the summary, the signals, the visits and the trail of what the assistant did before.",
             body, ["screens.css"], script, "screen", "buyer-record-generic.html", "Buyer record")


def buyer_record_generic():
    body = """
<header class="g-hero g-hero-small">
  <div class="g-hero-inner">
    <span class="g-pill">✨ AI Buyer Insight</span>
    <h1>Helena is ready to buy! 🔥</h1>
    <p class="g-lead">Our AI analyzed her visits and found a high-potential opportunity.</p>
  </div>
</header>
<main class="g-main">
  <section class="g-insight">
    <div class="g-score"><p class="g-score-value">92%</p><p class="g-score-label">Buyer intent score</p></div>
    <div class="g-insight-text">
      <h2>Recommended action ✅</h2>
      <p>Send a proposal today and follow up with a personalized message to keep the momentum going. Our AI thinks this deal is likely to close soon.</p>
      <div class="g-actions"><button type="button" class="g-btn g-btn-primary">Approve ✨</button><button type="button" class="g-btn g-btn-danger">Reject ❌</button></div>
    </div>
  </section>
  <section class="g-features">
    <div class="g-feature"><div class="g-icon">🎯</div><h3>Next Best Action</h3><p>AI-generated next steps tailored to every buyer.</p></div>
    <div class="g-feature"><div class="g-icon">💡</div><h3>Smart Summary</h3><p>Key takeaways from every visit, instantly.</p></div>
    <div class="g-feature"><div class="g-icon">🚀</div><h3>Auto-update</h3><p>Let AI keep your CRM up to date.</p></div>
  </section>
</main>
"""
    document("buyer-record-generic.html", "Buyer record, the generic version",
             "The same buyer as a typical generated screen: an intent score with no definition, two colored buttons, no evidence, no trail.",
             body, ["screens.css"], "", "generic", "buyer-record.html", "Buyer record")


# ---------------------------------------------------------------- home (built with the rules)


def home():
    def sg_href(x):
        if x["q"] in EXPLORE:
            return f'portfolio-explore.html#q={x["q"]}'
        return "portfolio-explore.html#q=none&t=" + urllib.parse.quote(x["text"])

    sg = "".join(
        f'<li><a class="sg" href="{e(sg_href(x))}">{logo(LISTINGS[x["listing"]]["name"]) if x["listing"] else ico("users", 14)}<span class="sg-t">{e(x["text"])}</span><span class="sg-k num">{e(x["when"])}</span></a></li>'
        for x in D["home_suggestions"]
    )
    ag = "".join(
        f'<li class="ag-i {e(a["status"])}"><span class="wh"><b class="num">{e(a["time"])}</b><small>{e(a["kind"])}</small></span>'
        f'<span><span class="tt">{e(BUYERS[a["buyer"]]["name"]) if a["buyer"] else "Developer call"} <span class="ch {"ch-ok" if a["status"] == "done" else ("ch-info" if a["status"] == "next" else "ch-neu")}">{e(a["status"])}</span></span>'
        f'<span class="ds">{logo(LISTINGS[a["listing"]]["name"])}{e(LISTINGS[a["listing"]]["name"])} · {e(a["note"])}</span></span></li>'
        for a in D["agenda"]
    )
    level_cls = {"Urgent": "l1", "Important": "l2", "Keep warm": "l3", "Build the future": "l4"}
    pr = "".join(
        f'<li class="al-r" id="pr-{i}"><div class="al-m"><span class="ch ch-lvl {level_cls[p["level"]]}">{e(p["level"])}</span><span class="dl">{e(p["when"])}</span></div>'
        f'<div class="al-b"><b><a class="lkn" href="buyer-record.html">{e(BUYERS[p["buyer"]]["name"])}</a></b><span class="ac">{logo(LISTINGS[p["listing"]]["name"])}{e(LISTINGS[p["listing"]]["name"])}</span></div>'
        f'<div class="al-w"><span class="rasc">{e(p["text"])}</span><span class="src">{e(SUGG[p["suggestion"]]["evidence"][0]["source"])} [{SUGG[p["suggestion"]]["evidence"][0]["ref"]}]</span></div>'
        f'<div class="al-a"><button type="button" class="b b-p b-sm" data-pr="{i}" data-task="{e(SUGG[p["suggestion"]]["writes"][0]["fields"])}">Create task</button><a class="b b-t b-sm" href="buyer-record.html">Open</a><span class="al-st" id="pr-st-{i}" hidden></span></div></li>'
        for i, p in enumerate(D["priorities"])
    )
    tk = "".join(
        f'<li class="tk-r" id="tk-{e(t["id"])}"><div class="wh {"late" if t["overdue_days"] else ""}">'
        + (f'<small>overdue {t["overdue_days"]} d</small>' if t["overdue_days"] else f'<small>{"today" if t["due"] == D["snapshot_date"] else "due " + day(t["due"])}</small>')
        + f'</div><div><div class="tt"><span class="ch ch-neu">{e(t["kind"])}</span>{e(t["subject"])}</div><div class="ds">{logo(LISTINGS[t["listing"]]["name"])}{e(LISTINGS[t["listing"]]["name"])} · <span class="src">{e(t["source"])}</span></div><div class="ds al-st" id="tk-st-{e(t["id"])}" hidden></div></div>'
        f'<div class="acts"><button type="button" class="b b-p b-sm" data-done="{e(t["id"])}">Complete</button></div></li>'
        for t in D["tasks"]
    )
    w = D["week"]
    fc = "".join(
        f'<div class="st"><span class="v{" na" if s["value"] is None and s["count"] == 0 else ""}">{s["count"]}</span><span class="l">{e(s["label"].lower())} · {e(short_money(s["value"])) if s["value"] is not None else "no value yet"}</span></div>'
        for s in D["forecast"]["stages"]
    )
    main = f"""
<section class="ex" aria-labelledby="h-greet">
  <h1 class="ex-t" id="h-greet">{greeting()}, {e(BROKER["first_name"])}</h1>
  <form class="cmp" id="ex-cmp" action="portfolio-explore.html" method="get">
    <label class="sr" for="ex-in">Ask about your portfolio</label>
    <textarea id="ex-in" rows="3" placeholder="Ask about a buyer, a listing or your week. The assistant answers only from the snapshot, with sources."></textarea>
    <div class="cmp-b">
      <span class="cmp-ctx" role="group" aria-label="Context"><button type="button" class="cmp-ctx-b">{ico("users", 14)}Whole portfolio</button></span>
      <button type="button" class="cmp-ic" aria-label="Attach a document (not in this mockup)">{ico("paperclip")}</button>
      <button type="button" class="cmp-ic" aria-label="Dictate (not in this mockup)">{ico("mic")}</button>
      <span class="grow"></span>
      <button type="submit" class="cmp-env" aria-label="Ask">{ico("arrow-up")}</button>
    </div>
  </form>
  <section class="ex-sg" aria-labelledby="h-sg">
    <h2 id="h-sg" class="ex-sgt">From your agenda</h2>
    <ul class="sg-l">{sg}</ul>
  </section>
</section>

<div class="strip" role="group" aria-label="This week in numbers">
  <div class="st"><span class="v">{w["visits"]}</span><span class="l">visits this week · <b>{w["visits_prev"]}</b> last week</span></div>
  <div class="st"><span class="v">{w["proposals_sent"]}</span><span class="l">proposals sent</span></div>
  <div class="st"><span class="v">{w["reservations"]}</span><span class="l">reservation accepted</span></div>
  <div class="st"><span class="v">{w["signed"]}</span><span class="l">signed · {e(short_money(w["signed_value"]))}</span></div>
  <div class="st"><span class="v na">no target</span><span class="l">April target not set in the CRM</span></div>
</div>

<section class="pn" aria-labelledby="h-agenda">
  <div class="pn-h"><h2 id="h-agenda">Today</h2><span class="pn-n">{len(D["agenda"])}</span><span class="pn-x"><span class="src">calendar and visit log [1]</span></span></div>
  <ul class="ag">{ag}</ul>
</section>

<section class="pn" id="priorities" aria-labelledby="h-pr">
  <div class="pn-h"><h2 id="h-pr">Priorities</h2><span class="pn-n hot">{len(D["priorities"])}</span><span class="pn-x"><span class="src">proposed by the assistant at {RUN}; nothing is written until you approve</span></span></div>
  <ol class="al">{pr}</ol>
  <div class="al-foot"><span class="t3">Level: Urgent today, Important this week, Keep warm this month, Build the future when the other side answers. The level comes from the days without contact and the stage, both in the CRM [2].</span></div>
</section>

<section class="pn" id="tasks" aria-labelledby="h-tk">
  <div class="pn-h"><h2 id="h-tk">Tasks</h2><span class="pn-n">{len(D["tasks"])}</span><span class="pn-x"><span class="t3">{sum(1 for t in D["tasks"] if t["overdue_days"])} overdue · {sum(1 for t in D["tasks"] if t["due"] == D["snapshot_date"])} for today</span></span></div>
  <ol class="ag tk">{tk}</ol>
</section>

<section class="pn" aria-labelledby="h-fc">
  <div class="pn-h"><h2 id="h-fc">Forecast, {e(D["forecast"]["month"])}</h2><span class="pn-x"><span class="src">CRM [2] · values are the proposal amounts, not estimates</span></span></div>
  <div class="strip in-card" role="group" aria-label="Forecast by stage">{fc}</div>
</section>
"""
    script = SHELL_JS + r"""
(function(){
  var form=document.getElementById('ex-cmp'), input=document.getElementById('ex-in');
  form.addEventListener('submit',function(ev){ev.preventDefault();var q=input.value.trim()||'Ask about a buyer, a listing or your week';var map={'which buyers visited but have no proposal':'q1','which listings have been on the market for more than 60 days':'q2','what closes this month':'q3'};var k=q.toLowerCase().replace(/[^a-z0-9 ]+/g,' ').replace(/\s+/g,' ').trim();location.href='portfolio-explore.html#q='+(map[k]||('none&t='+encodeURIComponent(q)));});
  input.addEventListener('keydown',function(ev){if(ev.key==='Enter'&&!ev.shiftKey){ev.preventDefault();form.dispatchEvent(new Event('submit',{cancelable:true}));}});
  function pad(n){return (n<10?'0':'')+n;}
  document.querySelectorAll('[data-pr]').forEach(function(b){
    b.addEventListener('click',function(){
      var i=b.getAttribute('data-pr'), st=document.getElementById('pr-st-'+i), row=document.getElementById('pr-'+i);
      var d=new Date(), t=pad(d.getHours())+':'+pad(d.getMinutes());
      b.hidden=true; st.hidden=false; st.textContent='Task created at '+t;
      row.classList.add('is-done');
      receipt('Done · Task created in the CRM',b.getAttribute('data-task'),function(){b.hidden=false;st.hidden=true;row.classList.remove('is-done');b.focus();});
    });
  });
  document.querySelectorAll('[data-done]').forEach(function(b){
    b.addEventListener('click',function(){
      var id=b.getAttribute('data-done'), row=document.getElementById('tk-'+id), st=document.getElementById('tk-st-'+id);
      var d=new Date(), t=pad(d.getHours())+':'+pad(d.getMinutes());
      row.classList.add('is-done'); b.hidden=true; st.hidden=false; st.textContent='Completed at '+t+' in the CRM';
      receipt('Done · Task completed in the CRM',row.querySelector('.tt').textContent.trim(),function(){row.classList.remove('is-done');b.hidden=false;st.hidden=true;b.focus();});
    });
  });
})();
"""
    body = shell("Home", main)
    document("home.html", "Home, built with the rules",
             "The broker's day: a greeting with the snapshot's time, a question box that answers only from the data, the agenda, the priorities the assistant proposes with their evidence, the tasks, and the week's numbers with their sources.",
             body, ["screens.css"], script, "screen", "home-generic.html", "Home")


def home_generic():
    body = f"""
<header class="g-hero g-hero-small">
  <div class="g-hero-inner">
    <span class="g-pill">☀️ Daily Dashboard</span>
    <h1>Good afternoon, {e(BROKER["first_name"])}! You're crushing it 🎉</h1>
    <p class="g-lead">Your AI-powered performance snapshot is ready.</p>
  </div>
</header>
<main class="g-main g-main-narrow">
  <section class="g-insight g-center">
    <div class="g-score"><p class="g-score-value">87%</p><p class="g-score-label">Pipeline health score</p></div>
    <p class="g-text">Amazing week! Keep up the momentum to hit your goals 🚀</p>
  </section>
  <section class="g-stats">
    <div class="g-stat"><p class="g-stat-value">10+</p><p class="g-stat-label">Visits</p></div>
    <div class="g-stat"><p class="g-stat-value">50</p><p class="g-stat-label">AI actions</p></div>
    <div class="g-stat"><p class="g-stat-value">$3M</p><p class="g-stat-label">Pipeline</p></div>
  </section>
  <section class="g-list g-center">
    <h2>Top opportunities 🏆</h2>
    <div class="g-grid g-grid-narrow">
      <div class="g-card g-center"><div class="g-icon">🥇</div><h3>Tomas</h3><p class="g-sub">95% intent score</p></div>
      <div class="g-card g-center"><div class="g-icon">🥈</div><h3>Helena</h3><p class="g-sub">80% intent score</p></div>
      <div class="g-card g-center"><div class="g-icon">🥉</div><h3>Mateo</h3><p class="g-sub">45% intent score</p></div>
    </div>
    <button type="button" class="g-btn g-btn-primary">View full report</button>
  </section>
</main>
"""
    document("home-generic.html", "Home, the generic version",
             "The same broker's day as a typical generated dashboard: a health score, medals, round numbers, centered everything.",
             body, ["screens.css"], "", "generic", "home.html", "Home")


# ---------------------------------------------------------------- gallery index

PAIRS = [
    {
        "slug": "portfolio-explore", "title": "The broker's portfolio",
        "job": "A broker between two visits, two minutes, laptop or phone: who in my portfolio is waiting on me, and for what?",
        "frame": (1280, 860),
        "notice": [
            ("1, 2, 6", "No hero, no icon grid, nothing centered. The first thing on the screen is the portfolio: person, stage, last contact with its date, next step, on real-looking data with its snapshot time."),
            ("7", "Two budgets, one phone and one price read \"no data\" because the source has none. The generic version rounds the budgets and shows $500,000 for the two empty ones."),
            ("source", "Every number in the strip, every proposal and every explore answer carries its source: visit log [1], CRM [2], portal leads [3], listings file [4]."),
            ("11", "Empty, loading and error are one click away in the state switcher; a filter with no match shows its own empty state. The generic page has one state."),
            ("15", "The button says what happens in the system: \"Create the task\", with Undo. Not \"Reach out\" with a check mark."),
            ("agent", "The assistant's proposal sits in its own column with the visit sentence it is based on. The explore box answers only from the snapshot and says so when it cannot."),
        ],
    },
    {
        "slug": "buyer-record", "title": "One buyer's record",
        "job": "The same broker decides whether to let the assistant write a task and a note into the CRM for one buyer.",
        "frame": (1280, 860),
        "notice": [
            ("4, 5", "No \"ready to buy!\", no intent score with no definition, no fire emoji. Four facts in a banner, each with its source and date."),
            ("agent", "Evidence first: the two visit sentences and the CRM line the suggestion rests on, then what it writes, field by field, then the button."),
            ("10", "Two buttons, one quiet one. Approve writes and shows Undo; Edit makes the text editable in place; \"Not now\" keeps it for tomorrow. Reject is not a red button."),
            ("agent", "The trail at the bottom: what the assistant did before, when, approved by whom, and one entry that was undone."),
            ("13", "Tabs are real tabs: arrow keys move between them, the panel follows, focus stays visible. Try it on both versions."),
        ],
    },
    {
        "slug": "home", "title": "The broker's day",
        "job": "Late afternoon, before the 16:30 visit: what is on today, what the assistant thinks is late, and how the week stands.",
        "frame": (1280, 860),
        "notice": [
            ("1, 14", "No health score, no medals, no confetti. A greeting with the snapshot's time, then the agenda, the priorities and the tasks on real-looking data."),
            ("4, 15", "Each priority says the fact that makes it a priority (\"the counter has waited 8 days\") and the source. Not \"you're crushing it\"."),
            ("7", "The week's strip reads \"no target\" where the CRM has none. The generic version invents a score."),
            ("agent", "Priorities are proposals: nothing is written until \"Create task\", and every write shows Undo in the receipt."),
            ("6, 9", "Left-aligned, one spacing scale, one accent. Dense on purpose: a broker opens this screen six times a day."),
        ],
    },
]


def gallery():
    pairs_html = []
    for p in PAIRS:
        w, h = p["frame"]
        notice = "".join(f'<li><span class="tell">{e(n)}</span><span>{e(t)}</span></li>' for n, t in p["notice"])
        pairs_html.append(f"""
<section class="pair" aria-labelledby="h-{p['slug']}">
  <div class="pair-head">
    <h2 id="h-{p['slug']}">{e(p['title'])}</h2>
    <p class="job">{e(p['job'])}</p>
  </div>
  <div class="pair-grid">
    <figure class="shot">
      <div class="preview" data-w="{w}" data-h="{h}"><iframe src="{p['slug']}.html" title="{e(p['title'])}, built with the rules" loading="lazy" tabindex="-1" aria-hidden="true"></iframe></div>
      <figcaption><a href="{p['slug']}.html">Built with the rules</a> <span class="muted">opens the live page</span></figcaption>
    </figure>
    <figure class="shot">
      <div class="preview" data-w="{w}" data-h="{h}"><iframe src="{p['slug']}-generic.html" title="{e(p['title'])}, the generic version" loading="lazy" tabindex="-1" aria-hidden="true"></iframe></div>
      <figcaption><a href="{p['slug']}-generic.html">The generic version</a> <span class="muted">most people would accept it</span></figcaption>
    </figure>
  </div>
  <div class="notice-list">
    <h3>What to notice <span class="muted">(numbers are the tells in the list)</span></h3>
    <ul>{notice}</ul>
  </div>
</section>
""")
    body = f"""
<header class="g-head">
  <div class="g-head-inner">
    <p class="site-name">No-slop design</p>
    <h1>Visual AI slop is manageable.</h1>
    <p class="lede">AI builds a screen in minutes, and the default result looks like every other AI screen. It costs credibility the moment a customer, a sponsor or a candidate opens it. Three screens of a broker's assistant for a fictional real-estate brokerage, each built with a small set of rules, next to the version most tools would produce from the same brief. Both are live pages: open them, click, press Tab.</p>
    <p class="lede-2">The layout is an operator product a broker opens all day: navigation on the canvas, the work in white cards on a sheet, the numbers of the day in a dark banner. Density and sources matter more than decoration.</p>
    <p class="actions"><a class="btn btn-primary" href="#pairs">See the screens</a> <a class="btn" href="{REPO_URL}">The rules on GitHub</a></p>
    <p class="muted">Fictional brokerage, people and numbers. Snapshot of {e(long_date(SNAPSHOT))}, {e(D["snapshot_time"])}. Every page is generated from the same data file by one script; nothing is edited by hand.</p>
  </div>
</header>
<main class="g-body" id="pairs">
{''.join(pairs_html)}
<section class="how" aria-labelledby="h-how">
  <h2 id="h-how">How these were made</h2>
  <ol class="how-list">
    <li><strong>Real-looking data, frozen.</strong> Fourteen people, nine listings, twelve visits, five proposals and four portal leads, dated 13 April 2026. Two budgets, one phone and one price are missing in the source, so the screens say so.</li>
    <li><strong>One generator, never a hand edit.</strong> A single Python script reads the data and the tokens and writes every page here, including the generic twins.</li>
    <li><strong>Measured, not squinted.</strong> Contrast on every text pair, two widths, keyboard reach, the four states. The tells list is the audit.</li>
  </ol>
  <p>The rules: <a href="{REPO_URL}/blob/main/docs/visual-slop-tells.md">sixteen visual tells and what to do instead</a>. The workflow: <a href="{REPO_URL}/blob/main/docs/mockup-first.md">from a brief to a validated decision in a thirty-minute session</a>. The worked example behind these screens: <a href="{REPO_URL}/tree/main/examples/acme-realty">brief, data snapshot, audit and session notes</a>. The skills: <a href="{REPO_URL}/tree/main/skills">html-mockup, visual-slop-audit, visual-validation-session, design-tokens-starter</a>. The tokens behind every screen: <a href="{REPO_URL}/blob/main/templates/tokens.css">tokens.css</a>.</p>
</section>
</main>
"""
    script = r"""
(function(){
  function fit(){
    document.querySelectorAll('.preview').forEach(function(p){
      var w=parseInt(p.getAttribute('data-w'),10), h=parseInt(p.getAttribute('data-h'),10);
      var avail=p.clientWidth; var s=Math.min(1, avail/w);
      var f=p.querySelector('iframe'); f.style.width=w+'px'; f.style.height=h+'px'; f.style.transform='scale('+s+')';
      p.style.height=Math.round(h*s)+'px';
    });
  }
  fit(); window.addEventListener('resize', fit);
})();
"""
    document("index.html", "No-slop design",
             "Visual AI slop is manageable. Three screens of a broker's assistant built with a small set of rules, each next to the generic version most tools would produce. Live pages, real-looking data, measured checks.",
             body, ["gallery.css"], script, "gallery")


# ---------------------------------------------------------------- stylesheets

SCREENS_CSS = r"""
/* Screens built with the rules. Tokens come from tokens.css; the operator shell adds its own
   derived variables below. Literal values only in the generic twin at the end of this file. */
:root {
  --t1: rgba(var(--ink-rgb), 0.88); --t2: rgba(var(--ink-rgb), 0.78); --t3: rgba(var(--ink-rgb), 0.67); --t4: rgba(var(--ink-rgb), 0.42);
  --line: rgba(var(--ink-rgb), 0.08); --line2: rgba(var(--ink-rgb), 0.06); --line3: rgba(var(--ink-rgb), 0.14); --line4: rgba(var(--ink-rgb), 0.22);
  --fill-0: rgba(var(--ink-rgb), 0.03); --fill-1: rgba(var(--ink-rgb), 0.04); --fill-2: rgba(var(--ink-rgb), 0.06); --fill-3: rgba(var(--ink-rgb), 0.10);
  --canvas: var(--paper); --sheet: #EEEFF2; --card: var(--surface);
  --act: #171A21; --act-h: #2A2E38; --on-act: #FFFFFF;
  --signal: #B4530A; --on-signal: #FFFFFF;
  --dk: #0B0D12; --dk-t1: #FFFFFF; --dk-t2: rgba(255,255,255,0.78); --dk-t3: rgba(255,255,255,0.62); --dk-line: rgba(255,255,255,0.14); --dk-fill: rgba(255,255,255,0.07);
  --dk-hot: #FFC857; --dk-link: #9AD9FF;
  --glow: radial-gradient(60% 150% at 92% 0%, rgba(16,148,133,0.42), transparent 60%), radial-gradient(55% 150% at 0% 100%, rgba(217,119,6,0.26), transparent 60%), radial-gradient(40% 120% at 100% 100%, rgba(56,132,255,0.10), transparent 60%);
  --ok: #1F6B45; --ok-bg: #E3F3EA; --ok-dot: #22A35A;
  --warn: #7A5600; --warn-bg: #FBF0D3; --warn-dot: #C9951E;
  --bad: #A12A22; --bad-bg: #FBE9E7; --bad-dot: #D15A4A;
  --info: #1E4A8F; --info-bg: #E6EEFC;
  --neu: #4A4F5A; --neu-bg: #F2F2F3;
  --mono: "DM Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
  --r: 6px; --r-chip: 5px; --r-field: 8px; --r-card: 10px; --r-sheet: 12px; --r-pill: 999px;
  --nav-w: 228px; --bar-h: 52px; --gap: 8px;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --sheet: #1F2530; --act: #E8ECF2; --act-h: #FFFFFF; --on-act: #0E1A3A; --signal: #F2A35B; --on-signal: #1A0F00;
    --ok: #5BC98A; --ok-bg: rgba(91,201,138,0.16); --warn: #E3A94F; --warn-bg: rgba(227,169,79,0.16); --bad: #F08A80; --bad-bg: rgba(240,138,128,0.16);
    --info: #8FB0FF; --info-bg: rgba(143,176,255,0.16); --neu: #C3CAD6; --neu-bg: rgba(195,202,214,0.14);
  }
}
:root[data-theme="dark"] {
  --sheet: #1F2530; --act: #E8ECF2; --act-h: #FFFFFF; --on-act: #0E1A3A; --signal: #F2A35B; --on-signal: #1A0F00;
  --ok: #5BC98A; --ok-bg: rgba(91,201,138,0.16); --warn: #E3A94F; --warn-bg: rgba(227,169,79,0.16); --bad: #F08A80; --bad-bg: rgba(240,138,128,0.16);
  --info: #8FB0FF; --info-bg: rgba(143,176,255,0.16); --neu: #C3CAD6; --neu-bg: rgba(195,202,214,0.14);
}

body.screen { background: var(--canvas); font-size: 13px; line-height: 18px; color: var(--t1); }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.frame { display: flex; flex-wrap: wrap; gap: var(--sp-3) var(--sp-4); align-items: center; padding: var(--sp-2) var(--sp-4); font-size: var(--fs-0); border-bottom: 1px solid var(--ink-12); background: var(--surface); }
.frame-home { font-weight: var(--w-strong); color: var(--ink); text-decoration: none; }
.frame-label { color: var(--ink-70); }
.frame-twin { margin-left: auto; }
.site-footer { padding: var(--sp-5) var(--sp-4); font-size: var(--fs-0); color: var(--ink-70); border-top: 1px solid var(--ink-12); margin-top: var(--sp-7); }
.site-footer p { margin: 0 0 var(--sp-1); }
.num { font-variant-numeric: tabular-nums; }
.mono { font-family: var(--mono); font-size: 12px; }
.t2 { color: var(--t2); } .t3 { color: var(--t3); font-size: 12px; }
.na { color: var(--t3); font-size: 12px; font-weight: 500; }
.sub { display: block; font-size: 12px; line-height: 16px; color: var(--t3); margin-top: 2px; }
.src { font-size: 12px; color: var(--t3); }
.grow { flex: 1; }
.ico { flex: none; vertical-align: -3px; }
.pad { padding: 0 16px 14px; }

/* ---- the shell: sidebar on the canvas, the sheet with its top bar ---- */
.app { display: grid; grid-template-columns: var(--nav-w) minmax(0, 1fr); align-items: start; min-height: 70vh; }
.side { position: sticky; top: 0; height: 100vh; display: flex; flex-direction: column; min-width: 0; padding: var(--gap) 0 0 var(--gap); }
.side-top { display: flex; flex-direction: column; gap: 10px; padding: 8px 8px 12px 6px; }
.ws { display: flex; align-items: center; gap: 10px; padding: 4px 4px 2px; }
.ws-mk { width: 26px; height: 26px; border-radius: var(--r); background: var(--act); position: relative; flex: none; }
.ws-mk::after { content: ""; position: absolute; width: 9px; height: 9px; left: 8.5px; top: 8.5px; background: var(--signal); transform: rotate(45deg); }
.ws-t { display: flex; flex-direction: column; min-width: 0; }
.ws-t b { font-weight: 500; color: var(--t1); }
.ws-t .who { font-size: 12px; color: var(--t3); }
.acct-b { display: flex; align-items: center; gap: 8px; height: 34px; padding: 0 8px 0 10px; border: 1px solid var(--line); border-radius: var(--r-field); background: var(--card); color: var(--t3); }
.acct-in { flex: 1; min-width: 0; border: 0; background: transparent; font: inherit; color: var(--t1); }
.acct-in::placeholder { color: var(--t3); }
.acct-in:focus { outline: none; }
.acct-b:focus-within { border-color: var(--t3); box-shadow: 0 0 0 3px var(--fill-2); }
kbd { font-family: var(--mono); font-size: 11px; color: var(--t3); border: 1px solid var(--line3); border-radius: 4px; padding: 0 5px; line-height: 16px; }
.nav { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 1px; padding: 0 8px 12px 6px; }
.nav-g { font-size: 12px; font-weight: 500; color: var(--t3); padding: 18px 8px 6px; }
.nav-g:first-child { padding-top: 4px; }
.nav-i { display: flex; align-items: center; gap: 10px; width: 100%; height: 30px; padding: 0 8px; border-radius: var(--r); color: var(--t2); text-decoration: none; font-size: 13px; line-height: 18px; }
.nav-i:hover { background: var(--fill-1); color: var(--t1); }
.nav-i.on { background: var(--fill-2); color: var(--t1); font-weight: 500; }
.nav-i .lb { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nav-i .nav-n { font-size: 11px; color: var(--t3); }
.nav-i.is-mock { color: var(--t3); cursor: default; }
.nav-foot { margin-top: auto; border-top: 1px solid var(--line); padding-top: 8px; display: flex; gap: 2px; }
.nav-foot .nav-i { justify-content: center; flex: 1; padding: 0 6px; }
.sheet { min-width: 0; margin: var(--gap) var(--gap) var(--gap) 0; }
.hd { position: sticky; top: 0; z-index: 50; }
.hd-in { height: var(--bar-h); display: flex; align-items: center; gap: 10px; padding: 0 12px 0 16px; background: var(--sheet); border: 1px solid var(--line); border-bottom: 0; border-radius: var(--r-sheet) var(--r-sheet) 0 0; }
.job { display: inline-flex; align-items: center; gap: 8px; height: 32px; padding: 0 12px 0 10px; min-width: 0; max-width: 62%; border: 1px solid var(--line); border-radius: var(--r-pill); background: var(--card); font-size: 13px; white-space: nowrap; color: var(--t3); }
.job .job-t { font-weight: 500; color: var(--t1); overflow: hidden; text-overflow: ellipsis; }
.job .job-s { color: var(--t3); overflow: hidden; text-overflow: ellipsis; }
.uav { width: 28px; height: 28px; border-radius: var(--r-pill); border: 0; background: var(--fill-3); color: var(--t1); font: inherit; font-size: 12px; font-weight: 500; display: inline-grid; place-items: center; cursor: pointer; }
.umenu { position: relative; }
.umenu .pop { position: absolute; right: 0; top: calc(100% + 6px); width: 280px; background: var(--card); border-radius: var(--r-card); box-shadow: var(--shadow-1); padding: 6px; z-index: 300; }
.pop-id { display: flex; align-items: center; gap: 10px; padding: 12px 16px; border-bottom: 1px solid var(--line2); margin-bottom: 4px; }
.pop-idt { display: flex; flex-direction: column; }
.pop-nm { font-weight: 500; color: var(--t1); }
.pop-org { font-size: 12px; color: var(--t3); }
.pi { display: flex; flex-direction: column; align-items: flex-start; gap: 1px; width: 100%; text-align: left; padding: 8px 10px; border: 0; border-radius: var(--r); background: none; color: var(--t1); font: inherit; font-size: 13px; font-weight: 500; cursor: pointer; }
.pi:hover { background: var(--fill-1); }
.pi .sub { margin-top: 0; }
.mn { min-width: 0; padding: 0 24px 32px; background: var(--sheet); border: 1px solid var(--line); border-top: 0; border-radius: 0 0 var(--r-sheet) var(--r-sheet); }

/* ---- buttons ---- */
.b { display: inline-flex; align-items: center; justify-content: center; gap: 6px; height: 28px; padding: 0 10px; border-radius: var(--r); font: inherit; font-size: 13px; font-weight: 500; white-space: nowrap; border: 1px solid transparent; background: transparent; color: var(--t1); cursor: pointer; text-decoration: none; }
.b-p { background: var(--act); color: var(--on-act); border-color: var(--act); }
.b-p:hover { background: var(--act-h); border-color: var(--act-h); }
.b-s { background: var(--fill-1); color: var(--t1); }
.b-s:hover { background: var(--fill-2); }
.b-t { color: var(--t2); padding: 0 8px; }
.b-t:hover { background: var(--fill-2); color: var(--t1); }
.b-l { color: var(--t1); padding: 0 6px; }
.b-l::after { content: "\2197"; font-size: 11px; margin-left: 2px; color: var(--t4); }
.b-l:hover { text-decoration: underline; }
.b-sm { height: 26px; padding: 0 9px; font-size: 12px; }
.b[aria-disabled="true"] { opacity: 0.6; cursor: not-allowed; }
.hd-in .b { height: 32px; padding: 0 14px 0 12px; }
.lk-b { background: none; border: 0; padding: 0; color: var(--t1); font: inherit; font-weight: 500; text-decoration: underline; text-underline-offset: 2px; cursor: pointer; }
.lkn { color: var(--t1); font-weight: 500; text-decoration: none; border-bottom: 1px solid var(--line3); }
.lkn:hover { border-bottom-color: var(--t1); }
.acts { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }

/* ---- page header, subnav, number strip ---- */
.ph { display: flex; align-items: center; gap: 24px; flex-wrap: wrap; padding: 28px 0 12px; }
.ph-t { display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap; }
.ph h1, .ex-t { font-size: 24px; line-height: 31px; font-weight: 500; letter-spacing: -0.0125em; }
.ph-s { font-size: 13px; color: var(--t3); }
.subnav { display: flex; align-items: center; gap: 2px; height: 44px; margin-bottom: 20px; border-bottom: 1px solid var(--line); }
.sn { display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 10px; border-radius: var(--r); font-size: 13px; font-weight: 500; color: var(--t3); text-decoration: none; }
.sn:hover { color: var(--t1); background: var(--fill-1); }
.sn.on { background: var(--fill-2); color: var(--t1); }
.sn .n { font-size: 12px; color: var(--t3); }
.sn.is-mock { cursor: default; }
.sx { margin-left: auto; display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--t3); }
.sx code { font-family: var(--mono); font-size: 12px; color: var(--t2); }
.strip { display: flex; flex-wrap: wrap; border-radius: var(--r-card); background-color: var(--dk); background-image: var(--glow); border: 1px solid var(--dk-line); color: var(--dk-t1); margin-bottom: 16px; }
.strip.in-card { margin: 0; border-radius: 0 0 var(--r-card) var(--r-card); border: 0; }
.st { flex: 1 1 0; min-width: 150px; display: flex; flex-direction: column; gap: 4px; padding: 14px 16px 13px; border-left: 1px solid var(--dk-line); text-align: left; color: var(--dk-t1); background: none; border-top: 0; border-right: 0; border-bottom: 0; font: inherit; }
.st:first-child { border-left: 0; }
.st.wide { flex: 1.3 1 0; }
.st .v { font-size: 24px; line-height: 30px; font-weight: 500; letter-spacing: -0.02em; color: var(--dk-t1); font-variant-numeric: tabular-nums; }
.st .v.hot { color: var(--dk-hot); }
.st .v.na { font-size: 15px; color: var(--dk-t3); font-weight: 500; }
.st .l { font-size: 13px; line-height: 1.35; color: var(--dk-t2); }
.st .l b { color: var(--dk-t1); font-weight: 500; }
.st .go { font-size: 12px; font-weight: 500; color: var(--dk-link); margin-top: auto; padding-top: 4px; }
.st .go::after { content: "\2192"; margin-left: 5px; }
button.st { cursor: pointer; border-radius: 0; }
button.st:hover { background: var(--dk-fill); }
button.st:focus-visible { outline: 2px solid var(--dk-t1); outline-offset: -4px; box-shadow: none; border-radius: var(--r); }

/* ---- filters, chips ---- */
.switcher { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; padding: 8px 0; font-size: 12px; margin-bottom: 4px; }
.switcher-label { color: var(--t3); margin-right: 8px; }
.filters { display: flex; flex-direction: column; gap: 6px; padding: 12px 16px; border-bottom: 1px solid var(--line2); }
.fgroup { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.fl { font-size: 12px; font-weight: 500; color: var(--t3); min-width: 128px; }
.fchip { display: inline-flex; align-items: center; gap: 7px; height: 28px; padding: 0 9px 0 11px; border: 1px solid var(--line3); border-radius: var(--r-pill); background: var(--card); font: inherit; font-size: 13px; font-weight: 500; color: var(--t2); white-space: nowrap; cursor: pointer; }
.fchip .n { min-width: 18px; height: 18px; padding: 0 5px; border-radius: var(--r-pill); background: var(--fill-2); color: var(--t2); font-size: 12px; display: inline-grid; place-items: center; line-height: 1; }
.fchip:hover { border-color: var(--t1); color: var(--t1); }
.fchip.on, .fchip[aria-pressed="true"] { background: var(--act); border-color: var(--act); color: var(--on-act); }
.fchip.on .n { background: rgba(255,255,255,0.18); color: var(--on-act); }
.ch { display: inline-flex; align-items: center; gap: 4px; height: 20px; padding: 0 7px; border-radius: var(--r-chip); font-size: 11px; line-height: 14px; font-weight: 500; white-space: nowrap; border: 1px solid transparent; }
.ch-ok { background: var(--ok-bg); color: var(--ok); }
.ch-warn { background: var(--warn-bg); color: var(--warn); }
.ch-bad { background: var(--bad-bg); color: var(--bad); }
.ch-info { background: var(--info-bg); color: var(--info); }
.ch-neu { background: var(--neu-bg); color: var(--neu); }
.ch-prop { background: var(--fill-2); color: var(--t1); border-color: var(--line3); }
.ch-dk { background: var(--dk-fill); color: var(--dk-t2); border-color: var(--dk-line); }
.ch-lvl { padding-left: 6px; }
.ch-lvl.l1 { background: var(--bad-bg); color: var(--bad); } .ch-lvl.l2 { background: var(--warn-bg); color: var(--warn); } .ch-lvl.l3 { background: var(--neu-bg); color: var(--neu); } .ch-lvl.l4 { background: transparent; color: var(--t3); border: 1px dashed var(--line4); }

/* ---- cards, tables ---- */
.pn { background: var(--card); border: 1px solid var(--line); border-radius: var(--r-card); margin-top: 16px; }
.pn:first-child { margin-top: 0; }
.pn-h { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 12px 16px; border-bottom: 1px solid var(--line2); }
.pn-h h2 { font-size: 15px; line-height: 20px; font-weight: 500; }
.pn-n { font-size: 12px; color: var(--t3); font-variant-numeric: tabular-nums; }
.pn-n.hot { display: inline-grid; place-items: center; min-width: 18px; height: 18px; padding: 0 5px; border-radius: var(--r-pill); background: var(--signal); color: var(--on-signal); font-size: 11px; font-weight: 500; }
.pn-x { margin-left: auto; display: flex; align-items: center; gap: 10px; }
.pn-b { padding: 14px 16px; }
.tbw { overflow: auto; }
.tb { width: 100%; border-collapse: collapse; font-size: 13px; }
.tb th { text-align: left; font-size: 12px; line-height: 16px; font-weight: 500; color: var(--t3); padding: 10px 12px; white-space: nowrap; border-bottom: 1px solid var(--line2); background: var(--card); }
.tb th.num { text-align: right; }
.tb td, .tb tbody th { padding: 10px 12px; border-top: 1px solid var(--line2); vertical-align: top; color: var(--t2); text-align: left; font-weight: 400; }
.tb tbody th { color: var(--t1); font-weight: 500; }
.tb tbody tr:first-child td, .tb tbody tr:first-child th { border-top: 0; }
.tb tbody tr:hover td, .tb tbody tr:hover th { background: var(--fill-0); }
.tb td.num { text-align: right; white-space: nowrap; }
.tb td.looking { min-width: 200px; }
.tb .col-prop { min-width: 300px; }
.tb tr.is-out { display: none; }
.tb-foot { display: flex; gap: 12px; padding: 10px 16px; font-size: 12px; color: var(--t3); border-top: 1px solid var(--line2); }
.lg { display: inline-grid; place-items: center; width: 16px; height: 16px; border-radius: 4px; color: #FFFFFF; font-size: 10px; font-weight: 500; margin-right: 6px; vertical-align: -3px; }
.lg-1 { background: #4F46A5; } .lg-2 { background: #0F6E78; } .lg-3 { background: #7C4A1E; } .lg-4 { background: #5B3F8C; } .lg-5 { background: #2F5D8A; } .lg-6 { background: #5E5E1C; }
.empty { padding: 14px 16px; font-size: 13px; color: var(--t2); border: 1px dashed var(--line3); border-radius: var(--r); display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin: 12px 16px; background: var(--card); }
.empty b { color: var(--t1); font-weight: 500; }
.empty.soft { border-style: solid; border-color: var(--line); background: var(--fill-0); flex-direction: column; align-items: flex-start; gap: 6px; padding: 16px; margin: 0; }
.empty.soft p { max-width: 72ch; }
.skeleton-rows { display: grid; gap: 12px; margin-top: 12px; }
.skeleton { height: 40px; }
.notice-bad, .notice-ok, .notice-neu { padding: 10px 14px; border-radius: var(--r); font-size: 13px; margin-bottom: 12px; }
.notice-bad { background: var(--bad-bg); color: var(--bad); }
.notice-bad b { color: var(--bad); }
.notice-ok { background: var(--ok-bg); color: var(--ok); }
.notice-ok b { color: var(--ok); }
.notice-neu { background: var(--neu-bg); color: var(--neu); }
.result { margin-top: 6px; }
#app .only-empty, #app .only-loading { display: none; }
#app .only-error:not(.only-normal) { display: none; }
#app[data-state="empty"] .only-normal { display: none; }
#app[data-state="empty"] .only-empty { display: block; }
#app[data-state="loading"] .only-normal { display: none; }
#app[data-state="loading"] .only-loading { display: block; }
#app[data-state="error"] .only-error:not(.only-normal) { display: block; }

/* ---- the assistant's proposal in the list ---- */
.prop { display: grid; gap: 4px; }
.prop-t { color: var(--t1); font-weight: 500; }
.prop-ev { color: var(--t2); }
.prop-w { font-size: 12px; color: var(--t2); }
.prop .acts { margin-top: 4px; }

/* ---- the explore box: a white card, the typed line in a reading column ---- */
.cmp { display: block; background: var(--card); border: 1px solid var(--line3); border-radius: var(--r-sheet); padding: 16px 18px; }
.cmp:focus-within { border-color: var(--line4); }
.cmp textarea { display: block; width: 100%; margin: 0; padding: 0; padding-right: max(0px, calc(100% - 680px)); border: 0; background: transparent; font: inherit; font-size: 15px; line-height: 24px; color: var(--t1); resize: vertical; min-height: 48px; }
.cmp textarea::placeholder { color: var(--t3); }
.cmp textarea:focus { outline: none; }
.cmp-b { display: flex; align-items: center; gap: 4px; margin-top: 12px; }
.cmp-ctx-b { display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 10px; border: 0; border-radius: var(--r-chip); background: var(--fill-1); color: var(--t2); font: inherit; font-size: 12px; font-weight: 500; cursor: pointer; }
.cmp-ctx-b:hover { background: var(--fill-2); color: var(--t1); }
.cmp-ic { width: 28px; height: 28px; border: 0; border-radius: var(--r); background: transparent; color: var(--t2); display: inline-grid; place-items: center; cursor: pointer; }
.cmp-ic:hover { background: var(--fill-2); color: var(--t1); }
.cmp-env { width: 28px; height: 28px; border: 0; border-radius: var(--r); background: var(--act); color: var(--on-act); display: inline-grid; place-items: center; cursor: pointer; }
.cmp-env:hover { background: var(--act-h); }
.ex-sgt { margin: 24px 0 6px; font-size: 12px; line-height: 16px; font-weight: 500; color: var(--t3); }
.sg-l { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
.sg { display: flex; align-items: center; gap: 10px; width: 100%; height: 34px; padding: 0 12px 0 8px; border: 0; border-radius: var(--r-field); background: transparent; color: var(--t1); font: inherit; font-size: 13px; text-align: left; text-decoration: none; cursor: pointer; }
.sg:hover { background: var(--fill-1); }
.sg .sg-t { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sg .sg-k { color: var(--t3); flex: none; padding-left: 12px; }
.ex-ans { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--line2); max-width: 680px; }
.ex-ans:focus { outline: none; }
.ex-q { font-size: 13px; color: var(--t1); margin-bottom: 10px; }
.ex-v { font-size: 15px; line-height: 24px; color: var(--t1); margin-bottom: 10px; }
.ex-f { margin: 0 0 10px; padding-left: 20px; font-size: 15px; line-height: 24px; color: var(--t1); }
.ex-f li { margin-bottom: 4px; }
.ref { font-size: 12px; color: var(--t3); text-decoration: none; margin-left: 2px; }
.ref:hover { color: var(--t1); }
.ex-o { font-size: 13px; color: var(--t2); margin-bottom: 8px; }
.ex-o b { color: var(--t1); font-weight: 500; }
.ex-conf { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; font-size: 12px; }
.ex-src { list-style: none; margin: 0 0 12px; padding: 8px 0 0; border-top: 1px solid var(--line2); font-size: 12px; line-height: 16px; color: var(--t3); }
.ex-src li { margin-top: 2px; }
.ex { max-width: 760px; margin: 0 auto; padding: 12vh 0 32px; }
.ex .ex-t { font-size: 28px; line-height: 36px; letter-spacing: -0.015em; margin-bottom: 20px; }
.ex .cmp textarea { min-height: 72px; }
.ex .ex-sg { margin-top: 32px; }
.ex .ex-sg h2 { margin-top: 0; }

/* ---- the buyer record: context strip, identity banner, tabs, blocks ---- */
.ctx { position: sticky; top: var(--bar-h); z-index: 40; display: flex; align-items: center; gap: 16px; height: 44px; margin: 0 -24px; padding: 0 24px; background: var(--sheet); border-bottom: 1px solid var(--line); overflow: hidden; }
.ctx-tr { display: flex; align-items: center; gap: 4px; flex: none; }
.ctx-all { display: inline-flex; align-items: center; gap: 6px; height: 28px; padding: 0 6px; margin-left: -6px; border-radius: var(--r); color: var(--t2); text-decoration: none; font-size: 13px; }
.ctx-all:hover { background: var(--fill-2); color: var(--t1); }
.ctx .sep { color: var(--t3); display: inline-flex; }
.ctx .cn { font-weight: 500; color: var(--t1); white-space: nowrap; }
.ctx .cf { display: flex; align-items: center; font-size: 13px; color: var(--t3); white-space: nowrap; overflow: hidden; height: 20px; }
.ctx .kf { display: inline-flex; align-items: baseline; gap: 5px; padding: 0 8px; border-left: 1px solid var(--line3); }
.ctx .kf:first-child { border-left: 0; }
.ctx .kf b { color: var(--t1); font-weight: 500; }
.ctx .kf i { font-style: normal; font-size: 12px; color: var(--t3); }
.ctx .ca { margin-left: auto; display: flex; align-items: center; gap: 8px; flex: none; }
.seg-g { display: inline-flex; }
.seg { display: inline-flex; align-items: center; height: 28px; padding: 0 11px; border: 1px solid var(--line3); background: var(--card); font-size: 13px; font-weight: 500; color: var(--t2); text-decoration: none; }
.seg:first-child { border-radius: var(--r) 0 0 var(--r); }
.seg:last-child { border-radius: 0 var(--r) var(--r) 0; margin-left: -1px; }
.seg.on { background: var(--act); border-color: var(--act); color: var(--on-act); }
.fid { margin: 20px 0 12px; padding: 18px 20px 16px; border-radius: var(--r-card); background-color: var(--dk); background-image: var(--glow); border: 1px solid var(--dk-line); color: var(--dk-t1); }
.fid h1 { font-size: 24px; line-height: 31px; font-weight: 500; letter-spacing: -0.0125em; color: var(--dk-t1); }
.fid .chs { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.fid .facts { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--dk-line); }
.fid .fact { display: flex; flex-direction: column; gap: 4px; padding: 0 16px; border-left: 1px solid var(--dk-line); min-width: 0; }
.fid .fact:first-child { border-left: 0; padding-left: 0; }
.fid .l { font-size: 12px; line-height: 16px; font-weight: 500; color: var(--dk-t3); }
.fid .v { font-size: 24px; line-height: 30px; font-weight: 500; color: var(--dk-t1); font-variant-numeric: tabular-nums; }
.fid .v.hot { color: var(--dk-hot); }
.fid .r { font-size: 12px; line-height: 16px; color: var(--dk-t3); }
.ftabs { display: flex; align-items: center; gap: 2px; position: sticky; top: calc(var(--bar-h) + 44px); z-index: 30; margin: 0 -24px 16px; padding: 0 24px; background: var(--sheet); border-bottom: 1px solid var(--line); }
.ft { display: inline-flex; align-items: center; gap: 6px; height: 44px; padding: 0 10px; border: 0; border-bottom: 2px solid transparent; margin-bottom: -1px; background: none; font: inherit; font-size: 13px; font-weight: 500; color: var(--t3); cursor: pointer; }
.ft:hover { color: var(--t1); }
.ft.on { color: var(--t1); border-bottom-color: var(--act); }
.ft .n { font-size: 12px; color: var(--t3); }
.kpanel { display: grid; gap: 16px; }
.blk { background: var(--card); border: 1px solid var(--line); border-radius: var(--r-card); padding: 18px 20px 20px; }
.blk-h { display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px 12px; padding-bottom: 12px; margin-bottom: 14px; border-bottom: 1px solid var(--line2); }
.blk-h h2 { font-size: 15px; line-height: 20px; font-weight: 500; }
.blk-h .src { margin-left: auto; }
.gr2 { display: grid; grid-template-columns: minmax(0, 1.55fr) minmax(300px, 1fr); gap: 16px; }
.hnc-f { display: flex; flex-wrap: wrap; gap: 12px 0; margin-bottom: 16px; }
.pf-i { display: flex; flex-direction: column; justify-content: center; padding: 2px 16px; border-left: 1px solid var(--line3); min-width: 0; }
.pf-i:first-child { border-left: 0; padding-left: 0; }
.pf-i b { font-size: 24px; line-height: 30px; font-weight: 500; color: var(--t1); white-space: nowrap; }
.pf-i b.na { font-size: 15px; color: var(--t3); }
.pf-i span { font-size: 12px; line-height: 16px; color: var(--t3); margin-top: 2px; }
.prop-card { border: 1px solid var(--line3); border-radius: var(--r-card); padding: 16px 18px; background: var(--fill-0); }
.prop-card h3 { font-size: 15px; line-height: 20px; font-weight: 500; margin: 8px 0 12px; }
.prop-card .t3 { margin-top: 10px; margin-bottom: 4px; }
.ev, .writes { margin: 0; padding-left: 18px; font-size: 13px; line-height: 18px; color: var(--t1); }
.ev li, .writes li { margin-bottom: 4px; }
.writes b { font-weight: 500; margin-right: 4px; }
.writes .editing { outline: 1px dashed var(--t3); padding: 2px 4px; border-radius: 4px; }
.prop-card .acts { margin-top: 14px; }
.never { margin-top: 12px; font-size: 12px; line-height: 16px; color: var(--t3); }
.never b { color: var(--t2); font-weight: 500; }
.exec p { font-size: 15px; line-height: 24px; color: var(--t1); max-width: 680px; margin-bottom: 10px; }
.exec .exec-l { font-size: 13px; line-height: 18px; font-weight: 500; color: var(--t3); margin-bottom: 2px; }
.signals { list-style: none; margin: 0; padding: 0; }
.signals li { display: flex; flex-direction: column; gap: 2px; padding: 9px 0; border-top: 1px solid var(--line2); }
.signals li:first-child { border-top: 0; padding-top: 0; }
.signals b { font-weight: 500; color: var(--t1); }
.signals span { font-size: 12px; color: var(--t3); }
.cov { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--line2); display: grid; gap: 6px; }
.pb { display: inline-flex; align-items: center; gap: 8px; }
.pb .tr { width: 120px; height: 6px; border-radius: var(--r-pill); background: var(--fill-2); overflow: hidden; display: flex; }
.pb .tr i { display: block; height: 100%; }
.pb .tr .ok { background: var(--ok-dot); }
.pb .pl { font-size: 13px; color: var(--t2); }
.pb .pl b { color: var(--t1); font-weight: 500; }

/* ---- agenda rows (visits, tasks, agenda) and the action list (priorities) ---- */
.ag { list-style: none; margin: 0; padding: 0; }
.ag > li { display: grid; grid-template-columns: 78px minmax(0, 1fr) auto; gap: 4px 12px; align-items: start; padding: 12px 16px; border-top: 1px solid var(--line2); }
.ag > li:first-child { border-top: 0; }
.ag > li:hover { background: var(--fill-0); }
.blk .ag > li { padding-left: 0; padding-right: 0; }
.ag .wh { font-size: 13px; font-weight: 500; color: var(--t1); line-height: 18px; }
.ag .wh small { display: block; font-size: 12px; color: var(--t3); font-weight: 500; }
.ag .wh.late, .ag .wh.late small { color: var(--bad); }
.ag .tt { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; font-weight: 500; color: var(--t1); }
.ag .ds { display: block; font-size: 12px; line-height: 16px; color: var(--t2); margin-top: 2px; }
.ag .acts { justify-content: flex-end; }
.ag > li.is-done .tt, .ag > li.is-done .wh { color: var(--t3); text-decoration: line-through; }
.ag > li.is-done .ds { color: var(--t4); }
.ag-i.done .tt { color: var(--t2); }
.al { list-style: none; margin: 0; padding: 0; }
.al-r { display: grid; grid-template-columns: 136px minmax(170px, 1fr) minmax(220px, 1.4fr) auto; gap: 4px 16px; align-items: center; padding: 11px 16px; border-top: 1px solid var(--line2); }
.al-r:first-child { border-top: 0; }
.al-r:hover { background: var(--fill-0); }
.al-m { display: flex; flex-direction: column; gap: 3px; align-items: flex-start; }
.al-m .dl { font-size: 12px; color: var(--t3); }
.al-b { min-width: 0; }
.al-b b { display: block; font-weight: 500; color: var(--t1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.al-b .ac { display: block; font-size: 12px; color: var(--t3); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.al-w .rasc { display: block; color: var(--t2); }
.al-w .src { display: block; margin-top: 2px; }
.al-a { display: flex; align-items: center; gap: 6px; justify-content: flex-end; white-space: nowrap; }
.al-st { font-size: 12px; color: var(--ok); font-weight: 500; }
.al-r.is-done .al-b b, .al-r.is-done .al-w .rasc { color: var(--t3); text-decoration: line-through; }
.al-foot { padding: 10px 16px; border-top: 1px solid var(--line2); }

/* ---- the receipt ---- */
.toast { position: fixed; left: 50%; bottom: 22px; z-index: 70; transform: translate(-50%, 14px); opacity: 0; display: flex; align-items: center; gap: 11px; max-width: min(640px, 92vw); padding: 10px 12px 10px 13px; border-radius: var(--r); background: var(--act); color: var(--on-act); transition: opacity 0.18s, transform 0.18s; pointer-events: none; }
.toast.on { opacity: 1; transform: translate(-50%, 0); pointer-events: auto; }
.toast .tk { display: inline-grid; place-items: center; width: 20px; height: 20px; border-radius: var(--r-pill); background: var(--ok-dot); color: #FFFFFF; font-size: 12px; flex: none; }
.toast .tx { display: flex; flex-direction: column; min-width: 0; }
.toast .tx b { font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.toast .tx i { font-style: normal; font-size: 12px; opacity: 0.8; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.toast .tu, .toast .tx-x { background: none; border: 0; color: inherit; font: inherit; font-weight: 500; cursor: pointer; min-height: 28px; padding: 4px 6px; border-radius: var(--r); }
.toast .tu { margin-left: auto; text-decoration: underline; text-underline-offset: 2px; }
.toast .tx-x { font-size: 15px; line-height: 1; opacity: 0.8; }

@media (max-width: 900px) {
  .app { grid-template-columns: 1fr; }
  .side { position: static; height: auto; padding: var(--gap) var(--gap) 0; }
  .nav { flex-direction: row; flex-wrap: nowrap; overflow-x: auto; padding: 0 0 8px; }
  .nav-g { display: none; }
  .nav-i { width: auto; flex: none; }
  .nav-foot { margin-top: 0; border-top: 0; padding-top: 0; }
  .sheet { margin: 0 var(--gap) var(--gap); }
  .mn { padding: 0 16px 24px; }
  .ctx, .ftabs { margin-left: -16px; margin-right: -16px; padding-left: 16px; padding-right: 16px; }
  .ctx .cf { display: none; }
  .job { max-width: 100%; }
  .hd-in .b { padding: 0 10px; }
  .fid .facts { grid-template-columns: 1fr 1fr; gap: 12px 0; }
  .fid .fact:nth-child(3) { border-left: 0; padding-left: 0; }
  .gr2 { grid-template-columns: 1fr; }
  .al-r { grid-template-columns: 1fr; gap: 6px; }
  .al-a { justify-content: flex-start; }
  .ag > li { grid-template-columns: 64px minmax(0, 1fr); }
  .ag .acts { grid-column: 1 / -1; justify-content: flex-start; }
  .ex { padding-top: 24px; }
  .fl { min-width: 100%; }
  .subnav { height: auto; flex-wrap: wrap; padding: 6px 0; }
  .sx { margin-left: 0; width: 100%; }
  .st { min-width: 50%; }
}
@media (prefers-reduced-motion: reduce) { .toast { transition: none; } }

/* ---------------------------------------------------------------- The generic twin.
   Literal values on purpose: this is what a typical generated page looks like. */
body.generic { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; background: #F9FAFB; color: #111827; }
.g-hero { background: linear-gradient(120deg, #6D5DFC 0%, #2E8CF6 100%); color: #FFFFFF; text-align: center; padding: 72px 24px; position: relative; overflow: hidden; }
.g-hero::before, .g-hero::after { content: ""; position: absolute; width: 360px; height: 360px; border-radius: 50%; background: rgba(255,255,255,0.18); filter: blur(60px); }
.g-hero::before { top: -120px; left: -80px; }
.g-hero::after { bottom: -140px; right: -60px; }
.g-hero-small { padding: 48px 24px; }
.g-hero-inner { position: relative; max-width: 760px; margin: 0 auto; }
.g-hero h1 { font-size: 44px; font-weight: 800; margin: 16px 0 12px; letter-spacing: -0.02em; }
.g-hero-small h1 { font-size: 34px; }
.g-lead { font-size: 18px; opacity: 0.9; margin: 0 0 24px; }
.g-pill { display: inline-block; padding: 6px 14px; border-radius: 999px; background: rgba(255,255,255,0.22); font-size: 13px; font-weight: 600; }
.g-hero-actions { display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }
.g-btn { border: 0; border-radius: 12px; padding: 12px 22px; font: inherit; font-weight: 600; cursor: pointer; }
.g-btn-light { background: #FFFFFF; color: #6D5DFC; }
.g-btn-ghost { background: transparent; color: #FFFFFF; border: 1px solid rgba(255,255,255,0.6); }
.g-btn-primary { background: linear-gradient(120deg, #7C3AED, #2563EB); color: #FFFFFF; box-shadow: 0 10px 20px rgba(124,58,237,0.3); }
.g-btn-secondary { background: #EEF2FF; color: #4338CA; }
.g-btn-danger { background: #FEE2E2; color: #DC2626; }
.g-main { max-width: 1080px; margin: 0 auto; padding: 32px 24px; }
.g-main-narrow { max-width: 640px; }
.g-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: -56px; position: relative; }
.g-stat { background: #FFFFFF; border-radius: 20px; padding: 24px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
.g-stat-value { font-size: 36px; font-weight: 800; margin: 0; background: linear-gradient(120deg, #7C3AED, #2563EB); -webkit-background-clip: text; background-clip: text; color: transparent; }
.g-stat-label { margin: 6px 0 0; color: #9CA3AF; font-size: 14px; }
.g-features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 40px; }
.g-feature { background: #FFFFFF; border-radius: 20px; padding: 28px 24px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); }
.g-icon { font-size: 36px; margin-bottom: 12px; }
.g-feature h3, .g-card h3 { margin: 0 0 8px; font-size: 18px; }
.g-feature p { margin: 0; color: #9CA3AF; font-size: 15px; }
.g-list { margin-top: 48px; text-align: center; }
.g-list h2 { font-size: 28px; margin: 0 0 20px; }
.g-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
.g-grid-narrow { grid-template-columns: repeat(3, 1fr); }
.g-card { background: #FFFFFF; border-radius: 20px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); text-align: left; display: flex; flex-direction: column; min-height: 220px; }
.g-card-top { margin-bottom: 10px; display: flex; gap: 6px; flex-wrap: wrap; }
.g-badge { display: inline-block; padding: 4px 10px; border-radius: 999px; background: #EDE9FE; color: #7C3AED; font-size: 12px; font-weight: 700; }
.g-badge-hot { background: #FEE2E2; color: #DC2626; }
.g-sub { color: #9CA3AF; margin: 0 0 10px; font-size: 14px; }
.g-text { color: #6B7280; margin: 0 0 16px; font-size: 15px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
.g-actions { display: flex; gap: 10px; margin-top: auto; flex-wrap: wrap; justify-content: center; }
.g-insight { display: grid; grid-template-columns: 200px 1fr; gap: 24px; align-items: center; background: #FFFFFF; border-radius: 24px; padding: 28px; box-shadow: 0 10px 30px rgba(0,0,0,0.08); margin-top: 24px; }
.g-score { text-align: center; }
.g-score-value { font-size: 56px; font-weight: 800; margin: 0; background: linear-gradient(120deg, #7C3AED, #2563EB); -webkit-background-clip: text; background-clip: text; color: transparent; }
.g-score-label { color: #9CA3AF; margin: 0; }
.g-insight-text h2 { margin: 0 0 8px; font-size: 22px; }
.g-insight-text p { color: #6B7280; margin: 0 0 16px; }
.g-center { text-align: center; grid-template-columns: 1fr; justify-items: center; }
body.generic .site-footer { color: #6B7280; }
@media (max-width: 760px) {
  .g-stats, .g-features, .g-grid-narrow { grid-template-columns: 1fr; }
  .g-insight { grid-template-columns: 1fr; }
  .g-hero h1 { font-size: 32px; }
  .g-stats { margin-top: -32px; }
}
"""

GALLERY_CSS = r"""
/* The gallery page. Tokens from tokens.css. */
.g-head { padding: var(--sp-7) var(--sp-4) var(--sp-6); border-bottom: 1px solid var(--ink-12); background: var(--surface); }
.g-head-inner { max-width: 880px; margin: 0 auto; }
.site-name { font-size: var(--fs-0); font-weight: var(--w-strong); color: var(--ink-70); margin-bottom: var(--sp-3); }
.g-head h1 { font-size: clamp(28px, 5vw, 44px); line-height: 1.1; max-width: 18ch; margin-bottom: var(--sp-4); }
.lede { font-size: var(--fs-2); max-width: 66ch; margin-bottom: var(--sp-4); }
.lede-2 { max-width: 66ch; color: var(--ink-70); margin-bottom: var(--sp-5); }
.actions { display: flex; flex-wrap: wrap; gap: var(--sp-3); margin-bottom: var(--sp-4); }
.g-body { max-width: 1180px; margin: 0 auto; padding: var(--sp-6) var(--sp-4) 0; }
.pair { padding: var(--sp-6) 0; border-bottom: 1px solid var(--ink-12); }
.pair-head { max-width: 760px; margin-bottom: var(--sp-5); }
.pair-head h2 { font-size: var(--fs-3); margin-bottom: var(--sp-2); }
.job { color: var(--ink-70); }
.pair-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--sp-5); align-items: start; }
.shot { margin: 0; }
.preview { position: relative; overflow: hidden; border: 1px solid var(--ink-12); border-radius: var(--radius-2); background: var(--surface); height: 300px; }
.preview iframe { position: absolute; top: 0; left: 0; width: 1280px; height: 860px; border: 0; transform: scale(0.3); transform-origin: 0 0; pointer-events: none; background: var(--paper); }
.shot figcaption { margin-top: var(--sp-2); font-size: var(--fs-0); }
.notice-list { margin-top: var(--sp-5); max-width: 880px; }
.notice-list h3 { margin-bottom: var(--sp-3); }
.notice-list ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.notice-list li { display: grid; grid-template-columns: 64px 1fr; gap: var(--sp-3); align-items: start; }
.tell { font-size: var(--fs-0); font-weight: var(--w-strong); color: var(--accent); background: var(--accent-soft); padding: 2px var(--sp-2); border-radius: var(--radius-1); text-align: center; }
.how { padding: var(--sp-6) 0; max-width: 880px; }
.how h2 { font-size: var(--fs-3); margin-bottom: var(--sp-4); }
.how-list { padding-left: var(--sp-5); margin: 0 0 var(--sp-4); display: grid; gap: var(--sp-2); }
.site-footer { padding: var(--sp-5) var(--sp-4); font-size: var(--fs-0); color: var(--ink-70); border-top: 1px solid var(--ink-12); margin-top: var(--sp-6); }
.site-footer p { margin: 0 0 var(--sp-1); }
@media (max-width: 760px) {
  .pair-grid { grid-template-columns: 1fr; }
  .notice-list li { grid-template-columns: 52px 1fr; }
}
"""

OG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="No-slop design">
<rect width="1200" height="630" fill="#F5F6F8"/>
<rect x="0" y="0" width="1200" height="12" fill="#2446A6"/>
<text x="80" y="250" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="72" font-weight="700" fill="#1C2230">No-slop design</text>
<text x="80" y="330" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="34" fill="#1C2230" fill-opacity="0.72">Visual AI slop is manageable.</text>
<text x="80" y="390" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="26" fill="#1C2230" fill-opacity="0.72">A broker's screens built with the rules, next to the generic version.</text>
<text x="80" y="560" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#1C2230" fill-opacity="0.56">benyoumen.github.io/no-slop-design</text>
</svg>
"""


def main():
    os.makedirs(SITE, exist_ok=True)
    for old in OLD_PAGES:
        p = os.path.join(SITE, old)
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(TOKENS, os.path.join(SITE, "tokens.css"))
    with open(os.path.join(SITE, "screens.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(SCREENS_CSS.lstrip())
    with open(os.path.join(SITE, "gallery.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(GALLERY_CSS.lstrip())
    with open(os.path.join(SITE, "og.svg"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(OG_SVG)
    portfolio_explore()
    portfolio_explore_generic()
    buyer_record()
    buyer_record_generic()
    home()
    home_generic()
    gallery()
    print("built", sorted(os.listdir(SITE)))


if __name__ == "__main__":
    main()
