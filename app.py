import streamlit as st
import pandas as pd
from pykrx import stock
import yfinance as yf
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from datetime import datetime, timedelta

# 1. 페이지 설정
st.set_page_config(page_title="BOHEMIAN STOCK Pro", layout="wide")
st.title("📊 BOHEMIAN STOCK Pro v4.0")
st.caption("외인·기관 수급 분석 및 기술적 지표 시스템")

# 2. 안전한 날짜 설정 로직 (에러 방지 핵심)
def get_safe_date():
    # 우선 오늘 날짜 확인
    now = datetime.now()
    
    # 성탄절(25일)이나 주말, 공휴일엔 데이터가 없으므로 
    # 안전하게 가장 최근 영업일인 '20251224'를 기본값으로 시도합니다.
    # 나중에 평일이 되면 이 코드가 자동으로 오늘/어제 데이터를 찾습니다.
    for i in range(0, 5):  # 최대 5일 전까지 거슬러 올라가며 확인
        check_date = (now - timedelta(days=i)).strftime("%Y%m%d")
        try:
            # 간단한 조회를 통해 데이터가 있는지 확인
            df = stock.get_market_ohlcv(check_date, check_date, "005930") # 삼성전자 기준 테스트
            if not df.empty:
                return check_date
        except:
            continue
    return "20251224" # 최후의 수단으로 12월 24일 지정

target_date = get_safe_date()

# 3. 사이드바 / UI 구성
st.subheader("분석 시장 선택")
market = st.radio("시장", ["KOSPI", "KOSDAQ"], horizontal=True)

if st.button("🚀 프리미엄 수급 분석 시작"):
    with st.spinner(f"{target_date} 데이터 분석 중..."):
        try:
            # 4. 데이터 불러오기
            df_base = stock.get_market_price_change_by_ticker(target_date, target_date, market=market)
            
            if df_base is None or df_base.empty:
                st.warning(f"{target_date}은 시장 데이터가 없습니다. 다른 날짜를 시도해 주세요.")
            else:
                # 5. 수급 데이터 가져오기
                df_investor = stock.get_market_net_purchases_of_equities_by_ticker(target_date, target_date, market)
                df = pd.concat([df_base, df_investor], axis=1)
                
                # 거래량 상위 10개
                top_10 = df.nlargest(10, '거래량')
                
                st.success(f"✅ {target_date} 분석 완료!")
                
                # 6. 결과 출력
                st.write(f"### 🏆 {market} 수급 상위 종목")
                st.dataframe(top_10[['종목명', '종가', '등락률', '외국인합계', '기관합계']])
                
                # 7. 차트 (첫 번째 종목)
                first_ticker = top_10.index[0]
                first_name = top_10.iloc[0]['종목명']
                yf_ticker = first_ticker + (".KS" if market == "KOSPI" else ".KQ")
                
                data = yf.download(yf_ticker, period="3mo", interval="1d")
                if not data.empty:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'].iloc[:,0] if isinstance(data['Close'], pd.DataFrame) else data['Close'], name="주가"))
                    fig.update_layout(title=f"{first_name} 최근 흐름", template="plotly_white")
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"오류 발생: {e}")
            st.info("시장이 열리지 않는 날에는 분석이 어려울 수 있습니다.")

else:
    st.info(f"분석 시작 버튼을 눌러주세요. (현재 기준 영업일: {target_date})")
