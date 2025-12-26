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

# --- 2. 럭셔리 다크 UI 디자인 (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+KR:wght@300;500;700&display=swap');

    /* 메인 배경 */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* 전체 폰트 설정 */
    html, body, [class*="css"] { font-family: 'Inter', 'Noto Sans KR', sans-serif; }

    /* 헤더 디자인 */
    .header-container { text-align: center; padding: 40px 10px 20px 10px; }
    .main-title { 
        font-size: 32px; font-weight: 800; 
        background: linear-gradient(135deg, #D4AF37 0%, #F9E29C 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -1px; margin-bottom: 5px;
    }
    .sub-title { font-size: 14px; color: #888; font-weight: 400; letter-spacing: 1px; }

    /* 시장 신호등 카드 */
    .signal-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center; margin-bottom: 30px;
    }

    /* 종목 카드 디자인 */
    .stock-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 18px; padding: 20px;
        margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.08);
        transition: transform 0.2s ease;
    }
    .stock-card:active { transform: scale(0.98); background: rgba(255, 255, 255, 0.07); }
    
    .stock-name { font-size: 18px; font-weight: 700; color: #FFFFFF; }
    .stock-price { font-size: 20px; font-weight: 600; color: #D4AF37; }
    .stock-change { font-size: 14px; font-weight: 500; }
    .stock-score { 
        display: inline-block; padding: 4px 12px; border-radius: 50px; 
        background: #2E7D32; color: white; font-size: 12px; font-weight: 600;
    }

    /* 분석 버튼 */
    .stButton>button {
        width: 100%; border-radius: 15px; height: 60px;
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%);
        color: #000; font-weight: 700; font-size: 18px; border: none;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2);
    }

    /* 사이드바 테마 수정 */
    section[data-testid="stSidebar"] { background-color: #161B22; }

    /* 하단 푸터 */
    .footer { text-align: center; padding: 40px; font-size: 12px; color: #555; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 (기존 로직 유지) ---

def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2: return "⚪ 준비중", "데이터 대기", "gray"
        rate = ((df['종가'].iloc[-1] - df['종가'].iloc[-2]) / df['종가'].iloc[-2]) * 100
        if rate > 0.5: return "🟢 시장 강세", f"현재 지수 {rate:.2f}% 상승 중. 매수 적기입니다.", "#2E7D32"
        elif rate > -0.5: return "🟡 시장 보합", f"현재 지수 {rate:.2f}% 보합. 관망이 필요합니다.", "#F57F17"
        else: return "🔴 시장 약세", f"현재 지수 {rate:.2f}% 하락 중. 현금 비중 확대!", "#C62828"
    except: return "⚪ 확인 불가", "데이터 연결 오류", "gray"

def analyze_stock(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 30: return 0
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        curr_close, curr_low = df['종가'].iloc[-1], df['저가'].iloc[-1]
        prev_low = df['저가'].iloc[-2]
        rsi = RSIIndicator(close=df["종가"], window=14, fillna=True).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5, fillna=True).sma_indicator().iloc[-1]
        
        score = 0
        if (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1]):
            if curr_close > df['bb_low'].iloc[-1]: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 50: score += 2
        return score
    except: return -1

# --- 4. 메인 화면 구성 ---

st.markdown("""
    <div class="header-container">
        <div class="main-title">MAGIC STOCK</div>
        <div class="sub-title">PREMIUM AI ANALYSIS</div>
    </div>
    """, unsafe_allow_html=True)

# 사이드바 설정
market_type = st.sidebar.selectbox("📊 시장 선택", ["KOSPI", "KOSDAQ"])
today_str = datetime.datetime.now().strftime("%Y%m%d")

# 분석 시작 버튼
if st.button('SEARCH OPPORTUNITY'):
    # A. 시장 현황 카드
    title, desc, color = get_market_status(market_type)
    st.markdown(f"""
        <div class="signal-card">
            <div style="font-size: 20px; font-weight: 700; color: {color}; margin-bottom: 8px;">{title}</div>
            <div style="font-size: 14px; color: #AAA;">{desc}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('실시간 데이터를 분석하고 있습니다...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        filtered = df_base[(df_base['등락률'] >= 0.5) & (df_base['등락률'] <= 2.5) & (df_base['거래량'] > 100000)].sort_values('거래량', ascending=False).head(15)

        picks = []
        for ticker in filtered.index:
            score = analyze_stock(ticker, today_str)
            if score >= 4:
                picks.append({
                    'name': stock.get_market_ticker_name(ticker),
                    'price': filtered.loc[ticker, '종가'],
                    'rate': filtered.loc[ticker, '등락률'],
                    'score': score,
                    'target': int(filtered.loc[ticker, '종가'] * 1.03),
                    'url': f"https://finance.naver.com/item/main.naver?code={ticker}"
                })

    # B. AI 결과 출력 (카드형 UI)
    st.markdown("<h3 style='font-size:20px; margin-left:5px;'>🎯 AI PICK</h3>", unsafe_allow_html=True)
    
    if picks:
        for p in picks:
            st.markdown(f"""
                <a href="{p['url']}" style="text-decoration: none;">
                    <div class="stock-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <span class="stock-name">{p['name']}</span>
                            <span class="stock-score">강력매수 {p['score']}점</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                            <div>
                                <div class="stock-price">₩{p['price']:,}</div>
                                <div class="stock-change" style="color: {'#FF4B4B' if p['rate'] > 0 else '#4B9BFF'}">
                                    {'+' if p['rate'] > 0 else ''}{p['rate']:.2f}% 상승 중
                                </div>
                            </div>
                            <div style="text-align: right;">
                                <div style="font-size: 11px; color: #888;">목표가(+3%)</div>
                                <div style="font-size: 15px; font-weight: 600; color: #00FF41;">₩{p['target']:,}</div>
                            </div>
                        </div>
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.info("현재 기준에 부합하는 종목이 없습니다.")

    # C. 실시간 순위 (심플 리스트)
    st.markdown("<h3 style='font-size:20px; margin: 30px 0 15px 5px;'>🔥 REAL-TIME TOP</h3>", unsafe_allow_html=True)
    top_10 = filtered.head(5)
    for ticker in top_10.index:
        name = stock.get_market_ticker_name(ticker)
        price = top_10.loc[ticker, '종가']
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 15px; color: #EEE;">{name}</span>
                <span style="font-size: 15px; color: #D4AF37; font-weight: 600;">₩{price:,.0f}</span>
            </div>
        """, unsafe_allow_html=True)

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        보헤미안 프리미엄 알고리즘 v2.0<br>
        본 데이터는 투자 참고용이며 최종 책임은 본인에게 있습니다.<br><br>
        COPYRIGHT © 2026 BOHEMIAN ALL RIGHTS RESERVED.
    </div>
    """, unsafe_allow_html=True)
