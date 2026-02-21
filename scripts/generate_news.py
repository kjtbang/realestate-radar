"""
부동산 레이더 - 뉴스 자동 생성 스크립트
Claude API로 최신 부동산 뉴스를 검색 후 index.html 생성
"""

import anthropic
import json
import re
from datetime import datetime

client = anthropic.Anthropic()

PROMPT = """당신은 한국 부동산 뉴스 전문 큐레이터입니다.
지금 날짜 기준 최신 한국 부동산 뉴스를 웹에서 검색하여 12개를 찾아주세요.

포함할 카테고리:
- 아파트 시세·거래량 뉴스 (cat: news)
- 정책·규제·세금·금융 뉴스 (cat: policy)  
- 분양·청약·입주 뉴스 (cat: sale)

반드시 아래 JSON 배열 형식으로만 응답하세요. 마크다운 없이 JSON만 출력:

[
  {
    "title": "뉴스 제목 (원문 그대로)",
    "desc": "150자 이내 핵심 요약",
    "source": "언론사명",
    "url": "실제 기사 URL",
    "date": "YYYY-MM-DD",
    "cat": "news 또는 policy 또는 sale"
  }
]

중요:
- 실제 존재하는 뉴스만 포함 (허위 정보 금지)
- URL은 실제 접속 가능한 주소
- 오늘 기준 가장 최신 뉴스 우선
- 12개 정확히 반환"""


def fetch_news():
    print("Claude API로 뉴스 검색 중...")
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": PROMPT}]
    )

    # 텍스트 블록에서 JSON 추출
    full_text = ""
    for block in response.content:
        if block.type == "text":
            full_text += block.text

    match = re.search(r'\[[\s\S]*\]', full_text)
    if not match:
        raise ValueError("JSON 파싱 실패: " + full_text[:200])

    news_list = json.loads(match.group())
    print(f"✅ {len(news_list)}개 뉴스 수집 완료")
    return news_list


def badge_cls(cat):
    return {"news": "b-news", "policy": "b-policy", "sale": "b-sale"}.get(cat, "b-news")


def badge_label(cat):
    return {"news": "🏠 시황", "policy": "📋 정책", "sale": "🏗️ 분양"}.get(cat, "🏠 뉴스")


