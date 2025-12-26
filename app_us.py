import pytz
korea = pytz.timezone("Asia/Seoul")
import streamlit as st
from pykrx import stock
import yfinance as yf # 미국 주식 라이브러리 추가
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 증권사 스타일 CSS (원본 유지) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #F2F4F7; color: #1A1A1A; }
    html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }

    /* [핵심] 상단 여백 제거 및 컨텐츠 위로 올리기 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Streamlit 기본 헤더(햄버거 메뉴 라인) 숨기기 */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* 상단 GNB (위치 보정) */
    .top-nav {
        background-color: #FFFFFF; 
        padding: 12px 25px;
        border-bottom: 1px solid #E5E8EB;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 999;
        margin-top: 0px;
    }
    
    .brand-name { font-size: 20px; font-weight: 700; color: #0052CC; letter-spacing: -0.5px; }
    .live-clock { font-size: 14px; font-weight: 500; color: #6B7684; }

    .section-title {
        font-size: 18px; font-weight: 700; color: #1A1A1A;
        margin: 25px 0 15px 0; padding-left: 10px; border-left: 4px solid #0052CC;
    }

    /* 카드 스타일 */
    .index-card {
        background: white; border-radius: 12px; padding: 15px; border: 1px solid #E5E8EB; text-align: left;
    }
    .index-name { font-size: 13px; color: #6B7684; font-weight: 500; }
    .index-value { font-size: 20px; font-weight: 700; margin: 4px 0; }
    .index-change { font-size: 13px; font-weight: 600; }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100% !important; height: 50px;
        background: #0052CC !important; color: #FFFFFF !important;
        border: none !important; border-radius: 8px !important;
        font-size: 16px !important; font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stButton>button:hover { background: #003fa3 !important; }

    /* 리스트 스타일 */
    .stock-row {
        background: white; border-bottom: 1px solid #F2F4F7; padding: 15px 20px;
        display: flex; justify-content: space-between; align-items: center; transition: background 0.2s;
    }
    .stock-row:hover { background: #F9FAFB; }
    .stock-info-main { display: flex; flex-direction: column; }
    .stock-name { font-size: 16px; font-weight: 600; color: #1A1A1A; }
    .stock-code { font-size: 12px; color: #ADB5BD; }
    .stock-price-area { text-align: right; }
    .current-price { font-size: 16px; font-weight: 700; }
    .price-change { font-size: 12px; font-weight: 500; }

    .up { color: #E52E2E; } 
    .down { color: #0055FF; }

    /* 푸터 */
    .footer { padding: 40px 20px; text-align: center; font-size: 12px; color: #8B95A1; background: #F9FAFB; margin-top: 50px; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 ---

# [기존] 국내 함수
def get_market_data(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        curr = df['종가'].iloc[-1]
        prev = df['종가'].iloc[-2]
        change = curr - prev
        rate = (change / prev) * 100
        return curr, change, rate
    except:
        return 0, 0, 0

def analyze_stock(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 30: return 0
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        curr_close, curr_low, prev_low = df['종가'].iloc[-1], df['저가'].iloc[-1], df['저가'].iloc[-2]
        rsi = RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5).sma_indicator().iloc[-1]
        
        score = 0
        if (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1]):
            if curr_close > df['bb_low'].iloc[-1]: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 50: score += 2
        if df['거래량'].iloc[-1] > df['거래량'].iloc[-20:-1].mean() * 1.1: score += 1
        return score
    except: return -1

# [추가] 미국 함수
def get_us_index(symbol):
    try:
        tk = yf.Ticker(symbol)
        df = tk.history(period="5d")
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        change = curr - prev
        rate = (change / prev) * 100
        return curr, change, rate
    except: return 0, 0, 0

def analyze_us_stock(ticker):
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="3mo")
        if len(df) < 30: return 0, 0, 0
        
        indicator_bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        
        curr_close = df['Close'].iloc[-1]
        curr_low = df['Low'].iloc[-1]
        prev_low = df['Low'].iloc[-2]
        rsi = RSIIndicator(close=df["Close"], window=14).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["Close"], window=5).sma_indicator().iloc[-1]
        
        score = 0
        if (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1]):
            if curr_close > df['bb_low'].iloc[-1]: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 50: score += 2
        
        vol_mean = df['Volume'].iloc[-20:-1].mean()
        if vol_mean > 0 and df['Volume'].iloc[-1] > vol_mean * 1.1: score += 1
        
        prev_close = df['Close'].iloc[-2]
        rate = ((curr_close - prev_close) / prev_close) * 100
        
        return score, curr_close, rate
    except: return -1, 0, 0

# --- 4. 메인 UI 구성 ---

# 상단 네비게이션
st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">📊 매직스톡 Ai</div>
        <div id="live-clock-text" class="live-clock">
            {datetime.datetime.now(korea).strftime('%Y.%m.%d %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# [핵심] 사이드바 없이 메인 화면에서 국가 선택 (라디오 버튼)
st.markdown('<div class="section-title">국가 선택</div>', unsafe_allow_html=True)
country_mode = st.radio("국가 선택", ["🇰🇷 국내주식 (KRX)", "🇺🇸 미국주식 (US)"], horizontal=True, label_visibility="collapsed")

# 메인 레이아웃 분기
main_col1, main_col2 = st.columns([2, 1])

# ==========================================
# 1. 국내주식 모드 (기존 소스 완벽 유지)
# ==========================================
if "국내" in country_mode:
    with main_col1:
        st.markdown('<div class="section-title">한국 시황</div>', unsafe_allow_html=True)
        idx_col1, idx_col2 = st.columns(2)
        
        for m_name, col in zip(["KOSPI", "KOSDAQ"], [idx_col1, idx_col2]):
            val, chg, rt = get_market_data(m_name)
            color_class = "up" if chg > 0 else "down"
            sign = "+" if chg > 0 else ""
            col.markdown(f"""
                <div class="index-card">
                    <div class="index-name">{m_name}</div>
                    <div class="index-value">{val:,.2f}</div>
                    <div class="index-change {color_class}">{sign}{chg:,.2f} ({sign}{rt:.2f}%)</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">시장선택</div>', unsafe_allow_html=True)
        m_type = st.radio("시장 선택", ["KOSPI", "KOSDAQ"], horizontal=True, label_visibility="collapsed")
        
        if st.button('🎯 AI 추천종목'):
            today_str = datetime.datetime.now().strftime("%Y%m%d")
            with st.spinner('AI 퀀트 알고리즘 추적중...'):
                df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=m_type)
                filtered = df_base[(df_base['등락률'] >= 0.5) & (df_base['거래량'] > 100000)].sort_values('거래량', ascending=False).head(20)

                picks = []
                for ticker in filtered.index:
                    score = analyze_stock(ticker, today_str)
                    if score >= 4:
                        picks.append({
                            'ticker': ticker, 'name': stock.get_market_ticker_name(ticker),
                            'price': filtered.loc[ticker, '종가'], 'rate': filtered.loc[ticker, '등락률'],
                            'score': score, 'target': int(filtered.loc[ticker, '종가'] * 1.05)
                        })

                if picks:
                    st.markdown('<div style="background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E5E8EB;">', unsafe_allow_html=True)
                    for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                        color_class = "up" if p['rate'] > 0 else "down"
                        st.markdown(f"""
                            <div class="stock-row">
                                <div class="stock-info-main">
                                    <span class="stock-name">{p['name']}</span>
                                    <span class="stock-code">{p['ticker']} | <b style="color:#0052CC">SCORE {p['score']}</b></span>
                                </div>
                                <div class="stock-price-area">
                                    <div class="current-price {color_class}">{p['price']:,}</div>
                                    <div class="price-change {color_class}">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                                    <div style="font-size:11px; color:#34C759; margin-top:2px;">Target: {p['target']:,}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("현재 분석 기준을 충족하는 종목이 없습니다.")

    with main_col2:
        st.markdown('<div class="section-title">실시간 거래 TOP 순위</div>', unsafe_allow_html=True)
        # 간단한 거래량 순위 테이블
        df_vol = stock.get_market_ohlcv_by_ticker(datetime.datetime.now().strftime("%Y%m%d"), market=m_type)
        top_vol = df_vol.sort_values('거래량', ascending=False).head(10)
        top_vol['종목명'] = [stock.get_market_ticker_name(t) for t in top_vol.index]
        
        for idx, row in top_vol.iterrows():
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding: 10px 5px; border-bottom: 1px solid #E5E8EB;">
                    <span style="font-size:14px; font-weight:500;">{row['종목명']}</span>
                    <span style="font-size:14px; color:#6B7684;">{row['거래량']//10000:,}만</span>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# 2. 미국주식 모드 (추가된 기능)
# ==========================================
else:
    with main_col1:
        st.markdown('<div class="section-title">현재재시황</div>', unsafe_allow_html=True)
        idx_col1, idx_col2 = st.columns(2)
        
        for name, ticker in zip(["S&P 500", "NASDAQ"], ["^GSPC", "^IXIC"]):
            val, chg, rt = get_us_index(ticker)
            color_class = "up" if chg > 0 else "down"
            sign = "+" if chg > 0 else ""
            
            # 국내장과 동일한 카드 디자인 적용
            with (idx_col1 if name == "S&P 500" else idx_col2):
                st.markdown(f"""
                    <div class="index-card">
                        <div class="index-name">{name}</div>
                        <div class="index-value">{val:,.2f}</div>
                        <div class="index-change {color_class}">{sign}{chg:,.2f} ({sign}{rt:.2f}%)</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="section-title">주요 종목 분석</div>', unsafe_allow_html=True)
        st.info("미국장은 주요 인기 종목 20개를 대상으로 분석합니다.")
        
        if st.button('🎯 AI 추천종목'):
            us_tickers = ['AAPL', 'NVDA', 'TSLA', 'MSFT', 'AMZN', 'GOOGL', 'META', 'AMD', 'INTC', 'QQQ', 'SPY', 'SOXL', 'TQQQ', 'COIN', 'PLTR', 'IONQ', 'JOBY', 'NFLX', 'DIS', 'KO']
            
            with st.spinner('Wall Street 데이터 분석중...'):
                picks = []
                bar = st.progress(0)
                
                for i, ticker in enumerate(us_tickers):
                    score, price, rate = analyze_us_stock(ticker)
                    if score >= 4:
                        picks.append({
                            'ticker': ticker, 'name': ticker,
                            'price': price, 'rate': rate,
                            'score': score, 'target': price * 1.05
                        })
                    bar.progress((i + 1) / len(us_tickers))
                bar.empty()

                if picks:
                    st.markdown('<div style="background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E5E8EB;">', unsafe_allow_html=True)
                    for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                        color_class = "up" if p['rate'] > 0 else "down"
                        st.markdown(f"""
                            <div class="stock-row">
                                <div class="stock-info-main">
                                    <span class="stock-name">{p['name']}</span>
                                    <span class="stock-code">US MARKET | <b style="color:#0052CC">SCORE {p['score']}</b></span>
                                </div>
                                <div class="stock-price-area">
                                    <div class="current-price {color_class}">${p['price']:,.2f}</div>
                                    <div class="price-change {color_class}">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                                    <div style="font-size:11px; color:#34C759; margin-top:2px;">Target: ${p['target']:,.2f}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("분석 기준(강력 매수 시그널)을 충족하는 종목이 없습니다.")

    with main_col2:
        st.markdown('<div class="section-title">관심 종목 시세</div>', unsafe_allow_html=True)
        watch_list = ['NVDA', 'TSLA', 'AAPL', 'SOXL']
        
        for ticker in watch_list:
            try:
                tk = yf.Ticker(ticker)
                hist = tk.history(period="2d")
                curr = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                chg = curr - prev
                rt = (chg/prev)*100
                color = "#E52E2E" if chg > 0 else "#0055FF"
                
                st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; padding: 15px 5px; border-bottom: 1px solid #E5E8EB;">
                        <span style="font-size:14px; font-weight:600;">{ticker}</span>
                        <span style="font-size:14px; color:{color}; font-weight:700;">${curr:.2f} ({rt:.2f}%)</span>
                    </div>
                """, unsafe_allow_html=True)
            except: pass

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        본 서비스에서 제공하는 모든 정보는 투자 참고 사항이며,<br>
        최종 투자 판단의 책임은 본인에게 있습니다.<br><br>
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)


