import streamlit as st
import yfinance as yf # 미국 주식 데이터 라이브러리
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK US", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 증권사 스타일 CSS (원본 동일) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #F2F4F7; color: #1A1A1A; }
    html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }

    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    header[data-testid="stHeader"] { display: none !important; }

    .top-nav {
        background-color: #FFFFFF; 
        padding: 12px 25px;
        border-bottom: 1px solid #E5E8EB;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 999;
    }
    
    .brand-name { font-size: 20px; font-weight: 700; color: #0052CC; letter-spacing: -0.5px; }
    .live-clock { font-size: 14px; font-weight: 500; color: #6B7684; }

    .section-title {
        font-size: 18px; font-weight: 700; color: #1A1A1A;
        margin: 25px 0 15px 0; padding-left: 10px; border-left: 4px solid #0052CC;
    }

    .index-card {
        background: white; border-radius: 12px; padding: 15px; border: 1px solid #E5E8EB; text-align: left;
    }
    .index-name { font-size: 13px; color: #6B7684; font-weight: 500; }
    .index-value { font-size: 20px; font-weight: 700; margin: 4px 0; }
    .index-change { font-size: 13px; font-weight: 600; }

    .stButton>button {
        width: 100% !important; height: 50px;
        background: #0052CC !important; color: #FFFFFF !important;
        border: none !important; border-radius: 8px !important;
        font-size: 16px !important; font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stButton>button:hover { background: #003fa3 !important; }

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

    .footer { padding: 40px 20px; text-align: center; font-size: 12px; color: #8B95A1; background: #F9FAFB; margin-top: 50px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

# --- 3. 미국 데이터 로직 (yfinance 사용) ---

# 분석 대상 주요 미국 주식 리스트 (빠른 속도를 위해 지정)
US_TARGETS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'NFLX', 'AMD', 'INTC', # 빅테크
    'SPY', 'QQQ', 'SOXL', 'TQQQ', 'TLT', # ETF
    'COIN', 'MSTR', 'PLTR', 'U', 'RBLX', # 성장/코인
    'JPM', 'BAC', 'WMT', 'KO', 'MCD', 'DIS', # 가치/소비재
    'AVGO', 'QCOM', 'MU', 'AMAT', 'LRCX', 'TSM', # 반도체
    'IONQ', 'JOBY', 'ACHR', 'PLUG' # 소형/미래
]

def get_us_market_index(symbol):
    try:
        # ^GSPC: S&P500, ^IXIC: NASDAQ
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        curr = df['Close'].iloc[-1]
        prev = df['Close'].iloc[-2]
        change = curr - prev
        rate = (change / prev) * 100
        return curr, change, rate
    except:
        return 0, 0, 0

def analyze_us_stock(ticker_symbol):
    try:
        # 미국장은 데이터가 많으므로 최근 3달치 호출
        tk = yf.Ticker(ticker_symbol)
        df = tk.history(period="3mo")
        
        if len(df) < 30: return -1, None
        
        # 보조지표 계산 (원본 로직 동일)
        indicator_bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        
        curr_close = df['Close'].iloc[-1]
        curr_low = df['Low'].iloc[-1]
        prev_low = df['Low'].iloc[-2]
        
        rsi = RSIIndicator(close=df["Close"], window=14).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["Close"], window=5).sma_indicator().iloc[-1]
        
        # 점수 계산 로직 (원본 동일)
        score = 0
        
        # 1. 볼린저밴드 하단 터치 후 반등 시그널 (강력 매수)
        if (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1]):
            if curr_close > df['bb_low'].iloc[-1]: score += 4
            
        # 2. 5일선 돌파
        if curr_close > sma5: score += 1
        
        # 3. RSI 과매도 구간 탈출 시도 (30~50)
        if 30 <= rsi <= 50: score += 2
        
        # 4. 거래량 급증 (평균 대비 1.1배)
        vol_mean = df['Volume'].iloc[-20:-1].mean()
        if vol_mean > 0 and df['Volume'].iloc[-1] > vol_mean * 1.1: score += 1
        
        # 등락률 계산을 위해 데이터 리턴
        prev_close = df['Close'].iloc[-2]
        change_rate = ((curr_close - prev_close) / prev_close) * 100
        
        return score, {
            'price': curr_close,
            'rate': change_rate,
            'vol': df['Volume'].iloc[-1]
        }
    except:
        return -1, None

# --- 4. 메인 UI 구성 ---

st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">🇺🇸 매직스톡 Ai (US Market)</div>
        <div id="live-clock-text" class="live-clock">
            {datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown('<div class="section-title">미국 증시 시황</div>', unsafe_allow_html=True)
    idx_col1, idx_col2 = st.columns(2)
    
    # 지수 데이터 표시
    indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC"}
    
    # 컬럼과 인덱스 매칭을 위해 zip 대신 리스트 인덱싱 사용하거나 enumerate 사용
    cols = [idx_col1, idx_col2]
    for i, (name, ticker) in enumerate(indices.items()):
        val, chg, rt = get_us_market_index(ticker)
        color_class = "up" if chg > 0 else "down"
        sign = "+" if chg > 0 else ""
        
        cols[i].markdown(f"""
            <div class="index-card">
                <div class="index-name">{name}</div>
                <div class="index-value">{val:,.2f}</div>
                <div class="index-change {color_class}">{sign}{chg:,.2f} ({sign}{rt:.2f}%)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">시장선택</div>', unsafe_allow_html=True)
    m_type = st.radio("시장 선택", ["NASDAQ/NYSE (주요종목)"], horizontal=True, label_visibility="collapsed")
    
    if st.button('🎯 AI 추천종목 분석 (US)'):
        with st.spinner('Wall Street 데이터 수신 및 퀀트 분석중...'):
            picks = []
            
            # 진행률 바
            progress_bar = st.progress(0)
            total_items = len(US_TARGETS)
            
            for idx, ticker in enumerate(US_TARGETS):
                score, data = analyze_us_stock(ticker)
                
                # 데이터가 정상적이고 점수가 4점 이상인 경우
                if score >= 4 and data is not None:
                    picks.append({
                        'ticker': ticker, 'name': ticker, # 미국은 종목명이 곧 티커인 경우가 많음
                        'price': data['price'], 'rate': data['rate'],
                        'score': score, 'target': data['price'] * 1.05
                    })
                
                # 진행률 업데이트
                progress_bar.progress((idx + 1) / total_items)
            
            progress_bar.empty()

            if picks:
                st.markdown(f'<div style="padding:10px 0; font-weight:bold; color:#0052CC;">Top Picks: {len(picks)}개 포착</div>', unsafe_allow_html=True)
                st.markdown('<div style="background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E5E8EB;">', unsafe_allow_html=True)
                
                for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                    color_class = "up" if p['rate'] > 0 else "down"
                    st.markdown(f"""
                        <div class="stock-row">
                            <div class="stock-info-main">
                                <span class="stock-name">{p['ticker']}</span>
                                <span class="stock-code">US Market | <b style="color:#0052CC">SCORE {p['score']}</b></span>
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
                st.info("현재 분석 기준(강력 매수 시그널)을 충족하는 종목이 없습니다.")

with main_col2:
    st.markdown('<div class="section-title">관심 종목 현황</div>', unsafe_allow_html=True)
    # 거래량 상위 대신, 주요 종목의 현재가를 리스트로 보여줌 (속도 문제로 대체)
    
    st.markdown('<div style="background:white; border-radius:12px; border:1px solid #E5E8EB; overflow:hidden;">', unsafe_allow_html=True)
    # 주요 5개 종목만 빠르게 보여주기
    top_watch = ['NVDA', 'TSLA', 'AAPL', 'SOXL', 'TQQQ']
    
    for t in top_watch:
        try:
            stock_info = yf.Ticker(t).history(period="2d")
            curr = stock_info['Close'].iloc[-1]
            prev = stock_info['Close'].iloc[-2]
            rate = ((curr - prev) / prev) * 100
            color = "#E52E2E" if rate > 0 else "#0055FF"
            
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding: 12px 15px; border-bottom: 1px solid #F2F4F7;">
                    <span style="font-size:14px; font-weight:600;">{t}</span>
                    <span style="font-size:14px; color:{color}; font-weight:700;">${curr:.2f} ({rate:.2f}%)</span>
                </div>
            """, unsafe_allow_html=True)
        except:
            pass
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        US Market Data Provided by Yahoo Finance<br>
        본 서비스는 투자 참고용이며, 수익을 보장하지 않습니다.<br><br>
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)
