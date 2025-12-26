import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="BOHEMIAN STOCK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 럭셔리 화이트 CSS (전문 증권사 HTS 스타일 리뉴얼) ---
st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Roboto:wght@300;400;700&family=Noto+Sans+KR:wght@300;400;700&display=swap');

    /* Global Settings */
    .stApp { 
        background-color: #F4F6F9; /* 프리미엄 플래티넘 그레이 배경 */
    }
    html, body, [class*="css"] { 
        font-family: 'Roboto', 'Noto Sans KR', sans-serif; 
        color: #2C3E50; 
    }
    
    /* Header & Titles */
    .main-title { 
        font-family: 'Playfair Display', serif;
        font-size: 42px; 
        font-weight: 700; 
        color: #1A237E; /* Deep Navy */
        text-align: center; 
        margin-top: 20px;
        margin-bottom: 5px; 
        letter-spacing: 1px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .sub-title { 
        font-size: 14px; 
        color: #78909C; 
        text-align: center; 
        margin-bottom: 30px; 
        font-weight: 500;
        letter-spacing: 2px;
        text-transform: uppercase;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }

    /* Analyze Button Styling (Luxury Gold Gradient) */
    .stButton>button {
        width: 100%; 
        height: 60px; 
        background: linear-gradient(135deg, #1A237E 0%, #283593 100%);
        color: #FFFFFF;
        border-radius: 8px; 
        font-size: 18px; 
        font-weight: 700; 
        border: none;
        box-shadow: 0 10px 20px rgba(26, 35, 126, 0.2); 
        margin: 20px auto; 
        display: block;
        transition: all 0.3s ease;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #283593 0%, #3949AB 100%);
        transform: translateY(-2px);
        box-shadow: 0 15px 25px rgba(26, 35, 126, 0.3);
    }
   
    /* Signal Box Design (Card Style) */
    .signal-box {
        padding: 25px; 
        border-radius: 12px; 
        text-align: center; 
        font-weight: 700;
        margin-bottom: 30px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
        backdrop-filter: blur(10px);
    }

    /* Data Table Container */
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #F0F0F0;
        margin-bottom: 20px;
    }

    /* Subheaders */
    h3 {
        color: #1A237E !important;
        font-family: 'Playfair Display', serif;
        font-weight: 700 !important;
        border-left: 5px solid #D4AF37; /* Champagne Gold Accent */
        padding-left: 15px;
        margin-top: 40px !important;
        margin-bottom: 20px !important;
    }

    /* Footer */
    .footer { 
        text-align: center; 
        padding: 40px; 
        font-size: 12px; 
        color: #90A4AE; 
        border-top: 1px solid #E0E0E0; 
        margin-top: 60px; 
        font-weight: 400;
        letter-spacing: 0.5px;
    }
    
    /* Horizontal Rule */
    hr {
        border-color: #E0E0E0;
        margin: 40px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 정의 (수정 없음) ---

# 시장 지수 신호등
def get_market_status(market_name):
    # 코스피는 '1001', 코스닥은 '2001'이라는 고유 번호를 사용하면 더 정확합니다.
    ticker = "1001" if market_name == "KOSPI" else "2001"
    
    # 오늘부터 과거 10일치 데이터를 넉넉하게 가져옵니다 (주말/공휴일 대비)
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")
    
    try:
        # 지수의 OHLCV(시가/고가/저가/종가) 데이터를 가져옴
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        
        if len(df) < 2:
            return "⚪ 데이터 준비중", "거래소 데이터를 불러오는 중입니다.", "#F9F9F9", "#9E9E9E"
        
        # 최신 종가와 전일 종가를 비교하여 등락률 계산
        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100
        
        # 상태 판정 로직
        if rate > 0.5:
            return "🟢 시장 강세", f"지수 {rate:.2f}% 상승 중. 적극 매수 시점입니다.", "#E8F5E9", "#2E7D32"
        elif rate > -0.5:
            return "🟡 시장 보합", f"지수 {rate:.2f}% 보합. 확실한 대장주만 공략하세요.", "#FFFDE7", "#F57F17"
        else:
            return "🔴 시장 약세", f"지수 {rate:.2f}% 하락 중. 현금 비중을 늘리세요.", "#FFEBEE", "#C62828"
            
    except Exception as e:
        return "⚪ 확인 불가", f"연결 오류: {str(e)}", "#F9F9F9", "#9E9E9E"

# 종목 상세 분석
def analyze_stock(ticker, today):
    try:
        # 최근 60일치 데이터를 가져옵니다 (이평선 및 BB 계산용)
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        
        if len(df) < 30: return 0
        
        # --- [추가] 볼린저 밴드 계산 (20일, 2표준편차) ---
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()   # 하단밴드
        
        curr_close = df['종가'].iloc[-1]
        curr_low = df['저가'].iloc[-1]
        prev_close = df['종가'].iloc[-2]
        prev_low = df['저가'].iloc[-2]
        
        # 기타 지표들 (RSI, SMA)
        rsi = RSIIndicator(close=df["종가"], window=14, fillna=True).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5, fillna=True).sma_indicator().iloc[-1]
        
        score = 0

        # --- [핵심] 볼린저 밴드 하단 반등 로직 (가점 4점) ---
        # 어제나 오늘 '저가'가 하단 밴드 아래로 내려갔다가 (과매도), 
        # 현재 종가가 하단 밴드 위로 올라오는 중인지 확인
        touched_bottom = (prev_low <= df['bb_low'].iloc[-2]) or (curr_low <= df['bb_low'].iloc[-1])
        is_rebounding = curr_close > df['bb_low'].iloc[-1]
        
        if touched_bottom and is_rebounding:
            score += 4  # 바닥권 반등 시 강력한 점수 부여

        # --- 추가 점수 (추세 확인) ---
        if curr_close > sma5: score += 1      # 5일선 위 (단기 추세 회복)
        if 30 <= rsi <= 50: score += 2       # RSI가 너무 낮지 않으면서 상승 여력 있음
        
        # 거래량 확인
        volume_curr = df['거래량'].iloc[-1]
        volume_avg = df['거래량'].iloc[-20:-1].mean()
        if volume_curr > volume_avg * 1.1: score += 1 # 평소보다 거래량이 늘면 신뢰도 상승
        
        return score
    except:
        return -1

# --- 4. 메인 UI ---
# (Title Design Updated with CSS Classes)
st.markdown('<H2 class="main-title">BOHEMIAN STOCK.</H2>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PREMIUM AI INVESTMENT ANALYTICS</p>', unsafe_allow_html=True)
st.markdown('<H4 class="sub-title" style="margin-top:-10px; font-size:11px; color:#B0BEC5;">[ MARKET OPEN: 09:00 - 15:30 ]</H4>', unsafe_allow_html=True)

market_type = st.sidebar.selectbox("📊 MARKET SELECT", ["KOSPI", "KOSDAQ"])
today_str = datetime.datetime.now().strftime("%Y%m%d")

if st.button('🔍 MARKET SCAN & ANALYZE'):
    # A. 시장 신호등
    title, desc, bg, txt = get_market_status(market_type)
    # (Style Injection for the signal box logic)
    st.markdown(f'<div class="signal-box" style="background-color:{bg}; color:{txt}; border-left: 5px solid {txt};">'
                f'<span style="font-size:22px; letter-spacing:-0.5px;">{title}</span><br>'
                f'<span style="font-size:14px; font-weight:400; opacity:0.9;">{desc}</span></div>', unsafe_allow_html=True)

    with st.spinner('Analyzing market data... Please wait.'):
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market_type)
        # 필터 변경: 등락률 0.5% ~ 2.5% 사이의 '조용한' 종목들 중 거래량 있는 것
        filtered = df_base[
            (df_base['등락률'] >= 0.5) & 
            (df_base['등락률'] <= 2.5) & 
            (df_base['거래량'] > 100000)
        ].sort_values('거래량', ascending=False).head(15) # 후보군을 30개로 확대

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
    st.subheader("🎯 AI RECOMMENDED STOCKS")
    
    if picks:
        df_picks = pd.DataFrame(picks).sort_values('점수', ascending=False).head(5)
        st.data_editor(
            df_picks,
            column_config={
                "점수": st.column_config.ProgressColumn("상승잠재력", min_value=0, max_value=7, format="%d"),
                "현재가": st.column_config.NumberColumn(format="₩%d"),
                "등락률": st.column_config.NumberColumn(format="%.2f%%"),
                "목표가(+3%)": st.column_config.NumberColumn(format="₩%d"),
                "상세정보": st.column_config.LinkColumn("분석정보", display_text="View")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("현재 분석 기준을 통과한 강력한 추천 종목이 없습니다.")

    st.markdown("---")
    st.subheader("📊 VOLUME LEADERS (TOP 10)")
    top_10 = filtered.head(10)[['종가', '등락률']].copy()
    top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10.index]
    st.dataframe(top_10[['종목명', '종가', '등락률']], use_container_width=True)

# --- 5. 푸터 ---
st.markdown(f"""
    <div class="footer">
        <b>HIGH-FREQUENCY ALGORITHMIC TRADING SYSTEM</b><br>
        투자결과에 따라 투자원금의 손실이 발생할 수 있습니다.<br>
        COPYRIGHT © 2026 BOHEMIAN LABS. ALL RIGHTS RESERVED.
    </div>
    """, unsafe_allow_html=True)
