import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict

# 초기 화면 설정
if "page" not in st.session_state:
    st.session_state.page = "survey"  # 기본 화면은 설문조사 화면

# 화면 전환 함수
def go_to_page(page_name):
    st.session_state.page = page_name

# 설문조사 화면
def survey_page():
    st.title("📋 당신을 위한 맞춤 포트폴리오")

    with st.expander('이 앱에 대하여'):
        st.write('이 앱은 투자 기간과 위험 성향에 맞추어 맞춤 포트폴리오를 제시합니다.')

    st.sidebar.header('📄 간단한 설문조사')
    st.session_state.user_name = st.sidebar.text_input('당신의 이름은 무엇인가요?', st.session_state.get("user_name", ""))
    st.session_state.user_gender = st.sidebar.selectbox('당신의 성별은 무엇인가요?', ['', '남성', '여성'], index=0 if "user_gender" not in st.session_state else ['', '남성', '여성'].index(st.session_state.user_gender))
    st.session_state.user_age = st.sidebar.text_input('당신의 나이는 어떻게 되시나요?', st.session_state.get("user_age", ""))
    st.session_state.user_risk = st.sidebar.selectbox('당신의 투자성향은?', ['', '안정추구형', '위험중립형', '공격투자형'], index=0 if "user_risk" not in st.session_state else ['', '안정추구형', '위험중립형', '공격투자형'].index(st.session_state.user_risk))
    st.session_state.user_horizon = st.sidebar.selectbox('당신의 투자 기간은?', ['', '6개월', '2년'], index=0 if "user_horizon" not in st.session_state else ['', '6개월', '2년'].index(st.session_state.user_horizon))

    st.header("👀 설문조사 결과")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.session_state.user_name:
            st.write(f'👋 안녕하세요 **{st.session_state.user_name}**님!')
        else:
            st.write('👈  **이름**을 입력해 주세요!')

    with col2:
        if st.session_state.user_risk:
            st.write(f'당신의 **투자성향**은 **{st.session_state.user_risk}**입니다!')
        else:
            st.write('👈 **투자성향**을 선택해 주세요!')

    with col3:
        if st.session_state.user_horizon:
            st.write(f'당신의 **투자기간**은 **{st.session_state.user_horizon}**입니다!')
        else:
            st.write('👈 **투자기간**을 선택해 주세요!')

    # 버튼 클릭 시 결과 화면으로 이동
    if st.session_state.user_risk and st.session_state.user_horizon:
        if st.button("추천 포트폴리오 보기"):
            go_to_page("portfolio")

def portfolio_page():

    st.title("📊 추천 포트폴리오")

      # 포트폴리오 데이터 결정
    if st.session_state.user_risk == "안정추구형" and st.session_state.user_horizon == "6개월":
      portfolio = {'Equity': 10, 'Fixed income': 90}
    elif st.session_state.user_risk == "안정추구형" and st.session_state.user_horizon == "2년":
      portfolio = {'Equity': 20, 'Fixed income': 80}
    elif st.session_state.user_risk == "위험중립형" and st.session_state.user_horizon == "6개월":
      portfolio = {'Equity': 50, 'Fixed income': 50}
    elif st.session_state.user_risk == "위험중립형" and st.session_state.user_horizon == "2년":
      portfolio = {'Equity': 60, 'Fixed income': 40}
    elif st.session_state.user_risk == "공격투자형" and st.session_state.user_horizon == "6개월":
      portfolio = {'Equity': 70, 'Fixed income': 30}
    else:
      portfolio = {'Equity': 80, 'Fixed income': 20}

    # 포트폴리오 표
    portfolio_df = pd.DataFrame({
        "자산": portfolio.keys(),
        "비율 (%)": portfolio.values()
    })
    styled_table = portfolio_df.style.set_table_styles(
        [{"selector": "thead", "props": [("background-color", "#f4f4f4"), ("font-size", "16px")]}]
    ).set_properties(**{"font-size": "14px", "text-align": "center"}).background_gradient(cmap="Blues", subset=["비율 (%)"])

    st.subheader("📋 포트폴리오 구성표")
    st.dataframe(styled_table, use_container_width=True)

    # 파이 차트
    st.subheader("📈 포트폴리오 비율")
    fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
    wedges, texts, autotexts = ax.pie(
        portfolio.values(),
        labels=portfolio.keys(),
        autopct="%1.1f%%",
        startangle=90,
        colors=["#4CAF50", "#2196F3", "#FFC107"],
        textprops={"fontsize": 10},
    )

    for autotext in autotexts:
      autotext.set_fontsize(8)
    st.pyplot(fig)

    # 다시 설문조사로 이동
    if st.button("다시 설문조사로 돌아가기"):
      go_to_page("survey")

# 화면 렌더링
if st.session_state.page == "survey":
   survey_page()
elif st.session_state.page == "portfolio":
   portfolio_page()