import streamlit as st
import FinanceDataReader as fdr
from pykrx import stock
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import datetime
import pandas as pd

# --- [설정] API 키 입력 (보안을 위해 실제 서비스 시 .env 사용 권장) ---
OPENAI_API_KEY = "여기에_사용자의_OpenAI_API_키를_넣으세요"

st.set_page_config(page_title="K-Market AI Agent", layout="wide")

# --- [함수] 데이터 수집: 가격 + 수급 ---
def get_stock_data(ticker, days=30):
    end_date = datetime.datetime.now().strftime("%Y%m%d")
    start_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
    
    # 1. 가격 데이터 (fdr)
    df_price = fdr.DataReader(ticker, start=start_date)
    
    # 2. 수급 데이터 (pykrx) - 국내장 성공의 핵심
    df_investor = stock.get_market_net_purchases_of_equities_by_ticker(start_date, end_date, ticker)
    
    return df_price, df_investor

# --- [함수] AI 분석 엔진 (독창적 로직) ---
def analyze_with_ai(price_df, investor_df):
    if not OPENAI_API_KEY or "여기에" in OPENAI_API_KEY:
        return "⚠️ OpenAI API 키를 설정해주세요."

    llm = ChatOpenAI(model="gpt-4o", openai_api_key=OPENAI_API_KEY)
    
    # 데이터 요약
    recent_price = price_df.tail(5).to_string()
    recent_supply = investor_df.to_string()
    
    template = """
    당신은 대한민국 코스피/코스닥 전문 프라이빗 뱅커(PB)입니다.
    아래 데이터를 바탕으로 '범접할 수 없는 성공 확률'을 위한 매매 전략을 세우세요.
    
    [최근 5일 가격 데이터]
    {price}
    
    [최근 수급 현황 (외국인/기관)]
    {supply}
    
    분석 가이드라인:
    1. 수급의 질을 평가하라 (개인만 사고 있다면 위험 신호).
    2. 가격 변동성과 거래량의 상관관계를 분석하라.
    3. '매수/관망/매도' 중 하나를 선택하고 그 근거를 논리적으로 설명하라.
    4. 예상 성공 확률을 %로 제시하라.
    """
    
    prompt = PromptTemplate.from_template(template)
    chain = prompt | llm
    
    response = chain.invoke({"price": recent_price, "supply": recent_supply})
    return response.content

# --- [UI] Streamlit 화면 구성 ---
st.title("🚀 독창적 K-Market AI 매매 참모")
st.markdown("국내 시장의 **가격 패턴**과 **메이저 수급**을 AI가 결합 분석합니다.")

ticker = st.sidebar.text_input("종목코드 (6자리)", value="005930") # 삼성전자 기본값
analyze_btn = st.sidebar.button("AI 심층 분석 실행")

if analyze_btn:
    with st.spinner('데이터 수집 및 AI 토론 중...'):
        try:
            # 데이터 가져오기
            price_df, investor_df = get_stock_data(ticker)
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📈 최근 주가 흐름")
                st.line_chart(price_df['Close'])
                
            with col2:
                st.subheader("👤 메이저 수급 현황")
                st.dataframe(investor_df)

            # AI 분석 결과
            st.divider()
            st.subheader("🤖 AI 전략 참모의 최종 판단")
            analysis_result = analyze_with_ai(price_df, investor_df)
            st.info(analysis_result)
            
        except Exception as e:
            st.error(f"오류 발생: {e}")

# --- [GitHub 관리 팁] ---
st.sidebar.divider()
st.sidebar.write("📂 **GitHub 업로드 팁**")
st.sidebar.caption("1. .gitignore에 .env 추가")
st.sidebar.caption("2. requirements.txt 생성")
