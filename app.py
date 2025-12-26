import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="BOHEMIAN STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 럭셔리 화이트 CSS (모바일/테이블 최적화) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; color: #1E1E1E; }
    
    .main-title { font-size: 24px; font-weight: 700; color: #000; text-align: center; margin-bottom: 5px; }
    .sub-title { font-size: 13px; color: #888; text-align: center; margin-bottom: 25px; }
    
    /* 분석 버튼 스타일 */
    .stButton>button {
        width: auto; height: 55px; background-color: #FFF; color: #000;
        border-radius: 12px; font-size: 16px; font-weight: 600; border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px auto; display: block;
    }
   
    /* 지수 신호등 디자인 */
    .signal-box {
        padding: 18px; border-radius: 15px; text-align: center; font-weight: 700;
        margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    /* 표 중앙 정렬 */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        display: flex; justify-content: center; margin: 0 auto; width: 100%;
    }

    .footer { text-align: center; padding: 30px; font-size: 11px; color: #AAA; border-top: 1px solid #F0F0F0; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 정의 ---

# --- 3. 로직 함수 정의 (신호등 & 수급분석 합본) ---

# [1] 시장 지수 신호등 (정상 작동 버전)
def get_market_status(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2:
            return "⚪ 데이터 준비중", "거래소 데이터를 불러오는 중입니다.", "#F9F9F9", "#9E9E9E"
        
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        if rate > 0.5:
            return "🟢 시장 강세", f"지수 {rate:.2f}% 상승 중. 적극 매수 시점입니다.", "#E8F5E9", "#2E7D32"
        elif rate > -0.5:
            return "🟡 시장 보합", f"지수 {rate:.2f}% 보합. 확실한 대장주만 공략하세요.", "#FFFDE7", "#F57F17"
        else:
            return "🔴 시장 약세", f"지수 {rate:.2f}% 하락 중. 현금 비중을 늘리세요.", "#FFEBEE", "#C62828"
    except:
        return "⚪ 확인 불가", "데이터 연결 오류", "#F9F9F9", "#9E9E9E"

# [2] 종목 상세 분석 (기술적 지표 + 수급 점수 포함)
def analyze_stock(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=100)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        
        if len(df) < 30: return 0
        
        curr = df['종가'].iloc[-1]
        high = df['고가'].iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5, fillna=True).sma_indicator().iloc[-1]
        rsi = RSIIndicator(close=df["종가"], window=14, fillna=True).rsi().iloc[-1]
        
        score = 0
        # 차트 지표 점수 (최대 7점)
        if curr > sma5: score += 2
        if 50 <= rsi <= 70: score += 3
        if curr >= high * 0.99: score += 2
        
        # 수급 데이터 점수 (최대 4점 추가)
        df_investor = stock.get_market_net_purchases_of_equities_by_ticker(today, today, ticker)
        if not df_investor.empty:
            foreigner = df_investor.loc[ticker, '외국인']
            institution = df_investor.loc[ticker, '기관합계']
            if foreigner > 0: score += 2
            if institution > 0: score += 2
            
        return score
    except: return -1
        
# --- 4. 메인 UI ---

st.markdown('<H2 class="main-title">📊 MAGIC STOCK. </H2>', unsafe_allow_html=True)
st.markdown('<p class="sub-title"># AI 실시간 빅데이터 분석 기반 #</p>', unsafe_allow_html=True)
st.markdown('<H4 class="sub-title">[ 09:00 - 15:30 ]</H4>', unsafe_allow_html=True)

market_type = st.sidebar.selectbox("📊 시장선택", ["KOSPI", "KOSDAQ"])
today_str = datetime.datetime.now().strftime("%Y%m%d")

if st.button('🔍 매수종목찾기'):
    # A. 시장 신호등
    title, desc, bg, txt = get_market_status(market_type)
    st.markdown(f'<div class="signal-box" style="background-color:{bg}; color:{txt}; border:1px solid {txt}22;">'
                f'<span style="font-size:19px;">{title}</span><br>'
                f'<span style="font-size:13px; font-weight:400;">{desc}</span></div>', unsafe_allow_html=True)

    with st.spinner('최적의 매수 종목을 선별하고 있습니다...'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        # 필터: 상승률 3%~25%, 거래량 상위
        filtered = df_base[(df_base['등락률'] >= 3.0) & (df_base['거래량'] > 100000)].sort_values('거래량', ascending=False).head(15)

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
                '목표가(+3%)': int(price * 1.03),
                '상세정보': f"https://finance.naver.com/item/main.naver?code={ticker}"
            })

    # C. 추천 종목 출력
    st.subheader("🎯 AI 추천종목")
    
    if picks:
        df_picks = pd.DataFrame(picks).sort_values('점수', ascending=False).head(5)
        st.data_editor(
            df_picks,
            column_config={
                "점수": st.column_config.ProgressColumn("상승잠재력", min_value=0, max_value=11, format="%d"),
                "현재가": st.column_config.NumberColumn(format="₩%d"),
                "등락률": st.column_config.NumberColumn(format="%.2f%%"),
                "목표가(+3%)": st.column_config.NumberColumn(format="₩%d"),
                "상세정보": st.column_config.LinkColumn("네이버증권", display_text="열기")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("현재 분석 기준을 통과한 강력한 추천 종목이 없습니다.")

    st.markdown("---")
    st.subheader("📊 실시간 거래량 TOP 10")
    top_10 = filtered.head(10)[['종가', '등락률']].copy()
    top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10.index]
    st.dataframe(top_10[['종목명', '종가', '등락률']], use_container_width=True)

# --- 5. 푸터 ---
st.markdown(f"""
    <div class="footer">
        투자결과에 따라 투자원금의 손실이 발생할 수 있습니다<BR>
        Copyright © 2026 보헤미안. All rights reserved.
    </div>
    """, unsafe_allow_html=True)




