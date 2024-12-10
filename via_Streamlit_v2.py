import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

# 초기 화면 설정
if "page" not in st.session_state:
    st.session_state.page = "survey"

# 화면 전환 함수
def go_to_page(page_name):
    st.session_state.page = page_name

# 리스크 허용 수준을 매핑하는 함수
def map_risk_level(user_risk):
    mapping = {
        "리스크를 피하고 싶음": "안정추구형",
        "일부 리스크는 감수 가능": "위험중립형",
        "높은 리스크도 수용 가능": "공격투자형",
    }
    return mapping.get(user_risk, "미선택")  # 기본값은 '미선택'

# 설문조사 화면
def survey_page():
    st.title("✨ 맞춤형 포트폴리오 설계")

    with st.sidebar:
        st.header("📝 설문조사")
        st.session_state.user_name = st.text_input("이름", st.session_state.get("user_name", ""))
        st.session_state.user_gender = st.selectbox(
            "성별", ["", "남성", "여성"],
            index=0 if "user_gender" not in st.session_state else ["", "남성", "여성"].index(st.session_state.user_gender)
        )
        st.session_state.user_goal = st.selectbox(
            "당신의 투자 목표는 무엇인가요?",
            ["", "자산 보호", "안정적 수익", "고수익 추구"],
            index=0 if "user_goal" not in st.session_state else ["", "자산 보호", "안정적 수익", "고수익 추구"].index(
                st.session_state.user_goal)
        )
        st.session_state.user_experience = st.selectbox(
            "투자 경험은 얼마나 되십니까?",
            ["", "전혀 없음", "초보 수준", "경험이 많음"],
            index=0 if "user_experience" not in st.session_state else ["", "전혀 없음", "초보 수준", "경험이 많음"].index(
                st.session_state.user_experience)
        )
        st.session_state.user_market = st.selectbox(
            "갑작스러운 시장 변동에 어떻게 대처하시겠습니까?",
            ["", "자산을 매도하여 손실을 최소화", "시장 상황을 관망", "추가 투자를 고려"],
            index=0 if "user_market" not in st.session_state else ["", "자산을 매도하여 손실을 최소화", "시장 상황을 관망", "추가 투자를 고려"].index(
                st.session_state.user_market)
        )
        st.session_state.user_risk = st.selectbox(
            "리스크 허용 수준에 대해 평가해주세요.",
            ["", "리스크를 피하고 싶음", "일부 리스크는 감수 가능", "높은 리스크도 수용 가능"],
            index=0 if "user_risk" not in st.session_state else ["", "리스크를 피하고 싶음", "일부 리스크는 감수 가능", "높은 리스크도 수용 가능"].index(
                st.session_state.user_risk)
        )
        st.session_state.user_horizon = st.selectbox(
            "당신이 생각하는 적정 투자기간은 어느정도인가요?",
            ["", "6개월", "2년"],
            index=0 if "user_horizon" not in st.session_state else ["", "6개월", "2년"].index(
                st.session_state.user_horizon)
        )

    # 투자 성향 계산 함수
    def calculate_investment_type(user_goal, user_experience, user_market, user_risk):
        score = 0

        # 투자 목표 가중치
        goal_mapping = {
            "자산 보호": 1,  # 안정적
            "안정적 수익": 2,  # 중립적
            "고수익 추구": 3  # 공격적
        }
        score += goal_mapping.get(user_goal, 0)

        # 투자 경험 가중치
        experience_mapping = {
            "전혀 없음": 1,  # 안정적
            "초보 수준": 2,  # 중립적
            "경험이 많음": 3  # 공격적
        }
        score += experience_mapping.get(user_experience, 0)

        # 시장 변동 대응 가중치
        market_mapping = {
            "자산을 매도하여 손실을 최소화": 1,  # 안정적
            "시장 상황을 관망": 2,  # 중립적
            "추가 투자를 고려": 3  # 공격적
        }
        score += market_mapping.get(user_market, 0)

        # 리스크 허용 수준 가중치
        risk_mapping = {
            "리스크를 피하고 싶음": 1,  # 안정적
            "일부 리스크는 감수 가능": 2,  # 중립적
            "높은 리스크도 수용 가능": 3  # 공격적
        }
        score += risk_mapping.get(user_risk, 0)

        # 성향 결정
        if score <= 5:
            return "안정추구형"
        elif score <= 8:
            return "위험중립형"
        else:
            return "공격투자형"

    # 입력 값 확인 및 투자 성향 출력
    if (
            st.session_state.user_goal and
            st.session_state.user_experience and
            st.session_state.user_market and
            st.session_state.user_risk
    ):
        # 모든 입력이 완료된 경우 투자 성향 계산
        investment_type = calculate_investment_type(
            st.session_state.user_goal,
            st.session_state.user_experience,
            st.session_state.user_market,
            st.session_state.user_risk
        )
    else:
        # 입력이 완료되지 않은 경우
        investment_type = "?"

    st.subheader("📋 설문조사 결과")
    st.write("아래 결과를 확인해주세요:")

    col1, col2, col3 = st.columns(3)
    col1.metric("이름", st.session_state.user_name or "미입력")
    col2.metric("투자 성향", investment_type)
    col3.metric("투자 기간", st.session_state.user_horizon or "미선택")

    if st.session_state.user_risk and st.session_state.user_horizon:
        if st.button("포트폴리오 보기 🚀"):
            go_to_page("portfolio")

# 포트폴리오 계산 함수
def get_portfolio(risk, horizon):
    portfolios = {
        ("안정추구형", "6개월"): {"Equity": 10, "Fixed Income": 90},
        ("안정추구형", "2년"): {"SPY": 33, "GLD": 42, "VNQ": 0.3, "PAVE": 5.5, "SPTL": 19},
        ("위험중립형", "6개월"): {"Equity": 50, "Fixed Income": 50},
        ("위험중립형", "2년"): {"SPY": 33, "SCHD": 33, "SPYD": 18, "SPTL": 16},
        ("공격투자형", "6개월"): {"Equity": 70, "Fixed Income": 30},
        ("공격투자형", "2년"): {"SPY": 81, "SKYY": 0.6, "SMH": 4.9, "VWO": 4.7, "SPTL": 8.6},
    }
    return portfolios.get((risk, horizon), {"Equity": 50, "Fixed Income": 50})

# 포트폴리오 화면
def portfolio_page():
    st.title("📈 추천 포트폴리오")

    # 데이터 생성
    portfolio = get_portfolio(map_risk_level(st.session_state.user_risk), st.session_state.user_horizon)
    portfolio_df = pd.DataFrame(portfolio.items(), columns=["자산", "비율 (%)"])

    # 데이터 테이블
    st.subheader("📊 포트폴리오 구성표")
    st.dataframe(portfolio_df.style.background_gradient(cmap="coolwarm"), use_container_width=True)

    # 파이 차트
    st.subheader("📊 포트폴리오 비율 시각화")
    fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
    ax.pie(
        portfolio.values(),
        labels=portfolio.keys(),
        autopct="%1.1f%%",
        startangle=90,
        colors=cm.Paired.colors,
    )
    ax.set_title("Allocation", fontsize=14)
    st.pyplot(fig)

    # 돌아가기 버튼
    if st.button("🔙 설문조사로 돌아가기"):
        go_to_page("survey")

# 화면 렌더링
if st.session_state.page == "survey":
    survey_page()
elif st.session_state.page == "portfolio":
    portfolio_page()
