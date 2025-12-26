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

# --- 2. 증권사 스타일 CSS (타이틀 크기 대폭 확대 및 시계 로직 개선) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

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
        padding: 25px 30px; 
        border-bottom: 3px solid #0052CC; /* 하단 포인트를 더 굵게 */
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 999;
        margin-bottom: 20px;
    }
    
    /* 타이틀 크기 대폭 확대 (요청 반영) */
    .brand-name {
        font-size: 48px; /* 기존보다 훨씬 크게 확대 */
        font-weight: 800;
        color: #0052CC;
        letter-spacing: -2px;
        line-height: 1;
    }

    /* 실시간 시계 디자인 개선 */
    .live-clock {
        font-size: 18px;
        font-weight: 700;
        color: #333D4B;
        background: #F9FAFB;
        padding: 10px 20px;
        border-radius: 12px;
        border: 1px solid #E5E8EB;
        font-family: 'Courier New', monospace; /* 숫자 간격 고정 */
        min-width: 220px;
        text-align: center;
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

    /* 지수 카드 및 기타 스타일 유지 */
    .index-card { background: white; border-radius: 12px; padding: 20px; border: 1px solid #E5E8EB; }
    .index-name { font-size: 14px; color: #6B7684; font-weight: 600; }
    .index-value { font-size: 24px; font-weight: 700; margin: 5px 0; }
    .index-change { font-size: 14px; font-weight: 600; }

    .stButton>button {
        width: 100% !important; height: 55px;
        background: #0052CC !important; color: #FFFFFF !important;
        border-radius: 12px !important; font-size: 18px !important; font-weight: 700 !important;
    }

    .stock-row { background: white; border-bottom: 1px solid #F2F4F7; padding: 18px 20px; display: flex; justify-content: space-between; align-items: center; }
    .stock-name { font-size: 17px; font-weight: 700; }
    .up { color: #E52E2E; }
    .down { color: #0055FF; }

    .footer { padding: 40px; text-align: center; font-size: 13px; color: #8B95A1; background: #F9FAFB; margin-top: 50px; }
    
    /* 기본 요소 제거 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 실시간 시계 및 타이틀 출력 (HTML과 Script를 결합하여 오류 방지) ---
st.markdown("""
    <div class="top-nav">
        <div class="brand-name">MAGIC STOCK.</div>
        <div id="live-clock-target" class="live-clock">시간 계산 중...</div>
    </div>

    <script>
    (function() {
        function updateClock() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            const timeString = `${year}.${month}.${day} ${hours}:${minutes}:${seconds}`;
            const element = document.getElementById('live-clock-target');
            if (element) {
                element.innerText = timeString;
            }
        }
        updateClock();
        setInterval(updateClock, 1000);
    })();
    </script>
    """, unsafe_allow_html=True)


# --- 4. 데이터 로직 (기존 유지) ---

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

# --- 5. 메인 UI 구성 ---

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
                                <span class="stock-name">{p['name']}</span>
                                <span style="font-size:13px; color:#ADB5BD;">{p['ticker']} | <b style="color:#0052CC">강력매수 SCORE {p['score']}</b></span>
                            </div>
                            <div style="text-align:right;">
                                <div class="current-price {color_class}">{p['price']:,}원</div>
                                <div class="price-change {color_class}">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                                <div style="font-size:11px; color:#34C759; margin-top:4px; font-weight:600;">목표가: {p['target']:,}원</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("현재 분석 기준(Score 4점 이상)을 충족하는 종목이 없습니다.")

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
                    <span style="font-size:14px; color:#0052CC; font-weight:700;">{row['거래량']//10000:,}만 주</span>
                </div>
            """, unsafe_allow_html=True)
    except:
        st.write("장 개시 전이거나 데이터를 불러올 수 없습니다.")

# --- 6. 푸터 ---
st.markdown("""
    <div class="footer">
        본 서비스의 알고리즘은 볼린저밴드 하단 이탈 및 RSI 과매도 구간을 분석합니다.<br>
        모든 투자의 책임은 투자자 본인에게 있습니다.<br><br>
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)
