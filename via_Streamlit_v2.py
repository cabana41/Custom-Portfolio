import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
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

# 백테스트 데이터 로드
@st.cache
def load_backtest_data():
    """백테스트 데이터를 로드합니다."""
    file_path = "backtest_data.xlsx"
    if not os.path.exists(file_path):
        st.error("백테스트 결과 파일이 존재하지 않습니다.")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    backtest_data = pd.read_csv(file_path)
    return backtest_data, asset_data

def load_asset_data():
    """Asset 데이터를 로드합니다."""
    file_path = "asset_data.xlsx"
    if not os.path.exists(file_path):
        st.error("Asset 결과 파일이 존재하지 않습니다.")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    asset_data = pd.read_csv(file_path)
    return backtest_data, asset_data

# 데이터 로드
backtest_data = load_backtest_data()
asset_data = load_asset_data()

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

def get_etf_description():
    """ETF 설명을 반환합니다."""
    return {
        "SPY": "S&P 500 지수를 추종하는 ETF로, 미국 대형주에 투자. 안정성과 성장이 혼합된 포트폴리오의 기본 구성 요소로 적합",
        "GLD": "금 가격에 직접 투자하는 ETF. 포트폴리오의 헤지(위험 대비) 및 가치 저장 수단으로 자주 사용",
        "VNQ": "미국 리츠(REITs, 부동산 투자 신탁)에 투자. 부동산 시장의 수익에 접근할 수 있는 방법 제공",
        "PAVE": "미국 기반 인프라 관련 기업에 투자하는 ETF. 장기적인 경제 성장 테마에 적합",
        "SPTL": "미국 장기 국채를 추종하는 ETF. 안정적인 소득 및 변동성 완화에 도움",
        "SCHD": "미국 고배당 성장 주식에 투자. 안정적 배당 수익과 성장을 목표로 설계",
        "SPYD": "고배당 주식에 투자하는 ETF로, 수익률 중심의 투자자에게 적합",
        "SKYY": "클라우드 컴퓨팅 관련 기업에 투자하는 ETF. 기술 성장 테마에 적합",
        "SMH": "반도체 산업 관련 주식에 집중 투자하는 ETF. 기술 혁신의 중심 산업에 투자",
        "VWO": "신흥 시장(EM) 주식에 투자. 높은 성장 가능성을 가진 국가에 접근",
        "QQQ": "미국 Nasdaq 지수를 추종하는 ETF로, 미국 주식 중 기술주 중심 투자. S&P보다는 높은 변동성",
        "IEF": "미국 국채 7-10년물에 투자하는 ETF",
        "BIL": "미국 국채 1년 이하 단기물에 투자하는 ETF",
        "IAU": "금 가격에 직접 투자하는 ETF. 포트폴리오의 헤지(위험 대비) 및 가치 저장 수단으로 자주 사용",
        "HYG": "미국 하이일드 채권에 투자하는 ETF. 일반적인 국채 및 투자등급 회사채에 비해 높은 Yield 제공"
    }

def get_portfolio(risk, horizon):
    """포트폴리오와 ETF 설명을 함께 반환합니다."""
    portfolios = {
        ("안정추구형", "6개월"): {"SPY": 20, "IEF": 20, "BIL": 48, "QQQ": 10, "IAU": 2},
        ("안정추구형", "2년"): {"SPY": 33, "GLD": 42, "VNQ": 0.3, "PAVE": 5.5, "SPTL": 19},
        ("위험중립형", "6개월"): {"SPY": 40, "IEF": 35, "HYG": 10, "QQQ": 10, "IAU": 5},
        ("위험중립형", "2년"): {"SPY": 33, "SCHD": 33, "SPYD": 18, "SPTL": 16},
        ("공격투자형", "6개월"): {"SPY": 25, "IEF": 10, "HYG": 20, "QQQ": 40, "SMH": 5},
        ("공격투자형", "2년"): {"SPY": 81, "SKYY": 0.6, "SMH": 4.9, "VWO": 4.7, "SPTL": 8.6}
    }
    portfolio = portfolios.get((risk, horizon), {"Equity": 50, "Fixed Income": 50})

    # ETF 설명 추가
    etf_descriptions = get_etf_description()
    portfolio_with_desc = {}

    for asset, weight in portfolio.items():
        description = etf_descriptions.get(asset, "ETF가 아닌 일반 자산군입니다.")
        portfolio_with_desc[asset] = {"비중": weight, "설명": description}

    return portfolio, portfolio_with_desc

