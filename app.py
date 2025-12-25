import streamlit as st
import pandas as pd
from pykrx import stock
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="BOHEMIAN STOCK Pro", layout="wide")
st.title("📊 BOHEMIAN STOCK Pro v4.0")
st.caption("외인·기관 수급 분석 및 기술적 지표 시스템")

# 2. 날짜 설정 (에러 방지 핵심 로직)
# 오늘 날짜를 가져오되, pykrx 기능을 이용해 가장 가까운 영업일로 자동 보정합니다.
curr_date = datetime.now().strftime("%Y%m%d")
target_date = stock.get_nearest_business_day_in_a_week(date=curr_date)

# 3. 사이드바 / UI 구성
st.subheader("분석 시장 선택")
market = st.radio("시장", ["KOSPI", "KOSDAQ"], horizontal=True)

if st.button("🚀 프리미엄 수급 분석 시작"):
    with st.spinner(f"{target_date} 데이터 분석 중..."):
        try:
            # 4. 데이터 불러오기 (오늘 휴장일이어도 target_date가 영업일을 찾아줌)
            df_base = stock.get_market_price_change_by_ticker(target_date, target_date, market=market)
            
            if df_base.empty:
                st.error("데이터를 불러올 수 없습니다. 날짜 설정을 확인해주세요.")
            else:
                # 5. 수급 데이터 가져오기 (외인/기관)
                df_investor = stock.get_market_net_purchases_of_equities_by_ticker(target_date, target_date, market)
                
                # 데이터 합치기
                df = pd.concat([df_base, df_investor], axis=1)
                
                # 상위 10개 종목 추출 (거래량 기준)
                top_10 = df.nlargest(10, '거래량')
                
                st.success(f"✅ {target_date} (최근 영업일) 분석 완료!")
                
                # 6. 결과 표 출력
                st.write(f"### 🏆 {market} 수급 상위 종목")
                st.dataframe(top_10[['종목명', '종가', '등락률', '외국인합계', '기관합계']])
                
                # 7. 차트 예시 (첫 번째 종목)
                first_ticker = top_10.index[0]
                first_name = top_10.iloc[0]['종목명']
                
                # yfinance용 티커 변환 (KOSPI: .KS, KOSDAQ: .KQ)
                yf_ticker = first_ticker + (".KS" if market == "KOSPI" else ".KQ")
                data = yf.download(yf_ticker, period="3mo", interval="1d")
                
                if not data.empty:
                    # RSI 지표 계산
                    rsi_inst = RSIIndicator(close=data['Close'].squeeze(), window=14)
                    data['RSI'] = rsi_inst.rsi()
                    
                    # 차트 그리기
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].squeeze(), name="주가"))
                    fig.update_layout(title=f"{first_name} 최근 3개월 흐름", xaxis_title="날짜", yaxis_title="가격")
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"분석 중 에러가 발생했습니다: {e}")
            st.info("Tip: pykrx 서버 응답이 늦을 수 있습니다. 잠시 후 다시 시도해 보세요.")

else:
    st.info(f"분석 시작 버튼을 눌러주세요. (현재 기준 영업일: {target_date})")
