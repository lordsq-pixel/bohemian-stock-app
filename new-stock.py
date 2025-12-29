import pytz
import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands
import time
import random
import streamlit.components.v1 as components  # 위젯 사용을 위한 컴포넌트 추가

# --- 0. 기본 설정 ---
korea = pytz.timezone("Asia/Seoul")

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="MAGIC STOCK",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="📈"
)

# --- 2. 증권사 스타일 CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    .stApp { background-color: #F2F4F7; color: #1A1A1A; }
    html, body, [class*="css"] { font-family: 'Pretendard', -apple-system, sans-serif; }

    /* [핵심] 상단 여백 제거 및 컨텐츠 위로 올리기 */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Streamlit 기본 헤더(햄버거 메뉴 라인) 숨기기 */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* 상단 GNB (위치 보정) */
    .top-nav {
        background-color: #FFFFFF; 
        padding: 12px 25px;
        border-bottom: 1px solid #E5E8EB;
        display: flex; justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 999;
        margin-top: 0px;
    }
    
    .brand-name { font-size: 20px; font-weight: 700; color: #0052CC; letter-spacing: -0.5px; }
    .live-clock { font-size: 14px; font-weight: 500; color: #6B7684; }

    .section-title {
        font-size: 18px; font-weight: 700; color: #1A1A1A;
        margin: 25px 0 15px 0; padding-left: 10px; border-left: 4px solid #0052CC;
    }

    /* 버튼 스타일 */
    .stButton>button {
        width: 100% !important; height: 50px;
        background: #0052CC !important; color: #FFFFFF !important;
        border: none !important; border-radius: 8px !important;
        font-size: 16px !important; font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .stButton>button:hover { background: #003fa3 !important; }

    /* 리스트 스타일 (AI 추천 결과용) */
    .stock-row {
        background: white; border-bottom: 1px solid #F2F4F7; padding: 15px 20px;
        display: flex; justify-content: space-between; align-items: center; transition: background 0.2s;
    }
    .stock-row:hover { background: #F9FAFB; }
    .stock-info-main { display: flex; flex-direction: column; }
    .stock-name { font-size: 16px; font-weight: 600; color: #1A1A1A; }
    .stock-code { font-size: 12px; color: #ADB5BD; }
    .stock-price-area { text-align: right; }
    .current-price { font-size: 16px; font-weight: 700; }
    .price-change { font-size: 12px; font-weight: 500; }

    .up { color: #E52E2E; } 
    .down { color: #0055FF; }

    /* 푸터 */
    .footer { padding: 40px 20px; text-align: center; font-size: 12px; color: #8B95A1; background: #F9FAFB; margin-top: 50px; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} 
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 ---

def get_latest_trading_day():
    """가장 최근 영업일을 찾습니다 (주말/공휴일 대비)"""
    date = datetime.datetime.now(korea)
    # 장 마감 전(오전 9시 이전)이면 전일 데이터를 쓰도록 할 수도 있으나, 
    # AI 분석은 '오늘' 날짜 기준으로 시도하고 실패시 전일을 찾음
    for _ in range(7):
        date_str = date.strftime("%Y%m%d")
        try:
            # 아주 가벼운 조회로 휴장일 체크
            check_df = stock.get_index_ohlcv_by_date(date_str, date_str, "1001")
            if not check_df.empty:
                return date_str
        except:
            pass
        date -= datetime.timedelta(days=1)
    return datetime.datetime.now(korea).strftime("%Y%m%d")

def analyze_stock(ticker, target_date):
    """AI 분석 로직 (기존 유지)"""
    try:
        end_date = target_date
        start_date = (datetime.datetime.strptime(target_date, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start_date, end_date, ticker)
        if len(df) < 30: return 0
        
        indicator_bb = BollingerBands(close=df["종가"], window=20, window_dev=2)
        df['bb_low'] = indicator_bb.bollinger_lband()
        
        curr_close, curr_low, prev_low = df['종가'].iloc[-1], df['저가'].iloc[-1], df['저가'].iloc[-2]
        rsi = RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1]
        sma5 = SMAIndicator(close=df["종가"], window=5).sma_indicator().iloc[-1]
        
        score = 0
        if (prev_low <= df['bb_low'].iloc[-2] * 1.02) or (curr_low <= df['bb_low'].iloc[-1] * 1.02):
            if curr_close > df['bb_low'].iloc[-1]: score += 4
        if curr_close > sma5: score += 1
        if 30 <= rsi <= 60: score += 2
        if df['거래량'].iloc[-1] > df['거래량'].iloc[-20:-1].mean() * 1.1: score += 1
        return score
    except:
        return -1

# --- 4. 메인 UI 구성 ---

# 상단 헤더
st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">📊 매직스톡 Ai</div>
        <div id="live-clock-text" class="live-clock">
            {datetime.datetime.now(korea).strftime('%Y.%m.%d %H:%M:%S')}
        </div>
    </div>
    """, unsafe_allow_html=True)

# [위젯 1] 상단 티커 (코스피, 코스닥, 환율, 주요 지수) - 서버 부하 0, 즉시 로딩
st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
components.html(
    """
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
      "symbols": [
        {
          "proName": "FOREXCOM:NSXUSD",
          "title": "US 100"
        },
        {
          "proName": "FX_IDC:KRWUSD",
          "title": "환율 (KRW/USD)"
        },
        {
          "description": "KOSPI",
          "proName": "KRX:KOSPI"
        },
        {
          "description": "KOSDAQ",
          "proName": "KRX:KOSDAQ"
        },
        {
          "description": "삼성전자",
          "proName": "KRX:005930"
        }
      ],
      "showSymbolLogo": true,
      "colorTheme": "light",
      "isTransparent": false,
      "displayMode": "adaptive",
      "locale": "kr"
    }
      </script>
    </div>
    <!-- TradingView Widget END -->
    """,
    height=50
)

# 메인 레이아웃 분할
main_col1, main_col2 = st.columns([2, 1])

# [왼쪽] AI 분석 영역 (여기는 사용자가 원할 때만 API 호출)
with main_col1:
    st.markdown('<div class="section-title">⚡ AI 퀀트 분석</div>', unsafe_allow_html=True)
    st.info("실시간 시세는 위젯으로 즉시 확인 가능합니다. 아래 버튼을 누르면 AI가 심층 분석을 시작합니다.")

    m_type = st.radio("분석 대상 시장", ["KOSPI", "KOSDAQ"], horizontal=True)
    
    if st.button('🎯 AI 추천종목 찾기 (Start Analysis)'):
        target_date = get_latest_trading_day()
        
        with st.spinner(f'{target_date} 기준 데이터 분석중... (약 10~20초 소요)'):
            try:
                # 1. 시세 데이터 가져오기 (여기는 Python API 사용 - 분석용)
                df_base = stock.get_market_price_change_by_ticker(target_date, target_date, market=m_type)
                
                # 2. 거래량 상위 & 상승 종목 1차 필터링
                filtered = df_base[(df_base['등락률'] >= 0.5) & (df_base['거래량'] > 100000)]
                filtered = filtered.sort_values('거래량', ascending=False).head(30) # 속도를 위해 상위 30개만

                picks = []
                progress_bar = st.progress(0)
                total_items = len(filtered)
                
                for idx, (ticker, row) in enumerate(filtered.iterrows()):
                    score = analyze_stock(ticker, target_date)
                    if score >= 4:
                        picks.append({
                            'ticker': ticker, 
                            'name': stock.get_market_ticker_name(ticker),
                            'price': row['종가'], 
                            'rate': row['등락률'],
                            'score': score, 
                            'target': int(row['종가'] * 1.05)
                        })
                    progress_bar.progress((idx + 1) / total_items)
                
                progress_bar.empty()

                if picks:
                    st.success(f"분석 완료! {len(picks)}개의 추천 종목을 찾았습니다.")
                    st.markdown('<div style="background: white; border-radius: 12px; overflow: hidden; border: 1px solid #E5E8EB;">', unsafe_allow_html=True)
                    
                    for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                        color_class = "up" if p['rate'] > 0 else "down"
                        st.markdown(f"""
                            <div class="stock-row">
                                <div class="stock-info-main">
                                    <span class="stock-name">{p['name']}</span>
                                    <span class="stock-code">{p['ticker']} | <b style="color:#0052CC">SCORE {p['score']}</b></span>
                                </div>
                                <div class="stock-price-area">
                                    <div class="current-price {color_class}">{p['price']:,}</div>
                                    <div class="price-change {color_class}">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                                    <div style="font-size:11px; color:#34C759; margin-top:2px;">Target: {p['target']:,}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.warning("현재 기준에 부합하는 종목이 없습니다.")
            except Exception as e:
                st.error(f"데이터 접속 중 오류 발생: {e}")

# [오른쪽] 실시간 순위 (위젯으로 대체)
with main_col2:
    st.markdown('<div class="section-title">🔥 실시간 핫이슈</div>', unsafe_allow_html=True)
    
    # [위젯 2] 실시간 등락률 상위 리스트 (서버 부하 없음)
    components.html(
        """
        <!-- TradingView Widget BEGIN -->
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-hotlists.js" async>
          {
          "colorTheme": "light",
          "dateRange": "12M",
          "exchange": "KRX",
          "showChart": true,
          "locale": "kr",
          "largeChartUrl": "",
          "isTransparent": false,
          "showSymbolLogo": true,
          "showFloatingTooltip": false,
          "width": "100%",
          "height": "500",
          "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
          "plotLineColorFalling": "rgba(41, 98, 255, 1)",
          "gridLineColor": "rgba(240, 243, 250, 0)",
          "scaleFontColor": "rgba(106, 109, 120, 1)",
          "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
          "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
          "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
          "symbolActiveColor": "rgba(41, 98, 255, 0.12)"
        }
          </script>
        </div>
        <!-- TradingView Widget END -->
        """,
        height=500
    )

# --- 5. 푸터 ---
st.markdown("""
    <div class="footer">
        데이터 지연 없이 실시간 정보를 제공합니다.<br>
        (Market Data provided by TradingView)<br><br>
        Copyright ⓒ 2026 Bohemian All rights reserved.
    </div>
    """, unsafe_allow_html=True)
