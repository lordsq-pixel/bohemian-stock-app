import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="BOHEMIAN THEME STOCK", layout="wide")

# --- 2. CSS 스타일 (생략/유지) ---
st.markdown("""
    <style>
    .main-title { font-size: 26px; font-weight: 700; text-align: center; }
    .stButton>button { width: 100%; background-color: #007BFF; color: white; border-radius: 8px; }
    .signal-box { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 20px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 핵심 분석 로직 ---

@st.cache_data(ttl=3600) # 업종 리스트는 1시간에 한 번만 갱신
def get_sectors(market):
    # KRX 업종별 리스트 가져오기
    return stock.get_market_ticker_list(market=market)

def get_market_status(market_name):
    today = datetime.datetime.now().strftime("%Y%m%d")
    try:
        df = stock.get_market_index_change_by_ticker(today, today, market_name)
        rate = df['등락률'].iloc[0]
        if rate > 0.5: return "🟢 강세", f"지수 {rate:.2f}% 상승", "#E8F5E9", "#2E7D32"
        elif rate > -0.5: return "🟡 보합", f"지수 {rate:.2f}% 보합", "#FFFDE7", "#F57F17"
        else: return "🔴 약세", f"지수 {rate:.2f}% 하락", "#FFEBEE", "#C62828"
    except: return "⚪ 대기", "데이터 준비중", "#F9F9F9", "#9E9E9E"

def analyze_stock_pro(ticker, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 20: return None
        
        curr = df['종가'].iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5).sma_indicator().iloc[-1]
        rsi = RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1]
        
        # 재무(PBR)
        fund = stock.get_market_fundamental(today, today, ticker)
        pbr = fund['PBR'].iloc[0] if not fund.empty else 0
        
        score = 0
        if curr > sma5: score += 2
        if 45 <= rsi <= 65: score += 3
        if 0 < pbr < 1.8: score += 2 # 재무 가점 기준 완화
        
        return {"score": score, "pbr": pbr, "history": df['종가']}
    except: return None

# --- 4. 메인 UI ---

st.markdown('<H1 class="main-title">🚀 MAGIC STOCK : THEME ANALYSIS</H1>', unsafe_allow_html=True)

# 사이드바: 테마 설정
with st.sidebar:
    st.header("🔍 필터 설정")
    market_type = st.selectbox("시장 선택", ["KOSPI", "KOSDAQ"])
    
    # 테마(업종) 선택 기능 추가
    # KRX 전종목 기본 정보를 가져와 업종 리스트 추출
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    df_listing = stock.get_market_listing(today_str, market=market_type)
    all_sectors = sorted(df_listing['업종'].unique().tolist())
    
    selected_sectors = st.multiselect("관심 테마/업종 선택", all_sectors, placeholder="전체 업종 분석")
    
    min_trade_value = st.slider("최소 거래대금 (억)", 10, 1000, 50) * 100_000_000
    st.info("💡 팁: 거래대금이 높은 업종이 주도 테마일 확률이 높습니다.")

if st.button('🎯 테마 종목 정밀 분석 시작'):
    title, desc, bg, txt = get_market_status(market_type)
    st.markdown(f'<div class="signal-box" style="background-color:{bg}; color:{txt};">'
                f'<b>{title}</b> | {desc}</div>', unsafe_allow_html=True)

    with st.spinner('테마별 수급과 기술적 지표를 분석 중입니다...'):
        # 1. 시세 데이터 가져오기
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        
        # 2. 업종 정보 결합
        df_total = pd.merge(df_base, df_listing[['업종']], left_index=True, right_index=True)
        
        # 3. 테마 필터링
        if selected_sectors:
            df_total = df_total[df_total['업종'].isin(selected_sectors)]

        # 4. 기본 필터 (등락률 2% 이상 & 거래대금)
        filtered = df_total[
            (df_total['등락률'] >= 2.0) & 
            (df_total['거래대금'] >= min_trade_value)
        ].sort_values('거래대금', ascending=False).head(30)

        picks = []
        for ticker in filtered.index:
            name = stock.get_market_ticker_name(ticker)
            res = analyze_stock_pro(ticker, today_str)
            
            if res and res['score'] >= 4:
                price = int(filtered.loc[ticker, '종가'])
                picks.append({
                    '테마': filtered.loc[ticker, '업종'],
                    '종목명': name,
                    '현재가': price,
                    '등락률': f"{filtered.loc[ticker, '등락률']:.2f}%",
                    '거래대금(억)': int(filtered.loc[ticker, '거래대금'] / 100_000_000),
                    '점수': res['score'],
                    '손절가(-3%)': int(price * 0.97),
                    '목표가(+5%)': int(price * 1.05),
                    'history': res['history']
                })

    # D. 결과 출력
    if picks:
        df_picks = pd.DataFrame(picks).sort_values(['점수', '거래대금(억)'], ascending=False)
        
        st.subheader(f"🎯 {market_type} 추천 포트폴리오")
        st.dataframe(df_picks.drop(columns=['history']), use_container_width=True, hide_index=True)

        # 차트 시각화
        st.markdown("---")
        st.subheader("📈 테마별 주도주 흐름")
        cols = st.columns(2)
        for idx, pick in enumerate(picks[:6]): # 상위 6개
            with cols[idx % 2]:
                st.write(f"**[{pick['테마']}] {pick['종목명']}**")
                st.line_chart(pick['history'])
    else:
        st.warning("선택하신 테마 내에 조건(거래대금, 상승률)을 만족하는 종목이 없습니다. 필터를 조정해 보세요.")

st.markdown('<div style="text-align:center; color:#aaa; font-size:12px; margin-top:50px;">© 2026 BOHEMIAN AI STOCK SYSTEM</div>', unsafe_allow_html=True)
