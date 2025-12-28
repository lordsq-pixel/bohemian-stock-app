# new-stock.py
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="KOREA STOCK Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 0.8rem; padding-bottom: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## ⚙️ 연결 설정")
    st.caption("Netlify Functions를 쓰는 경우, 네 Netlify 사이트 주소를 넣으면 그쪽으로 API 호출합니다.")
    api_origin = st.text_input(
        "API Origin (예: https://너의사이트.netlify.app)",
        value="",
        placeholder="비우면 현재 주소(location.origin)를 사용",
    ).strip()
    st.caption("• 로컬 Streamlit이면 비워두면 `/.netlify/functions/...`가 없어서 에러가 날 수 있어요.\n"
               "• Netlify에 배포된 사이트 주소를 넣으면 정상 호출됩니다.")

API_ORIGIN_JS = api_origin.replace('"', '\\"')

html = f"""
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>KOREA STOCK Radar</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    :root{{
      --bg:#0b1220;
      --panel:#0f1a2f;
      --card:rgba(255,255,255,.04);
      --border:rgba(255,255,255,.08);
      --text:#e7eefc;
      --muted:#9fb0d0;
      --green:#00d0a3;
      --red:#ff4d6d;
      --amber:#fbbf24;
      --shadow: 0 18px 60px -26px rgba(0,0,0,.75);
      --radius:16px;
    }}
    body{{
      background:
        radial-gradient(1200px 600px at 20% 0%, rgba(0,208,163,.10), transparent 60%),
        radial-gradient(900px 500px at 90% 10%, rgba(59,130,246,.10), transparent 55%),
        var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Pretendard", "Noto Sans KR", "Segoe UI", Roboto, Arial;
    }}
    .card{{
      background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}
    .muted{{ color: var(--muted); }}
    .badge{{
      display:inline-flex; align-items:center; gap:8px;
      padding: 6px 10px; border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.03);
      font-size: 12px; color: var(--muted);
    }}
    .dot{{ width:8px; height:8px; border-radius:50%; background: rgba(159,176,208,.7); }}
    .btn{{
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.10);
      background: linear-gradient(135deg, rgba(0,208,163,.18), rgba(59,130,246,.14));
      padding: .7rem 1rem;
      box-shadow: var(--shadow);
      font-weight: 900;
      font-size: 14px;
    }}
    .btn:hover{{ transform: translateY(-1px); }}
    table{{ border-collapse: collapse; width: 100%; }}
    th, td{{ border-bottom: 1px solid rgba(255,255,255,.08); padding: 10px 8px; font-size: 13px; }}
    th{{ color: var(--muted); text-align:left; font-weight: 900; }}
    .toast{{
      position: fixed; right: 16px; bottom: 16px;
      max-width: 560px;
      background: rgba(15,26,47,.92);
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 14px;
      box-shadow: var(--shadow);
      padding: 12px 12px;
      display: none;
      z-index: 50;
    }}
    .toast.show{{ display:block; }}
    .pill{{
      display:inline-flex; align-items:center; gap:6px;
      padding:4px 10px; border-radius: 999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      font-size:12px; color: var(--muted);
    }}
    .good{{ color: var(--green); font-weight: 900; }}
    .bad{{ color: var(--red); font-weight: 900; }}
    .warn{{ color: var(--amber); font-weight: 900; }}
    .mono{{ font-variant-numeric: tabular-nums; }}
  </style>
</head>
<body class="min-h-screen">
  <div class="max-w-6xl mx-auto px-4 py-5">
    <div class="card p-4">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div class="text-xl font-black tracking-tight">📡 KOREA STOCK Radar.</div>
          <div class="text-xs muted mt-1">
            거래량 순위 후보 → 1~2초 폴링 → 점수 상위 1~3개만 알림(ENTRY) + 추적(목표권/EXIT)
          </div>
        </div>
        <div class="badge"><span class="dot"></span><span id="clock"></span></div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-10 gap-3 mt-4">
        <div class="card p-3 md:col-span-2">
          <div class="text-xs muted">시장</div>
          <select id="market" class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2">
            <option value="KOSPI">KOSPI</option>
            <option value="KOSDAQ" selected>KOSDAQ</option>
          </select>
        </div>

        <div class="card p-3">
          <div class="text-xs muted">히든 개수</div>
          <select id="topK" class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2">
            <option value="1">1개</option>
            <option value="2" selected>2개</option>
            <option value="3">3개</option>
          </select>
        </div>

        <div class="card p-3">
          <div class="text-xs muted">순위 TopN</div>
          <input id="topN" type="number" min="10" max="30" value="30"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">감시 N</div>
          <input id="watchN" type="number" min="5" max="30" value="15"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">폴링(초)</div>
          <input id="pollSec" type="number" min="0.8" max="5" step="0.1" value="1.5"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">유입가속 최소(x)</div>
          <input id="minFlow" type="number" min="1.0" max="4.0" step="0.05" value="1.20"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">모멘텀 최소(60s, %)</div>
          <input id="minMom60" type="number" min="-2" max="5" step="0.05" value="0.20"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">확인(초)</div>
          <input id="confirmSec" type="number" min="2" max="10" step="0.5" value="3.5"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">쿨다운(분)</div>
          <input id="cooldownMin" type="number" min="1" max="30" value="7"
            class="mt-2 w-full bg-white/5 border border-white/10 rounded-xl px-3 py-2" />
        </div>

        <div class="card p-3">
          <div class="text-xs muted">상태</div>
          <div class="mt-2 flex flex-wrap items-center gap-2">
            <span class="pill" id="state">OFF</span>
            <span class="pill" id="rate">-</span>
          </div>
        </div>
      </div>

      <div class="flex flex-wrap gap-3 mt-4">
        <button id="btnPerm" class="btn">🔔 알림 허용</button>
        <button id="btnStart" class="btn">▶ 레이더 시작</button>
        <button id="btnStop" class="btn">⏹ 레이더 정지</button>
        <button id="btnClear" class="btn">🧹 로그/추적 초기화</button>
      </div>
    </div>

    <div class="card p-4 mt-4">
      <div class="flex items-center justify-between">
        <div class="font-extrabold">🎯 히든 후보(실시간)</div>
        <div class="text-xs muted" id="status">대기 중</div>
      </div>
      <div class="overflow-auto mt-3">
        <table>
          <thead>
            <tr>
              <th>순위</th>
              <th>종목</th>
              <th>현재가</th>
              <th>등락</th>
              <th>15s/60s MOM</th>
              <th>유입가속</th>
              <th>거래대금(추정)</th>
              <th>점수</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody id="rows"></tbody>
        </table>
      </div>
      <div class="text-xs muted mt-2">
        상태: <span class="good">READY</span> → <span class="warn">CONFIRM</span> → <span class="good">ENTRY</span>(추적) → <span class="bad">EXIT</span>(청산 시그널)
      </div>
    </div>

    <div class="card p-4 mt-4">
      <div class="font-extrabold">🛰️ 추적 중(ENTRY 이후)</div>
      <div class="text-xs muted mt-1">+2%/+3% 목표권 알림 + EXIT(둔화/유입붕괴/트레일링) 감시</div>
      <div class="overflow-auto mt-3">
        <table>
          <thead>
            <tr>
              <th>종목</th>
              <th>진입가</th>
              <th>현재가</th>
              <th>수익률</th>
              <th>유입가속</th>
              <th>15s/60s MOM</th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody id="watchRows"></tbody>
        </table>
      </div>
    </div>

    <div class="card p-4 mt-4">
      <div class="font-extrabold">🔔 알림 로그</div>
      <div id="log" class="mt-3 space-y-2"></div>
    </div>
  </div>

  <div id="toast" class="toast">
    <div class="font-extrabold" id="toastTitle"></div>
    <div class="text-xs muted mt-1" id="toastBody"></div>
  </div>

<script>
  // Streamlit에서 Netlify Functions를 쓰려면, 필요 시 아래 API_ORIGIN에 Netlify 사이트 주소를 넣어 호출 가능
  const API_ORIGIN = "{API_ORIGIN_JS}".trim();

  const fmt = (n) => (Number.isFinite(n) ? n.toLocaleString("ko-KR") : "-");
  const fmt2 = (n) => (Number.isFinite(n) ? n.toFixed(2) : "-");
  const pct = (n) => (Number.isFinite(n) ? (n>=0?"+":"") + n.toFixed(2) + "%" : "-");
  const kstNow = () => new Date().toLocaleString("ko-KR", {{ hour12:false }});

  function toast(title, body){{
    const t = document.getElementById("toast");
    document.getElementById("toastTitle").textContent = title;
    document.getElementById("toastBody").textContent = body;
    t.classList.add("show");
    setTimeout(()=>t.classList.remove("show"), 4200);
  }}

  function notify(title, body){{
    toast(title, body);
    pushLog(title, body);
    if("Notification" in window && Notification.permission === "granted"){{
      new Notification(title, {{ body }});
    }}
  }}

  function pushLog(title, body){{
    const log = document.getElementById("log");
    const div = document.createElement("div");
    div.className = "card p-3";
    div.innerHTML = `
      <div class="flex items-center justify-between gap-2 flex-wrap">
        <div class="font-extrabold">${{title}}</div>
        <div class="badge"><span class="dot"></span>${{kstNow()}}</div>
      </div>
      <div class="text-xs muted mt-1">${{body}}</div>
    `;
    log.prepend(div);
  }}

  async function api(action, params={{}}){{
    const origin = API_ORIGIN || location.origin;
    const u = new URL("/.netlify/functions/kis", origin);
    u.searchParams.set("action", action);
    Object.entries(params).forEach(([k,v])=>u.searchParams.set(k, String(v)));
    const r = await fetch(u.toString(), {{ headers: {{ "accept":"application/json" }} }});
    const d = await r.json().catch(()=> ({{ ok:false, error:"JSON parse failed" }}));
    if(!r.ok || !d.ok) throw new Error(d.error || `HTTP ${{r.status}}`);
    return d;
  }}

  let running = false;
  let timer = null;
  let tickCount = 0;
  let rateTimer = null;

  const meta = new Map();
  const last = new Map();
  const series = new Map();
  const stateFlag = new Map();
  const pending = new Map();
  const lastAlert = new Map();
  const watch = new Map();

  function canAlert(code, cooldownMin){{
    const now = Date.now();
    const prev = lastAlert.get(code) || 0;
    if(now - prev >= cooldownMin*60*1000){{
      lastAlert.set(code, now);
      return true;
    }}
    return false;
  }}

  function pushPoint(code, p, chgRate){{
    if(!series.has(code)) series.set(code, []);
    const arr = series.get(code);
    const prev = arr.length ? arr[arr.length-1].p : p;
    const amtEst = Math.abs(p - prev) * p;

    arr.push({{ ts: Date.now(), p, amtEst, chgRate }});
    const cutoff = Date.now() - 210*1000;
    while(arr.length && arr[0].ts < cutoff) arr.shift();
  }}

  function win(code, sec){{
    const arr = series.get(code) || [];
    const cutoff = Date.now() - sec*1000;
    const w = arr.filter(x => x.ts >= cutoff);
    if(w.length < 2) return null;

    const first = w[0].p;
    const lastp = w[w.length-1].p;
    const mom = (lastp/first - 1) * 100;

    const amt = w.reduce((a,x)=>a + x.amtEst, 0);
    return {{ mom, amt, n:w.length, first, last:lastp }};
  }}

  function clamp(x,a,b){{ return Math.max(a, Math.min(b,x)); }}
  function log2(x){{ return Math.log(x)/Math.log(2); }}

  function scoreCode(code){{
    const s15 = win(code, 15);
    const s60 = win(code, 60);
    const s180 = win(code, 180);
    const L = last.get(code);
    if(!L || !s60) return {{ ok:false, score:-1e9, why:"데이터 부족" }};

    const mom15 = s15 ? s15.mom : 0;
    const mom60 = s60.mom;

    const avg60 = s180 ? (s180.amt/3) : s60.amt;
    const flowRatio = s60.amt / (avg60 + 1e-12);

    let heat = 0;
    if(mom15 > 0.8) heat += 0.8;
    if(mom60 > 2.2) heat += 1.0;

    let score = 0;
    score += 1.4 * clamp(mom60/1.2, -1, 1.6);
    score += 1.0 * clamp(mom15/0.6, -1, 1.6);
    score += 1.2 * clamp((mom15 - mom60*0.25)/0.25, -1, 1.8);

    const flowScore = clamp(log2(flowRatio + 1), 0, 2.6);
    score += 1.6 * flowScore;

    score += 0.35 * clamp((L.chgRate||0)/3.0, -1, 1.5);
    score -= heat;

    return {{
      ok:true,
      score,
      p:L.p,
      chgRate:L.chgRate,
      mom15, mom60,
      flowRatio,
      amt60:s60.amt,
    }};
  }}

  function entryGate(r){{
    const minFlow = parseFloat(document.getElementById("minFlow").value || "1.2");
    const minMom60 = parseFloat(document.getElementById("minMom60").value || "0.2");

    if(r.flowRatio < minFlow) return {{ pass:false, why:`유입가속 부족(x${{fmt2(r.flowRatio)}})` }};
    if(r.mom60 < minMom60) return {{ pass:false, why:`60s 모멘텀 부족(${{pct(r.mom60)}})` }};
    if(r.mom15 < -0.05) return {{ pass:false, why:`15s 둔화(${{pct(r.mom15)}})` }};
    return {{ pass:true, why:"OK" }};
  }}

  function exitCheck(code){{
    const w = watch.get(code);
    if(!w) return;

    const r = scoreCode(code);
    if(!r.ok) return;

    const p = r.p;
    const entry = w.entryPrice;
    const ret = (p/entry - 1) * 100;

    if(!Number.isFinite(w.maxP) || p > w.maxP) w.maxP = p;

    if(!w.hit2 && ret >= 2.0){{
      w.hit2 = true;
      notify(`🎯 목표권 +2%: ${{code}}`, `${{fmt(entry)}} → ${{fmt(p)}} (${{pct(ret)}})`);
    }}
    if(!w.hit3 && ret >= 3.0){{
      w.hit3 = true;
      notify(`🏁 목표권 +3%: ${{code}}`, `${{fmt(entry)}} → ${{fmt(p)}} (${{pct(ret)}})`);
    }}

    const triggers = [];
    if(r.mom15 < -0.05) triggers.push(`모멘텀 둔화(15s ${{pct(r.mom15)}})`);
    if(r.mom60 < 0.10 && ret > 0.8) triggers.push(`60s 약화(${{pct(r.mom60)}})`);
    if(r.flowRatio < 1.05) triggers.push(`유입 붕괴(x${{fmt2(r.flowRatio)}})`);

    const peakRet = (w.maxP/entry - 1) * 100;
    const drawdown = peakRet - ret;
    if(peakRet >= 2.2 && drawdown >= 0.9) triggers.push(`트레일링(DD ${{fmt2(drawdown)}}%)`);

    const now = Date.now();
    if(triggers.length){{
      if(!w.lastExitTs || (now - w.lastExitTs) > 60*1000){{
        w.lastExitTs = now;
        stateFlag.set(code, "EXIT");
        notify(`⏹ EXIT 시그널: ${{code}}`, `수익률 ${{pct(ret)}} | ${{triggers.slice(0,3).join(" / ")}}`);
      }}
    }}
  }}

  function renderMain(top){{
    const tbody = document.getElementById("rows");
    tbody.innerHTML = "";
    if(!top.length){{
      tbody.innerHTML = `<tr><td colspan="9" class="muted">조건 충족 종목이 없습니다(데이터 쌓이는 중일 수 있음).</td></tr>`;
      return;
    }}

    top.forEach((r,i)=>{{
      const gate = entryGate(r);
      const st = stateFlag.get(r.code) || (gate.pass ? "READY" : "-");
      if(!stateFlag.has(r.code) && gate.pass) stateFlag.set(r.code, "READY");

      const tr = document.createElement("tr");
      const cls = r.mom60 >= 0 ? "good" : "bad";
      tr.innerHTML = `
        <td class="muted">${{i+1}}</td>
        <td><div class="font-extrabold">${{r.code}}</div><div class="text-xs muted">(${{r.name||"name?"}})</div></td>
        <td class="mono">${{fmt(r.p)}}</td>
        <td class="${{(r.chgRate||0)>=0?'good':'bad'}} mono">${{pct(r.chgRate||0)}}</td>
        <td class="${{cls}} mono">${{pct(r.mom15)}} / ${{pct(r.mom60)}}</td>
        <td class="mono">x${{fmt2(r.flowRatio)}}</td>
        <td class="mono">${{fmt2(r.amt60||0)}}</td>
        <td class="font-extrabold mono">${{fmt2(r.score)}}</td>
        <td class="${{st==='READY'||st==='ENTRY'?'good':(st==='CONFIRM'?'warn':(st==='EXIT'?'bad':'muted'))}}">
          ${{st}}${{gate.pass ? "" : " (NO)"}}
        </td>
      `;
      tbody.appendChild(tr);
    }});
  }}

  function renderWatch(){{
    const tbody = document.getElementById("watchRows");
    tbody.innerHTML = "";
    const entries = Array.from(watch.entries());
    if(!entries.length){{
      tbody.innerHTML = `<tr><td colspan="7" class="muted">추적 중 종목이 없습니다(ENTRY 발생 시 자동 등록).</td></tr>`;
      return;
    }}

    for(const [code, w] of entries){{
      const r = scoreCode(code);
      if(!r.ok) continue;

      const p = r.p;
      const ret = (p/w.entryPrice - 1) * 100;
      const st = stateFlag.get(code) || "ENTRY";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><div class="font-extrabold">${{code}}</div><div class="text-xs muted">${{meta.get(code)?.name||""}}</div></td>
        <td class="mono">${{fmt(w.entryPrice)}}</td>
        <td class="mono">${{fmt(p)}}</td>
        <td class="${{ret>=0?'good':'bad'}} mono">${{pct(ret)}}</td>
        <td class="mono">x${{fmt2(r.flowRatio)}}</td>
        <td class="mono">${{pct(r.mom15)}} / ${{pct(r.mom60)}}</td>
        <td class="${{st==='EXIT'?'bad':'good'}}">${{st}}</td>
      `;
      tbody.appendChild(tr);
    }}
  }}

  function scheduleEntry(r){{
    const confirmSec = parseFloat(document.getElementById("confirmSec").value || "3.5");
    const cooldownMin = parseInt(document.getElementById("cooldownMin").value,10) || 7;

    const gate = entryGate(r);
    if(!gate.pass) return;
    if(!canAlert(r.code, cooldownMin)) return;
    if(pending.has(r.code)) return;

    stateFlag.set(r.code, "CONFIRM");
    const tid = setTimeout(()=>{{
      pending.delete(r.code);

      const rr = scoreCode(r.code);
      if(!rr.ok){{ stateFlag.set(r.code, "READY"); return; }}

      const gate2 = entryGate(rr);
      if(!gate2.pass){{ stateFlag.set(r.code, "READY"); return; }}

      stateFlag.set(r.code, "ENTRY");
      const entryPrice = rr.p;
      watch.set(r.code, {{ entryPrice, maxP: entryPrice, hit2:false, hit3:false, lastExitTs:0 }});

      notify(`✅ ENTRY 시그널: ${{r.code}}`, `진입가 ${{fmt(entryPrice)}} | 유입 x${{fmt2(rr.flowRatio)}} | MOM60 ${{pct(rr.mom60)}} | 등락 ${{pct(rr.chgRate||0)}}`);
    }}, confirmSec*1000);

    pending.set(r.code, tid);
  }}

  function pickTop(){{
    const topK = parseInt(document.getElementById("topK").value,10);
    const scored = [];

    for(const code of last.keys()){{
      const r = scoreCode(code);
      if(!r.ok) continue;
      const name = meta.get(code)?.name || "";
      scored.push({{ code, name, ...r }});
    }}
    scored.sort((a,b)=> b.score - a.score);
    return scored.slice(0, topK);
  }}

  async function refreshUniverse(){{
    const market = document.getElementById("market").value;
    const topN = parseInt(document.getElementById("topN").value,10) || 30;
    const watchN = parseInt(document.getElementById("watchN").value,10) || 15;

    document.getElementById("status").textContent = "거래량 순위 후보 구성 중…";

    const d = await api("rank_price", {{ market, topN, watchN }});
    const codes = d.pickCodes || [];

    for(const x of (d.rank||[])){{
      const code = String(x.stck_shrn_iscd || x.iscd || x.code || x.ticker || "").padStart(6,"0");
      if(!code || code === "000000") continue;
      const name = x.hts_kor_isnm || x.kor_isnm || x.name || x.stck_issu_abbrv_name || "";
      if(!meta.has(code)) meta.set(code, {{}});
      if(name) meta.get(code).name = name;
    }}

    for(const it of (d.prices||[])){{
      const code = it.code;
      const raw = it.raw || {{}};
      const p = Number(raw.stck_prpr || raw.last || raw.prpr || raw.price || NaN);
      const chgRate = Number(raw.prdy_ctrt || raw.change_rate || raw.rate || NaN);
      if(Number.isFinite(p)){{
        last.set(code, {{ p, chgRate, ts: Date.now() }});
        pushPoint(code, p, chgRate);
      }}
    }}

    document.getElementById("status").textContent = `후보 ${{codes.length}}개 준비 완료. 폴링 시작…`;
    return codes;
  }}

  async function pollPrices(codes){{
    const market = document.getElementById("market").value;
    const chunk = codes.slice(0, 30);

    const d = await api("price", {{ market, codes: chunk.join(",") }});

    for(const it of (d.prices||[])){{
      const code = it.code;
      const raw = it.raw || {{}};
      const p = Number(raw.stck_prpr || raw.last || raw.prpr || raw.price || NaN);
      const chgRate = Number(raw.prdy_ctrt || raw.change_rate || raw.rate || NaN);

      if(Number.isFinite(p)){{
        last.set(code, {{ p, chgRate, ts: Date.now() }});
        pushPoint(code, p, chgRate);
      }}
    }}
  }}

  async function start(){{
    if(running) return;
    running = true;
    document.getElementById("state").textContent = "ON";

    let codes = [];
    try{{
      codes = await refreshUniverse();
    }}catch(e){{
      running = false;
      document.getElementById("state").textContent = "OFF";
      document.getElementById("status").textContent = "시작 실패";
      notify("시작 실패", e.message);
      return;
    }}

    tickCount = 0;
    if(rateTimer) clearInterval(rateTimer);
    rateTimer = setInterval(()=>{{
      document.getElementById("rate").textContent = `TICK: ${{tickCount}}/s`;
      tickCount = 0;
    }}, 1000);

    const loop = async ()=>{{
      if(!running) return;

      try{{
        await pollPrices(codes);
        tickCount++;

        const top = pickTop();
        renderMain(top);

        for(const r of top) scheduleEntry(r);
        for(const code of watch.keys()) exitCheck(code);

        renderWatch();

        if(!start._lastRebuild) start._lastRebuild = Date.now();
        if(Date.now() - start._lastRebuild > 60*1000){{
          start._lastRebuild = Date.now();
          codes = await refreshUniverse();
        }}

      }}catch(e){{
        document.getElementById("status").textContent = `에러: ${{e.message}}`;
      }}finally{{
        const pollSec = parseFloat(document.getElementById("pollSec").value || "1.5");
        timer = setTimeout(loop, Math.max(0.8, pollSec)*1000);
      }}
    }};

    document.getElementById("status").textContent = "실시간 폴링 중… (초기 60초 데이터 쌓이는 중)";
    loop();
  }}

  function stop(){{
    running = false;
    document.getElementById("state").textContent = "OFF";
    document.getElementById("rate").textContent = "-";
    if(timer) clearTimeout(timer), timer = null;
    if(rateTimer) clearInterval(rateTimer), rateTimer = null;
    for(const [,tid] of pending.entries()){{ try{{ clearTimeout(tid); }}catch(_){{}} }}
    pending.clear();
    document.getElementById("status").textContent = "정지됨";
    toast("레이더 정지", "폴링을 멈췄습니다.");
  }}

  document.getElementById("btnPerm").addEventListener("click", async ()=>{{
    if(!("Notification" in window)){{ toast("알림 미지원", "이 브라우저는 Notification을 지원하지 않습니다."); return; }}
    const p = await Notification.requestPermission();
    toast("알림 권한", `현재 상태: ${{p}}`);
  }});

  document.getElementById("btnStart").addEventListener("click", start);
  document.getElementById("btnStop").addEventListener("click", stop);

  document.getElementById("btnClear").addEventListener("click", ()=>{{
    document.getElementById("log").innerHTML = "";
    lastAlert.clear();
    stateFlag.clear();
    watch.clear();
    for(const [,tid] of pending.entries()){{ try{{ clearTimeout(tid); }}catch(_){{}} }}
    pending.clear();
    toast("초기화", "로그/상태/추적/확인예약을 초기화했습니다.");
  }});

  setInterval(()=>{{ document.getElementById("clock").textContent = kstNow(); }}, 500);
  document.getElementById("clock").textContent = kstNow();
  document.getElementById("status").textContent = "대기 중(레이더 시작을 누르세요).";
</script>
</body>
</html>
"""

# Streamlit에 HTML을 그대로 임베드
components.html(html, height=1400, scrolling=True)
