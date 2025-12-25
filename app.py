import streamlit as st
from pykrx import stock
import pandas as pd
import datetime
import requests
import json
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator

# --- 1. 페이지 설정 및 초기화 ---
st.set_page_config(page_title="BOHEMIAN STOCK v4.0", layout="wide")

# --- 2. 카카오톡 알림 함수 (REST API 키 필요) ---
def send_kakao_message(text):
    # 카카오 개발자 센터에서 발급받은 Access Token이 필요합니다.
    access_token = "YOUR_KAKAO_ACCESS_TOKEN" 
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": f"[BOHEMIAN PICK]\n{text}",
            "link": {"web_url": "https://m.stock.naver.com", "mobile_web_url": "https://m.stock.naver.com"}
        })
    }
    # 실제 연동 시 주석 해제하여 사용
    # response = requests.post(url, headers=headers, data=data)
    # return response.status_code

# --- 3. 핵심 분석 로직 ---

@st.cache_data(ttl=300)
def get_supply_data(ticker, days=3):
    """최근 n일간 외인/기관 순매수 합계 계산"""
    end = datetime.datetime.now().strftime("%Y%m%d")
    start = (datetime.datetime.now() - datetime.timedelta(days=days+5)).strftime("%Y%m%d")
    try:
        df = stock.get_market_net_purchases_of_equities_by_ticker(start, end, ticker)
        # 해당 종목의 외인/기관 합계 추출
        inv_sum = df.loc[ticker, '기관합계']
        frg_sum = df.loc[ticker, '외국인합계']
        return inv_sum, frg_sum
    except:
        return 0, 0

def analyze_stock_pro(ticker, name, today):
    try:
        start = (datetime.datetime.strptime(today, "%Y%m%d") - datetime.timedelta(days=60)).strftime("%Y%m%d")
        df = stock.get_market_ohlcv_by_date(start, today, ticker)
        if len(df) < 20: return None
        
        curr_price = int(df['종가'].iloc[-1])
        rsi = RSIIndicator(close=df["종가"], window=14).rsi().iloc[-1]
        inv_sum, frg_sum = get_supply_data(ticker)
        
        score = 0
        desc_tags = []
        
        # [수급] 외인/기관 동반 매수 시 가점
        if inv_sum > 0: score += 2; desc_tags.append("기관매수")
        if frg_sum > 0: score += 2; desc_tags.append("외인매수")
        
        # [기술] RSI 및 정배열
        if 45 <= rsi <= 65: score += 2; desc_tags.append("매수타점")
        
        # [재료/뉴스] 거래량 급증 (뉴스/공시 가능성)
        if df['거래량'].iloc[-1] > df['거래량'].iloc[-2] * 2: 
            score += 2; desc_tags.append("거래폭발")

        return {
            '종목명': name,
            '현재가': curr_price,
            '등락률': round(((df['종가'].iloc[-1] / df['종가'].iloc[-2]) - 1) * 100, 2),
            '수급(기관)': inv_sum,
            '수급(외인)': frg_sum,
            '점수': score,
            '특이사항': ", ".join(desc_tags)
        }
    except:
        return None

# --- 4. 메인 UI ---

st.title("📊 BOHEMIAN STOCK Pro v4.0")
st.markdown("외인·기관 수급 분석 및 카카오톡 알림 시스템")

market = st.radio("분석 시장", ["KOSPI", "KOSDAQ"], horizontal=True)
today_str = "20251224"

if st.button('🚀 프리미엄 수급 분석 시작'):
    with st.spinner('전 종목 수급 및 기술적 지표 분석 중...'):
        # 1. 거래량 상위 종목 베이스 추출
        df_base = stock.get_market_price_change_by_ticker(today_str, today_str, market=market)
        candidates = df_base[(df_base['등락률'] >= 2.0)].sort_values('거래량', ascending=False).head(30)
        
        results = []
        for ticker in candidates.index:
            name = stock.get_market_ticker_name(ticker)
            analysis = analyze_stock_pro(ticker, name, today_str)
            if analysis and analysis['점수'] >= 5:
                results.append(analysis)
        
        if results:
            df_res = pd.DataFrame(results).sort_values('점수', ascending=False)
            
            # 결과 출력
            st.subheader("🎯 오늘의 TOP 수급 매수주")
            st.data_editor(
                df_res,
                column_config={
                    "점수": st.column_config.ProgressColumn("상승강도", min_value=0, max_value=8),
                    "현재가": st.column_config.NumberColumn(format="₩%d"),
                    "수급(기관)": st.column_config.NumberColumn(format="%d주"),
                    "수급(외인)": st.column_config.NumberColumn(format="%d주"),
                },
                hide_index=True, use_container_width=True
            )
            
            # 1위 종목 카톡 알림 보내기 (옵션)
            top_pick = df_res.iloc[0]
            if st.button(f"📲 '{top_pick['종목명']}' 카톡 알림 전송"):
                msg = f"오늘의 픽: {top_pick['종목명']}\n점수: {top_pick['점수']}점\n현재가: {top_pick['현재가']}원\n수급: {top_pick['특이사항']}"
                # send_kakao_message(msg) # 토큰 설정 후 주석 해제
                st.success("카카오톡으로 알림을 보냈습니다! (API 연결 필요)")
        else:
            st.info("현재 분석 기준(5점 이상)을 충족하는 종목이 없습니다.")

st.divider()

st.caption("💡 Tip: 외인과 기관이 동반 매수(양매수)하면서 거래량이 터진 종목은 신뢰도가 매우 높습니다.")