# 포트폴리오 페이지
def portfolio_page():
    st.title("📈 추천 포트폴리오")

    # 사용자 입력값
    risk = map_risk_level(st.session_state.user_risk)
    horizon = st.session_state.user_horizon

    # 포트폴리오 데이터
    portfolio = get_portfolio(risk, horizon)

    # 기대수익률 및 변동성 매핑
    asset_data = asset_data.set_index("Asset")  # Asset 열을 인덱스로 설정
    expected_returns = {asset: asset_data.loc[asset, "ExpectedReturn"] for asset in portfolio}
    volatilities = {asset: asset_data.loc[asset, "Volatility"] for asset in portfolio}

    # 포트폴리오 기대수익률 및 변동성 계산
    portfolio_return = sum(weight * expected_returns[asset] / 100 for asset, weight in portfolio.items())
    portfolio_volatility = sum(weight * volatilities[asset] / 100 for asset, weight in portfolio.items())

    # 포트폴리오 메타 정보 강조
    st.markdown(f"""
    ### 포트폴리오 기대수익률: **{portfolio_return:.2%}**
    ### 포트폴리오 변동성: **{portfolio_volatility:.2%}**
    """)

    # 포트폴리오 테이블 생성
    portfolio_data = {
        "자산": list(portfolio.keys()),
        "비중 (%)": list(portfolio.values()),
        "기대수익률 (%)": [expected_returns[asset] * 100 for asset in portfolio],
        "변동성 (%)": [volatilities[asset] * 100 for asset in portfolio]
    }
    portfolio_df = pd.DataFrame(portfolio_data)
    st.dataframe(portfolio_df)

    # 파이 차트
    st.subheader("📊 포트폴리오 비율")
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    ax.pie(
        portfolio.values(),
        labels=portfolio.keys(),
        autopct="%1.1f%%",
        startangle=90,
        colors=cm.Paired.colors
    )
    ax.set_title("포트폴리오 구성", fontsize=14)
    st.pyplot(fig)

    # 다음 페이지로 이동
    if st.button("📄 백테스트 결과 보기"):
        go_to_page("backtest")

    # 돌아가기 버튼
    if st.button("🔙 설문조사로 돌아가기"):
        go_to_page("survey")
        
# 백테스트 결과 페이지
def backtest_page():
    st.title("📉 백테스트 결과")

    # 누적 수익률 그래프
    st.write("### 누적 수익률")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(backtest_data["Date"], backtest_data["Cumulative Return"], label="누적 수익률", color="blue")
    ax.set_title("누적 수익률", fontsize=16)
    ax.set_xlabel("날짜", fontsize=12)
    ax.set_ylabel("수익률 (%)", fontsize=12)
    ax.legend(fontsize=12)
    st.pyplot(fig)

    # MDD 그래프
    st.write("### MDD (Maximum Drawdown)")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(backtest_data["Date"], backtest_data["Drawdown"], label="MDD (최대 손실)", color="red")
    ax.fill_between(backtest_data["Date"], backtest_data["Drawdown"], color="red", alpha=0.2, label="Drawdown 영역")
    ax.set_title("MDD (Maximum Drawdown)", fontsize=16)
    ax.set_xlabel("날짜", fontsize=12)
    ax.set_ylabel("손실 (%)", fontsize=12)
    ax.legend(fontsize=12)
    st.pyplot(fig)

    # 돌아가기 버튼
    if st.button("🔙 포트폴리오로 돌아가기"):
        go_to_page("portfolio")

# 화면 렌더링
if st.session_state.page == "survey":
    survey_page()
elif st.session_state.page == "portfolio":
    portfolio_page()
elif st.session_state.page == "backtest":
    backtest_page()
