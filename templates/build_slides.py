#!/usr/bin/env python3
"""Chapter-report slide generator.

Usage:  python3 build_slides.py <out_dir> <frontend-slides>/viewport-base.css

Edit three things:
  THEME  — colours + fonts of the style the user picked
  META   — title, chapter, pages, presenters
  SLIDES — the outline, written with the layout helpers below
Every slide is a fixed 1920×1080 stage scaled to the window (frontend-slides rules).
deck.js (navigation) and edit-sync.js (cloud editor) are read from this folder.
"""
import html
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(sys.argv[1])
BASE_CSS = pathlib.Path(sys.argv[2]).read_text()
JS = (HERE / "deck.js").read_text() + "\n" + (HERE / "edit-sync.js").read_text()

# ------------------------------------------------------------------
# THEME — replace with the chosen style (keep a CJK font in each stack)
# ------------------------------------------------------------------
THEME = {
    "fonts": "https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@1,6..72,400"
             "&family=DM+Mono:wght@400;500&family=Noto+Serif+TC:wght@400;700;900&display=swap",
    "paper": "#F2EDE3",      # slide background
    "ink": "#1E2A44",        # text, rules
    "accent": "#C2552D",     # one accent colour
    "faint": "rgba(30,42,68,.16)",
    "stage": "#d8d2c4",      # letterbox colour around the slide
    "f_cjk": '"Noto Serif TC",serif',
    "f_en": '"Newsreader","Noto Serif TC",serif',
    "f_mono": '"DM Mono",ui-monospace,monospace',
}

META = {
    "title": "〔章名〕",
    "title_en": "〔English title〕",
    "chapter": "CH.〔N〕",
    "source": "〔作者〕《〔書名〕》第〔N〕章 · 頁 〔x–y〕",
    "presenters": [("〔學號〕", "〔姓名〕"), ("〔學號〕", "〔姓名〕")],
}

CSS = r"""
:root{
  --stage-bg:@stage;--slide-bg:@paper;--paper:@paper;--ink:@ink;--accent:@accent;--faint:@faint;
  --f-cjk:@f_cjk;--f-en:@f_en;--f-mono:@f_mono;--edge:96px;--ease:cubic-bezier(.16,1,.3,1);
}
*{margin:0;padding:0;box-sizing:border-box}
@@BASE@@
.slide{color:var(--ink);font-family:var(--f-cjk);transition:opacity .28s,visibility .28s}
.slide>*{position:absolute;z-index:2}
.slide.dark{background:var(--ink);color:var(--paper)}
.chrome{left:var(--edge);right:var(--edge);top:50px;display:flex;justify-content:space-between;font:400 18px var(--f-mono);letter-spacing:.1em;opacity:.75}
.foot{left:var(--edge);right:var(--edge);bottom:46px;display:flex;justify-content:space-between;font:400 17px var(--f-mono);letter-spacing:.06em;opacity:.6}
.frame{top:120px;left:var(--edge);right:var(--edge);bottom:110px;display:flex;flex-direction:column}
.frame>.cols,.frame>.ledger{margin-top:auto;margin-bottom:auto}
.kicker{font:500 20px var(--f-mono);letter-spacing:.14em;color:var(--accent)}
.en{font:italic 400 92px/1 var(--f-en)}
.hero{font:900 180px/1.1 var(--f-cjk)}
.quote{font:900 80px/1.4 var(--f-cjk)}
.head{font:700 64px/1.25 var(--f-cjk)}
.lede{font:400 34px/1.75 var(--f-cjk)}
.body{font:400 30px/1.7 var(--f-cjk)}
.small{font:400 22px/1.7 var(--f-cjk)}
.mono{font:400 18px var(--f-mono);letter-spacing:.08em}
.num{font:500 22px var(--f-mono)}
.topbar{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid currentColor;padding-bottom:18px;flex:none}
.topbar .mono{padding-bottom:10px}
.cols{display:grid;gap:56px}
.col{border-top:6px solid var(--accent);padding-top:24px}
.col .num{display:block;margin-bottom:10px}
.col h3{font:700 44px/1.3 var(--f-cjk);margin-bottom:12px}
.ledger{display:flex;flex-direction:column}
.ledger .r{display:grid;grid-template-columns:380px 1fr;gap:36px;padding:24px 0;border-bottom:1px solid var(--faint);align-items:baseline}
.ledger .name{font:700 36px/1.3 var(--f-cjk)}
.ledger .r>.body{font-size:29px}
.attr{border-top:1.5px solid currentColor;padding-top:16px;display:flex;justify-content:space-between}
.reveal{opacity:0;transform:translateY(22px);transition:opacity .7s var(--ease),transform .7s var(--ease);transition-delay:var(--d,0s)}
.slide.visible .reveal{opacity:1;transform:none}
.progress{position:fixed;left:0;bottom:0;height:3px;background:var(--accent);z-index:1000;transition:width .3s var(--ease)}
/* ← 回首頁: hover the top-right corner (faintly visible on touch screens) */
.home-zone{position:fixed;top:0;right:0;width:200px;height:110px;z-index:10002;display:flex;justify-content:flex-end;align-items:flex-start;padding:16px}
.home-btn{opacity:0;pointer-events:none;transition:opacity .25s;text-decoration:none;font:500 14px var(--f-mono);letter-spacing:.08em;background:var(--paper);color:var(--ink);border:1.5px solid var(--ink);padding:9px 14px}
.home-zone:hover .home-btn,.home-btn:focus-visible{opacity:1;pointer-events:auto}
.home-btn:hover{background:var(--ink);color:var(--paper)}
@media (hover:none){.home-btn{opacity:.55;pointer-events:auto}}
"""