def build_html(news_list):
    now = datetime.now()
    now_str = now.strftime("%Y.%m.%d %H:%M")
    date_str = now.strftime("%Y-%m-%d")

    news_js = json.dumps(news_list, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>부동산 레이더 — 실시간 뉴스</title>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Noto+Sans+KR:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  :root{{
    --bg:#0d1117;--surface:#161b22;--surface2:#1c2128;--border:#30363d;
    --text:#e6edf3;--muted:#7d8590;--accent:#f0883e;--green:#3fb950;
    --blue:#58a6ff;--red:#f85149;
  }}
  body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);font-weight:300;min-height:100vh}}

  header{{position:sticky;top:0;z-index:100;background:rgba(13,17,23,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:60px}}
  .logo{{display:flex;align-items:center;gap:12px}}
  .logo-icon{{width:32px;height:32px;background:var(--accent);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}}
  .logo-text{{font-family:'Black Han Sans',sans-serif;font-size:20px}}
  .logo-text span{{color:var(--accent)}}
  .header-right{{display:flex;align-items:center;gap:14px}}
  .live-badge{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--green);letter-spacing:.1em;text-transform:uppercase}}
  .live-dot{{width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.4;transform:scale(.7)}}}}
  .update-time{{font-size:12px;color:var(--muted)}}

  .hero{{background:linear-gradient(135deg,#1a1f2e 0%,#0d1117 100%);border-bottom:1px solid var(--border);padding:36px 32px 28px;position:relative;overflow:hidden}}
  .hero::before{{content:'';position:absolute;top:-80px;right:-80px;width:350px;height:350px;background:radial-gradient(circle,rgba(240,136,62,.07) 0%,transparent 70%);pointer-events:none}}
  .hero-title{{font-family:'Black Han Sans',sans-serif;font-size:clamp(26px,4vw,44px);letter-spacing:-.02em;line-height:1.1;margin-bottom:10px}}
  .hero-title span{{color:var(--accent)}}
  .hero-sub{{font-size:13px;color:var(--muted);margin-bottom:24px}}
  .stats-bar{{display:flex;gap:32px;flex-wrap:wrap}}
  .stat-item{{display:flex;flex-direction:column;gap:3px}}
  .stat-value{{font-family:'Black Han Sans',sans-serif;font-size:20px;color:var(--accent)}}
  .stat-label{{font-size:11px;color:var(--muted);letter-spacing:.05em}}

  .filter-bar{{padding:12px 32px;border-bottom:1px solid var(--border);display:flex;gap:8px;flex-wrap:wrap;align-items:center;background:var(--surface)}}
  .filter-label{{font-size:11px;color:var(--muted);letter-spacing:.1em;text-transform:uppercase;margin-right:4px}}
  .filter-btn{{padding:5px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--muted);font-family:'Noto Sans KR',sans-serif;font-size:12px;cursor:pointer;transition:all .2s}}
  .filter-btn.active{{background:var(--accent);border-color:var(--accent);color:#000;font-weight:500}}
  .filter-btn:hover:not(.active){{border-color:var(--muted);color:var(--text)}}

  .main{{display:grid;grid-template-columns:1fr 290px;gap:24px;max-width:1280px;margin:0 auto;padding:24px 32px}}
  .section-label{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:14px;display:flex;align-items:center;gap:10px}}
  .section-label::after{{content:'';flex:1;height:1px;background:var(--border)}}

  .featured-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:24px 28px;margin-bottom:14px;cursor:pointer;transition:all .2s;position:relative;overflow:hidden;text-decoration:none;display:block;color:inherit}}
  .featured-card::before{{content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent)}}
  .featured-card:hover{{border-color:var(--accent);transform:translateY(-1px)}}

  .card-badge{{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:4px;font-size:11px;font-weight:500;margin-bottom:12px}}
  .b-news{{background:rgba(240,136,62,.15);color:var(--accent)}}
  .b-policy{{background:rgba(88,166,255,.15);color:var(--blue)}}
  .b-sale{{background:rgba(63,185,80,.15);color:var(--green)}}

  .card-title{{font-size:17px;font-weight:500;line-height:1.55;margin-bottom:9px}}
  .card-desc{{font-size:13px;color:var(--muted);line-height:1.9;margin-bottom:14px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
  .card-meta{{display:flex;align-items:center;gap:14px;font-size:12px;color:var(--muted)}}
  .source-tag{{background:var(--surface2);border:1px solid var(--border);padding:2px 8px;border-radius:4px;font-size:11px}}

  .news-list{{display:flex;flex-direction:column;gap:2px}}
  .news-item{{background:var(--surface);border:1px solid transparent;border-radius:8px;padding:14px 18px;cursor:pointer;transition:all .2s;display:grid;grid-template-columns:1fr auto;gap:12px;align-items:start;text-decoration:none;color:inherit}}
  .news-item:hover{{background:var(--surface2);border-color:var(--border)}}
  .news-item-title{{font-size:13.5px;line-height:1.65;margin-bottom:5px}}
  .news-item-meta{{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--muted)}}
  .news-item-time{{font-size:11px;color:var(--muted);white-space:nowrap;padding-top:2px}}

  .sidebar{{display:flex;flex-direction:column;gap:16px}}
  .sidebar-card{{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px}}
  .sidebar-title{{font-size:13px;font-weight:500;margin-bottom:14px;display:flex;align-items:center;gap:8px}}

  .price-row{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)}}
  .price-row:last-child{{border-bottom:none}}
  .up{{color:var(--red)}}.dn{{color:var(--blue)}}.flat{{color:var(--muted)}}

  .kw-wrap{{display:flex;flex-wrap:wrap;gap:6px}}
  .kw-tag{{padding:4px 11px;background:var(--surface2);border:1px solid var(--border);border-radius:20px;font-size:12px;color:var(--muted);cursor:pointer;transition:all .2s}}
  .kw-tag:hover{{border-color:var(--accent);color:var(--accent)}}

  .auto-note{{background:rgba(63,185,80,.08);border:1px solid rgba(63,185,80,.2);border-radius:8px;padding:10px 14px;font-size:12px;color:var(--green);line-height:1.7;margin-bottom:16px}}

  @keyframes fadeUp{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
  .fade{{animation:fadeUp .35s ease forwards}}

  @media(max-width:900px){{.main{{grid-template-columns:1fr;padding:16px}}.sidebar{{display:none}}header,.hero,.filter-bar{{padding-left:16px;padding-right:16px}}}}
  footer{{border-top:1px solid var(--border);padding:20px 32px;text-align:center;font-size:11px;color:var(--muted);margin-top:32px}}
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="logo-icon">🏠</div>
    <span class="logo-text">부동산 <span>레이더</span></span>
  </div>
  <div class="header-right">
    <div class="live-badge"><div class="live-dot"></div>자동 업데이트</div>
    <span class="update-time">🕐 {now_str} 수집</span>
  </div>
</header>

<div class="hero">
  <h1 class="hero-title">한국 부동산 <span>실시간</span> 뉴스</h1>
  <p class="hero-sub">Claude AI가 5분마다 자동 수집 · 최신 부동산 뉴스 · 정책/규제 · 분양 정보</p>
  <div class="stats-bar">
    <div class="stat-item"><span class="stat-value">{len(news_list)}건</span><span class="stat-label">수집된 뉴스</span></div>
    <div class="stat-item"><span class="stat-value">{now_str}</span><span class="stat-label">마지막 업데이트</span></div>
    <div class="stat-item"><span class="stat-value">Claude AI</span><span class="stat-label">검색 엔진</span></div>
  </div>
</div>

<div class="filter-bar">
  <span class="filter-label">카테고리</span>
  <button class="filter-btn active" onclick="applyFilter('all',this)">전체</button>
  <button class="filter-btn" onclick="applyFilter('news',this)">🏠 시황/시세</button>
  <button class="filter-btn" onclick="applyFilter('policy',this)">📋 정책/규제</button>
  <button class="filter-btn" onclick="applyFilter('sale',this)">🏗️ 분양/청약</button>
</div>

<div class="main">
  <div>
    <div class="auto-note">
      ✅ GitHub Actions가 5분마다 자동으로 Claude AI에게 최신 뉴스를 수집해 이 페이지를 업데이트합니다.
      뉴스 클릭 시 원문으로 이동합니다.
    </div>
    <p class="section-label">🔥 주요 뉴스</p>
    <div id="featured"></div>
    <p class="section-label" style="margin-top:22px">📰 전체 뉴스</p>
    <div class="news-list" id="list"></div>
  </div>

  <div class="sidebar">
    <div class="sidebar-card">
      <div class="sidebar-title">📊 아파트 주간 시세</div>
      <div class="price-row"><span>서울 전체</span><span class="up">▲ 0.04%</span></div>
      <div class="price-row"><span>강남 3구</span><span class="up">▲ 0.07%</span></div>
      <div class="price-row"><span>경기도</span><span class="dn">▼ 0.02%</span></div>
      <div class="price-row"><span>인천</span><span class="flat">— 0.00%</span></div>
      <div class="price-row"><span>부산</span><span class="dn">▼ 0.03%</span></div>
      <p style="font-size:10px;color:var(--muted);margin-top:8px">한국부동산원 기준</p>
    </div>
    <div class="sidebar-card">
      <div class="sidebar-title">🔍 주요 키워드</div>
      <div class="kw-wrap">
        <span class="kw-tag" onclick="filterKw('재건축')">#재건축</span>
        <span class="kw-tag" onclick="filterKw('청약')">#청약</span>
        <span class="kw-tag" onclick="filterKw('전세')">#전세</span>
        <span class="kw-tag" onclick="filterKw('금리')">#금리</span>
        <span class="kw-tag" onclick="filterKw('DSR')">#DSR</span>
        <span class="kw-tag" onclick="filterKw('규제')">#규제</span>
        <span class="kw-tag" onclick="filterKw('강남')">#강남</span>
        <span class="kw-tag" onclick="filterKw('분양')">#분양</span>
      </div>
    </div>
    <div class="sidebar-card">
      <div class="sidebar-title">⚙️ 자동화 정보</div>
      <p style="font-size:12px;color:var(--muted);line-height:2">
        🤖 수집 엔진: Claude Sonnet 4<br>
        ⏱️ 업데이트 주기: 5분<br>
        🔧 자동화: GitHub Actions<br>
        🚀 배포: Netlify<br>
        📅 마지막 수집: {now_str}
      </p>
    </div>
  </div>
</div>

<footer>
  부동산 레이더 · Claude AI 자동 수집 · GitHub Actions · Netlify · 뉴스 저작권은 각 언론사에 있습니다
</footer>

<script>
const NEWS = {news_js};
let currentFilter = 'all';
let currentKw = '';

const badgeCls = c => ({{news:'b-news',policy:'b-policy',sale:'b-sale'}}[c]||'b-news');
const badgeLbl = c => ({{news:'🏠 시황',policy:'📋 정책',sale:'🏗️ 분양'}}[c]||'🏠');

function applyFilter(f, btn) {{
  currentFilter = f; currentKw = '';
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  render();
}}
function filterKw(kw) {{
  currentKw = kw; currentFilter = 'all';
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.filter-btn')[0].classList.add('active');
  render();
}}
function render() {{
  let data = NEWS;
  if (currentFilter !== 'all') data = data.filter(n => n.cat === currentFilter);
  if (currentKw) data = data.filter(n => n.title.includes(currentKw) || n.desc.includes(currentKw));

  const feat = data[0];
  const fa = document.getElementById('featured');
  if (!feat) {{ fa.innerHTML = '<p style="color:var(--muted);font-size:13px;padding:16px 0">해당 항목이 없습니다.</p>'; document.getElementById('list').innerHTML=''; return; }}

  fa.innerHTML = `<a class="featured-card fade" href="${{feat.url||'#'}}" target="_blank" rel="noopener">
    <div class="card-badge ${{badgeCls(feat.cat)}}">${{badgeLbl(feat.cat)}}</div>
    <h2 class="card-title">${{feat.title}}</h2>
    <p class="card-desc">${{feat.desc}}</p>
    <div class="card-meta"><span class="source-tag">📰 ${{feat.source}}</span><span>${{feat.date}}</span></div>
  </a>`;

  document.getElementById('list').innerHTML = data.slice(1).map((n,i) => `
    <a class="news-item fade" href="${{n.url||'#'}}" target="_blank" rel="noopener" style="animation-delay:${{i*.04}}s">
      <div>
        <div class="news-item-title">${{n.title}}</div>
        <div class="news-item-meta">
          <span class="card-badge ${{badgeCls(n.cat)}}" style="padding:2px 7px;margin:0;font-size:10px">${{badgeLbl(n.cat)}}</span>
          <span>${{n.source}}</span>
        </div>
      </div>
      <div class="news-item-time">${{n.date}}</div>
    </a>`).join('');
}}
render();
</script>
</body>
</html>"""
    return html


def main():
    news_list = fetch_news()
    html = build_html(news_list)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ index.html 생성 완료")


if __name__ == "__main__":
    main()
