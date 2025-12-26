import pytz
korea = pytz.timezone("Asia/Seoul")
import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 증권사 스타일 CSS (High-Density Professional UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    /* 전체 배경: 증권사 특유의 밝은 회색 배경 */
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
        padding: 15px 25px;
        border-bottom: 1px solid #E5E8EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .brand-name {
        font-size: 20px;
        font-weight: 700;
        color: #0052CC; /* 증권사 블루 */
        letter-spacing: -0.5px;
    }

    /* 실시간 시계 */
    .live-clock {
        font-size: 14px;
        font-weight: 500;
        color: #6B7684;
    }

    /* 섹션 제목 스타일 */
    .section-title {
        font-size: 18px;
        font-weight: 700;
        color: #1A1A1A;
        margin: 25px 0 15px 0;
        padding-left: 10px;
        border-left: 4px solid #0052CC;
    }

    /* 시장 지수 카드 */
    .index-card {
        background: white;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #E5E8EB;
        text-align: left;
    }
    .index-name { font-size: 13px; color: #6B7684; font-weight: 500; }
    .index-value { font-size: 20px; font-weight: 700; margin: 4px 0; }
    .index-change { font-size: 13px; font-weight: 600; }

    /* 분석 버튼: 증권사 메인 버튼 스타일 */
    .stButton>button {
        width: 100% !important;
        height: 50px;
        background: #0052CC !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }

    /* 종목 리스트 스타일 (MTS 스타일) */
    .stock-row {
        background: white;
        border-bottom: 1px solid #F2F4F7;
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: background 0.2s;
    }
    .stock-row:hover { background: #F9FAFB; }
    .stock-info-main { display: flex; flex-direction: column; }
    .stock-name { font-size: 16px; font-weight: 600; color: #1A1A1A; }
    .stock-code { font-size: 12px; color: #ADB5BD; }
    
    .stock-price-area { text-align: right; }
    .current-price { font-size: 16px; font-weight: 700; }
    .price-change { font-size: 12px; font-weight: 500; }

    .up { color: #E52E2E; } /* 상승: 빨강 */
    .down { color: #0055FF; } /* 하락: 파랑 */

    /* 푸터 */
    .footer {
        padding: 40px 20px;
        text-align: center;
        font-size: 12px;
        color: #8B95A1;
        background: #F9FAFB;
        margin-top: 50px;
    }

    /* Streamlit 기본 요소 제거 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    
    <script>
    function updateClock() {
        const now = new Date();
        const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        document.getElementById('live-clock-text').innerText = now.toLocaleString('ko-KR', options);
    }
    setInterval(updateClock, 1000);
    </script>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 (기존 로직 유지) ---

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

# 상단 네비게이션 바
st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">📊 MAGIC STOCK.</div>
        <div id="live-clock-text" class="live-clock">
            {datetime.datetime.now(korea).strftime('%Y.%m.%d %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 메인 레이아웃
main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown('<div class="section-title">현재시황</div>', unsafe_allow_html=True)
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

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        본 서비스에서 제공하는 모든 정보는 투자 참고 사항이며,<br>
        최종 투자 판단의 책임은 본인에게 있습니다.<br><br>
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)