def esc(t):
    return html.escape(t, quote=False)


def chrome(right):
    return (f'<div class="chrome"><span>{META["chapter"]}</span><span>{right}</span></div>'
            f'<div class="foot"><span>{esc(META["source"])}</span><span data-page></span></div>')


def wrap(label, right, inner, dark=False):
    return f'<section class="slide{" dark" if dark else ""}" aria-label="{label}">\n{chrome(right)}\n{inner}\n</section>'


# ------------------------------------------------------------------
# LAYOUT HELPERS — combine these to write the outline
# ------------------------------------------------------------------
def cover():
    who = "".join(f'<span class="small" style="margin-right:40px"><span class="num">{i}</span>&nbsp;{n}</span>'
                  for i, n in META["presenters"])
    return wrap("封面", "pp.", f"""
<div class="kicker reveal" style="left:var(--edge);top:190px">{META["chapter"]}</div>
<div class="en reveal" style="left:92px;top:250px;--d:.1s">{META["title_en"]}</div>
<h1 class="hero reveal" style="left:90px;top:370px;--d:.2s">{META["title"]}</h1>
<p class="small reveal" style="left:var(--edge);top:700px;--d:.35s">{esc(META["source"])}</p>
<div class="reveal" style="left:var(--edge);top:790px;--d:.45s;border-top:1px solid currentColor;padding-top:16px">{who}</div>""")


def statement(label, kicker, title, text="", note="", dark=False):
    """Big sentence + optional paragraph (question, core concept, conclusion)."""
    t = f'<p class="lede reveal" style="left:var(--edge);top:560px;width:1500px;--d:.3s">{text}</p>' if text else ""
    n = f'<div class="attr reveal" style="left:var(--edge);top:880px;width:1500px;--d:.45s"><span class="small">{note}</span></div>' if note else ""
    return wrap(label, kicker, f"""
<div class="kicker reveal" style="left:var(--edge);top:180px">{kicker}</div>
<h2 class="quote reveal" style="left:92px;top:240px;width:1600px;--d:.12s">{title}</h2>{t}{n}""", dark)


