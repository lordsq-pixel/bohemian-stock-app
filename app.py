import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="MAGIC STOCK", layout="wide", initial_sidebar_state="expanded")

# --- 2. 모던 프로페셔널 CSS 적용 ---
st.markdown("""
    <style>
    /* 폰트 임포트 (Pretendard) */
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    /* 전체 배경 및 폰트 설정 */
    .stApp {
        background-color: #F4F6F9; /* 아주 연한 회색 배경 */
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', 'Segoe UI', 'Apple SD Gothic Neo', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
        color: #333;
    }

    /* 메인 타이틀 스타일 */
    .main-title {
        font-size: 32px; font-weight: 800; color: #0A192F; /* 딥 네이비 */
        text-align: center; margin-bottom: 5px; letter-spacing: -0.5px;
    }
    .main-title span { color: #FFD700; } /* 골드 포인트 */

    /* 서브 타이틀 스타일 */
    .sub-title {
        font-size: 14px; color: #6c757d; text-align: center; margin-bottom: 30px; font-weight: 500;
    }

    /* 카드형 컨테이너 스타일 */
    .card-container {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); /* 부드러운 그림자 */
        margin-bottom: 25px;
        border: 1px solid #EAECEF;
    }

    /* 섹션 헤더 스타일 */
    .section-header {
        font-size: 20px; font-weight: 700; color: #0A192F;
        margin-bottom: 20px; display: flex; align-items: center;
    }
    .section-header span { margin-right: 10px; font-size: 24px; }

    /* 분석 버튼 스타일 (그라데이션 적용) */
    .stButton>button {
        width: 60%; height: 60px;
        background: linear-gradient(90deg, #0A192F 0%, #1e3c72 100%); /* 딥 네이비 그라데이션 */
        color: #FFFFFF; border-radius: 30px; font-size: 18px; font-weight: 700; border: none;
        box-shadow: 0 8px 20px rgba(10, 25, 47, 0.2);
        margin: 30px auto; display: block; transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px rgba(10, 25, 47, 0.3);
    }

    /* 지수 신호등 배너 스타일 */
    .signal-banner {
        padding: 20px; border-radius: 12px; display: flex; align-items: center;
        margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .signal-icon { font-size: 36px; margin-right: 20px; }
    .signal-content h3 { margin: 0 0 5px 0; font-size: 22px; font-weight: 700; }
    .signal-content p { margin: 0; font-size: 15px; font-weight: 500; }

    /* 표(DataFrame) 스타일 커스터마이징 */
    [data-testid="stDataFrame"] {
        border: none;
    }
    [data-testid="stDataFrame"] div[class*="stDataFrame"] {
        border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    /* 헤더 배경색 변경 */
    [data-testid="stDataFrame"] thead tr th {
        background-color: #0A192F !important; color: white !important;
        font-weight: 600; font-size: 15px; border-bottom: none !important;
    }
    /* 셀 스타일 */
    [data-testid="stDataFrame"] tbody tr td {
        font-size: 14px; font-weight: 500; padding: 12px !important;
        border-bottom: 1px solid #F0F0F0 !important;
    }

    /* 사이드바 스타일 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF; border-right: 1px solid #EAECEF;
    }

    /* 푸터 스타일 */
    .footer {
        text-align: center; padding: 30px; font-size: 12px; color: #999;
        border-top: 1px solid #EAECEF; margin-top: 50px; background-color: #F4F6F9;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. 로직 함수 정의 (기존과 동일) ---

def get_market_status_banner(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=10)).strftime("%Y%m%d")

    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        if len(df) < 2:
            return "⚪", "데이터 준비중", "거래소 데이터를 불러오는 중입니다.", "#F9F9F9", "#9E9E9E"

        curr_price = df['종가'].iloc[-1]
        prev_price = df['종가'].iloc[-2]
        rate = ((curr_price - prev_price) / prev_price) * 100

        if rate > 0.5:
            return "🟢", "시장 강세", f"지수 {rate:.2f}% 상승 중. 적극 매수 시점입니다.", "#E8F5E9", "#2E7D32"
        elif rate > -0.5:
            return "🟡", "시장 보합", f"지수 {rate:.2f}% 보합. 확실한 대장주만 공략하세요.", "#FFFDE7", "#F57F17"
        else:
            return "🔴", "시장 약세", f"지수 {rate:.2f}% 하락 중. 현금 비중을 늘리세요.", "#FFEBEE", "#C62828"
    except Exception as e:
        return "⚪", "확인 불가", f"연결 오류: {str(e)}", "#F9F9F9", "#9E9E9E"

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
    except:
        return -1

# --- 4. 메인 UI ---

# 사이드바
with st.sidebar:
    st.markdown("### 📊 시장 선택")
    market_type = st.selectbox("", ["KOSPI", "KOSDAQ"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("<small>Powered by Pykrx & Streamlit</small>", unsafe_allow_html=True)

# 메인 컨텐츠
st.markdown('<H1 class="main-title">📈 MAGIC <span>STOCK</span></H1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI 실시간 빅데이터 분석 기반 | [ 09:00 - 15:30 ]</p>', unsafe_allow_html=True)

today_str = datetime.datetime.now().strftime("%Y%m%d")

if st.button('🔍 시장 분석 시작'):
    # A. 시장 신호등 (배너 형태)
    icon, title, desc, bg, txt = get_market_status_banner(market_type)
    st.markdown(f"""
        <div class="signal-banner" style="background-color:{bg}; color:{txt}; border-left: 5px solid {txt};">
            <div class="signal-icon">{icon}</div>
            <div class="signal-content">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # B. 종목 분석 및 추천 (카드형 컨테이너 적용)
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span>🎯</span> AI 추천 종목</div>', unsafe_allow_html=True)

    with st.spinner('데이터를 분석하고 있습니다... 잠시만 기다려주세요.'):
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
                    '종목명': name,
                    '현재가': price,
                    '등락률': filtered.loc[ticker, '등락률'],
                    '점수': score,
                    '목표가(+3%)': int(price * 1.03),
                    '상세정보': f"https://finance.naver.com/item/main.naver?code={ticker}"
                })

    if picks:
        df_picks = pd.DataFrame(picks).sort_values('점수', ascending=False).head(5)
        st.data_editor(
            df_picks,
            column_config={
                "점수": st.column_config.ProgressColumn("상승잠재력", min_value=0, max_value=7, format="%d점"),
                "현재가": st.column_config.NumberColumn(format="₩%d"),
                "등락률": st.column_config.NumberColumn(format="%.2f%%"),
                "목표가(+3%)": st.column_config.NumberColumn(format="₩%d"),
                "상세정보": st.column_config.LinkColumn("네이버증권", display_text="열기")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("현재 분석 기준을 통과한 강력한 추천 종목이 없습니다.")
    st.markdown('</div>', unsafe_allow_html=True) # 카드 컨테이너 닫기

    # C. 실시간 거래량 TOP 10 (카드형 컨테이너 적용)
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-header"><span>📊</span> 실시간 거래량 TOP 10</div>', unsafe_allow_html=True)
    top_10 = filtered.head(10)[['종가', '등락률']].copy()
    top_10.reset_index(inplace=True) # 티커를 컬럼으로
    top_10['종목명'] = [stock.get_market_ticker_name(t) for t in top_10['티커']]
    # 컬럼 순서 재배치 및 티커 숨기기
    st.dataframe(
        top_10[['종목명', '종가', '등락률']],
        hide_index=True,
        use_container_width=True,
        column_config={
             "종가": st.column_config.NumberColumn(format="₩%d"),
             "등락률": st.column_config.NumberColumn(format="%.2f%%")
        }
    )
    st.markdown('</div>', unsafe_allow_html=True) # 카드 컨테이너 닫기

# --- 5. 푸터 ---
st.markdown(f"""
    <div class="footer">
        투자결과에 따라 투자원금의 손실이 발생할 수 있습니다.<br>
        Copyright © 2026 보헤미안. All rights reserved.
    </div>
    """, unsafe_allow_html=True)
