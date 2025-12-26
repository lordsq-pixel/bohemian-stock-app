import streamlit as st
import FinanceDataReader as fdr
from langchain.chat_models import ChatOpenAI

# 1. 한국 시장 데이터 로드 (KOSPI/KOSDAQ)
@st.cache_data
def get_kr_data(ticker):
    df = fdr.DataReader(ticker)
    return df.tail(100) # 최근 100일 데이터

# 2. AI 판단 로직 (에이전트)
def ai_investment_decision(data, news):
    llm = ChatOpenAI(model="gpt-4o")
    prompt = f"다음 주가 데이터와 뉴스를 보고 국내 시장 관점에서 매수 승률을 계산해줘: {data}, {news}"
    return llm.predict(prompt)

# 3. Streamlit UI
st.title("🚀 K-Market AI 독창적 매매 시스템")
ticker = st.text_input("종목코드 입력 (예: 005930)", "005930")

if st.button("AI 심층 분석 시작"):
    data = get_kr_data(ticker)
    # 여기에 DART 공시나 실시간 뉴스 크롤링 로직 추가 가능
    result = ai_investment_decision(data, "최근 공시 및 뉴스 요약 데이터")
    st.write(result)
