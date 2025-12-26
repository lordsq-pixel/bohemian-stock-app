import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="BOHEMIAN BLACK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 하이엔드 럭셔리 CSS (블랙 & 골드 모바일 최적화) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;600;700&family=Noto+Sans+KR:wght@300;500;700&display=swap');

    /* 메인 앱 배경 및 폰트 */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1c1c1e 0%, #0a0a0b 100%);
        color: #FFFFFF;
    }
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans KR', sans-serif; 
    }

    /* 제목 영역 */
    .header-box { text-align: center; padding: 60px 10px 40px 10px; }
    .main-title { 
        font-family: 'Playfair Display', serif;
        font-size: 42px; font-weight: 700; 
        background: linear-gradient(135deg, #D4AF37 0%, #F9E29C 50%, #B88A44 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 5px; letter-spacing: -1.5px;
    }
    .sub-title { font-size: 13px; color: #8E8E93; font-weight: 300; letter-spacing: 3px; text-transform: uppercase; }

    /* 프리미엄 버튼 */
    .stButton>button {
        width: 100% !important; height: 65px; 
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
        color: #000000 !important; border: none !important;
        border-radius: 14px !important; font-size: 18px !important; 
        font-weight: 700 !important; letter-spacing: 0.5px !important;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.2) !important;
        transition: all 0.3s ease !important;
        margin-top: 15px;
    }
    .stButton>button:active { transform: scale(0.97); }

    /* 지수 신호등 디자인 */
    .signal-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px; text-align: center; margin-bottom: 35px;
    }

    /* 종목 결과 카드 디자인 */
    .stock-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px; padding: 22px; margin-bottom: 15px;
        display: flex; justify-content: space-between; align-items: center;
        transition: background 0.3s;
    }
    .stock-card:active { background: rgba(255, 255, 255, 0.08); }
    
    .card-left { display: flex; flex-direction: column; }
    .card-name { font-size: 19px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; }
    .card-score { 
        display: inline-block; background: #D4AF37; color: #000; 
        padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; 
        margin-bottom: 8px; width: fit-content;
    }
    
    .card-right { text-align: right; }
    .card-price { font-size: 20px; font-weight: 700; color: #D4AF37; }
    .card-change { font-size: 14px; font-weight: 600; }
    .card-target { font-size: 13px; color: #00FFAB; font-weight: 500; margin-top: 5px; }

    /* 섹션 헤더 */
    .section-header { font-size: 18px; font-weight: 700; margin: 30px 0 15px 5px; color: #F9E29C; }

    /* 푸터 */
    .footer { text-align: center; padding: 50px 20px; font-size: 11px; color: #555; border-top: 1px solid #222; margin-top: 40px; }

    /* 기본 요소 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 (원본 기능 100% 보존) ---

def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2: return "⚪ 준비중", "데이터 로딩중", "#9E9E9E"
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        if rate > 0.5:
            return "🟢 MARKET STRONG", f"지수 {rate:.2f}% 급등 중. 적극 매수 시점입니다.", "#4CAF50"
        elif rate > -0.5:
            return "🟡 MARKET SIDEWAYS", f"지수 {rate:.2f}% 보합. 확실한 대장주 위주로 대응.", "#FFB300"
        else:
            return "🔴 MARKET WEAK", f"지수 {rate:.2f}% 하락 중. 현금 비중을 늘리세요.", "#FF5252"
    except: return "⚪ 확인 불가", "연결 오류", "#9E9E9E"

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
        # 원본 분석 로직 (볼린저 밴드 하단 반등 4점 가점 등)
        touched_bottom = (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1])
        if touched_bottom and curr_close > df['bb_low'].iloc[-1]: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 50: score += 2
        
        volume_curr = df['거래량'].iloc[-1]
        volume_avg = df['거래량'].iloc[-20:-1].mean()
        if volume_curr > volume_avg * 1.1: score += 1
        return score
    except: return -1

# --- 4. 메인 UI 구성 ---

st.markdown("""
    <div class="header-box">
        <div class="main-title">MAGIC STOCK</div>
        <div class="sub-title">Premium Algorithm Analysis</div>
    </div>
    """, unsafe_allow_html=True)

# 레이아웃 정렬
col_sel, col_empty = st.columns([1, 1])
with col_sel:
    market_type = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"], label_visibility="collapsed")
today_str = datetime.datetime.now().strftime("%Y%m%d")

if st.button('🔍 분석 엔진 가동'):
    # A. 시장 신호등 카드
    title, desc, color = get_market_status(market_type)
    st.markdown(f"""
        <div class="signal-card" style="border-top: 4px solid {color};">
            <div style="font-size: 20px; font-weight: 800; color: {color}; margin-bottom: 6px;">{title}</div>
            <div style="font-size: 13px; color: #AAA;">{desc}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('실시간 빅데이터 분석 중...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        # 원본 필터링 조건
        filtered = df_base[
            (df_base['등락률'] >= 0.5) & 
            (df_base['등락률'] <= 2.5) & 
            (df_base['거래량'] > 100000)
        ].sort_values('거래량', ascending=False).head(15)

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

    # B. AI 추천 종목 카드 리스트
    st.markdown('<div class="section-header">🎯 AI GOLDEN PICK</div>', unsafe_allow_html=True)
    
    if picks:
        picks_sorted = sorted(picks, key=lambda x: x['score'], reverse=True)
        for p in picks_sorted:
            st.markdown(f"""
                <a href="{p['url']}" target="_blank" style="text-decoration: none;">
                    <div class="stock-card">
                        <div class="card-left">
                            <span class="card-score">MATCH {p['score']}0%</span>
                            <span class="card-name">{p['name']}</span>
                            <span class="card-change" style="color: {'#FF5252' if p['rate'] > 0 else '#5271FF'}">
                                {'+' if p['rate'] > 0 else ''}{p['rate']:.2f}% Trending
                            </span>
                        </div>
                        <div class="card-right">
                            <div class="card-price">₩{p['price']:,}</div>
                            <div class="card-target">Target ₩{p['target']:,}</div>
                        </div>
                    </div>
                </a>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="padding: 40px; text-align: center; color: #555; background: rgba(255,255,255,0.02); border-radius: 20px;">
                현재 분석 기준을 통과한 강력 추천 종목이 없습니다.
            </div>
        """, unsafe_allow_html=True)

    # C. 실시간 거래량 TOP 5 (심플 리스트)
    st.markdown('<div class="section-header">🔥 HOT VOLUME</div>', unsafe_allow_html=True)
    for ticker in filtered.head(5).index:
        name = stock.get_market_ticker_name(ticker)
        price = filtered.loc[ticker, '종가']
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; padding: 15px 10px; border-bottom: 1px solid #1c1c1e;">
                <span style="color: #EEE;">{name}</span>
                <span style="color: #D4AF37; font-weight: 700;">₩{price:,}</span>
            </div>
        """, unsafe_allow_html=True)

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        <b>HIGH-END STOCK CURATION</b><br>
        모든 투자의 책임은 본인에게 있으며, 원금 손실이 발생할 수 있습니다.<br><br>
        Copyright © 2026 BOHEMIAN BLACK. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
