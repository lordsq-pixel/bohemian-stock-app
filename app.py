import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands
import time

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 화이트톤 프리미엄 CSS (실시간 시계 및 깔끔한 UI) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');

    /* 메인 배경: 밝은 화이트/그레이 */
    .stApp {
        background-color: #F8F9FA;
        color: #1D1D1F;
    }
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }

    /* 헤더 영역 */
    .header-box {
        text-align: center;
        padding: 40px 20px 20px 20px;
        background: white;
        border-bottom: 1px solid #E5E5E7;
        margin-bottom: 30px;
    }
    .main-title {
        font-size: 32px;
        font-weight: 800;
        color: #007AFF; /* 신뢰감 있는 블루 */
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    .sub-title {
        font-size: 13px;
        color: #86868B;
        font-weight: 400;
        letter-spacing: 1.5px;
        text-transform: uppercase;
    }

    /* 실시간 시계 스타일 */
    .clock-container {
        font-size: 16px;
        font-weight: 600;
        color: #1D1D1F;
        text-align: right;
        margin-bottom: 10px;
    }

    /* 분석 버튼: 애플 스타일 블루 */
    .stButton>button {
        width: 100% !important;
        height: 55px;
        background: #007AFF !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 17px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background: #0051FF !important;
        box-shadow: 0 4px 15px rgba(0, 122, 255, 0.3);
    }

    /* 시장 신호등 카드 (화이트 모드) */
    .signal-container {
        background: white;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #F2F2F7;
    }

    /* 종목 결과 카드 */
    .stock-item {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
        border: 1px solid #E5E5E7;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease;
    }
    .stock-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.08);
    }

    /* 지표 강조 */
    .metric-label { font-size: 11px; color: #86868B; }
    .metric-value { font-size: 17px; font-weight: 700; color: #1D1D1F; }

    /* 푸터 */
    .footer {
        text-align: center;
        padding: 60px 20px;
        font-size: 12px;
        color: #A1A1A6;
        line-height: 1.6;
    }

    /* 테이블 스타일 조정 */
    .stDataEditor {
        background-color: white !important;
        border-radius: 12px !important;
    }

    /* Streamlit 요소 정리 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    
    <script>
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ko-KR', { hour12: false });
        const dateString = now.toLocaleDateString('ko-KR');
        document.getElementById('live-clock').innerText = dateString + " " + timeString;
    }
    setInterval(updateClock, 1000);
    </script>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 (기존 로직 유지) ---

def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2:
            return "⚪ 준비중", "데이터 로딩 중...", "#F2F2F7", "#1D1D1F"
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        if rate > 0.5:
            return "📈 MARKET BULL", f"지수 {rate:.2f}% 상승 중. 공격적인 투자가 유리한 시점입니다.", "#E1F5FE", "#0288D1"
        elif rate > -0.5:
            return "⚖️ MARKET NEUTRAL", f"지수 {rate:.2f}% 보합. 철저한 종목별 차별화 장세입니다.", "#FFF9C4", "#FBC02D"
        else:
            return "📉 MARKET BEAR", f"지수 {rate:.2f}% 하락 중. 현금 비중을 높이고 보수적으로 대응하세요.", "#FFEBEE", "#D32F2F"
    except:
        return "⚪ ERROR", "연결 실패", "#F2F2F7", "#1D1D1F"

def analyze_stock(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 30: return 0
        
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        
        curr_close = df['종가'].iloc[-1]
        curr_low = df['저가'].iloc[-1]
        prev_low = df['저가'].iloc[-2]
        
        rsi = RSIIndicator(close=df["종가"], window=14, fillna=True).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5, fillna=True).sma_indicator().iloc[-1]
        
        score = 0
        touched_bottom = (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1])
        is_rebounding = curr_close > df['bb_low'].iloc[-1]
        
        if touched_bottom and is_rebounding: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 50: score += 2
        
        volume_curr = df['거래량'].iloc[-1]
        volume_avg = df['거래량'].iloc[-20:-1].mean()
        if volume_curr > volume_avg * 1.1: score += 1
        
        return score
    except: return -1

# --- 4. 메인 UI 구성 ---

# 헤더 & 실시간 시계
st.markdown(f"""
    <div class="header-box">
        <div class="main-title">MAGIC STOCK</div>
        <div class="sub-title">Smart AI Investment Curator</div>
    </div>
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 20px;">
        <div id="live-clock" class="clock-container">
            {datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# 레이아웃 컨테이너
container = st.container()

with container:
    col_sel, col_empty = st.columns([1, 2])
    with col_sel:
        market_type = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"], label_visibility="collapsed")

    today_str = datetime.datetime.now().strftime("%Y%m%d")

    if st.button('🔍 시장 분석 시작'):
        # A. 시장 상태 알림
        title, desc, bg_color, text_color = get_market_status(market_type)
        st.markdown(f"""
            <div class="signal-container" style="background-color: {bg_color}; border: 1px solid {text_color}44;">
                <div style="font-size: 20px; font-weight: 800; color: {text_color}; margin-bottom: 5px;">{title}</div>
                <div style="font-size: 14px; color: #48484A;">{desc}</div>
            </div>
        """, unsafe_allow_html=True)

        with st.spinner('알고리즘이 유망 종목을 선별하고 있습니다...'):
            df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
            filtered = df_base[
                (df_base['등락률'] >= 0.5) & 
                (df_base['등락률'] <= 3.0) & 
                (df_base['거래량'] > 100000)
            ].sort_values('거래량', ascending=False).head(20)

            picks = []
            for ticker in filtered.index:
                name = stock.get_market_ticker_name(ticker)
                score = analyze_stock(ticker, today_str)
                if score >= 4:
                    price = filtered.loc[ticker, '종가']
                    picks.append({
                        'ticker': ticker,
                        'name': name,
                        'price': price,
                        'rate': filtered.loc[ticker, '등락률'],
                        'score': score,
                        'target': int(price * 1.03)
                    })

        # B. 추천 종목 리스트
        st.markdown("<div style='margin: 30px 0 15px 5px; font-weight:800; font-size:20px; color:#1D1D1F;'>🎯 오늘의 골든 타이밍</div>", unsafe_allow_html=True)
        
        if picks:
            picks_sorted = sorted(picks, key=lambda x: x['score'], reverse=True)[:5]
            for p in picks_sorted:
                st.markdown(f"""
                    <div class="stock-item">
                        <div style="flex: 1;">
                            <div style="font-size: 11px; color: #86868B; margin-bottom: 2px;">{p['ticker']}</div>
                            <div style="font-size: 19px; font-weight: 700; color: #1D1D1F;">{p['name']}</div>
                            <div style="display: flex; gap: 8px; margin-top: 8px;">
                                <span style="background: #007AFF; color: #FFF; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">AI SCORE {p['score']}</span>
                                <span style="color: {'#FF3B30' if p['rate'] > 0 else '#007AFF'}; font-size: 13px; font-weight: 600;">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</span>
                            </div>
                        </div>
                        <div style="text-align: right; margin-right: 20px;">
                            <div class="metric-label">현재가</div>
                            <div class="metric-value">₩{p['price']:,}</div>
                            <div class="metric-label" style="margin-top: 4px;">목표가</div>
                            <div style="font-size: 14px; font-weight: 600; color: #34C759;">₩{p['target']:,}</div>
                        </div>
                        <div>
                            <a href="https://finance.naver.com/item/main.naver?code={p['ticker']}" target="_blank" style="text-decoration: none;">
                                <div style="background: #F2F2F7; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #007AFF; font-weight: bold;">→</div>
                            </a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("조건에 부합하는 종목이 발견되지 않았습니다.")

        # C. 실시간 거래량 TOP 10
        st.markdown("<div style='margin: 40px 0 15px 5px; font-weight:800; font-size:20px; color:#1D1D1F;'>🔥 실시간 거래량 TOP 10</div>", unsafe_allow_html=True)
        top_10 = filtered.head(10).copy()
        top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10.index]
        
        st.data_editor(
            top_10[['종목명', '종가', '등락률']],
            column_config={
                "종목명": "종목명",
                "종가": st.column_config.NumberColumn("현재가", format="₩%d"),
                "등락률": st.column_config.NumberColumn("등락율", format="%.2f%%"),
            },
            hide_index=True,
            use_container_width=True,
            disabled=True
        )

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        <b>투자 참고용 주의사항</b><br>
        본 서비스는 공공 데이터를 기반으로 한 AI 분석 결과이며, 투자 손실에 대한 책임을 지지 않습니다.<br>
        성공적인 투자를 위해 시장 상황을 종합적으로 판단하시기 바랍니다.<br><br>
        Curated by <b>BOHEMIAN</b> | Clean Design Version<br>
        Copyright © 2025. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
