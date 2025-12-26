import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="MAGIC STOCK | PREMIUM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 럭셔리 화이트 & 미니멀 블랙 CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@100;300;400;500;700&display=swap');

    /* 전체 배경 및 폰트 */
    .stApp { background-color: #FBFBFB; }
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #2C2C2C; }

    /* 메인 타이틀 섹션 */
    .header-container { text-align: center; padding: 40px 0 20px 0; }
    .main-title { 
        font-size: 38px; font-weight: 700; color: #1A1A1A; letter-spacing: -1.5px; 
        margin-bottom: 0px; text-transform: uppercase;
    }
    .sub-title { font-size: 14px; color: #999; font-weight: 300; letter-spacing: 2px; margin-top: -5px; }

    /* 럭셔리 버튼 스타일 */
    .stButton>button {
        width: 100%; max-width: 400px; height: 60px; 
        background: #1A1A1A; color: #FFFFFF;
        border-radius: 30px; font-size: 18px; font-weight: 500; border: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
        margin: 0 auto; display: block;
    }
    .stButton>button:hover {
        background: #333333; transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(0,0,0,0.2);
    }

    /* 지수 신호등 프리미엄 카드 */
    .signal-card {
        padding: 25px; border-radius: 20px; text-align: center;
        margin-bottom: 30px; border: 1px solid rgba(0,0,0,0.05);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        background-color: #FFFFFF;
    }
    .signal-title { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
    .signal-desc { font-size: 14px; opacity: 0.8; }

    /* 데이터 테이블/에디터 중앙 정렬 및 스타일 */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        background-color: #FFFFFF; padding: 20px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    /* 구분선 */
    hr { border: 0; height: 1px; background: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0)); margin: 40px 0; }

    /* 푸터 */
    .footer { text-align: center; padding: 50px; font-size: 12px; color: #BBB; font-weight: 300; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 정의 (기존 기능 유지) ---

def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2:
            return "⚪ DATA PREPARING", "시장 데이터를 분석 중입니다.", "#FFFFFF", "#9E9E9E"
        
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        if rate > 0.5:
            return "🟢 BULLISH MARKET", f"지수 {rate:.2f}% 상승 중. 공격적인 투자 전략이 유효합니다.", "#F6FFF8", "#2E7D32"
        elif rate > -0.5:
            return "🟡 NEUTRAL MARKET", f"지수 {rate:.2f}% 보합권. 선별적인 종목 접근이 필요합니다.", "#FFFEF2", "#F57F17"
        else:
            return "🔴 BEARISH MARKET", f"지수 {rate:.2f}% 하락 중. 리스크 관리와 현금 비중 확보가 우선입니다.", "#FFF5F5", "#C62828"
            
    except Exception as e:
        return "⚪ SYSTEM ERROR", f"데이터 연결에 일시적인 문제가 발생했습니다.", "#FFFFFF", "#9E9E9E"

def analyze_stock(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 30: return 0
        
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        
        curr_close = df['종가'].iloc[-1]
        curr_low = df['저가'].iloc[-1]
        prev_close = df['종가'].iloc[-2]
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
    except:
        return -1

# --- 4. 메인 UI ---
st.markdown("""
    <div class="header-container">
        <div class="main-title">Magic Stock</div>
        <div class="sub-title">PREMIUM ALGORITHMIC ANALYSIS</div>
    </div>
    """, unsafe_allow_html=True)

# 사이드바 디자인 (미니멀)
st.sidebar.markdown("### CONFIGURATION")
market_type = st.sidebar.selectbox("Market Select", ["KOSPI", "KOSDAQ"])
today_str = datetime.datetime.now().strftime("%Y%m%d")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    search_clicked = st.button('🔍 START AI ANALYSIS')

if search_clicked:
    # A. 시장 신호등 카드
    title, desc, bg, txt = get_market_status(market_type)
    st.markdown(f"""
        <div class="signal-card" style="background-color:{bg}; border-color:{txt}33;">
            <div class="signal-title" style="color:{txt};">{title}</div>
            <div class="signal-desc" style="color:{txt};">{desc}</div>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('빅데이터 및 지표 분석을 진행하고 있습니다...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        filtered = df_base[
            (df_base['등락률'] >= 0.5) & 
            (df_base['등락률'] <= 2.5) & 
            (df_base['거래량'] > 100000)
        ].sort_values('거래량', ascending=False).head(15)

    # B. 분석 결과
    picks = []
    for ticker in filtered.index:
        name = stock.get_market_ticker_name(ticker)
        score = analyze_stock(ticker, today_str)
        if score >= 4:
            price = filtered.loc[ticker, '종가']
            picks.append({
                '종목명': name,
                '현재가': price,
                '등락률': filtered.loc[ticker, '등락률'],
                '잠재력': score,
                '목표가': int(price * 1.03),
                '분석': f"https://finance.naver.com/item/main.naver?code={ticker}"
            })

    # C. 추천 종목 출력 섹션
    st.markdown("<h3 style='text-align:center; font-weight:500; margin-top:30px;'>🎯 Top Picks</h3>", unsafe_allow_html=True)
    
    if picks:
        df_picks = pd.DataFrame(picks).sort_values('잠재력', ascending=False).head(5)
        st.data_editor(
            df_picks,
            column_config={
                "잠재력": st.column_config.ProgressColumn("상승 에너지", min_value=0, max_value=8, format="%d"),
                "현재가": st.column_config.NumberColumn(format="₩%d"),
                "등락률": st.column_config.NumberColumn(format="%.2f%%"),
                "목표가": st.column_config.NumberColumn(format="₩%d"),
                "분석": st.column_config.LinkColumn("상세보기", display_text="Open")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("현재 프리미엄 알고리즘 기준을 통과한 종목이 없습니다.")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; font-weight:500;'>📊 Trading Volume Top 10</h3>", unsafe_allow_html=True)
    
    top_10 = filtered.head(10)[['종가', '등락률']].copy()
    top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10.index]
    st.dataframe(top_10[['종목명', '종가', '등락률']], use_container_width=True)

# --- 5. 푸터 ---
st.markdown(f"""
    <div class="footer">
        보헤미안 프리미엄 알고리즘 v1.2<br>
        본 서비스의 정보는 투자 참고 사항이며, 최종 책임은 투자자 본인에게 있습니다.<br><br>
        Copyright © {datetime.datetime.now().year} BOHEMIAN. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
