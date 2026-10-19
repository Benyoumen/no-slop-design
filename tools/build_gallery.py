#!/usr/bin/env python3
"""Build the no-slop-design gallery (site/) from the Acme data snapshot and the token file.

Standard library only. The HTML is never edited by hand: change this file, run it again.

    python tools/build_gallery.py

Inputs:  examples/acme-sales-assistant/data-snapshot.json, templates/tokens.css
Outputs: site/index.html, six screen pages, site/tokens.css, site/screens.css, site/gallery.css
"""
import datetime as dt
import html
import json
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "examples", "acme-sales-assistant", "data-snapshot.json")
TOKENS = os.path.join(ROOT, "templates", "tokens.css")
SITE = os.path.join(ROOT, "site")
BASE_URL = "https://benyoumen.github.io/no-slop-design/"
REPO_URL = "https://github.com/Benyoumen/no-slop-design"
FOOTER = "Fictional company, people and numbers."

with open(DATA, encoding="utf-8") as fh:
    D = json.load(fh)

SNAPSHOT = dt.date.fromisoformat(D["snapshot_date"])
REPS = {r["id"]: r for r in D["reps"]}
ME = REPS[D["current_rep"]]


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def money(amount, currency="USD"):
    if amount is None:
        return '<span class="muted">no data</span>'
    sym = "$" if currency == "USD" else currency + " "
    return f'<span class="num">{sym}{amount:,.0f}</span>'


def pct(x):
    return '<span class="muted">no data</span>' if x is None else f'<span class="num">{round(x * 100)}%</span>'


def is_today(m):
    return len(m["time"]) == 5  # "HH:MM"


def long_date(d):
    return d.strftime("%A, %d %B %Y").replace(" 0", " ")


def short_date(s):
    d = dt.date.fromisoformat(s)
    return d.strftime("%a %d %b").replace(" 0", " ")


TODAY = [m for m in D["meetings"] if is_today(m)]
EARLIER = [m for m in D["meetings"] if not is_today(m)]
PROPOSALS_WAITING = [m for m in TODAY if m["proposal"] and not m["updated"]]
STALE = [m for m in D["meetings"] if m["last_activity_days_before"] >= 14 and m["stage"] not in ("Closed won", "Closed lost")]
LAST_RUN = dt.datetime.fromisoformat(D["last_agent_run"]).strftime("%H:%M")


def stage_cell(stage):
    return '<span class="muted">no data</span>' if stage is None else e(stage)


def proposal_text(p):
    if p["kind"] == "stage":
        return f'Stage: {e(p["from"])} to <strong>{e(p["to"])}</strong>'
    if p["kind"] == "next_step":
        return f'Next step: <strong>{e(p["to"])}</strong>'
    return f'Note: <strong>{e(p["to"])}</strong>'


# ---------------------------------------------------------------- shell


