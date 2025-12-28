import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정 (와이드 모드)
st.set_page_config(
    page_title="KOREA STOCK Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 여백 최소화 CSS
st.markdown(
    """
    <style>
    .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; }
    iframe { width: 100% !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 개선된 HTML/JS 소스코드 (f-string이 아닌 일반 문자열 사용)
html_code = """
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>KOREA STOCK Radar</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Phosphor Icons for UI elements -->
  <script src="https://unpkg.com/@phosphor-icons/web"></script>
  <style>
    :root{
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
    }
    body{
      background:
        radial-gradient(1200px 600px at 20% 0%, rgba(0,208,163,.10), transparent 60%),
        radial-gradient(900px 500px at 90% 10%, rgba(59,130,246,.10), transparent 55%),
        var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Pretendard", "Noto Sans KR", "Segoe UI", Roboto, Arial;
      margin: 0;
      overflow-x: hidden;
    }
    /* Scrollbar */
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

    .card{
      background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .muted{ color: var(--muted); }
    .badge{
      display:inline-flex; align-items:center; gap:8px;
      padding: 6px 10px; border-radius: 999px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,.03);
      font-size: 12px; color: var(--muted);
    }
    .dot{ width:8px; height:8px; border-radius:50%; background: rgba(159,176,208,.7); }
    .btn{
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,.10);
      background: linear-gradient(135deg, rgba(0,208,163,.18), rgba(59,130,246,.14));
      padding: .7rem 1.2rem;
      box-shadow: var(--shadow);
      font-weight: 700;
      font-size: 14px;
      transition: all 0.2s;
      cursor: pointer;
      color: white;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn:hover{ transform: translateY(-2px); filter: brightness(1.1); }
    .btn:active{ transform: translateY(0); }
    
    .btn-secondary {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
    }

    table{ border-collapse: collapse; width: 100%; white-space: nowrap; }
    th, td{ border-bottom: 1px solid rgba(255,255,255,.08); padding: 12px 10px; font-size: 13px; }
    th{ color: var(--muted); text-align:left; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 11px;}
    
    .input-field {
        background: rgba(0,0,0,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        color: white;
        border-radius: 8px;
        padding: 8px 12px;
        width: 100%;
        outline: none;
        transition: border-color 0.2s;
    }
    .input-field:focus { border-color: var(--green); }

    .toast{
      position: fixed; right: 16px; bottom: 16px;
      max-width: 400px;
      width: 90%;
      background: rgba(15,26,47,.95);
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 14px;
      box-shadow: var(--shadow);
      padding: 16px;
      display: none;
      z-index: 100;
      backdrop-filter: blur(8px);
      animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideIn { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .toast.show{ display:block; }
    
    .pill{
      display:inline-flex; align-items:center; gap:6px;
      padding:4px 10px; border-radius: 999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      font-size:12px; color: var(--muted);
    }
    .good{ color: var(--green); font-weight: 700; }
    .bad{ color: var(--red); font-weight: 700; }
    .warn{ color: var(--amber); font-weight: 700; }
    .mono{ font-family: 'SF Mono', 'Roboto Mono', Menlo, monospace; font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }

    /* Modal */
    .modal-overlay {
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.7);
        backdrop-filter: blur(4px);
        display: none; justify-content: center; align-items: center;
        z-index: 90;
    }
    .modal-overlay.open { display: flex; }
    .modal {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 24px;
        width: 90%; max-width: 500px;
        box-shadow: var(--shadow);
    }

    /* Animation for updates */
    @keyframes flash-green { 0% { background-color: rgba(0,208,163,0.3); } 100% { background-color: transparent; } }
    @keyframes flash-red { 0% { background-color: rgba(255,77,109,0.3); } 100% { background-color: transparent; } }
    .flash-up { animation: flash-green 0.5s ease-out; }
    .flash-down { animation: flash-red 0.5s ease-out; }
  </style>
</head>
<body class="min-h-screen">
  <div class="max-w-7xl mx-auto px-4 py-6">
    <!-- Header -->
    <div class="card p-5 mb-4 relative overflow-hidden">
      <div class="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
        <i class="ph ph-radar text-9xl"></i>
      </div>
      <div class="flex flex-wrap items-center justify-between gap-4 relative z-10">
        <div>
          <div class="flex items-center gap-3">
             <div class="bg-blue-500/20 p-2 rounded-lg border border-blue-500/30">
                <i class="ph ph-wave-sine text-2xl text-blue-400"></i>
             </div>
             <div>
                <h1 class="text-2xl font-black tracking-tight text-white leading-none">KOREA STOCK Radar</h1>
                <div class="text-xs text-blue-300/70 mt-1 font-mono">REAL-TIME VOLATILITY SCANNER</div>
             </div>
          </div>
          <div class="text-xs muted mt-2 max-w-xl">
            거래량 순위 후보 → 1~2초 폴링 → 점수 상위 1~3개만 알림(ENTRY) + 추적(목표권/EXIT)<br>
            <span class="text-amber-400/80">* API 연결 실패 시 자동으로 모의투자(Demo) 데이터로 작동합니다.</span>
          </div>
        </div>
        <div class="flex flex-col items-end gap-2">
            <button id="btnSettings" class="btn btn-secondary text-xs py-1 px-3">
                <i class="ph ph-gear"></i> 설정
            </button>
            <div class="badge font-mono"><span class="dot" id="connDot"></span><span id="clock">00:00:00</span></div>
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 gap-3">
        <div class="card p-3">
          <div class="text-[10px] uppercase tracking-wider muted mb-1">시장</div>
          <select id="market" class="input-field bg-white/5 border-white/10 text-sm py-1">
            <option value="KOSPI">KOSPI</option>
            <option value="KOSDAQ" selected>KOSDAQ</option>
          </select>
        </div>

        <div class="card p-3">
          <div class="text-[10px] uppercase tracking-wider muted mb-1">히든 개수</div>
          <select id="topK" class="input-field bg-white/5 border-white/10 text-sm py-1">
            <option value="1">1개</option>
            <option value="2" selected>2개</option>
            <option value="3">3개</option>
          </select>
        </div>

        <div class="card p-3">
          <div class="text-[10px] uppercase tracking-wider muted mb-1">순위 TopN</div>
          <input id="topN" type="number" min="10" max="50" value="30" class="input-field bg-white/5 border-white/10 text-sm py-1" />
        </div>

        <div class="card p-3">
            <div class="text-[10px] uppercase tracking-wider muted mb-1">폴링(초)</div>
            <input id="pollSec" type="number" min="0.5" max="5" step="0.1" value="1.5" class="input-field bg-white/5 border-white/10 text-sm py-1" />
        </div>

        <div class="card p-3">
            <div class="text-[10px] uppercase tracking-wider muted mb-1">유입가속(x)</div>
            <input id="minFlow" type="number" min="1.0" max="4.0" step="0.05" value="1.20" class="input-field bg-white/5 border-white/10 text-sm py-1" />
        </div>

        <div class="card p-3">
            <div class="text-[10px] uppercase tracking-wider muted mb-1">모멘텀(60s)</div>
            <input id="minMom60" type="number" min="-2" max="5" step="0.05" value="0.20" class="input-field bg-white/5 border-white/10 text-sm py-1" />
        </div>

        <div class="card p-3">
            <div class="text-[10px] uppercase tracking-wider muted mb-1">확인(초)</div>
            <input id="confirmSec" type="number" min="1" max="10" step="0.5" value="3.5" class="input-field bg-white/5 border-white/10 text-sm py-1" />
        </div>

        <div class="card p-3 flex flex-col justify-center items-center">
            <div class="text-[10px] uppercase tracking-wider muted mb-1 w-full text-left">상태</div>
            <div class="flex items-center gap-2 w-full">
                <span class="pill font-mono text-xs font-bold" id="state">OFF</span>
                <span class="text-[10px] muted font-mono" id="rate">-</span>
            </div>
        </div>
    </div>

    <!-- Actions -->
    <div class="flex flex-wrap gap-3 mt-4">
        <button id="btnPerm" class="btn btn-secondary"><i class="ph ph-bell"></i> 알림 권한</button>
        <button id="btnStart" class="btn"><i class="ph ph-play"></i> 레이더 시작</button>
        <button id="btnStop" class="btn hidden bg-red-500/20 border-red-500/30 hover:bg-red-500/30"><i class="ph ph-stop"></i> 레이더 정지</button>
        <button id="btnClear" class="btn btn-secondary ml-auto"><i class="ph ph-trash"></i> 로그 초기화</button>
    </div>

    <!-- Main Grid -->
    <div class="grid lg:grid-cols-3 gap-6 mt-6">
        
        <!-- Left Column: Candidates -->
        <div class="lg:col-span-2 space-y-4">
            <div class="card p-0 overflow-hidden flex flex-col h-full min-h-[400px]">
                <div class="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
                    <div class="flex items-center gap-2">
                        <i class="ph ph-crosshair text-amber-400"></i>
                        <span class="font-extrabold text-sm">히든 후보 (실시간)</span>
                    </div>
                    <div class="text-xs muted font-mono" id="status">대기 중</div>
                </div>
                <div class="overflow-x-auto flex-1">
                    <table class="w-full">
                    <thead>
                        <tr>
                        <th class="w-12 text-center">No.</th>
                        <th>종목명</th>
                        <th class="text-right">현재가</th>
                        <th class="text-right">등락률</th>
                        <th class="text-center">MOM(15s/60s)</th>
                        <th class="text-center">유입가속</th>
                        <th class="text-right">SCORE</th>
                        <th class="text-center">STATUS</th>
                        </tr>
                    </thead>
                    <tbody id="rows">
                        <tr><td colspan="8" class="text-center py-8 text-muted/50">데이터 대기 중...</td></tr>
                    </tbody>
                    </table>
                </div>
                <div class="p-3 border-t border-white/10 bg-black/20 text-[11px] muted flex gap-4 justify-center">
                    <span><span class="good">READY</span>: 감시중</span>
                    <span><span class="warn">CONFIRM</span>: 조건충족(확인중)</span>
                    <span><span class="good">ENTRY</span>: 진입신호</span>
                    <span><span class="bad">EXIT</span>: 청산신호</span>
                </div>
            </div>
        </div>

        <!-- Right Column: Tracking & Logs -->
        <div class="space-y-4 flex flex-col h-full">
            
            <!-- Tracking List -->
            <div class="card p-0 flex flex-col max-h-[400px]">
                <div class="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
                    <div class="flex items-center gap-2">
                        <i class="ph ph-binoculars text-green-400"></i>
                        <span class="font-extrabold text-sm">추적 중 (Entry)</span>
                    </div>
                    <div class="text-[10px] muted bg-white/10 px-2 py-0.5 rounded">+2%/+3% 알림</div>
                </div>
                <div class="overflow-y-auto overflow-x-auto flex-1 p-0">
                    <table class="w-full">
                    <thead>
                        <tr>
                        <th>종목</th>
                        <th class="text-right">수익률</th>
                        <th class="text-right">진입가</th>
                        <th class="text-right">현재가</th>
                        <th class="text-center">상태</th>
                        </tr>
                    </thead>
                    <tbody id="watchRows">
                        <tr><td colspan="5" class="text-center py-8 text-muted/50 text-xs">ENTRY 발생 시 자동 등록됩니다.</td></tr>
                    </tbody>
                    </table>
                </div>
            </div>

            <!-- Logs -->
            <div class="card p-0 flex flex-col flex-1 min-h-[300px]">
                <div class="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
                    <div class="flex items-center gap-2">
                        <i class="ph ph-list-dashes text-blue-400"></i>
                        <span class="font-extrabold text-sm">알림 로그</span>
                    </div>
                </div>
                <div id="log" class="p-3 space-y-2 overflow-y-auto h-0 flex-1 custom-scroll"></div>
            </div>
        </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div id="toast" class="toast">
    <div class="flex items-start gap-3">
        <div id="toastIcon" class="mt-1 text-xl">🔔</div>
        <div>
            <div class="font-extrabold text-sm text-white" id="toastTitle"></div>
            <div class="text-xs muted mt-1 leading-relaxed" id="toastBody"></div>
        </div>
    </div>
  </div>

  <!-- Settings Modal -->
  <div id="settingsModal" class="modal-overlay">
      <div class="modal">
          <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-bold text-white">⚙️ 설정</h2>
              <button id="btnCloseSettings" class="text-muted hover:text-white"><i class="ph ph-x text-xl"></i></button>
          </div>
          <div class="space-y-4">
              <div>
                  <label class="block text-xs uppercase muted mb-2">API Origin (Netlify Functions)</label>
                  <input type="text" id="apiOriginInput" class="input-field" placeholder="예: https://yoursite.netlify.app">
                  <p class="text-[10px] muted mt-2">
                      Netlify에 배포된 백엔드 주소입니다. 비워두면 현재 주소를 사용합니다.<br>
                      <span class="text-amber-400">* 연결 실패 시 자동으로 모의투자(Demo) 모드로 전환됩니다.</span>
                  </p>
              </div>
              <button id="btnSaveSettings" class="btn w-full justify-center">저장</button>
          </div>
      </div>
  </div>

<script>
  // --- Constants & Config ---
  let API_ORIGIN = localStorage.getItem("stock_radar_api_origin") || "";
  let DEMO_MODE = false;

  const fmt = (n) => (Number.isFinite(n) ? n.toLocaleString("ko-KR") : "-");
  const fmt2 = (n) => (Number.isFinite(n) ? n.toFixed(2) : "-");
  const pct = (n) => (Number.isFinite(n) ? (n>=0?"+":"") + n.toFixed(2) + "%" : "-");
  const kstNow = () => new Date().toLocaleString("ko-KR", { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12:false });

  // --- UI Helpers ---
  function toast(title, body, icon="🔔"){
    const t = document.getElementById("toast");
    document.getElementById("toastTitle").textContent = title;
    document.getElementById("toastBody").textContent = body;
    document.getElementById("toastIcon").textContent = icon;
    t.classList.remove("hidden");
    t.classList.add("show");
    
    // Reset animation
    t.style.animation = 'none';
    t.offsetHeight; /* trigger reflow */
    t.style.animation = null;

    if(window.toastTimer) clearTimeout(window.toastTimer);
    window.toastTimer = setTimeout(()=>{
        t.classList.remove("show");
    }, 4000);
  }

  function notify(title, body, type="info"){
    let icon = "🔔";
    if(type === "entry") icon = "✅";
    if(type === "exit") icon = "⏹";
    if(type === "profit") icon = "🎯";
    
    toast(title, body, icon);
    pushLog(title, body, type);
    
    if("Notification" in window && Notification.permission === "granted"){
      new Notification(title, { body });
    }
  }

  function pushLog(title, body, type){
    const log = document.getElementById("log");
    const div = document.createElement("div");
    
    let borderClass = "border-white/10";
    if(type==="entry") borderClass = "border-green-500/30 bg-green-500/5";
    if(type==="exit") borderClass = "border-red-500/30 bg-red-500/5";
    if(type==="profit") borderClass = "border-amber-500/30 bg-amber-500/5";

    div.className = `card p-3 border ${borderClass} text-sm animate-fade-in-down`;
    div.innerHTML = `
      <div class="flex items-center justify-between gap-2 flex-wrap mb-1">
        <div class="font-bold text-white flex items-center gap-2">
            ${type==="entry" ? '<i class="ph ph-arrow-right text-green-400"></i>' : ''}
            ${type==="exit" ? '<i class="ph ph-stop-circle text-red-400"></i>' : ''}
            ${title}
        </div>
        <div class="text-[10px] font-mono muted">${kstNow()}</div>
      </div>
      <div class="text-xs muted pl-1 border-l-2 border-white/10">${body}</div>
    `;
    log.prepend(div);
    if(log.children.length > 50) log.lastElementChild.remove();
  }

  // --- API / Mock Data ---
  
  // Mock Data Generators
  const mockTickers = [
    {code:"005930", name:"삼성전자"}, {code:"000660", name:"SK하이닉스"}, 
    {code:"035420", name:"NAVER"}, {code:"035720", name:"카카오"},
    {code:"247540", name:"에코프로비엠"}, {code:"086520", name:"에코프로"},
    {code:"000270", name:"기아"}, {code:"005380", name:"현대차"},
    {code:"041510", name:"에스엠"}, {code:"068270", name:"셀트리온"},
    {code:"001570", name:"금양"}, {code:"028300", name:"HLB"}
  ];

  // Helper to simulate random walks
  const mockState = new Map();
  function getMockPrice(code) {
    if(!mockState.has(code)) {
        mockState.set(code, { p: 10000 + Math.random()*90000, vol: 1000 });
    }
    const s = mockState.get(code);
    // Random walk
    const change = (Math.random() - 0.48) * (s.p * 0.005); // slight upward bias
    s.p += change;
    const rate = ((Math.random() - 0.5) * 5); // daily rate
    return {
        code,
        raw: {
            stck_prpr: Math.floor(s.p),
            prdy_ctrt: rate.toFixed(2),
            prdy_vrss: Math.floor(change)
        }
    };
  }

  async function api(action, params={}){
    if(DEMO_MODE) {
        return mockApi(action, params);
    }

    const origin = API_ORIGIN || location.origin;
    let urlString = origin.includes("http") ? origin : "https://" + origin;
    // Remove trailing slash
    if(urlString.endsWith("/")) urlString = urlString.slice(0,-1);
    
    // If no custom origin and we are in a sandbox/iframe (likely), verify if we can actually call relative
    // For this artifact, we default to relative if empty.
    
    try {
        const u = new URL("/.netlify/functions/kis", urlString);
        u.searchParams.set("action", action);
        Object.entries(params).forEach(([k,v])=>u.searchParams.set(k, String(v)));

        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), 3000); // 3s timeout
        
        const r = await fetch(u.toString(), { 
            headers: { "accept":"application/json" },
            signal: controller.signal
        });
        clearTimeout(id);
        
        const d = await r.json();
        if(!r.ok || !d.ok) throw new Error(d.error || `HTTP ${r.status}`);
        document.getElementById("connDot").style.backgroundColor = "#00d0a3"; // Green
        return d;
    } catch(e) {
        if(!DEMO_MODE) {
            console.warn("API connect failed, switching to DEMO MODE", e);
            DEMO_MODE = true;
            document.getElementById("connDot").style.backgroundColor = "#fbbf24"; // Amber
            toast("데모 모드 전환", "API 연결 실패로 가상 데이터를 사용합니다.");
            return mockApi(action, params);
        }
        throw e;
    }
  }

  async function mockApi(action, params) {
      // Simulate network delay
      await new Promise(r => setTimeout(r, 100 + Math.random() * 200));

      if(action === "rank_price") {
        const picks = [];
        // Select random 15 stocks
        const shuffled = [...mockTickers].sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, params.watchN || 15);
        
        const prices = selected.map(t => getMockPrice(t.code));
        
        return {
            ok: true,
            pickCodes: selected.map(t => t.code),
            rank: selected, // rank contains metadata
            prices: prices
        };
      } else if (action === "price") {
          const codes = (params.codes || "").split(",");
          const prices = codes.map(c => getMockPrice(c));
          return { ok: true, prices };
      }
      return { ok: false };
  }


  // --- Logic ---
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

  function canAlert(code, cooldownMin=7){
    const now = Date.now();
    const prev = lastAlert.get(code) || 0;
    // Basic debounce: if we alerted recently, skip
    if(now - prev >= cooldownMin*60*1000){
      lastAlert.set(code, now);
      return true;
    }
    return false;
  }

  function pushPoint(code, p, chgRate){
    if(!series.has(code)) series.set(code, []);
    const arr = series.get(code);
    const prev = arr.length ? arr[arr.length-1].p : p;
    // Estimate "Amount" as Price * |Delta Price|. Rough proxy for volume impact.
    // In real app, you'd use actual volume if available.
    const amtEst = Math.abs(p - prev) * p;

    arr.push({ ts: Date.now(), p, amtEst, chgRate });
    // Keep 3.5 minutes of history
    const cutoff = Date.now() - 210*1000;
    while(arr.length && arr[0].ts < cutoff) arr.shift();
  }

  function win(code, sec){
    const arr = series.get(code) || [];
    const cutoff = Date.now() - sec*1000;
    const w = arr.filter(x => x.ts >= cutoff);
    if(w.length < 2) return null;

    const first = w[0].p;
    const lastp = w[w.length-1].p;
    const mom = (lastp/first - 1) * 100;

    const amt = w.reduce((a,x)=>a + x.amtEst, 0);
    return { mom, amt, n:w.length, first, last:lastp };
  }

  function clamp(x,a,b){ return Math.max(a, Math.min(b,x)); }
  function log2(x){ return Math.log(x)/Math.log(2); }

  function scoreCode(code){
    const s15 = win(code, 15);
    const s60 = win(code, 60);
    const s180 = win(code, 180);
    const L = last.get(code);
    if(!L || !s60) return { ok:false, score:-1e9, why:"데이터 부족" };

    const mom15 = s15 ? s15.mom : 0;
    const mom60 = s60.mom;

    const avg60 = s180 ? (s180.amt/3) : s60.amt;
    const flowRatio = s60.amt / (avg60 + 1e-12); // Recent activity vs Average activity

    // Penalty for overheating
    let heat = 0;
    if(mom15 > 0.8) heat += 0.8;
    if(mom60 > 2.2) heat += 1.0;

    let score = 0;
    score += 1.4 * clamp(mom60/1.2, -1, 1.6);
    score += 1.0 * clamp(mom15/0.6, -1, 1.6);
    // Bonus if short term momentum is accelerating faster than long term
    score += 1.2 * clamp((mom15 - mom60*0.25)/0.25, -1, 1.8);

    const flowScore = clamp(log2(flowRatio + 1), 0, 2.6);
    score += 1.6 * flowScore;

    score += 0.35 * clamp((L.chgRate||0)/3.0, -1, 1.5);
    score -= heat;

    return {
      ok:true,
      score,
      p:L.p,
      chgRate:L.chgRate,
      mom15, mom60,
      flowRatio,
      amt60:s60.amt,
    };
  }

  function entryGate(r){
    const minFlow = parseFloat(document.getElementById("minFlow").value || "1.2");
    const minMom60 = parseFloat(document.getElementById("minMom60").value || "0.2");

    if(r.flowRatio < minFlow) return { pass:false, why:`유입가속 부족(x${fmt2(r.flowRatio)})` };
    if(r.mom60 < minMom60) return { pass:false, why:`60s 모멘텀 부족(${pct(r.mom60)})` };
    if(r.mom15 < -0.05) return { pass:false, why:`15s 둔화(${pct(r.mom15)})` };
    return { pass:true, why:"OK" };
  }

  function exitCheck(code){
    const w = watch.get(code);
    if(!w) return;

    const r = scoreCode(code);
    if(!r.ok) return;

    const p = r.p;
    const entry = w.entryPrice;
    const ret = (p/entry - 1) * 100;

    if(!Number.isFinite(w.maxP) || p > w.maxP) w.maxP = p;

    // Profit Targets
    if(!w.hit2 && ret >= 2.0){
      w.hit2 = true;
      notify(`🎯 목표권 +2%: ${meta.get(code)?.name || code}`, `${fmt(entry)} → ${fmt(p)} (${pct(ret)})`, "profit");
    }
    if(!w.hit3 && ret >= 3.0){
      w.hit3 = true;
      notify(`🏁 목표권 +3%: ${meta.get(code)?.name || code}`, `${fmt(entry)} → ${fmt(p)} (${pct(ret)})`, "profit");
    }

    // Exit Signals
    const triggers = [];
    if(r.mom15 < -0.05) triggers.push(`모멘텀 둔화(15s ${pct(r.mom15)})`);
    if(r.mom60 < 0.10 && ret > 0.8) triggers.push(`60s 약화(${pct(r.mom60)})`);
    if(r.flowRatio < 1.05) triggers.push(`유입 붕괴(x${fmt2(r.flowRatio)})`);

    const peakRet = (w.maxP/entry - 1) * 100;
    const drawdown = peakRet - ret;
    if(peakRet >= 2.2 && drawdown >= 0.9) triggers.push(`트레일링(DD ${fmt2(drawdown)}%)`);

    // Cooldown on exit alerts
    const now = Date.now();
    if(triggers.length){
      if(!w.lastExitTs || (now - w.lastExitTs) > 60*1000){
        w.lastExitTs = now;
        stateFlag.set(code, "EXIT");
        notify(`⏹ EXIT 시그널: ${meta.get(code)?.name || code}`, `수익률 ${pct(ret)} | ${triggers.slice(0,3).join(" / ")}`, "exit");
      }
    }
  }

  function renderMain(top){
    const tbody = document.getElementById("rows");
    
    if(!top.length){
      // Only show empty message if we actually have data but no candidates
      if(last.size > 0)
        tbody.innerHTML = `<tr><td colspan="9" class="text-center py-8 text-muted/50">조건 충족 종목이 없습니다.</td></tr>`;
      return;
    }
    
    // Clear efficiently
    tbody.innerHTML = "";

    top.forEach((r,i)=>{
      const gate = entryGate(r);
      // Determine state: Ready -> Confirm -> Entry -> Exit
      let st = stateFlag.get(r.code);
      if(!st && gate.pass) {
          st = "READY";
          stateFlag.set(r.code, "READY");
      }
      if(!st) st = "-";

      const tr = document.createElement("tr");
      tr.className = "hover:bg-white/5 transition-colors border-b border-white/5";
      
      const momCls = r.mom60 >= 0 ? "good" : "bad";
      const name = r.name || "Unknown";
      
      // Determine Badge Color for Status
      let badgeCls = "bg-white/5 text-muted";
      if(st === "READY") badgeCls = "bg-green-500/20 text-green-400";
      if(st === "CONFIRM") badgeCls = "bg-amber-500/20 text-amber-400 animate-pulse";
      if(st === "ENTRY") badgeCls = "bg-blue-500/20 text-blue-400 font-bold";
      if(st === "EXIT") badgeCls = "bg-red-500/20 text-red-400 font-bold";

      tr.innerHTML = `
        <td class="muted text-center text-xs">${i+1}</td>
        <td>
            <div class="font-bold text-sm text-white">${name}</div>
            <div class="text-[10px] muted font-mono">${r.code}</div>
        </td>
        <td class="mono text-right">${fmt(r.p)}</td>
        <td class="${(r.chgRate||0)>=0?'good':'bad'} mono text-right">${pct(r.chgRate||0)}</td>
        <td class="mono text-center">
            <span class="${r.mom15>=0?'good':'bad'} text-xs">${pct(r.mom15)}</span>
            <span class="muted text-[10px] mx-1">/</span>
            <span class="${r.mom60>=0?'good':'bad'} text-xs">${pct(r.mom60)}</span>
        </td>
        <td class="mono text-center text-xs">x${fmt2(r.flowRatio)}</td>
        <td class="font-bold mono text-right text-blue-300">${fmt2(r.score)}</td>
        <td class="text-center">
          <span class="px-2 py-0.5 rounded text-[10px] ${badgeCls}">
            ${st}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderWatch(){
    const tbody = document.getElementById("watchRows");
    const entries = Array.from(watch.entries());
    
    if(!entries.length){
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-muted/50 text-xs">추적 중 종목이 없습니다.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    for(const [code, w] of entries){
      const r = scoreCode(code);
      if(!r.ok) continue;

      const p = r.p;
      const ret = (p/w.entryPrice - 1) * 100;
      const st = stateFlag.get(code) || "ENTRY";
      
      const name = meta.get(code)?.name || code;

      const tr = document.createElement("tr");
      tr.className = "hover:bg-white/5 border-b border-white/5";
      tr.innerHTML = `
        <td>
            <div class="font-bold text-sm text-white">${name}</div>
        </td>
        <td class="${ret>=0?'good':'bad'} mono text-right">${pct(ret)}</td>
        <td class="mono text-right text-xs muted">${fmt(w.entryPrice)}</td>
        <td class="mono text-right">${fmt(p)}</td>
        <td class="text-center">
            <span class="text-[10px] px-1.5 py-0.5 rounded ${st==='EXIT'?'bg-red-500/20 text-red-400':'bg-green-500/20 text-green-400'}">
                ${st}
            </span>
        </td>
      `;
      tbody.appendChild(tr);
    }
  }

  function scheduleEntry(r){
    const confirmSec = parseFloat(document.getElementById("confirmSec").value || "3.5");
    // Hardcoded cooldown for safety in this version, could be inputs
    const cooldownMin = 7; 

    const gate = entryGate(r);
    if(!gate.pass) {
        // If it was confirming but failed gate, revert
        if(stateFlag.get(r.code) === "CONFIRM") {
            stateFlag.set(r.code, "READY");
            pending.delete(r.code);
        }
        return;
    }
    
    // If already tracked or cooling down, skip
    if(watch.has(r.code)) return;
    if(!canAlert(r.code, cooldownMin)) return;
    if(pending.has(r.code)) return; // Already scheduled

    stateFlag.set(r.code, "CONFIRM");
    const tid = setTimeout(()=>{
      pending.delete(r.code);

      const rr = scoreCode(r.code);
      if(!rr.ok){ stateFlag.set(r.code, "READY"); return; }

      const gate2 = entryGate(rr);
      if(!gate2.pass){ stateFlag.set(r.code, "READY"); return; }

      stateFlag.set(r.code, "ENTRY");
      const entryPrice = rr.p;
      watch.set(r.code, { entryPrice, maxP: entryPrice, hit2:false, hit3:false, lastExitTs:0 });

      notify(`✅ ENTRY 시그널: ${meta.get(r.code)?.name || r.code}`, `진입가 ${fmt(entryPrice)} | 유입 x${fmt2(rr.flowRatio)} | MOM60 ${pct(rr.mom60)}`, "entry");
    }, confirmSec*1000);

    pending.set(r.code, tid);
  }

  function pickTop(){
    const topK = parseInt(document.getElementById("topK").value,10);
    const scored = [];

    for(const code of last.keys()){
      const r = scoreCode(code);
      if(!r.ok) continue;
      const name = meta.get(code)?.name || "";
      scored.push({ code, name, ...r });
    }
    scored.sort((a,b)=> b.score - a.score);
    return scored.slice(0, topK);
  }

  async function refreshUniverse(){
    const market = document.getElementById("market").value;
    const topN = parseInt(document.getElementById("topN").value,10) || 30;
    // We fetch a few more than watched to have a pool
    const watchN = 20; 

    document.getElementById("status").textContent = "종목 유니버스 갱신 중...";

    const d = await api("rank_price", { market, topN, watchN });
    const codes = d.pickCodes || [];

    for(const x of (d.rank||[])){
      const code = String(x.stck_shrn_iscd || x.iscd || x.code || x.ticker || "").padStart(6,"0");
      if(!code || code === "000000") continue;
      const name = x.hts_kor_isnm || x.kor_isnm || x.name || x.stck_issu_abbrv_name || "";
      if(!meta.has(code)) meta.set(code, {});
      if(name) meta.get(code).name = name;
    }

    // Initial price population
    for(const it of (d.prices||[])){
      const code = it.code;
      const raw = it.raw || {};
      const p = Number(raw.stck_prpr || raw.last || raw.prpr || raw.price || NaN);
      const chgRate = Number(raw.prdy_ctrt || raw.change_rate || raw.rate || NaN);
      if(Number.isFinite(p)){
        last.set(code, { p, chgRate, ts: Date.now() });
        pushPoint(code, p, chgRate);
      }
    }

    document.getElementById("status").textContent = `감시 대상 ${codes.length}개 설정 완료`;
    return codes;
  }

  async function pollPrices(codes){
    const market = document.getElementById("market").value;
    // Chunking if needed, but for 20-30 codes, one call is usually fine
    const d = await api("price", { market, codes: codes.join(",") });

    for(const it of (d.prices||[])){
      const code = it.code;
      const raw = it.raw || {};
      const p = Number(raw.stck_prpr || raw.last || raw.prpr || raw.price || NaN);
      const chgRate = Number(raw.prdy_ctrt || raw.change_rate || raw.rate || NaN);

      if(Number.isFinite(p)){
        last.set(code, { p, chgRate, ts: Date.now() });
        pushPoint(code, p, chgRate);
      }
    }
  }

  // --- Main Loop ---
  async function start(){
    if(running) return;
    
    // UI Update
    document.getElementById("btnStart").classList.add("hidden");
    document.getElementById("btnStop").classList.remove("hidden");
    document.getElementById("state").textContent = "ON";
    document.getElementById("state").classList.add("good");
    
    running = true;
    let codes = [];
    
    try{
      codes = await refreshUniverse();
    }catch(e){
      stop();
      notify("시작 실패", e.message);
      return;
    }

    // Rate counter
    tickCount = 0;
    if(rateTimer) clearInterval(rateTimer);
    rateTimer = setInterval(()=>{
      document.getElementById("rate").textContent = `${tickCount} TPS`;
      tickCount = 0;
    }, 1000);

    const loop = async ()=>{
      if(!running) return;

      try{
        await pollPrices(codes);
        tickCount++;

        const top = pickTop();
        renderMain(top);

        for(const r of top) scheduleEntry(r);
        for(const code of watch.keys()) exitCheck(code);

        renderWatch();

        // Refresh universe every minute (in case ranking changed)
        if(!start._lastRebuild) start._lastRebuild = Date.now();
        if(Date.now() - start._lastRebuild > 60*1000){
          start._lastRebuild = Date.now();
          codes = await refreshUniverse();
        }

      }catch(e){
        document.getElementById("status").textContent = `에러: ${e.message}`;
      }finally{
        const pollSec = parseFloat(document.getElementById("pollSec").value || "1.5");
        timer = setTimeout(loop, Math.max(0.5, pollSec)*1000);
      }
    };

    document.getElementById("status").textContent = "실시간 감시 중...";
    loop();
  }

  function stop(){
    running = false;
    document.getElementById("btnStart").classList.remove("hidden");
    document.getElementById("btnStop").classList.add("hidden");
    document.getElementById("state").textContent = "OFF";
    document.getElementById("state").classList.remove("good");
    document.getElementById("rate").textContent = "-";
    
    if(timer) clearTimeout(timer), timer = null;
    if(rateTimer) clearInterval(rateTimer), rateTimer = null;
    
    for(const [,tid] of pending.entries()){ try{ clearTimeout(tid); }catch(_){ } }
    pending.clear();
    
    document.getElementById("status").textContent = "정지됨";
    toast("레이더 정지", "감시를 종료했습니다.");
  }

  // --- Event Listeners ---
  document.getElementById("btnPerm").addEventListener("click", async ()=>{
    if(!("Notification" in window)){ toast("알림 미지원", "이 브라우저는 시스템 알림을 지원하지 않습니다."); return; }
    const p = await Notification.requestPermission();
    toast("알림 권한", `현재 상태: ${p}`);
  });

  document.getElementById("btnStart").addEventListener("click", start);
  document.getElementById("btnStop").addEventListener("click", stop);

  document.getElementById("btnClear").addEventListener("click", ()=>{
    document.getElementById("log").innerHTML = "";
    lastAlert.clear();
    stateFlag.clear();
    watch.clear();
    for(const [,tid] of pending.entries()){ try{ clearTimeout(tid); }catch(_){ } }
    pending.clear();
    toast("초기화", "모든 상태와 로그가 초기화되었습니다.");
    renderWatch();
    renderMain([]);
  });

  // Settings Modal Logic
  const modal = document.getElementById("settingsModal");
  const apiInput = document.getElementById("apiOriginInput");
  
  document.getElementById("btnSettings").addEventListener("click", ()=>{
      apiInput.value = API_ORIGIN;
      modal.classList.add("open");
  });
  document.getElementById("btnCloseSettings").addEventListener("click", ()=>{
      modal.classList.remove("open");
  });
  document.getElementById("btnSaveSettings").addEventListener("click", ()=>{
      API_ORIGIN = apiInput.value.trim();
      localStorage.setItem("stock_radar_api_origin", API_ORIGIN);
      // Reset Demo Mode flag so user can try connecting again
      DEMO_MODE = false; 
      document.getElementById("connDot").style.backgroundColor = ""; // Reset color
      modal.classList.remove("open");
      toast("설정 저장됨", "API 주소가 업데이트되었습니다.");
  });

  // Clock
  setInterval(()=>{ document.getElementById("clock").textContent = kstNow(); }, 1000);
  document.getElementById("clock").textContent = kstNow();

</script>
</body>
</html>
"""

components.html(html_code, height=1400, scrolling=True)
