import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="BOHEMIAN STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CSS ---
st.markdown("""
<style>
.stApp { background-color: #FFFFFF; }
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1E1E1E; }

.main-title { font-size: 24px; font-weight: 700; text-align: center; }
.sub-title { font-size: 13px; color: #888; text-align: center; margin-bottom: 20px; }

.stButton>button {
    height: 55px; border-radius: 12px; font-size: 16px; font-weight: 600;
    background-color: #fff; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.signal-box {
    padding: 18px; border-radius: 15px; text-align: center;
    font-weight: 700; margin-bottom: 25px;
}

.footer {
    text-align: center; padding: 30px; font-size: 11px; color: #AAA;
    border-top: 1px solid #F0F0F0; margin-top: 50px;
}
</style>
""", unsafe_allow_html=True)

# --- 3. 로직 함수 정의 ---

def get_latest_trading_day(market_code: str) -> str | None:
    """
    오늘 기준으로 가장 최근의 거래일을 YYYYMMDD 문자열로 반환
    """
    today = datetime.datetime.today()

    for i in range(10):  # 최대 10일 전까지 탐색
        day = (today - datetime.timedelta(days=i)).strftime("%Y%m%d")
        try:
            df = stock.get_market_index_change_by_ticker(day, day, market_code)
            if not df.empty:
                return day
        except:
            continue

    return None


def get_market_status(market_code, today):
    df = stock.get_market_index_change_by_ticker(today, today, market_code)

    if df.empty:
        return "⚪ 관망 구간", "지수 데이터 미확정", "#F5F5F5", "#9E9E9E"

    rate = df['등락률'].iloc[0]

    if rate > 0.5:
        return "🟢 시장 강세", f"지수 {rate:.2f}% 상승", "#E8F5E9", "#2E7D32"
    elif rate > -0.5:
        return "🟡 시장 보합", f"지수 {rate:.2f}% 보합", "#FFFDE7", "#F57F17"
    else:
        return "🔴 시장 약세", f"지수 {rate:.2f}% 하락", "#FFEBEE", "#C62828"


def analyze_stock(ticker, today):
    start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=90)).strftime("%Y%m%d")
    df = stock.get_market_ohlcv_by_date(start, today, ticker)

    if df.empty or len(df) < 30:
        return 0

    sma5 = SMAIndicator(df["종가"], window=5).sma_indicator()
    rsi = RSIIndicator(df["종가"], window=14).rsi()

    if sma5.isna().iloc[-1] or rsi.isna().iloc[-1]:
        return 0

    score = 0
    if df['종가'].iloc[-1] > sma5.iloc[-1]: score += 2
    if 50 <= rsi.iloc[-1] <= 70: score += 3
    if df['종가'].iloc[-1] >= df['고가'].iloc[-1] * 0.99: score += 2

    return score


# --- 4. UI ---

st.markdown('<h2 class="main-title">📊 MAGIC STOCK.</h2>', unsafe_allow_html=True)
st.markdown('<p class="sub-title"># AI 실시간 빅데이터 분석 기반 #</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">[ 09:00 - 15:30 ]</p>', unsafe_allow_html=True)

market_type = st.sidebar.selectbox("📊 시장선택", ["KOSPI", "KOSDAQ"])
market_code = market_type

today_str = get_latest_trading_day(market_code)
if not today_str:
    st.error("최근 거래일을 찾을 수 없습니다.")
    st.stop()

if st.button("🔍 매수종목찾기"):
    title, desc, bg, txt = get_market_status(market_code, today_str)
    st.markdown(
        f'<div class="signal-box" style="background:{bg};color:{txt};border:1px solid {txt}22;">'
        f'{title}<br><span style="font-size:13px;font-weight:400">{desc}</span></div>',
        unsafe_allow_html=True
    )

    with st.spinner("종목 분석 중..."):
        df = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        df = df[(df['등락률'] >= 3) & (df['거래량'] > 100000)].sort_values('거래량', ascending=False).head(15)

    picks = []
    for ticker in df.index:
        score = analyze_stock(ticker, today_str)
        if score >= 4:
            price = df.loc[ticker, '종가']
            picks.append({
                "종목명": stock.get_market_ticker_name(ticker),
                "현재가": price,
                "등락률": df.loc[ticker, '등락률'],
                "점수": score,
                "목표가(+3%)": int(price * 1.03),
                "상세정보": f"https://finance.naver.com/item/main.naver?code={ticker}"
            })

    if picks:
        st.data_editor(pd.DataFrame(picks).sort_values("점수", ascending=False),
                       hide_index=True, use_container_width=True)
    else:
        st.info("조건을 만족하는 종목이 없습니다.")

# --- 5. 푸터 ---
st.markdown("""
<div class="footer">
투자결과에 따라 원금 손실이 발생할 수 있습니다.<br>
Copyright © 2026 보헤미안
</div>
""", unsafe_allow_html=True)