def shell(path, title, description, body, extra_css=(), script="", kind="screen", twin=None, label=None):
    """kind: 'screen' (built with the rules), 'generic' (the twin) or 'gallery'."""
    css = ['<link rel="stylesheet" href="tokens.css">'] + [f'<link rel="stylesheet" href="{c}">' for c in extra_css]
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&display=swap" rel="stylesheet">'
    )
    frame = ""
    if kind != "gallery":
        side = "Built with the rules" if kind == "screen" else "The generic version"
        other = "See the generic version" if kind == "screen" else "See it built with the rules"
        frame = (
            '<div class="frame" role="region" aria-label="Gallery frame">'
            f'<a class="frame-home" href="index.html">No-slop design</a>'
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


# ---------------------------------------------------------------- daily list (rules)


def daily_list():
    rows = []
    for m in TODAY:
        p = m["proposal"]
        mid = e(m["id"])
        if p and not m["updated"]:
            quote = p["evidence"][0]
            prop = (
                f'<div class="proposal" id="prop-{mid}">'
                f'<p class="proposal-tag">Agent proposes</p>'
                f'<p class="proposal-value">{proposal_text(p)}</p>'
                f'<p class="proposal-evidence">"{e(quote["quote"])}" <span class="muted">at {e(quote["t"])} in the notes</span></p>'
                + (f'<p class="proposal-draft"><a href="proposal-review.html">Follow-up email draft ready, not sent</a></p>' if p["email_draft"] else "")
                + "</div>"
                f'<div class="result" id="result-{mid}" hidden></div>'
            )
            actions = (
                f'<button type="button" class="btn btn-primary" data-approve="{mid}">Save to CRM</button> '
                f'<button type="button" class="btn btn-quiet" data-later="{mid}">Not now</button> '
                f'<a class="row-link" href="proposal-review.html">Open in CRM</a>'
            )
        elif m["updated"]:
            prop = '<p class="muted">Updated after the meeting</p>'
            actions = '<a class="row-link" href="proposal-review.html">Open in CRM</a>'
        else:
            prop = '<p class="muted">Nothing to propose: no notes for this meeting yet</p>'
            actions = '<a class="row-link" href="proposal-review.html">Open in CRM</a>'
        rows.append(
            f'<tr id="row-{mid}" data-pending="{"1" if (p and not m["updated"]) else "0"}">'
            f'<td class="num">{e(m["time"])}</td>'
            f'<td><strong>{e(m["customer"])}</strong><br><span class="muted">{e(m["contact"])}</span></td>'
            f'<td>{stage_cell(m["stage"])}</td>'
            f'<td>{money(m["amount"], m["currency"])}</td>'
            f'<td class="col-proposal">{prop}</td>'
            f'<td class="col-actions">{actions}</td>'
            "</tr>"
        )
    earlier_rows = []
    for m in EARLIER:
        if m["updated"]:
            continue
        earlier_rows.append(
            f'<tr><td class="num">{e(short_date(m["time"]))}</td>'
            f'<td><strong>{e(m["customer"])}</strong><br><span class="muted">{e(m["contact"])}</span></td>'
            f'<td>{stage_cell(m["stage"])}</td><td>{money(m["amount"], m["currency"])}</td>'
            f'<td><span class="muted">No notes for this meeting; nothing to propose</span></td>'
            f'<td class="col-actions"><a class="row-link" href="proposal-review.html">Open in CRM</a></td></tr>'
        )
    done_today = sum(1 for m in TODAY if m["updated"])
    body = f"""
<header class="app-header">
  <div class="app-id"><span class="app-name">Acme Field Sales Assistant</span><span class="app-user">{e(ME["name"])}</span></div>
  <p class="app-date">{e(long_date(SNAPSHOT))}</p>
  <p class="presence" id="presence">Agent ran at {LAST_RUN}: <span class="num" id="presence-count">{len(PROPOSALS_WAITING)}</span> proposals from today's notes.</p>
</header>
<div class="switcher" role="group" aria-label="Mockup state">
  <span class="switcher-label">Mockup state</span>
  <button type="button" class="btn btn-quiet is-on" data-state="normal" aria-pressed="true">Normal</button>
  <button type="button" class="btn btn-quiet" data-state="empty" aria-pressed="false">Empty</button>
  <button type="button" class="btn btn-quiet" data-state="loading" aria-pressed="false">Loading</button>
  <button type="button" class="btn btn-quiet" data-state="error" aria-pressed="false">Error</button>
</div>
<main class="app" id="app" data-state="normal">
  <section class="kpis" aria-label="Today in numbers">
    <div class="kpi"><p class="label">Meetings today</p><p class="value" id="kpi-meetings">{len(TODAY)}</p><p class="reading">{done_today} already updated in the CRM</p></div>
    <div class="kpi"><p class="label">Proposals waiting</p><p class="value" id="kpi-waiting">{len(PROPOSALS_WAITING)}</p><p class="reading">from today's notes, run of {LAST_RUN}</p></div>
    <div class="kpi"><p class="label">Updated within 24 hours</p><p class="value">{round(ME["updated_within_24h"] * 100)}%</p><p class="reading">your last 4 weeks, team target 90%</p></div>
  </section>

  <div class="only-error notice notice-danger" role="alert">
    <strong>CRM sync failed at {LAST_RUN}.</strong> The list shows yesterday's data. The agent will retry at 07:35, or
    <button type="button" class="link" data-state="normal">retry now</button>.
  </div>

  <section class="block only-normal only-error" aria-labelledby="h-today">
    <h2 id="h-today">Today</h2>
    <table class="table list">
      <thead><tr><th scope="col">Time</th><th scope="col">Customer</th><th scope="col">Stage, recorded</th><th scope="col">Amount, recorded</th><th scope="col">Agent proposes</th><th scope="col"><span class="visually-hidden">Actions</span></th></tr></thead>
      <tbody id="today-rows">{''.join(rows)}</tbody>
    </table>
  </section>

  <section class="block only-normal only-error" aria-labelledby="h-earlier">
    <h2 id="h-earlier">Earlier this week, not yet updated</h2>
    <table class="table list">
      <thead><tr><th scope="col">Date</th><th scope="col">Customer</th><th scope="col">Stage, recorded</th><th scope="col">Amount, recorded</th><th scope="col">Agent proposes</th><th scope="col"><span class="visually-hidden">Actions</span></th></tr></thead>
      <tbody>{''.join(earlier_rows)}</tbody>
    </table>
  </section>

  <section class="only-empty empty" aria-label="No meetings">
    <h2>No meetings today</h2>
    <p>Your next meeting is in your calendar. The agent reads the notes of each meeting and runs again tomorrow at 07:05.</p>
    <p><a class="btn" href="weekly-summary.html">Open this week</a></p>
  </section>

  <section class="only-loading" aria-label="Loading" aria-busy="true">
    <p class="muted">Syncing with the CRM, started {LAST_RUN}.</p>
    <div class="skeleton-rows"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div>
  </section>
</main>
"""
    script = r"""
(function(){
  var app=document.getElementById('app');
  document.querySelectorAll('[data-state]').forEach(function(b){
    b.addEventListener('click',function(){
      var s=b.getAttribute('data-state'); app.setAttribute('data-state',s);
      document.querySelectorAll('.switcher [data-state]').forEach(function(x){var on=x.getAttribute('data-state')===s;x.classList.toggle('is-on',on);x.setAttribute('aria-pressed',on?'true':'false');});
    });
  });
  var waiting=document.getElementById('kpi-waiting'), presence=document.getElementById('presence-count');
  function recount(){var n=document.querySelectorAll('#today-rows tr[data-pending="1"]').length; waiting.textContent=n; presence.textContent=n;}
  var timers={};
  function pad(n){return (n<10?'0':'')+n;}
  document.querySelectorAll('[data-approve]').forEach(function(b){
    b.addEventListener('click',function(){
      var id=b.getAttribute('data-approve'), row=document.getElementById('row-'+id), prop=document.getElementById('prop-'+id), res=document.getElementById('result-'+id);
      var d=new Date(); var t=pad(d.getHours())+':'+pad(d.getMinutes());
      prop.hidden=true; res.hidden=false; res.className='result notice notice-success';
      res.innerHTML='Saved to CRM at '+t+'. <button type="button" class="link" data-undo="'+id+'">Undo</button> <span class="muted" id="undo-left-'+id+'">10 s</span>';
      row.setAttribute('data-pending','0'); row.querySelector('.col-actions').hidden=true; recount();
      var left=10; timers[id]=setInterval(function(){left--; var el=document.getElementById('undo-left-'+id); if(!el){clearInterval(timers[id]);return;} if(left<=0){clearInterval(timers[id]); res.innerHTML='Saved to CRM at '+t+'. <a class="row-link" href="proposal-review.html">See the record</a>';} else {el.textContent=left+' s';}},1000);
      res.querySelector('[data-undo]').addEventListener('click',function(){clearInterval(timers[id]); res.hidden=true; prop.hidden=false; row.setAttribute('data-pending','1'); row.querySelector('.col-actions').hidden=false; recount(); b.focus();});
      res.querySelector('[data-undo]').focus();
    });
  });
  document.querySelectorAll('[data-later]').forEach(function(b){
    b.addEventListener('click',function(){
      var id=b.getAttribute('data-later'), row=document.getElementById('row-'+id), prop=document.getElementById('prop-'+id), res=document.getElementById('result-'+id);
      prop.hidden=true; res.hidden=false; res.className='result notice';
      res.innerHTML='Kept for tomorrow. The proposal returns in tomorrow\'s list. <button type="button" class="link" data-back="'+id+'">Bring it back</button>';
      row.setAttribute('data-pending','0'); row.querySelector('.col-actions').hidden=true; recount();
      res.querySelector('[data-back]').addEventListener('click',function(){res.hidden=true; prop.hidden=false; row.setAttribute('data-pending','1'); row.querySelector('.col-actions').hidden=false; recount(); b.focus();});
      res.querySelector('[data-back]').focus();
    });
  });
})();
"""
    shell("daily-list.html", "Daily list, built with the rules", "The rep's daily list of meetings with the agent's proposals in their own column, real-looking data, four states, approve with undo.", body, ["screens.css"], script, "screen", "daily-list-generic.html", "Daily list")


# ---------------------------------------------------------------- daily list (generic twin)


def daily_list_generic():
    cards = []
    for m in TODAY:
        amt = "$" + f"{round((m['amount'] or 0) / 5000) * 5000 or 10000:,}"
        cards.append(
            f'<div class="g-card"><div class="g-card-top"><span class="g-badge">✨ AI insight</span></div>'
            f'<h3>{e(m["customer"])}</h3><p class="g-sub">{e(m["stage"] or "Qualified")} · {amt}</p>'
            f'<p class="g-text">Our AI recommends following up today to maximize your conversion potential.</p>'
            f'<div class="g-actions"><button type="button" class="g-btn g-btn-primary">Approve ✅</button><button type="button" class="g-btn g-btn-secondary">View details</button></div></div>'
        )
    body = f"""
<header class="g-hero">
  <div class="g-hero-inner">
    <span class="g-pill">✨ AI-powered</span>
    <h1>Welcome back, {e(ME["name"])}! 👋</h1>
    <p class="g-lead">Unlock smarter selling with AI. Your personalized insights are ready to supercharge your pipeline.</p>
    <div class="g-hero-actions"><button type="button" class="g-btn g-btn-light">Get started</button><button type="button" class="g-btn g-btn-ghost">Learn more</button></div>
  </div>
</header>
<main class="g-main">
  <section class="g-stats">
    <div class="g-stat"><p class="g-stat-value">100+</p><p class="g-stat-label">Meetings analyzed</p></div>
    <div class="g-stat"><p class="g-stat-value">$1M</p><p class="g-stat-label">Pipeline value</p></div>
    <div class="g-stat"><p class="g-stat-value">98%</p><p class="g-stat-label">AI accuracy</p></div>
  </section>
  <section class="g-features">
    <div class="g-feature"><div class="g-icon">🤖</div><h3>AI Insights</h3><p>Harness next-gen AI to transform your sales journey.</p></div>
    <div class="g-feature"><div class="g-icon">📈</div><h3>Pipeline Growth</h3><p>Seamlessly boost your pipeline with smart recommendations.</p></div>
    <div class="g-feature"><div class="g-icon">⚡</div><h3>Instant Updates</h3><p>Keep your CRM in sync effortlessly, in real time.</p></div>
  </section>
  <section class="g-list">
    <h2>Your meetings 🗓️</h2>
    <div class="g-grid">{''.join(cards)}</div>
  </section>
</main>
"""
    shell("daily-list-generic.html", "Daily list, the generic version", "The same rep's daily list as a typical generated page: gradient hero, three icon cards, centered copy, round numbers, no states.", body, ["screens.css"], "", "generic", "daily-list.html", "Daily list")


# ---------------------------------------------------------------- proposal review (rules)


def proposal_review():
    m = next(x for x in TODAY if x["id"] == "M-1041")
    p = m["proposal"]
    trail_rows = "".join(
        f'<tr><td class="num">{e(t["when"].replace("T", " "))}</td><td>{e(t["what"])}</td><td>{e(t["deal"])}</td><td>{e(t["approved_by"])}</td>'
        f'<td>{"<span class=\"state state-neutral\">undone</span>" if t["undone"] else "<span class=\"state state-success\">in the CRM</span>"}</td></tr>'
        for t in D["trail"]
    )
    body = f"""
<header class="app-header">
  <div class="app-id"><span class="app-name">Acme Field Sales Assistant</span><span class="app-user">{e(ME["name"])}</span></div>
  <p class="app-date"><a href="daily-list.html">Back to today</a></p>
  <p class="presence">Agent ran at {LAST_RUN}. Proposal from the notes of the {e(m["time"])} meeting.</p>
</header>
<main class="app app-narrow" id="app">
  <section class="deal-head" aria-labelledby="h-deal">
    <h1 id="h-deal">{e(m["customer"])}</h1>
    <p class="muted">{e(m["contact"])} · meeting today at {e(m["time"])} · deal {e(m["id"])}</p>
  </section>

  <section class="proposal-card" aria-labelledby="h-prop">
    <p class="proposal-tag" id="h-prop">Agent proposes</p>
    <table class="table changes">
      <thead><tr><th scope="col">Field</th><th scope="col">Recorded in the CRM</th><th scope="col">Proposed</th></tr></thead>
      <tbody>
        <tr><td>Stage</td><td>{e(p["from"])}</td><td><strong>{e(p["to"])}</strong></td></tr>
        <tr><td>Next step</td><td><span class="muted">none recorded</span></td><td><strong>Send the revised pricing before Thursday</strong></td></tr>
        <tr><td>Amount</td><td>{money(m["amount"])}</td><td><span class="muted">unchanged</span></td></tr>
      </tbody>
    </table>
    <h2>Based on</h2>
    <ul class="evidence">
      <li>"{e(p["evidence"][0]["quote"])}" <span class="muted">at {e(p["evidence"][0]["t"])} in the notes</span></li>
      <li>"Thursday is the board; if the number works we move." <span class="muted">at 00:52 in the notes</span></li>
    </ul>
    <details class="draft">
      <summary>Follow-up email draft, not sent</summary>
      <p>Subject: Revised pricing for Thursday</p>
      <p>Thank you for the time this morning. Attached is the revised pricing we discussed, with the onboarding date held at 5 May. I am available Wednesday if the board has questions before Thursday.</p>
      <p class="muted">Saving to the CRM does not send this email. Sending is a separate step you take yourself.</p>
    </details>
    <div class="proposal-actions" id="actions">
      <button type="button" class="btn btn-primary" id="approve">Save to CRM</button>
      <button type="button" class="btn" id="edit">Edit the proposal</button>
      <a class="row-link" href="#trail">What the agent did before</a>
    </div>
    <div class="result" id="result" hidden></div>
    <p class="never"><strong>The agent will not:</strong> write to the CRM without your approval, change an amount it did not hear, or send the email.</p>
  </section>

  <section class="block" id="trail" aria-labelledby="h-trail">
    <h2 id="h-trail">What the agent did, and who approved it</h2>
    <table class="table">
      <thead><tr><th scope="col">When</th><th scope="col">What</th><th scope="col">Deal</th><th scope="col">Approved by</th><th scope="col">Status</th></tr></thead>
      <tbody id="trail-rows">{trail_rows}</tbody>
    </table>
  </section>
</main>
"""
    script = r"""
(function(){
  var approve=document.getElementById('approve'), edit=document.getElementById('edit'), actions=document.getElementById('actions'), res=document.getElementById('result'), rows=document.getElementById('trail-rows');
  function pad(n){return (n<10?'0':'')+n;}
  var timer=null, added=null;
  approve.addEventListener('click',function(){
    var d=new Date(); var t=pad(d.getHours())+':'+pad(d.getMinutes());
    actions.hidden=true; res.hidden=false; res.className='result notice notice-success';
    res.innerHTML='Saved to CRM at '+t+': stage Negotiation, next step recorded. <button type="button" class="link" id="undo">Undo</button> <span class="muted" id="left">10 s</span>';
    added=document.createElement('tr'); added.innerHTML='<td class="num">'+d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate())+' '+t+'</td><td>Stage: Proposal to Negotiation; next step</td><td>Northwind Logistics</td><td>Ana</td><td><span class="state state-success">in the CRM</span></td>';
    rows.insertBefore(added, rows.firstChild);
    var left=10; timer=setInterval(function(){left--; var el=document.getElementById('left'); if(!el){clearInterval(timer);return;} if(left<=0){clearInterval(timer); res.innerHTML='Saved to CRM at '+t+'. <a class="row-link" href="daily-list.html">Back to today</a>';} else {el.textContent=left+' s';}},1000);
    document.getElementById('undo').addEventListener('click',function(){clearInterval(timer); res.hidden=true; actions.hidden=false; if(added){added.querySelector('td:last-child').innerHTML='<span class="state state-neutral">undone</span>';} approve.focus();});
    document.getElementById('undo').focus();
  });
  edit.addEventListener('click',function(){
    var cells=document.querySelectorAll('.changes tbody td:last-child strong');
    cells.forEach(function(c){ if(c.getAttribute('contenteditable')) return; c.setAttribute('contenteditable','true'); c.classList.add('editing'); });
    edit.textContent='Editing: change the proposed values, then save';
    if(cells[0]) cells[0].focus();
  });
})();
"""
    shell("proposal-review.html", "Proposal review, built with the rules", "One proposed CRM update with its evidence from the meeting notes, approval with undo, and the trail of what the agent did before.", body, ["screens.css"], script, "screen", "proposal-review-generic.html", "Proposal review")


def proposal_review_generic():
    body = """
<header class="g-hero g-hero-small">
  <div class="g-hero-inner">
    <span class="g-pill">✨ AI Deal Insight</span>
    <h1>Northwind Logistics is heating up! 🔥</h1>
    <p class="g-lead">Our AI analyzed your meeting and found a high-potential opportunity.</p>
  </div>
</header>
<main class="g-main">
  <section class="g-insight">
    <div class="g-score"><p class="g-score-value">92%</p><p class="g-score-label">Confidence score</p></div>
    <div class="g-insight-text">
      <h2>Recommended action ✅</h2>
      <p>Move this deal to the next stage and send a follow-up to keep the momentum going. Our AI thinks this deal is likely to close soon.</p>
      <div class="g-actions"><button type="button" class="g-btn g-btn-primary">Approve ✨</button><button type="button" class="g-btn g-btn-danger">Reject ❌</button></div>
    </div>
  </section>
  <section class="g-features">
    <div class="g-feature"><div class="g-icon">🎯</div><h3>Next Best Action</h3><p>AI-generated next steps tailored to your deal.</p></div>
    <div class="g-feature"><div class="g-icon">💡</div><h3>Smart Summary</h3><p>Key takeaways from your meeting, instantly.</p></div>
    <div class="g-feature"><div class="g-icon">🚀</div><h3>Auto-update</h3><p>Let AI keep your CRM up to date.</p></div>
  </section>
</main>
"""
    shell("proposal-review-generic.html", "Proposal review, the generic version", "The same proposal as a typical generated screen: a confidence score, two colored buttons, no evidence, no trail.", body, ["screens.css"], "", "generic", "proposal-review.html", "Proposal review")


# ---------------------------------------------------------------- weekly summary (rules, phone first)


def weekly_summary():
    w = D["week"]
    rep_rows = "".join(
        f'<li class="rep-row"><span class="rep-name">{e(r["name"])}</span><span class="rep-meetings muted num">{r["weekly_meetings"]} meetings</span><span class="rep-pct">{pct(r["updated_within_24h"])}</span></li>'
        for r in D["reps"]
    )
    stale_rows = "".join(
        f'<li class="stale-row"><div><strong>{e(m["customer"])}</strong><br><span class="muted">{stage_cell(m["stage"])} · {money(m["amount"], m["currency"])}</span></div>'
        f'<div class="stale-right"><span class="state state-warning num">{m["last_activity_days_before"]} days</span><br><a class="row-link" href="proposal-review.html">Open deal</a></div></li>'
        for m in sorted(STALE, key=lambda x: -x["last_activity_days_before"])
    )
    delta = round((w["updated_within_24h"] - w["updated_within_24h_prev"]) * 100)
    body = f"""
<header class="app-header app-header-narrow">
  <div class="app-id"><span class="app-name">Acme Field Sales Assistant</span><span class="app-user">Manager</span></div>
  <p class="app-date">Week {e(w["iso"][-2:])}, 13 to 17 April 2026 · as of {e(long_date(SNAPSHOT))}</p>
</header>
<main class="app phone" id="app">
  <section class="kpi kpi-lead" aria-label="The number">
    <p class="label">Updated within 24 hours of a meeting</p>
    <p class="value">{round(w["updated_within_24h"] * 100)}%</p>
    <p class="reading">last week {round(w["updated_within_24h_prev"] * 100)}%, {"+" if delta >= 0 else ""}{delta} points · target 90%</p>
  </section>
  <section class="kpis kpis-phone" aria-label="This week in numbers">
    <div class="kpi"><p class="label">Meetings</p><p class="value">{w["meetings"]}</p><p class="reading">this week, all reps</p></div>
    <div class="kpi"><p class="label">Proposals approved</p><p class="value">{w["proposals_approved"]}</p><p class="reading">{w["proposals_pending"]} still waiting</p></div>
  </section>
  <section class="block" aria-labelledby="h-reps">
    <h2 id="h-reps">By rep</h2>
    <ul class="rep-list">{rep_rows}</ul>
    <p class="muted small">Diego's CRM account was connected on Thursday; the first number arrives next week.</p>
  </section>
  <section class="block" aria-labelledby="h-stale">
    <h2 id="h-stale">Needs attention: no activity for 14 days or more</h2>
    <ul class="stale-list">{stale_rows}</ul>
  </section>
  <section class="block">
    <a class="btn" href="daily-list.html">Open a rep's daily list</a>
  </section>
</main>
"""
    shell("weekly-summary.html", "Weekly summary, built with the rules", "A manager's weekly summary, phone first: the number, the reading behind it, the team by rep, and the deals that need attention.", body, ["screens.css"], "", "screen", "weekly-summary-generic.html", "Weekly summary")


def weekly_summary_generic():
    body = """
<header class="g-hero g-hero-small">
  <div class="g-hero-inner">
    <span class="g-pill">📊 Weekly Dashboard</span>
    <h1>Great job this week, team! 🎉</h1>
    <p class="g-lead">Your AI-powered performance snapshot is ready.</p>
  </div>
</header>
<main class="g-main g-main-narrow">
  <section class="g-insight g-center">
    <div class="g-score"><p class="g-score-value">68%</p><p class="g-score-label">CRM health score</p></div>
    <p class="g-text">You're doing amazing! Keep up the momentum to hit your goals 🚀</p>
  </section>
  <section class="g-stats">
    <div class="g-stat"><p class="g-stat-value">70+</p><p class="g-stat-label">Meetings</p></div>
    <div class="g-stat"><p class="g-stat-value">40</p><p class="g-stat-label">AI actions</p></div>
    <div class="g-stat"><p class="g-stat-value">$500K</p><p class="g-stat-label">Pipeline</p></div>
  </section>
  <section class="g-list g-center">
    <h2>Top performers 🏆</h2>
    <div class="g-grid g-grid-narrow">
      <div class="g-card g-center"><div class="g-icon">🥇</div><h3>Carla</h3><p class="g-sub">90% CRM score</p></div>
      <div class="g-card g-center"><div class="g-icon">🥈</div><h3>Ana</h3><p class="g-sub">75% CRM score</p></div>
      <div class="g-card g-center"><div class="g-icon">🥉</div><h3>Bruno</h3><p class="g-sub">40% CRM score</p></div>
    </div>
    <button type="button" class="g-btn g-btn-primary">View full report</button>
  </section>
</main>
"""
    shell("weekly-summary-generic.html", "Weekly summary, the generic version", "The same weekly summary as a typical generated dashboard: a health score, medals, round numbers, centered everything.", body, ["screens.css"], "", "generic", "weekly-summary.html", "Weekly summary")


# ---------------------------------------------------------------- gallery index


PAIRS = [
    {
        "slug": "daily-list", "title": "The rep's daily list",
        "job": "A field rep between two meetings, two minutes, laptop or phone: what do I owe the CRM today?",
        "frame": (1280, 800),
        "notice": [
            ("1, 2, 6", "No hero, no icon grid, nothing centered. The first thing on the screen is today's meetings in time order, on real-looking data with its date."),
            ("7", "Three amounts and one stage read \"no data\" because the CRM has none. The generic version rounds them to the nearest five thousand."),
            ("11", "Empty, loading and error are one click away in the state switcher. The generic page has one state."),
            ("15", "The button says what happens in the system: \"Save to CRM\", with Undo for ten seconds. Not \"Approve\" with a check mark."),
            ("agent", "The agent's proposal sits in its own column with the quote it is based on. A proposal never shares a cell with a recorded fact."),
        ],
    },
    {
        "slug": "proposal-review", "title": "One proposal, reviewed",
        "job": "The same rep decides whether to let the agent write a stage change and a next step into the CRM.",
        "frame": (1280, 800),
        "notice": [
            ("4, 5", "No \"heating up\", no confidence score with no definition, no fire emoji. Recorded value next to proposed value, field by field."),
            ("agent", "Evidence: the two sentences from the notes the proposal is based on, with their timestamps. The generic version asks for trust without showing why."),
            ("10", "Two buttons, one link. Approve writes and shows Undo. Edit makes the proposed values editable in place. Reject is not a red button; \"Not now\" lives on the list."),
            ("agent", "The trail at the bottom: what the agent did before, when, approved by whom, and one entry that was undone."),
            ("15", "A short \"the agent will not\" line where the decision is made, not in a footer."),
        ],
    },
    {
        "slug": "weekly-summary", "title": "The manager's week, on a phone",
        "job": "A sales manager on Friday afternoon, phone in hand: did my team update the CRM after their meetings, and who needs a call?",
        "frame": (390, 844),
        "notice": [
            ("1, 14", "No health score, no medals, no confetti. One number with its label above and its reading below: last week, the change, the target."),
            ("7", "One rep reads \"no data\" with the reason in one line. The generic version gives him a bronze medal and 40%."),
            ("12", "The \"needs attention\" list is content-sized: days without activity, the recorded stage and amount, one link per deal."),
            ("6, 9", "Left-aligned, one spacing scale, phone width first. Nothing is centered because nothing is a poster."),
            ("13", "Every control is reachable with a keyboard and the focus is visible. Try Tab on both versions."),
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
    <p class="lede">AI builds a screen in minutes, and the default result looks like every other AI screen. It costs credibility the moment a customer, a sponsor or a candidate opens it. Three screens for a fictional sales assistant, each built with a small set of rules, next to the version most tools would produce from the same brief. Both are live pages: open them, click, press Tab.</p>
    <p class="actions"><a class="btn btn-primary" href="#pairs">See the screens</a> <a class="btn" href="{REPO_URL}">The rules on GitHub</a></p>
    <p class="muted">Fictional company, people and numbers. Snapshot of {e(long_date(SNAPSHOT))}. Every page is generated from the same data file by one script; nothing is edited by hand.</p>
  </div>
</header>
<main class="g-body" id="pairs">
{''.join(pairs_html)}
<section class="how" aria-labelledby="h-how">
  <h2 id="h-how">How these were made</h2>
  <ol class="how-list">
    <li><strong>Real data, frozen.</strong> Twelve meetings and deals, anonymized, dated 13 April 2026. Three amounts and one stage are missing in the source, so the screens say so.</li>
    <li><strong>One generator, never a hand edit.</strong> A single Python script reads the data and the tokens and writes every page here, including the generic twins.</li>
    <li><strong>Measured, not squinted.</strong> Contrast on every text pair, two widths, keyboard reach, the four states. The tells list is the audit.</li>
  </ol>
  <p>The rules: <a href="{REPO_URL}/blob/main/docs/visual-slop-tells.md">sixteen visual tells and what to do instead</a>. The workflow: <a href="{REPO_URL}/blob/main/docs/mockup-first.md">from a brief to a validated decision in a thirty-minute session</a>. The skills: <a href="{REPO_URL}/tree/main/skills">html-mockup, visual-slop-audit, visual-validation-session, design-tokens-starter</a>. The tokens behind every screen: <a href="{REPO_URL}/blob/main/templates/tokens.css">tokens.css</a>.</p>
</section>
</main>
"""
    script = r"""
(function(){
  function fit(){
    document.querySelectorAll('.preview').forEach(function(p){
      var w=parseInt(p.getAttribute('data-w'),10), h=parseInt(p.getAttribute('data-h'),10);
      var avail=p.clientWidth; var s=Math.min(1, avail/w);
      if(w<500){ s=Math.min(s, 460/h); }
      var f=p.querySelector('iframe'); f.style.width=w+'px'; f.style.height=h+'px'; f.style.transform='scale('+s+')';
      p.style.height=Math.round(h*s)+'px';
    });
  }
  fit(); window.addEventListener('resize', fit);
})();
"""
    shell("index.html", "No-slop design", "Visual AI slop is manageable. Three screens built with a small set of rules, each next to the generic version most tools would produce. Live pages, real-looking data, measured checks.", body, ["gallery.css"], script, "gallery")


# ---------------------------------------------------------------- stylesheets

SCREENS_CSS = r"""
/* Screens built with the rules. Tokens come from tokens.css; nothing literal below except the generic twin. */
.visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.frame { display: flex; flex-wrap: wrap; gap: var(--sp-3) var(--sp-4); align-items: center; padding: var(--sp-2) var(--sp-4); font-size: var(--fs-0); border-bottom: 1px solid var(--ink-12); background: var(--surface); }
.frame-home { font-weight: var(--w-strong); color: var(--ink); text-decoration: none; }
.frame-label { color: var(--ink-70); }
.frame-twin { margin-left: auto; }
.site-footer { padding: var(--sp-5) var(--sp-4); font-size: var(--fs-0); color: var(--ink-70); border-top: 1px solid var(--ink-12); margin-top: var(--sp-7); }
.site-footer p { margin: 0 0 var(--sp-1); }

.app-header { display: grid; grid-template-columns: 1fr auto; gap: var(--sp-1) var(--sp-4); align-items: baseline; padding: var(--sp-4); border-bottom: 1px solid var(--ink-12); background: var(--surface); }
.app-id { display: flex; gap: var(--sp-3); align-items: baseline; }
.app-name { font-weight: var(--w-strong); }
.app-user { color: var(--ink-70); }
.app-date { color: var(--ink-70); font-size: var(--fs-0); text-align: right; }
.presence { grid-column: 1 / -1; font-size: var(--fs-0); color: var(--ink-70); }
.app-header-narrow { grid-template-columns: 1fr; }
.app-header-narrow .app-date { text-align: left; }

.switcher { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-1); padding: var(--sp-2) var(--sp-4); font-size: var(--fs-0); border-bottom: 1px dashed var(--ink-30); }
.switcher-label { color: var(--ink-70); margin-right: var(--sp-2); }
.switcher .btn { min-height: 32px; padding: 0 var(--sp-3); font-size: var(--fs-0); }
.switcher .btn.is-on { background: var(--ink); color: var(--paper); }

.app { padding: var(--sp-4); max-width: 1180px; margin: 0 auto; }
.app-narrow { max-width: 860px; }
.kpis { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--sp-4); padding: var(--sp-4) 0 var(--sp-5); }
.kpi-lead { padding: var(--sp-4) 0; }
.block { margin-top: var(--sp-5); }
.block h2 { margin-bottom: var(--sp-3); }
.list th:nth-child(1), .list td:nth-child(1) { width: 72px; white-space: nowrap; }
.col-proposal { min-width: 260px; }
.col-actions { white-space: nowrap; }
.col-actions .btn { margin-bottom: var(--sp-1); }
.row-link { font-size: var(--fs-0); }
.proposal { border: 1px dashed var(--accent); border-left: 3px solid var(--accent); border-radius: var(--radius-1); padding: var(--sp-2) var(--sp-3); background: var(--accent-soft); }
.proposal-tag { font-size: var(--fs-0); font-weight: var(--w-strong); color: var(--accent); margin-bottom: var(--sp-1); }
.proposal-evidence { font-size: var(--fs-0); margin-top: var(--sp-1); }
.proposal-draft { font-size: var(--fs-0); margin-top: var(--sp-1); }
.result { margin-top: var(--sp-1); }
.skeleton-rows { display: grid; gap: var(--sp-3); margin-top: var(--sp-4); }
.skeleton { height: 44px; }
.empty { margin-top: var(--sp-4); }
.empty h2 { margin-bottom: var(--sp-2); color: var(--ink); }
.empty p { margin-bottom: var(--sp-3); }

/* State switching: only the matching sections show. display lives in state rules, never in the component. */
.app .only-empty, .app .only-loading { display: none; }
.app .only-error:not(.only-normal) { display: none; }
.app[data-state="empty"] .only-normal { display: none; }
.app[data-state="empty"] .only-empty { display: block; }
.app[data-state="loading"] .only-normal { display: none; }
.app[data-state="loading"] .only-loading { display: block; }
.app[data-state="error"] .only-error:not(.only-normal) { display: block; }

/* Proposal review */
.deal-head { padding-bottom: var(--sp-4); }
.proposal-card { border: 1px solid var(--ink-12); border-left: 3px solid var(--accent); border-radius: var(--radius-2); padding: var(--sp-4); background: var(--surface); }
.proposal-card h2 { margin-top: var(--sp-5); margin-bottom: var(--sp-2); font-size: var(--fs-1); }
.changes td:first-child { color: var(--ink-70); width: 120px; }
.changes .editing { outline: 1px dashed var(--accent); padding: 2px var(--sp-1); }
.evidence { margin: 0; padding-left: var(--sp-4); }
.evidence li { margin-bottom: var(--sp-1); }
.draft { margin-top: var(--sp-4); border: 1px solid var(--ink-12); border-radius: var(--radius-1); padding: var(--sp-2) var(--sp-3); }
.draft summary { cursor: pointer; font-weight: var(--w-strong); }
.draft p { margin-top: var(--sp-2); }
.proposal-actions { display: flex; flex-wrap: wrap; align-items: center; gap: var(--sp-2) var(--sp-3); margin-top: var(--sp-5); }
.never { margin-top: var(--sp-4); font-size: var(--fs-0); color: var(--ink-70); }

/* Weekly summary, phone first */
.phone { max-width: 480px; }
.kpis-phone { grid-template-columns: repeat(2, minmax(0, 1fr)); padding-top: 0; }
.rep-list, .stale-list { list-style: none; margin: 0; padding: 0; }
.rep-row { display: grid; grid-template-columns: 1fr auto 64px; gap: var(--sp-3); align-items: baseline; padding: var(--sp-3) 0; border-bottom: 1px solid var(--ink-12); }
.rep-pct { text-align: right; font-weight: var(--w-strong); }
.stale-row { display: flex; justify-content: space-between; gap: var(--sp-3); padding: var(--sp-3) 0; border-bottom: 1px solid var(--ink-12); }
.stale-right { text-align: right; }
.small { font-size: var(--fs-0); margin-top: var(--sp-2); }

@media (max-width: 900px) {
  .kpis { grid-template-columns: 1fr; gap: var(--sp-3); }
  .list thead { display: none; }
  .list tr { display: grid; grid-template-columns: 1fr 1fr; gap: var(--sp-1) var(--sp-3); padding: var(--sp-3) 0; border-bottom: 1px solid var(--ink-12); }
  .list td { display: block; padding: 0; border: 0; }
  .list td:nth-child(1) { width: auto; }
  .list .col-proposal, .list .col-actions { grid-column: 1 / -1; min-width: 0; }
  .list .col-actions { white-space: normal; }
  .list tbody tr:hover { background: transparent; }
  .app-header { grid-template-columns: 1fr; }
  .app-date { text-align: left; }
}

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
.g-card-top { margin-bottom: 10px; }
.g-badge { display: inline-block; padding: 4px 10px; border-radius: 999px; background: #EDE9FE; color: #7C3AED; font-size: 12px; font-weight: 700; }
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
.lede { font-size: var(--fs-2); max-width: 66ch; margin-bottom: var(--sp-5); }
.actions { display: flex; flex-wrap: wrap; gap: var(--sp-3); margin-bottom: var(--sp-4); }
.g-body { max-width: 1180px; margin: 0 auto; padding: var(--sp-6) var(--sp-4) 0; }
.pair { padding: var(--sp-6) 0; border-bottom: 1px solid var(--ink-12); }
.pair-head { max-width: 760px; margin-bottom: var(--sp-5); }
.pair-head h2 { font-size: var(--fs-3); margin-bottom: var(--sp-2); }
.job { color: var(--ink-70); }
.pair-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--sp-5); align-items: start; }
.shot { margin: 0; }
.preview { position: relative; overflow: hidden; border: 1px solid var(--ink-12); border-radius: var(--radius-2); background: var(--surface); height: 300px; }
.preview iframe { position: absolute; top: 0; left: 0; width: 1280px; height: 800px; border: 0; transform: scale(0.3); transform-origin: 0 0; pointer-events: none; background: var(--paper); }
.shot figcaption { margin-top: var(--sp-2); font-size: var(--fs-0); }
.notice-list { margin-top: var(--sp-5); max-width: 880px; }
.notice-list h3 { margin-bottom: var(--sp-3); }
.notice-list ul { list-style: none; margin: 0; padding: 0; display: grid; gap: var(--sp-2); }
.notice-list li { display: grid; grid-template-columns: 56px 1fr; gap: var(--sp-3); align-items: start; }
.tell { font-size: var(--fs-0); font-weight: var(--w-strong); color: var(--accent); background: var(--accent-soft); padding: 2px var(--sp-2); border-radius: var(--radius-1); text-align: center; }
.how { padding: var(--sp-6) 0; max-width: 880px; }
.how h2 { font-size: var(--fs-3); margin-bottom: var(--sp-4); }
.how-list { padding-left: var(--sp-5); margin: 0 0 var(--sp-4); display: grid; gap: var(--sp-2); }
.site-footer { padding: var(--sp-5) var(--sp-4); font-size: var(--fs-0); color: var(--ink-70); border-top: 1px solid var(--ink-12); margin-top: var(--sp-6); }
.site-footer p { margin: 0 0 var(--sp-1); }
@media (max-width: 760px) {
  .pair-grid { grid-template-columns: 1fr; }
  .notice-list li { grid-template-columns: 48px 1fr; }
}
"""

OG_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" role="img" aria-label="No-slop design">
<rect width="1200" height="630" fill="#F5F6F8"/>
<rect x="0" y="0" width="1200" height="12" fill="#2446A6"/>
<text x="80" y="250" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="72" font-weight="700" fill="#1C2230">No-slop design</text>
<text x="80" y="330" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="34" fill="#1C2230" fill-opacity="0.72">Visual AI slop is manageable.</text>
<text x="80" y="390" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="26" fill="#1C2230" fill-opacity="0.72">Three screens built with the rules, next to the generic version.</text>
<text x="80" y="560" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="22" fill="#1C2230" fill-opacity="0.56">benyoumen.github.io/no-slop-design</text>
</svg>
"""


def main():
    os.makedirs(SITE, exist_ok=True)
    shutil.copyfile(TOKENS, os.path.join(SITE, "tokens.css"))
    with open(os.path.join(SITE, "screens.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(SCREENS_CSS.lstrip())
    with open(os.path.join(SITE, "gallery.css"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(GALLERY_CSS.lstrip())
    with open(os.path.join(SITE, "og.svg"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(OG_SVG)
    daily_list()
    daily_list_generic()
    proposal_review()
    proposal_review_generic()
    weekly_summary()
    weekly_summary_generic()
    gallery()
    print("built", sorted(os.listdir(SITE)))


if __name__ == "__main__":
    main()
