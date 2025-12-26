import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

# --- 1. 페이지 설정 ---
st.set_page_config(page_title="MAGIC SECURITIES", layout="wide", initial_sidebar_state="collapsed")

# --- 2. 증권사 스타일 CSS (수급 배지 디자인 추가) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');

    .stApp { background-color: #F2F4F7; color: #1A1A1A; }
    html, body, [class*="css"] { font-family: 'Pretendard', sans-serif; }

    .top-nav {
        background-color: #FFFFFF; padding: 15px 25px;
        border-bottom: 1px solid #E5E8EB; display: flex;
        justify-content: space-between; align-items: center;
        position: sticky; top: 0; z-index: 999;
    }
    .brand-name { font-size: 20px; font-weight: 700; color: #0052CC; }
    .live-clock { font-size: 14px; color: #6B7684; }

    .section-title {
        font-size: 18px; font-weight: 700; color: #1A1A1A;
        margin: 25px 0 15px 0; padding-left: 10px; border-left: 4px solid #0052CC;
    }

    /* 수급 배지 스타일 */
    .badge {
        padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 4px;
    }
    .badge-for { background-color: #E8F2FF; color: #0052CC; border: 1px solid #CCE0FF; } /* 외인 */
    .badge-ins { background-color: #FFF0F5; color: #D63384; border: 1px solid #FFD6E7; } /* 기관 */

    .stock-row {
        background: white; border-bottom: 1px solid #F2F4F7;
        padding: 15px 20px; display: flex; justify-content: space-between; align-items: center;
    }
    .stock-row:hover { background: #F9FAFB; }
    
    .up { color: #E52E2E; }
    .down { color: #0055FF; }

    .stButton>button {
        width: 100% !important; height: 50px; background: #0052CC !important;
        color: white !important; border-radius: 8px !important; font-weight: 600 !important;
    }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. 데이터 로직 (수급 분석 추가) ---

def get_market_data(market_name):
    ticker = "1001" if market_name == "KOSPI" else "2001"
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y%m%d")
    try:
        df = stock.get_index_ohlcv_by_date(start, end, ticker)
        curr, prev = df['종가'].iloc[-1], df['종가'].iloc[-2]
        change = curr - prev
        rate = (change / prev) * 100
        return curr, change, rate
    except: return 0, 0, 0

def analyze_stock_with_supply(ticker, today):
    try:
        # A. 가격 및 지표 분석 (기존 로직)
        start_date = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start_date, today, ticker)
        
        indicator_bb = BollingerBands(close=df["종가"], window=20)
        bb_low = indicator_bb.bollinger_lband().iloc[-1]
        rsi = RSIIndicator(close=df["종가"]).rsi().iloc[-1]
        
        score = 0
        if df['저가'].iloc[-1] <= bb_low * 1.01: score += 4  # 바닥권
        if 30 <= rsi <= 55: score += 2
        
        # B. 수급 분석 (추가된 부분)
        # 당일 외국인/기관 순매수량 확인
        df_investor = stock.get_market_net_purchases_of_equities_by_ticker(today, today, ticker)
        is_foreigner_buy = df_investor.loc[ticker, '외국인'] > 0
        is_institution_buy = df_investor.loc[ticker, '기관합계'] > 0
        
        if is_foreigner_buy: score += 2
        if is_institution_buy: score += 2
        
        return score, is_foreigner_buy, is_institution_buy
    except:
        return -1, False, False

# --- 4. 메인 UI 구성 ---

st.markdown(f"""
    <div class="top-nav">
        <div class="brand-name">MAGIC SECURITIES</div>
        <div class="live-clock">{datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

main_col1, main_col2 = st.columns([2, 1])

with main_col1:
    st.markdown('<div class="section-title">MARKET INDEX</div>', unsafe_allow_html=True)
    idx_col1, idx_col2 = st.columns(2)
    for m_name, col in zip(["KOSPI", "KOSDAQ"], [idx_col1, idx_col2]):
        val, chg, rt = get_market_data(m_name)
        color = "up" if chg > 0 else "down"
        col.markdown(f"""
            <div style="background:white; padding:15px; border-radius:12px; border:1px solid #E5E8EB;">
                <div style="font-size:12px; color:#6B7684;">{m_name}</div>
                <div style="font-size:20px; font-weight:700;">{val:,.2f}</div>
                <div class="{color}" style="font-size:13px; font-weight:600;">{'▲' if chg > 0 else '▼'} {abs(chg):,.2f} ({rt:.2f}%)</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">AI 수급 분석 포착</div>', unsafe_allow_html=True)
    m_type = st.radio("시장", ["KOSPI", "KOSDAQ"], horizontal=True, label_visibility="collapsed")
    
    if st.button('실시간 수급 & 차트 스캔 시작'):
        today_str = datetime.datetime.now().strftime("%Y%m%d")
        with st.spinner('전 종목 수급 데이터를 분석 중입니다...'):
            df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=m_type)
            # 거래량이 어느 정도 있는 종목 중 등락률이 안정적인 종목 필터링
            filtered = df_base[(df_base['거래량'] > 150000) & (df_base['등락률'] >= -1)].sort_values('거래량', ascending=False).head(30)

            picks = []
            for ticker in filtered.index:
                score, f_buy, i_buy = analyze_stock_with_supply(ticker, today_str)
                if score >= 5: # 수급이 포함되어 기준 점수를 조금 높임
                    picks.append({
                        'ticker': ticker, 'name': stock.get_market_ticker_name(ticker),
                        'price': filtered.loc[ticker, '종가'], 'rate': filtered.loc[ticker, '등락률'],
                        'score': score, 'f_buy': f_buy, 'i_buy': i_buy
                    })

            if picks:
                for p in sorted(picks, key=lambda x: x['score'], reverse=True):
                    f_badge = '<span class="badge badge-for">외인</span>' if p['f_buy'] else ''
                    i_badge = '<span class="badge badge-ins">기관</span>' if p['i_buy'] else ''
                    color_class = "up" if p['rate'] > 0 else "down"
                    
                    st.markdown(f"""
                        <div class="stock-row">
                            <div>
                                <div class="stock-name">{p['name']} <span style="font-size:12px; color:#0052CC; margin-left:5px;">★ {p['score']}</span></div>
                                <div style="margin-top:5px;">{f_badge}{i_badge}<span class="stock-code">{p['ticker']}</span></div>
                            </div>
                            <div style="text-align:right;">
                                <div class="current-price {color_class}">{p['price']:,}</div>
                                <div class="price-change {color_class}">{'+' if p['rate'] > 0 else ''}{p['rate']:.2f}%</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("현재 수급과 기술적 지표가 일치하는 종목이 없습니다.")

with main_col2:
    st.markdown('<div class="section-title">수급 TOP 5 (당일)</div>', unsafe_allow_html=True)
    # 당일 외국인 순매수 상위
    df_inv = stock.get_market_net_purchases_of_equities_by_ticker(datetime.datetime.now().strftime("%Y%m%d"), datetime.datetime.now().strftime("%Y%m%d"), m_type)
    top_f = df_inv.sort_values('외국인', ascending=False).head(5)
    
    for t, row in top_f.iterrows():
        name = stock.get_market_ticker_name(t)
        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:12px 5px; border-bottom:1px solid #E5E8EB;">
                <span style="font-size:14px;">{name}</span>
                <span style="font-size:14px; color:#0052CC; font-weight:600;">+{row['외국인']//1000:,.0f}K</span>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="footer">ⓒ 2025 MAGIC SECURITIES | 본 데이터는 투자 참고용입니다.</div>', unsafe_allow_html=True)
