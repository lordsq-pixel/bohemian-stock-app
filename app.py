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

# --- 2. 하이엔드 럭셔리 CSS (모바일 최적화) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@300;500;700&display=swap');

    /* 메인 배경: 딥 차콜 */
    .stApp {
        background: linear-gradient(180deg, #0F0F0F 0%, #1A1A1A 100%);
        color: #FFFFFF;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    /* 헤더 영역 */
    .header-box {
        text-align: center;
        padding: 50px 20px 30px 20px;
    }
    .main-title {
        font-size: 36px;
        font-weight: 800;
        background: linear-gradient(135deg, #D4AF37 0%, #F9E29C 50%, #B8860B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        letter-spacing: -1.5px;
    }
    .sub-title {
        font-size: 14px;
        color: #8E8E93;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* 분석 버튼: 골드 카드 스타일 */
    .stButton>button {
        width: 100% !important;
        height: 65px;
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 16px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3) !important;
        transition: all 0.3s ease !important;
        margin-top: 20px;
    }
    .stButton>button:active {
        transform: scale(0.96);
    }

    /* 시장 신호등 카드 */
    .signal-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 25px;
        text-align: center;
        margin: 20px 0;
    }

    /* 종목 결과 카드 */
    .stock-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* 지표 강조 */
    .metric-label { font-size: 12px; color: #8E8E93; }
    .metric-value { font-size: 18px; font-weight: 700; color: #D4AF37; }

    /* 푸터 */
    .footer {
        text-align: center;
        padding: 50px 20px;
        font-size: 11px;
        color: #444;
        line-height: 1.8;
    }

    /* Streamlit 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 (원본 기능 100% 유지) ---

def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2:
            return "⚪ 준비중", "데이터 로딩 중...", "rgba(255,255,255,0.1)", "#FFFFFF"
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        if rate > 0.5:
            return "🟢 MARKET BULL", f"지수 {rate:.2f}% 급등. 적극적인 매수 전략이 유효합니다.", "rgba(46, 125, 50, 0.1)", "#4CAF50"
        elif rate > -0.5:
            return "🟡 MARKET NEUTRAL", f"지수 {rate:.2f}% 보합. 철저히 대장주 위주로 대응하세요.", "rgba(255, 160, 0, 0.1)", "#FFB300"
        else:
            return "🔴 MARKET BEAR", f"지수 {rate:.2f}% 하락. 현금 비중을 확보하고 관망하세요.", "rgba(198, 40, 40, 0.1)", "#FF5252"
    except:
        return "⚪ ERROR", "연결 실패", "rgba(255,255,255,0.1)", "#FFFFFF"

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
        # 볼린저 밴드 하단 반등 로직 (원본 가점 4점 동일)
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

# 헤더
st.markdown("""
    <div class="header-box">
        <div class="main-title">MAGIC STOCK</div>
        <div class="sub-title">Premium AI Analysis System</div>
    </div>
    """, unsafe_allow_html=True)

# 시장 선택 (사이드바 대신 상단에 배치하여 모바일 접근성 향상)
col1, col2 = st.columns([1, 1])
with col1:
    market_type = st.selectbox("Market Select", ["KOSPI", "KOSDAQ"], label_visibility="collapsed")
with col2:
    st.markdown(f"<div style='text-align:right; color:#8E8E93; padding-top:10px;'>{datetime.datetime.now().strftime('%Y.%m.%d')}</div>", unsafe_allow_html=True)

today_str = datetime.datetime.now().strftime("%Y%m%d")

# 메인 실행 버튼
if st.button('🔍 ANALYSIS START'):
    # A. 시장 신호등
    title, desc, bg_color, text_color = get_market_status(market_type)
    st.markdown(f"""
        <div class="signal-container" style="background: {bg_color}; border: 1px solid {text_color}33;">
            <div style="font-size: 20px; font-weight: 800; color: {text_color}; margin-bottom: 5px;">{title}</div>
            <div style="font-size: 13px; color: #FFFFFF; opacity: 0.8;">{desc}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('AI가 골든 타이밍 종목을 추출하고 있습니다...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        filtered = df_base[
            (df_base['등락률'] >= 0.5) & 
            (df_base['등락률'] <= 2.5) & 
            (df_base['거래량'] > 100000)
        ].sort_values('거래량', ascending=False).head(15)

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

    # B. AI 추천 종목 리스트 (카드형)
    st.markdown("<div style='margin: 30px 0 15px 5px; font-weight:700; font-size:18px;'>🎯 ROYAL RECOMMEND</div>", unsafe_allow_html=True)
    
    if picks:
        # 점수 순으로 정렬
        picks_sorted = sorted(picks, key=lambda x: x['score'], reverse=True)[:5]
        for p in picks_sorted:
            st.markdown(f"""
                <div class="stock-item">
                    <div style="flex: 1;">
                        <div style="font-size: 11px; color: #8E8E93; margin-bottom: 2px;">{p['ticker']}</div>
                        <div style="font-size: 18px; font-weight: 700; color: #FFFFFF;">{p['name']}</div>
                        <div style="display: flex; gap: 10px; margin-top: 8px;">
                            <span style="background: #D4AF37; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800;">POINT {p['score']}</span>
                            <span style="color: {'#FF5252' if p['rate'] > 0 else '#5271FF'}; font-size: 12px; font-weight: 600;">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</span>
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="metric-label">현재가</div>
                        <div class="metric-value">₩{p['price']:,}</div>
                        <div class="metric-label" style="margin-top: 5px;">목표가</div>
                        <div style="font-size: 14px; font-weight: 600; color: #00FFAB;">₩{p['target']:,}</div>
                    </div>
                    <div style="margin-left: 15px;">
                        <a href="https://finance.naver.com/item/main.naver?code={p['ticker']}" target="_blank" style="text-decoration: none;">
                            <div style="background: rgba(255,255,255,0.1); width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #D4AF37;">▶</div>
                        </a>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("현재 시장 조건에 부합하는 종목이 없습니다.")

    # C. 실시간 거래량 TOP 10 (심플 테이블 스타일)
    st.markdown("<div style='margin: 40px 0 15px 5px; font-weight:700; font-size:18px;'>🔥 VOLUME HOT 10</div>", unsafe_allow_html=True)
    top_10 = filtered.head(10).copy()
    top_10['Name'] = [stock.get_market_ticker_name(t) for t in top_10.index]
    
    # 데이터 에디터 스타일링
    st.data_editor(
        top_10[['Name', '종가', '등락률']],
        column_config={
            "Name": "종목명",
            "종가": st.column_config.NumberColumn("현재가", format="₩%d"),
            "등락률": st.column_config.NumberColumn("등락", format="%.2f%%"),
        },
        hide_index=True,
        use_container_width=True,
        disabled=True
    )

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        <b>[투자 유의사항]</b><br>
        본 서비스의 분석 결과는 AI 알고리즘에 기초한 참고 자료이며,<br>
        수익을 보장하지 않습니다. 모든 투자의 책임은 본인에게 있습니다.<br><br>
        Premium Stock Curation by <b>BOHEMIAN</b><br>
        Copyright © 2026. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
