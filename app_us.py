import streamlit as st
import pytz
import datetime
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# 라이브러리 예외처리 (설치 안 된 경우 안내)
try:
    from pykrx import stock
    import yfinance as yf
except ImportError:
    st.error("필수 라이브러리가 설치되지 않았습니다. 터미널에 'pip install pykrx yfinance ta'를 입력하세요.")
    st.stop()

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK ALL-IN-ONE", layout="wide", initial_sidebar_state="expanded")

korea = pytz.timezone("Asia/Seoul")

# --- 2. 스타일 CSS (공통) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #F2F4F7; color: #1A1A1A; }
    html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }

    .block-container { padding-top: 1rem !important; padding-bottom: 3rem !important; }
    header[data-testid="stHeader"] { display: none !important; }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E5E8EB; }

    /* 상단 네비게이션 */
    .top-nav {
        background-color: #FFFFFF; padding: 15px 25px; border-bottom: 1px solid #E5E8EB;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;
        border-radius: 12px;
    }
    .brand-name { font-size: 22px; font-weight: 800; color: #0052CC; }
    .market-badge { 
        background-color: #EBF3FF; color: #0052CC; padding: 4px 10px; 
        border-radius: 6px; font-size: 13px; font-weight: 600; margin-left: 10px;
    }

    /* 카드 및 리스트 스타일 */
    .section-title { font-size: 18px; font-weight: 700; color: #1A1A1A; margin: 25px 0 15px 0; border-left: 4px solid #0052CC; padding-left: 10px; }
    .index-card { background: white; border-radius: 12px; padding: 15px; border: 1px solid #E5E8EB; }
    .index-value { font-size: 20px; font-weight: 700; margin: 4px 0; }
    .stock-row { background: white; border-bottom: 1px solid #F2F4F7; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
    .stock-row:hover { background: #F9FAFB; }
    
    .up { color: #E52E2E; } 
    .down { color: #0055FF; }

    /* 버튼 커스텀 */
    .stButton>button {
        width: 100%; border-radius: 8px; font-weight: 600;
        background-color: #0052CC; color: white; border: none; height: 45px;
    }
    .stButton>button:hover { background-color: #0043a8; color: white; }
    
    .footer { text-align: center; color: #8B95A1; font-size: 12px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 공통 함수 및 로직 ---

# [국내] 주말/공휴일 처리
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

# [국내] 데이터 로직
def get_kr_index(market_name):
    if market_name == "KONEX": return 0, 0, 0
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
        
        # 전략
        if (df['저가'].iloc[-2] <= df['bb_low'].iloc[-2] or df['저가'].iloc[-1] <= df['bb_low'].iloc[-1]) and df['종가'].iloc[-1] > df['bb_low'].iloc[-1]: score += 4
        if df['종가'].iloc[-1] > SMAIndicator(close=df["종가"], window=5).sma_indicator().iloc[-1]: score += 1
        if 30 <= RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1] <= 50: score += 2
        if df['거래량'].iloc[-20:-1].mean() > 0 and df['거래량'].iloc[-1] > df['거래량'].iloc[-20:-1].mean() * 1.1: score += 1
        
        return score
    except: return -1

# [미국] 데이터 로직
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

# --- 4. 사이드바 및 메인 레이아웃 ---

with st.sidebar:
    st.markdown("## 🔮 MAGIC STOCK")
    mode = st.radio("시장 선택", ["🇰🇷 국내 증시 (KRX)", "🇺🇸 미국 증시 (US)"], index=0)
    st.markdown("---")
    st.info("국내장은 KOSPI/KOSDAQ/KONEX 전 종목을, 미국장은 주요 우량주/ETF 50여개를 대상으로 분석합니다.")

# --- 메인 화면 렌더링 ---

# 1. 국내 증시 모드
if mode == "🇰🇷 국내 증시 (KRX)":
    st.markdown(f"""
        <div class="top-nav">
            <div style="display:flex; align-items:center;">
                <span class="brand-name">Domestic Market</span>
                <span class="market-badge">KRX</span>
            </div>
            <div style="color:#6B7684; font-size:14px;">{datetime.datetime.now(korea).strftime('%Y.%m.%d %H:%M')} (기준: {KR_TARGET_DATE})</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 지수
        ic1, ic2 = st.columns(2)
        for idx, (m, c) in enumerate(zip(["KOSPI", "KOSDAQ"], [ic1, ic2])):
            val, chg, rt = get_kr_index(m)
            c.markdown(f"""
                <div class="index-card">
                    <div style="color:#6B7684; font-size:13px;">{m}</div>
                    <div class="index-value">{val:,.2f}</div>
                    <div class="{'up' if chg>0 else 'down'}" style="font-size:13px; font-weight:600;">{'+' if chg>0 else ''}{chg:,.2f} ({'+' if chg>0 else ''}{rt:.2f}%)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">AI 추천종목 분석</div>', unsafe_allow_html=True)
        kr_market = st.radio("분석 대상", ["KOSPI", "KOSDAQ", "KONEX"], horizontal=True)
        
        if st.button("🚀 국내 종목 분석 시작"):
            with st.spinner("전 종목 스캔 및 퀀트 분석 중..."):
                try:
                    base = stock.get_market_price_change_by_ticker(KR_TARGET_DATE, KR_TARGET_DATE, market=kr_market)
                    vol_cut = 10000 if kr_market == "KONEX" else 100000
                    filtered = base[(base['등락률'] >= 0.5) & (base['거래량'] > vol_cut)].sort_values('거래량', ascending=False).head(30)
                    
                    picks = []
                    bar = st.progress(0)
                    for i, t in enumerate(filtered.index):
                        s = analyze_kr_stock(t)
                        if s >= 4:
                            picks.append({'t': t, 'n': stock.get_market_ticker_name(t), 'p': filtered.loc[t,'종가'], 'r': filtered.loc[t,'등락률'], 's': s})
                        bar.progress((i+1)/len(filtered))
                    bar.empty()
                    
                    if picks:
                        st.success(f"분석 완료! {len(picks)}개 종목 포착")
                        for p in sorted(picks, key=lambda x: x['s'], reverse=True):
                            st.markdown(f"""
                                <div class="stock-row">
                                    <div>
                                        <div style="font-weight:600; font-size:16px;">{p['n']}</div>
                                        <div style="font-size:12px; color:#999;">{p['t']} | <b style="color:#0052CC">SCORE {p['s']}</b></div>
                                    </div>
                                    <div style="text-align:right;">
                                        <div class="{'up' if p['r']>0 else 'down'}" style="font-weight:700; font-size:16px;">{p['p']:,}원</div>
                                        <div class="{'up' if p['r']>0 else 'down'}" style="font-size:12px;">{'+' if p['r']>0 else ''}{p['r']:.2f}%</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                    else: st.info("조건에 맞는 종목이 없습니다.")
                except Exception as e: st.error(f"데이터 오류: {e}")

    with col2:
        st.markdown(f'<div class="section-title">{kr_market} 거래 상위</div>', unsafe_allow_html=True)
        try:
            top = stock.get_market_ohlcv_by_ticker(KR_TARGET_DATE, market=kr_market).sort_values('거래량', ascending=False).head(10)
            for t in top.index:
                st.markdown(f"""
                    <div style="padding:10px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between;">
                        <span>{stock.get_market_ticker_name(t)}</span>
                        <span style="color:#666;">{top.loc[t,'거래량']//1000:,}천주</span>
                    </div>
                """, unsafe_allow_html=True)
        except: st.write("대기중...")

# 2. 미국 증시 모드
else:
    st.markdown(f"""
        <div class="top-nav">
            <div style="display:flex; align-items:center;">
                <span class="brand-name">US Market</span>
                <span class="market-badge">NASDAQ / NYSE</span>
            </div>
            <div style="color:#6B7684; font-size:14px;">{datetime.datetime.now().strftime('%Y.%m.%d %H:%M')}</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        ic1, ic2 = st.columns(2)
        indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
        for i, (n, t) in enumerate(indices.items()):
            val, chg, rt = get_us_index(t)
            (ic1 if i==0 else ic2).markdown(f"""
                <div class="index-card">
                    <div style="color:#6B7684; font-size:13px;">{n}</div>
                    <div class="index-value">{val:,.2f}</div>
                    <div class="{'up' if chg>0 else 'down'}" style="font-size:13px; font-weight:600;">{'+' if chg>0 else ''}{chg:,.2f} ({'+' if chg>0 else ''}{rt:.2f}%)</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="section-title">AI 추천종목 분석 (Major Tech & ETF)</div>', unsafe_allow_html=True)
        
        if st.button("🚀 미국 종목 분석 시작"):
            with st.spinner("월스트리트 데이터 수신 중..."):
                picks = []
                bar = st.progress(0)
                for i, t in enumerate(US_TARGETS):
                    s, d = analyze_us_stock(t)
                    if s >= 4 and d:
                        picks.append({'t': t, 'p': d['price'], 'r': d['rate'], 's': s})
                    bar.progress((i+1)/len(US_TARGETS))
                bar.empty()
                
                if picks:
                    st.success(f"분석 완료! {len(picks)}개 종목 포착")
                    for p in sorted(picks, key=lambda x: x['s'], reverse=True):
                        st.markdown(f"""
                            <div class="stock-row">
                                <div>
                                    <div style="font-weight:600; font-size:16px;">{p['t']}</div>
                                    <div style="font-size:12px; color:#999;">US STOCK | <b style="color:#0052CC">SCORE {p['s']}</b></div>
                                </div>
                                <div style="text-align:right;">
                                    <div class="{'up' if p['r']>0 else 'down'}" style="font-weight:700; font-size:16px;">${p['p']:,.2f}</div>
                                    <div class="{'up' if p['r']>0 else 'down'}" style="font-size:12px;">{'+' if p['r']>0 else ''}{p['r']:.2f}%</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else: st.info("강력 매수 신호가 포착되지 않았습니다.")

    with col2:
        st.markdown('<div class="section-title">관심 종목 시세</div>', unsafe_allow_html=True)
        watch_list = ['NVDA', 'TSLA', 'AAPL', 'SOXL', 'TQQQ']
        for t in watch_list:
            try:
                df = yf.Ticker(t).history(period="2d")
                curr = df['Close'].iloc[-1]
                rt = ((curr - df['Close'].iloc[-2])/df['Close'].iloc[-2])*100
                st.markdown(f"""
                    <div style="padding:12px 0; border-bottom:1px solid #eee; display:flex; justify-content:space-between;">
                        <span style="font-weight:600;">{t}</span>
                        <span class="{'up' if rt>0 else 'down'}" style="font-weight:700;">${curr:.2f} ({'+' if rt>0 else ''}{rt:.2f}%)</span>
                    </div>
                """, unsafe_allow_html=True)
            except: pass

st.markdown('<div class="footer">Copyright ⓒ 2026 Bohemian All rights reserved.</div>', unsafe_allow_html=True)
