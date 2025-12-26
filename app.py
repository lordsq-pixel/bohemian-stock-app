import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK.", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 증권사 스타일 CSS 및 실시간 시계 스크립트 (타이틀 확대 및 시계 로직 강화) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800;900&display=swap');

    /* 전체 배경 */
    .stApp {
        background-color: #F2F4F7;
        color: #1A1A1A;
    }
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, sans-serif;
    }

    /* 상단 GNB 스타일 */
    .top-nav {
        background-color: #FFFFFF;
        padding: 30px 40px; 
        border-bottom: 4px solid #0052CC; /* 블루 포인트 강조 */
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* 타이틀 크기 대폭 확대 (요청 반영: 압도적인 크기) */
    .brand-name {
        font-size: 64px; /* 훨씬 더 크게 확대 */
        font-weight: 900;
        color: #0052CC;
        letter-spacing: -3px;
        line-height: 1;
    }

    /* 실시간 시계 디자인 (폰트 가독성 강조) */
    .live-clock {
        font-size: 20px;
        font-weight: 800;
        color: #333D4B;
        background: #F9FAFB;
        padding: 12px 24px;
        border-radius: 14px;
        border: 1px solid #E5E8EB;
        font-family: 'Tahoma', sans-serif;
        min-width: 250px;
        text-align: center;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.03);
    }

    /* 섹션 제목 */
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #1A1A1A;
        margin: 30px 0 15px 0;
        padding-left: 12px;
        border-left: 5px solid #0052CC;
    }

    /* 기존 카드 스타일 유지 */
    .index-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E5E8EB; }
    .index-name { font-size: 14px; color: #6B7684; font-weight: 600; }
    .index-value { font-size: 24px; font-weight: 700; margin: 5px 0; }
    
    .stButton>button {
        width: 100% !important; height: 55px;
        background: #0052CC !important; color: #FFFFFF !important;
        border-radius: 12px !important; font-size: 18px !important; font-weight: 700 !important;
    }

    .stock-row { background: white; border-bottom: 1px solid #F2F4F7; padding: 18px 20px; display: flex; justify-content: space-between; align-items: center; }
    .up { color: #E52E2E; }
    .down { color: #0055FF; }

    .footer { padding: 40px; text-align: center; font-size: 13px; color: #8B95A1; background: #F9FAFB; margin-top: 50px; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>

    <div class="top-nav">
        <div class="brand-name">MAGIC STOCK.</div>
        <div id="live-clock-display" class="live-clock">계산 중...</div>
    </div>

    <script>
    // 시계 업데이트 함수
    function runClock() {
        const target = document.getElementById('live-clock-display');
        if (target) {
            const now = new Date();
            const y = now.getFullYear();
            const m = String(now.getMonth() + 1).padStart(2, '0');
            const d = String(now.getDate()).padStart(2, '0');
            const hh = String(now.getHours()).padStart(2, '0');
            const mm = String(now.getMinutes()).padStart(2, '0');
            const ss = String(now.getSeconds()).padStart(2, '0');
            target.innerText = `${y}.${m}.${d} ${hh}:${mm}:${ss}`;
        }
    }

    // 엘리먼트가 나타날 때까지 반복 확인 후 실행
    const clockInterval = setInterval(() => {
        if (document.getElementById('live-clock-display')) {
            runClock();
            setInterval(runClock, 1000);
            clearInterval(clockInterval);
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 (원본 소스 수정 없음) ---

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

# --- 4. 메인 UI 구성 ---

main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown('<div class="section-title">국내시장 상황</div>', unsafe_allow_html=True)
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

    st.markdown('<div class="section-title">국내시장 분석</div>', unsafe_allow_html=True)
    m_type = st.radio("시장 선택", ["KOSPI", "KOSDAQ"], horizontal=True, label_visibility="collapsed")
    
    if st.button('실시간 AI 추천종목 탐색'):
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        with st.spinner('전 종목 퀀트 알고리즘 스캔 중...'):
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
                st.markdown('<div style="background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E5E8EB; margin-top:10px;">', unsafe_allow_html=True)
                for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                    color_class = "up" if p['rate'] > 0 else "down"
                    st.markdown(f"""
                        <div class="stock-row">
                            <div class="stock-info-main">
                                <span class="stock-name" style="font-size:17px; font-weight:700;">{p['name']}</span>
                                <span style="font-size:13px; color:#ADB5BD;">{p['ticker']} | <b style="color:#0052CC">SCORE {p['score']}</b></span>
                            </div>
                            <div style="text-align:right;">
                                <div class="current-price {color_class}" style="font-size:18px; font-weight:700;">{p['price']:,}</div>
                                <div class="price-change {color_class}" style="font-size:13px;">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("조건을 충족하는 종목이 없습니다.")

with main_col2:
    st.markdown('<div class="section-title">거래량 TOP 10</div>', unsafe_allow_html=True)
    try:
        df_vol = stock.get_market_ohlcv_by_ticker(datetime.datetime.now().strftime("%Y%m%d"), market=m_type)
        top_vol = df_vol.sort_values('거래량', ascending=False).head(10)
        
        for ticker, row in top_vol.iterrows():
            name = stock.get_market_ticker_name(ticker)
            st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding: 14px 5px; border-bottom: 1px solid #E5E8EB;">
                    <span style="font-size:15px; font-weight:600;">{name}</span>
                    <span style="font-size:14px; color:#0052CC; font-weight:700;">{row['거래량']//10000:,}만</span>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("데이터 로딩 실패")

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)
