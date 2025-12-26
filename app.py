import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC STOCK | PREMIUM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 프리미엄 금융 UI CSS (증권사 스타일) ---
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 전체 배경 및 폰트 */
    .stApp { background-color: #F4F7FA; font-family: 'Pretendard', sans-serif; }
    
    /* 타이틀 섹션 */
    .header-container { text-align: center; padding: 40px 0 20px 0; background: #fff; border-bottom: 1px solid #E0E4E8; margin-bottom: 30px; }
    .main-title { font-size: 32px; font-weight: 800; color: #1A1E27; letter-spacing: -1px; margin-bottom: 10px; }
    .sub-title { font-size: 14px; color: #6B7684; font-weight: 400; }
    
    /* 카드 스타일 */
    .css-1r6slb0, .stVerticalBlock { gap: 1.5rem; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 700 !important; }
    
    /* 섹션 카드 디자인 */
    .reportview-container .main .block-container { max-width: 1200px; }
    .st-emotion-cache-12w0qpk { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }

    /* 분석 실행 버튼 커스텀 */
    .stButton>button {
        width: 100%;
        max-width: 400px;
        height: 60px;
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 16px;
        font-size: 18px;
        font-weight: 700;
        margin: 20px auto;
        display: block;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(37, 99, 235, 0.3);
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
    }

    /* 지수 신호등 프리미엄 디자인 */
    .signal-card {
        padding: 24px;
        border-radius: 20px;
        text-align: left;
        border-left: 8px solid;
        background: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    /* 푸터 */
    .footer { text-align: center; padding: 60px 0 40px 0; font-size: 12px; color: #9BA5B1; line-height: 1.6; }
    
    /* 테이블 스타일 조정 */
    .stDataFrame { border-radius: 15px; overflow: hidden; background: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 (기존 로직 유지) ---
def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2: return "⚪ 데이터 준비중", "거래소 데이터를 불러오는 중입니다.", "#F9F9F9", "#9E9E9E"
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        if rate > 0.5:
            return "🟢 시장 강세", f"지수 {rate:.2f}% 상승 중. 적극 매수 시점입니다.", "#EBF7ED", "#1B5E20"
        elif rate > -0.5:
            return "🟡 시장 보합", f"지수 {rate:.2f}% 보합. 확실한 대장주만 공략하세요.", "#FFF9E6", "#7A5600"
        else:
            return "🔴 시장 약세", f"지수 {rate:.2f}% 하락 중. 현금 비중을 늘리세요.", "#FEEBED", "#B91C1C"
    except Exception as e:
        return "⚪ 확인 불가", f"연결 오류: {str(e)}", "#F9F9F9", "#9E9E9E"

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
    except: return -1

# --- 4. 메인 UI (디자인 강화) ---
st.markdown("""
    <div class="header-container">
        <div class="main-title">MAGIC STOCK AI</div>
        <div class="sub-title">실시간 시장 데이터 기반 최적의 매수 타점 분석 시스템</div>
    </div>
    """, unsafe_allow_html=True)

# 사이드바 설정 (깔끔하게)
with st.sidebar:
    st.markdown("### ⚙️ 분석 설정")
    market_type = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"])
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    st.info(f"분석 기준일: {today_str}")

# 중앙 버튼
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    search_clicked = st.button('🔍 실시간 종목 분석 시작')

if search_clicked:
    # A. 시장 신호등 카드
    title, desc, bg, txt = get_market_status(market_type)
    st.markdown(f"""
        <div class="signal-card" style="border-color: {txt}; background-color: {bg};">
            <div style="font-size: 14px; color: {txt}; font-weight: 600; margin-bottom: 4px;">MARKET STATUS</div>
            <div style="font-size: 24px; font-weight: 800; color: {txt}; margin-bottom: 8px;">{title}</div>
            <div style="font-size: 15px; color: {txt}; opacity: 0.8;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    with st.spinner('🚀 AI가 시장의 바닥권 반등 종목을 추출하고 있습니다...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        filtered = df_base[
            (df_base['등락률'] >= 0.5) & 
            (df_base['등락률'] <= 2.5) & 
            (df_base['거래량'] > 100000)
        ].sort_values('거래량', ascending=False).head(15)

    # B. 결과 리스트업
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
                '점수': score,
                '목표가': int(price * 1.03),
                '상세정보': f"https://finance.naver.com/item/main.naver?code={ticker}"
            })

    # C. 추천 종목 출력 (카드 형태의 데이터 에디터)
    st.markdown("---")
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.subheader("🎯 AI 추천 바닥 반등 종목")
        if picks:
            df_picks = pd.DataFrame(picks).sort_values('점수', ascending=False).head(5)
            st.data_editor(
                df_picks,
                column_config={
                    "점수": st.column_config.ProgressColumn("상승 에너지", min_value=0, max_value=8, format="%d"),
                    "현재가": st.column_config.NumberColumn("현재가", format="₩%d"),
                    "등락률": st.column_config.NumberColumn("등락률", format="%.2f%%"),
                    "목표가": st.column_config.NumberColumn("익절가(+3%)", format="₩%d"),
                    "상세정보": st.column_config.LinkColumn("분석차트", display_text="보기 🔗")
                },
                hide_index=True, use_container_width=True
            )
        else:
            st.info("현재 분석 기준을 통과한 강력한 추천 종목이 없습니다.")

    with col_side:
        st.subheader("🔥 실시간 거래량 TOP")
        top_10 = filtered.head(10)[['종가', '등락률']].copy()
        top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10.index]
        st.dataframe(
            top_10[['종목명', '종가', '등락률']], 
            column_config={
                "등락률": st.column_config.NumberColumn(format="%.2f%%"),
                "종가": st.column_config.NumberColumn(format="%d")
            },
            hide_index=True, use_container_width=True
        )

# --- 5. 푸터 ---
st.markdown(f"""
    <div class="footer">
        본 서비스는 투자 판단을 돕기 위한 보조 도구이며, 모든 투자의 책임은 본인에게 있습니다.<br>
        데이터 제공: KRX(한국거래소) | 시스템: MAGIC STOCK AI PREMIUM v2.0<br>
        Copyright © 2026 보헤미안. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