def cols(label, title, pages, items):
    """2–4 columns: items = [(small label, heading, body), ...]"""
    cells = "\n    ".join(
        f'<div class="col reveal" style="--d:{.1 + k * .12:.2f}s"><span class="num">{a}</span><h3>{b}</h3><p class="body">{c}</p></div>'
        for k, (a, b, c) in enumerate(items))
    return wrap(label, pages, f"""
<div class="frame">
  <div class="topbar reveal"><h2 class="head">{title}</h2><span class="mono">{pages}</span></div>
  <div class="cols" style="grid-template-columns:repeat({len(items)},1fr)">
    {cells}
  </div>
</div>""")


def ledger(label, title, pages, rows):
    """Rows of name + explanation: rows = [(name, text), ...]"""
    body = "\n    ".join(
        f'<div class="r reveal" style="--d:{.08 * (k + 1):.2f}s"><div class="name">{a}</div><div class="body">{b}</div></div>'
        for k, (a, b) in enumerate(rows))
    return wrap(label, pages, f"""
<div class="frame">
  <div class="topbar reveal"><h2 class="head">{title}</h2><span class="mono">{pages}</span></div>
  <div class="ledger">
    {body}
  </div>
</div>""")


def discussion(question, hint=""):
    h = f'<p class="lede reveal" style="left:var(--edge);top:640px;width:1500px;opacity:.85;--d:.35s">{hint}</p>' if hint else ""
    return wrap("討論問題", "FOR DISCUSSION", f"""
<div class="kicker reveal" style="left:var(--edge);top:200px">ONE QUESTION FOR THE CLASS</div>
<h2 class="quote reveal" style="left:92px;top:270px;width:1650px;--d:.15s">{question}</h2>{h}""", dark=True)


# ------------------------------------------------------------------
# SLIDES — the outline (replace every 〔…〕 with real content)
# ------------------------------------------------------------------
SLIDES = [
    cover(),
    statement("作者的問題", "THE QUESTION", "〔作者想回答的問題〕", "〔一兩句背景說明〕", "〔研究方法〕"),
    cols("背景", "〔背景或先決條件的標題〕", "pp.〔x–y〕", [
        ("01", "〔重點〕", "〔說明與書中例子〕"),
        ("02", "〔重點〕", "〔說明與書中例子〕"),
        ("03", "〔重點〕", "〔說明與書中例子〕"),
    ]),
    statement("核心概念", "KEY IDEA", "〔一句話說完這章的核心〕", "〔補充說明〕"),
    ledger("主要內容", "〔主要內容的標題〕", "pp.〔x–y〕", [
        ("〔項目〕", "〔說明〕"),
        ("〔項目〕", "〔說明〕"),
        ("〔項目〕", "〔說明〕"),
    ]),
    statement("結論", "CONCLUSION", "〔作者的結論〕", "〔一段說明〕", dark=True),
    ledger("對設計研究的啟發", "對設計研究的啟發", "MEANING", [
        ("〔概念〕", "〔對設計研究或自己的啟發〕"),
        ("〔概念〕", "〔對設計研究或自己的啟發〕"),
    ]),
    cols("台灣與亞洲脈絡", "放到台灣、亞洲，還成立嗎？", "IN CONTEXT", [
        ("成立的部分", "〔標題〕", "〔說明〕"),
        ("需要修正的部分", "〔標題〕", "〔說明〕"),
    ]),
    discussion("〔留給全班的一個問題〕"),
]


def page(title, slides):
    css = CSS.replace("@@BASE@@", BASE_CSS)
    for k, v in THEME.items():
        css = css.replace("@" + k, v)
    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{THEME["fonts"]}" rel="stylesheet">
<style>{css}</style>
</head>
<body data-page="slides">
<div class="home-zone"><a class="home-btn" href="index.html" title="回首頁">&larr;&nbsp;回首頁</a></div>
<div class="deck-viewport">
<main class="deck-stage" id="deckStage" aria-label="{title}">
{chr(10).join(slides)}
</main>
</div>
<div class="progress" id="progress"></div>
<script>{JS}</script>
</body>
</html>"""


name = META["title"].strip("〔〕") or "chapter"
(OUT / f"{name}-上台版.html").write_text(page(f'{META["title"]}｜上台版', SLIDES))
print("ok", len(SLIDES), "slides")
