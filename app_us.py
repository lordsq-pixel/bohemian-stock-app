import streamlit as st
import pytz
import datetime
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# 라이브러리 예외처리
try:
    from pykrx import stock
    import yfinance as yf
except ImportError:
    st.error("필수 라이브러리 설치 필요: pip install pykrx yfinance ta")
    st.stop()

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="MAGIC STOCK PREMIUM", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

korea = pytz.timezone("Asia/Seoul")

# --- 2. 프리미엄 다크 UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap');
    
    /* [전체 테마] 다크 모드 기반 */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

    /* [레이아웃] 여백 최적화 */
    .block-container { 
        padding-top: 1rem !important; 
        padding-bottom: 3rem !important; 
        max-width: 1200px !important;
    }
    header[data-testid="stHeader"] { display: none !important; }
    
    /* [네비게이션] 글래스모피즘 헤더 */
    .top-nav {
        background: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #30363D;
        padding: 15px 20px;
        display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 25px; border-radius: 0 0 16px 16px;
    }
    .brand-name { 
        font-size: 20px; font-weight: 800; 
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px; 
    }
    .current-time { font-size: 13px; color: #8B949E; font-family: 'Courier New', monospace; }

    /* [탭] 고급스러운 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 20px; border-bottom: 1px solid #30363D; padding-bottom: 0px; 
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px; font-size: 16px; font-weight: 500; color: #8B949E; 
        background: transparent; border: none; flex: 1;
    }
    .stTabs [aria-selected="true"] { 
        color: #58A6FF !important; 
        border-bottom: 2px solid #58A6FF !important; 
        font-weight: 700;
    }

    /* [카드] 다크 카드 스타일 */
    .section-title { 
        font-size: 16px; font-weight: 600; color: #FFFFFF; 
        margin: 25px 0 12px 0; border-left: 3px solid #58A6FF; padding-left: 10px; 
        letter-spacing: 0.5px;
    }
    
    .index-card { 
        background: #161B22; border-radius: 12px; padding: 18px; 
        border: 1px solid #30363D; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 12px; transition: transform 0.2s;
    }
    .index-card:hover { transform: translateY(-2px); border-color: #58A6FF; }
    
    .index-name { font-size: 12px; color: #8B949E; font-weight: 500; text-transform: uppercase; }
    .index-value { font-size: 24px; font-weight: 700; color: #FFFFFF; margin-top: 4px; }
    
    /* [리스트] 주식 Row 스타일 */
    .stock-row { 
        background: #161B22; border-bottom: 1px solid #21262D; padding: 16px; 
        display: flex; justify-content: space-between; align-items: center;
        transition: background 0.2s;
    }
    .stock-row:hover { background: #1F242C; }
    .stock-row:first-child { border-top-left-radius: 12px; border-top-right-radius: 12px; }
    .stock-row:last-child { border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; border-bottom: none; }
    
    .stock-name { font-size: 15px; font-weight: 600; color: #E6EDF3; }
    .stock-sub { font-size: 11px; color: #8B949E; margin-top: 2px; }
    .stock-price { font-size: 16px; font-weight: 700; text-align: right; }
    
    /* [컬러] 네온 액센트 (한국장 기준: 상승=빨강) */
    .up { color: #FF5252 !important; text-shadow: 0 0 10px rgba(255, 82, 82, 0.2); } 
    .down { color: #448AFF !important; text-shadow: 0 0 10px rgba(68, 138, 255, 0.2); }
    .score-badge { 
        background: rgba(88, 166, 255, 0.15); color: #58A6FF; 
        padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }

    /* [버튼] 프리미엄 그라디언트 버튼 */
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 600; font-size: 15px;
        background: linear-gradient(135deg, #238636 0%, #2EA043 100%); /* GitHub Green Style */
        color: white; border: 1px solid rgba(255,255,255,0.1); height: 50px;
        box-shadow: 0 4px 12px rgba(35, 134, 54, 0.4);
        transition: all 0.2s;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); box-shadow: 0 6px 15px rgba(35, 134, 54, 0.6); filter: brightness(1.1);
    }
    
    /* [푸터] */
    .footer { text-align: center; color: #484F58; font-size: 11px; margin-top: 50px; border-top: 1px solid #21262D; padding-top: 20px;}
    
    /* 모바일 대응 */
    @media screen and (max-width: 768px) {
        .block-container { padding: 0.5rem !important; }
        .index-value { font-size: 20px; }
        .stock-name { font-size: 14px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 (기능 유지) ---

def get_latest_business_day():
    now = datetime.datetime.now(korea)
    if now.weekday() == 5: target = now - datetime.timedelta(days=1)
    elif now.weekday() == 6: target = now - datetime.timedelta(days=2)
    elif now.hour < 9: 
        target = now - datetime.timedelta(days=1)
        if target.weekday() >= 5: target = target - datetime.timedelta(days=(target.weekday() - 4))
    else: target = now
    return target.strftime("%Y%m%d")

KR_TARGET_DATE = get_latest_business_day()

def get_kr_index(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    try:
        df = stock.get_index_ohlcv_by_date((datetime.datetime.strptime(KR_TARGET_DATE, "%Y%m%d")-datetime.timedelta(days=7)).strftime("%Y%m%d"), KR_TARGET_DATE, ticker)
        curr, prev = df['종가'].iloc[-1], df['종가'].iloc[-2]
        return curr, curr-prev, ((curr-prev)/prev)*100
    except: return 0, 0, 0

def analyze_kr_stock(ticker):
    try:
        start = (datetime.datetime.strptime(KR_TARGET_DATE, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, KR_TARGET_DATE, ticker)
        if len(df) < 30: return 0
        bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = bb.bollinger_lband()
        score = 0
        if (df['저가'].iloc[-2] <= df['bb_low'].iloc[-2] or df['저가'].iloc[-1] <= df['bb_low'].iloc[-1]) and df['종가'].iloc[-1] > df['bb_low'].iloc[-1]: score += 4
        if df['종가'].iloc[-1] > SMAIndicator(close=df["종가"], window=5).sma_indicator().iloc[-1]: score += 1
        if 30 <= RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1] <= 50: score += 2
        if df['거래량'].iloc[-20:-1].mean() > 0 and df['거래량'].iloc[-1] > df['거래량'].iloc[-20:-1].mean() * 1.1: score += 1
        return score
    except: return -1

US_TARGETS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'GOOGL', 'META', 'NFLX', 'AMD', 'INTC', 'SPY', 'QQQ', 'SOXL', 'TQQQ', 'COIN', 'PLTR', 'IONQ', 'JOBY']

def get_us_index(symbol):
    try:
        df = yf.Ticker(symbol).history(period="5d")
        curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
        return curr, curr-prev, ((curr-prev)/prev)*100
    except: return 0, 0, 0

def analyze_us_stock(symbol):
    try:
        df = yf.Ticker(symbol).history(period="3mo")
        if len(df) < 30: return 0, None
        bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df['bb_low'] = bb.bollinger_lband()
        score = 0
        if (df['Low'].iloc[-2] <= df['bb_low'].iloc[-2] or df['Low'].iloc[-1] <= df['bb_low'].iloc[-1]) and df['Close'].iloc[-1] > df['bb_low'].iloc[-1]: score += 4
        if df['Close'].iloc[-1] > SMAIndicator(close=df["Close"], window=5).sma_indicator().iloc[-1]: score += 1
        if 30 <= RSIIndicator(close=df["Close"], window=14).rsi().iloc[-1] <= 50: score += 2
        if df['Volume'].iloc[-20:-1].mean() > 0 and df['Volume'].iloc[-1] > df['Volume'].iloc[-20:-1].mean() * 1.1: score += 1
        return score, {'price': df['Close'].iloc[-1], 'rate': ((df['Close'].iloc[-1]-df['Close'].iloc[-2])/df['Close'].iloc[-2])*100}
    except: return 0, None

# --- 4. 메인 UI 구성 ---

st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">MAGIC STOCK <span style="font-size:12px; font-weight:400; color:#58A6FF; vertical-align:middle; margin-left:5px; border:1px solid #58A6FF; padding:1px 4px; border-radius:4px;">PRO</span></div>
        <div class="current-time">{datetime.datetime.now(korea).strftime('%m.%d %H:%M')}</div>
    </div>
""", unsafe_allow_html=True)

tab_kr, tab_us = st.tabs(["KOREA (KRX)", "USA (NYSE/NAS)"])

# === [TAB 1] 국내 증시 ===
with tab_kr:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-title">MARKET INDEX</div>', unsafe_allow_html=True)
        ic1, ic2 = st.columns(2)
        for m, c in zip(["KOSPI", "KOSDAQ"], [ic1, ic2]):
            val, chg, rt = get_kr_index(m)
            c.markdown(f"""
                <div class="index-card">
                    <div class="index-name">{m}</div>
                    <div class="index-value">{val:,.2f}</div>
                    <div class="{'up' if chg>0 else 'down'}" style="font-size:14px; font-weight:600;">{'+' if chg>0 else ''}{chg:,.2f} ({'+' if chg>0 else ''}{rt:.2f}%)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">AI QUANT STRATEGY</div>', unsafe_allow_html=True)
        # 라디오 버튼 커스텀 스타일이 어려우므로 텍스트로 대체하거나 기본 사용
        kr_market = st.radio("Target Market", ["KOSPI", "KOSDAQ"], horizontal=True, key="kr_radio", label_visibility="collapsed")
        
        if st.button("START ANALYSIS", key="btn_kr"):
            with st.spinner("QUANT ENGINE RUNNING..."):
                try:
                    base = stock.get_market_price_change_by_ticker(KR_TARGET_DATE, KR_TARGET_DATE, market=kr_market)
                    filtered = base[(base['등락률'] >= 0.5) & (base['거래량'] > 100000)].sort_values('거래량', ascending=False).head(30)
                    
                    picks = []
                    bar = st.progress(0)
                    for i, t in enumerate(filtered.index):
                        s = analyze_kr_stock(t)
                        if s >= 4:
                            picks.append({'t': t, 'n': stock.get_market_ticker_name(t), 'p': filtered.loc[t,'종가'], 'r': filtered.loc[t,'등락률'], 's': s})
                        bar.progress((i+1)/len(filtered))
                    bar.empty()
                    
                    if picks:
                        st.markdown(f'<div style="padding:10px 0; font-size:13px; color:#58A6FF;">DETECTED: {len(picks)} STOCKS</div>', unsafe_allow_html=True)
                        st.markdown('<div style="border-radius:12px; overflow:hidden; border:1px solid #30363D;">', unsafe_allow_html=True)
                        for p in sorted(picks, key=lambda x: x['s'], reverse=True):
                            st.markdown(f"""
                                <div class="stock-row">
                                    <div>
                                        <div class="stock-name">{p['n']} <span class="score-badge">SCORE {p['s']}</span></div>
                                        <div class="stock-sub">{p['t']}</div>
                                    </div>
                                    <div class="stock-price">
                                        <div class="{'up' if p['r']>0 else 'down'}">{p['p']:,}</div>
                                        <div class="{'up' if p['r']>0 else 'down'}" style="font-size:12px;">{'+' if p['r']>0 else ''}{p['r']:.2f}%</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else: st.info("NO SIGNALS DETECTED.")
                except Exception as e: st.error(f"ERROR: {e}")

    with col2:
        st.markdown('<div class="section-title">TOP VOLUME</div>', unsafe_allow_html=True)
        try:
            top = stock.get_market_ohlcv_by_ticker(KR_TARGET_DATE, market=kr_market).sort_values('거래량', ascending=False).head(10)
            st.markdown('<div style="border-radius:12px; overflow:hidden; border:1px solid #30363D;">', unsafe_allow_html=True)
            for t in top.index:
                st.markdown(f"""
                    <div class="stock-row" style="padding:12px 16px;">
                        <span class="stock-name" style="font-size:14px;">{stock.get_market_ticker_name(t)}</span>
                        <span style="font-size:13px; color:#8B949E; font-family:'Courier New';">{top.loc[t,'거래량']//1000:,}K</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except: st.write("-")

# === [TAB 2] 미국 증시 ===
with tab_us:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-title">WALL STREET</div>', unsafe_allow_html=True)
        ic1, ic2 = st.columns(2)
        indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
        for i, (n, t) in enumerate(indices.items()):
            val, chg, rt = get_us_index(t)
            (ic1 if i==0 else ic2).markdown(f"""
                <div class="index-card">
                    <div class="index-name">{n}</div>
                    <div class="index-value">{val:,.2f}</div>
                    <div class="{'up' if chg>0 else 'down'}" style="font-size:14px; font-weight:600;">{'+' if chg>0 else ''}{chg:,.2f} ({'+' if chg>0 else ''}{rt:.2f}%)</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="section-title">AI QUANT ANALYZE</div>', unsafe_allow_html=True)
        st.info("Tracking Top 50 Major US Stocks & ETFs")
        
        if st.button("START ANALYSIS", key="btn_us"):
            with st.spinner("FETCHING DATA..."):
                picks = []
                bar = st.progress(0)
                for i, t in enumerate(US_TARGETS):
                    s, d = analyze_us_stock(t)
                    if s >= 4 and d:
                        picks.append({'t': t, 'p': d['price'], 'r': d['rate'], 's': s})
                    bar.progress((i+1)/len(US_TARGETS))
                bar.empty()
                
                if picks:
                    st.markdown(f'<div style="padding:10px 0; font-size:13px; color:#58A6FF;">DETECTED: {len(picks)} STOCKS</div>', unsafe_allow_html=True)
                    st.markdown('<div style="border-radius:12px; overflow:hidden; border:1px solid #30363D;">', unsafe_allow_html=True)
                    for p in sorted(picks, key=lambda x: x['s'], reverse=True):
                        st.markdown(f"""
                            <div class="stock-row">
                                <div>
                                    <div class="stock-name">{p['t']} <span class="score-badge">SCORE {p['s']}</span></div>
                                    <div class="stock-sub">US MARKET</div>
                                </div>
                                <div class="stock-price">
                                    <div class="{'up' if p['r']>0 else 'down'}">${p['p']:,.2f}</div>
                                    <div class="{'up' if p['r']>0 else 'down'}" style="font-size:12px;">{'+' if p['r']>0 else ''}{p['r']:.2f}%</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else: st.info("NO STRONG SIGNALS.")

    with col2:
        st.markdown('<div class="section-title">WATCHLIST (TOP 10)</div>', unsafe_allow_html=True)
        watch_list = ['NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD', 'SOXL', 'TQQQ']
        
        st.markdown('<div style="border-radius:12px; overflow:hidden; border:1px solid #30363D;">', unsafe_allow_html=True)
        for t in watch_list:
            try:
                df = yf.Ticker(t).history(period="2d")
                curr = df['Close'].iloc[-1]
                rt = ((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2])*100
                st.markdown(f"""
                    <div class="stock-row" style="padding:12px 16px;">
                        <span class="stock-name" style="font-size:15px;">{t}</span>
                        <span class="{'up' if rt>0 else 'down'}" style="font-weight:700; font-size:15px;">${curr:.2f} <span style="font-size:12px; font-weight:500;">({rt:.2f}%)</span></span>
                    </div>
                """, unsafe_allow_html=True)
            except: pass
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">MAGIC STOCK PRO ver 2.0 | Secured by Python</div>', unsafe_allow_html=True)
