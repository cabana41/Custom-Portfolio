import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import cm

st.set_page_config(layout="wide")
# 초기 화면 설정
if "page" not in st.session_state:
    st.session_state.page = "survey"

# 화면 전환 함수
def go_to_page(page_name):
    st.session_state.page = page_name

# 위험성향 스코어링 함수
def map_risk_level_by_score(score):
    if score <= 5:
        return "안정추구형"
    elif score <= 8:
        return "위험중립형"
    else:
        return "공격투자형"

# 투자 성향 점수를 기반으로 리스크 레벨 계산
def calculate_risk_score(user_goal, user_experience, user_market, user_risk):
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
        "자산을 매도하여 손실 최소화": 1,  # 안정적
        "시장 상황을 관망": 2,  # 중립적
        "추가 투자를 고려": 3  # 공격적
    }
    score += market_mapping.get(user_market, 0)

    # 리스크 허용 수준 가중치
    risk_mapping = {
        "리스크를 피하고 싶음": 1,  # 안정적
        "일부 리스크 감수 가능": 2,  # 중립적
        "높은 리스크도 수용 가능": 3  # 공격적
    }
    score += risk_mapping.get(user_risk, 0)

    return score

# 데이터 로드
@st.cache_data
def load_backtest_data(risk, horizon):
    """백테스트 데이터를 로드합니다."""
    
    if risk=="안정추구형" and horizon=="6개월":
        file_path = "back_data_단기_RA.csv"
    elif risk=="위험중립형" and horizon=="6개월":
        file_path = "back_data_단기_RN.csv"
    elif risk=="공격투자형" and horizon=="6개월":
        file_path = "back_data_단기_RT.csv"
    elif risk=="안정추구형" and horizon=="2년":
        file_path = "back_data_장기_RA.csv"
    elif risk=="위험중립형" and horizon=="2년":
        file_path = "back_data_장기_RN.csv"
    else:
        file_path = "back_data_장기_RT.csv"

    if not os.path.exists(file_path):
        st.error("백테스트 결과 파일이 존재하지 않습니다.")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    backtest_data = pd.read_csv(file_path)
    backtest_data["Date"] = pd.to_datetime(backtest_data["Date"])
    return backtest_data

def load_asset_data(horizon):
    """Asset 데이터를 로드합니다."""
    
    if horizon=="6개월":
        file_path = "asset_data_단기.csv"
    else:
        file_path = "asset_data_장기.csv"

    if not os.path.exists(file_path):
        st.error("Asset 결과 파일이 존재하지 않습니다.")
        return pd.DataFrame()  # 빈 데이터프레임 반환
    asset_data = pd.read_csv(file_path)
    return asset_data

# 설문조사 화면
def survey_page():
    st.markdown("""
    <style>
    .stSelectbox, .stTextInput {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("✨ 맞춤형 포트폴리오 설계")

    with st.sidebar:
        st.header("📝 설문조사")
        st.session_state.user_name = st.text_input("이름", st.session_state.get("user_name", ""))
        st.session_state.user_gender = st.selectbox(
        "성별",
        ["", "남성", "여성"],
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
            ["", "자산을 매도하여 손실 최소화", "시장 상황을 관망", "추가 투자를 고려"],
            index=0 if "user_market" not in st.session_state else ["", "자산을 매도하여 손실 최소화", "시장 상황을 관망", "추가 투자를 고려"].index(
                st.session_state.user_market)
        )
        st.session_state.user_risk = st.selectbox(
            "리스크 허용 수준에 대해 평가해주세요.",
            ["", "리스크를 피하고 싶음", "일부 리스크 감수 가능", "높은 리스크도 수용 가능"],
            index=0 if "user_risk" not in st.session_state else ["", "리스크를 피하고 싶음", "일부 리스크 감수 가능", "높은 리스크도 수용 가능"].index(
                st.session_state.user_risk)
        )
        st.session_state.user_horizon = st.selectbox(
            "당신이 생각하는 적정 투자기간은 어느정도인가요?",
            ["", "6개월", "2년"],
            index=0 if "user_horizon" not in st.session_state else ["", "6개월", "2년"].index(
                st.session_state.user_horizon)
        )

    # 입력 값 확인 및 리스크 레벨 결정
    if (
            st.session_state.user_goal and
            st.session_state.user_experience and
            st.session_state.user_market and
            st.session_state.user_risk
    ):
        # 모든 입력값이 있을 경우 점수를 계산
        total_score = calculate_risk_score(
            st.session_state.user_goal,
            st.session_state.user_experience,
            st.session_state.user_market,
            st.session_state.user_risk
        )
        # 점수 기반 리스크 레벨 매핑
        investment_type = map_risk_level_by_score(total_score)
    else:
        # 입력이 완료되지 않은 경우
        investment_type = "?"

    st.subheader("📋 설문조사 결과")
    st.write("아래 결과를 확인해주세요:")
    col1, col2, col3 = st.columns(3)
    col1.metric("이름:", st.session_state.user_name or "**미입력**")
    col2.metric("투자 성향:", investment_type)
    col3.metric("투자 기간:", st.session_state.user_horizon or "**미선택**")

    # 다음 페이지로
    if st.button("포트폴리오 보기 🚀"):
        if investment_type!="?" and st.session_state.user_horizon:
            go_to_page("portfolio")
        else:
            st.warning("모든 설문을 완료해주세요.")

    # 버튼 아래에 메시지 추가
    st.markdown("<small>버튼을 더블클릭해주세요</small>", unsafe_allow_html=True)
            
def get_etf_description():
    """ETF 설명을 반환합니다."""
    return {
        "SPY": "S&P 500 지수를 추종하는 ETF로, 미국 대형주에 투자. 포트폴리오의 기본 구성 요소로 적합",
        "VNQ": "미국 리츠(REITs, 부동산 투자 신탁)에 투자. 부동산 시장의 수익에 접근할 수 있는 방법 제공",
        "PAVE": "미국 기반 인프라 관련 기업에 투자하는 ETF. 장기적인 경제 성장 테마에 적합",
        "SCHD": "미국 고배당 성장 주식에 투자. 안정적 배당 수익과 성장을 목표로 설계",
        "SPYD": "고배당 주식에 투자하는 ETF로, 수익률 중심의 투자자에게 적합",
        "SKYY": "클라우드 컴퓨팅 관련 기업에 투자하는 ETF. 기술 성장 테마에 적합",
        "SMH": "반도체 산업 관련 주식에 집중 투자하는 ETF. 기술 혁신의 중심 산업에 투자",
        "VWO": "신흥 시장(EM) 주식에 투자. 높은 성장 가능성을 가진 국가에 접근",
        "QQQ": "미국 Nasdaq 지수를 추종하는 ETF로, 미국 주식 중 기술주 중심 투자",
        "IEF": "미국 국채 7-10년물에 투자하는 ETF",
        "BIL": "미국 국채 1년 이하 단기물에 투자하는 ETF",
        "IAU": "금 가격에 직접 투자하는 ETF. 포트폴리오의 헤지(위험 대비) 및 가치 저장 수단으로 자주 사용",
        "HYG": "미국 하이일드 채권에 투자하는 ETF. 일반적인 국채 및 투자등급 회사채에 비해 높은 Yield 제공"
    }

def get_portfolio(risk, horizon):
    """포트폴리오와 ETF 설명을 함께 반환합니다."""
    portfolios = {
        ("안정추구형", "6개월"): {"SPY": 20, "IEF": 20, "BIL": 40, "QQQ": 15, "IAU": 5},
        ("안정추구형", "2년"): {"SPY": 25, "IAU": 5, "SCHD": 20, "SPYD": 15, "IEF": 30},
        ("위험중립형", "6개월"): {"SPY": 15, "BIL": 40, "HYG": 20, "QQQ": 20, "IAU": 15},
        ("위험중립형", "2년"): {"SPY": 30, "IAU": 25, "VNQ": 5, "PAVE": 30, "IEF": 10},
        ("공격투자형", "6개월"): {"SPY": 10, "BIL": 15, "HYG": 25, "QQQ": 30, "SMH": 20},
        ("공격투자형", "2년"): {"SPY": 30, "SKYY": 5, "SMH": 20, "VWO": 5, "IEF": 40}
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

    total_score = calculate_risk_score(
    st.session_state.user_goal,
    st.session_state.user_experience,
    st.session_state.user_market,
    st.session_state.user_risk
    )

    # 사용자 입력값
    risk = map_risk_level_by_score(total_score)
    horizon = st.session_state.user_horizon

    # 포트폴리오 데이터
    portfolio, portfolio_with_desc = get_portfolio(risk, horizon)

    # Asset 데이터 로드
    asset_data = load_asset_data(horizon)
    if asset_data.empty:
        st.error("Asset 데이터를 불러올 수 없습니다.")
        return

    # 기대수익률 및 변동성 매핑
    asset_data = asset_data.set_index("Asset")  # Asset 열을 인덱스로 설정
    expected_returns = {}
    volatilities = {}

    assets = list(portfolio.keys())
    for asset in assets:
        if asset in asset_data.index:
            expected_returns[asset] = asset_data.loc[asset, "ExpectedReturn"]
            volatilities[asset] = asset_data.loc[asset, "Volatility"]
        else:
            # Handle the case where asset is not in asset_data.index
            st.warning(f"Asset 데이터에 {asset} 정보가 없습니다.")
            expected_returns[asset] = 0  # 기본값 설정
            volatilities[asset] = 0  # 기본값 설정

    # 포트폴리오 기대수익률 및 변동성 계산
    portfolio_return = sum(weight * expected_returns[asset] / 100 for asset, weight in portfolio.items())
    portfolio_volatility = sum(weight * volatilities[asset] / 100 for asset, weight in portfolio.items())

    # 포트폴리오 메타 정보 강조
    col1, col2 = st.columns(2)
    with col1:
        st.metric("포트폴리오 기대수익률", f"{portfolio_return:.2%}")
    with col2:
        st.metric("포트폴리오 변동성", f"{portfolio_volatility:.2%}")

    # 해외 ETF 매핑 데이터
    global_etf_mapping = {
        "SPY": "SPDR S&P500",
        "VNQ": "Vanguard Real Estate Index Fund",
        "PAVE": "Global X U.S. Infrastructure Development",
        "SCHD": "Schwab US Dividend Equity",
        "SPYD": "SPDR Portfolio S&P500 High Dividend",
        "SKYY": "First Trust Cloud Computing",
        "SMH": "VanEck Semiconductor",
        "VWO": "Vanguard FTSE Emerging Markets",
        "QQQ": "Invesco QQQ Trust, Series1",
        "IEF": "iShares 7-10 Year Treasury Bond",
        "BIL": "SPDR Lehman 1-3 Month T-Bill",
        "IAU": "iShares Gold Trust",
        "HYG": "iShares iBoxx $ High Yield Corporate Bond"
    }
    
    # 국내 ETF 매핑 데이터
    domestic_etf_mapping = {
        "SPY": "KOSEF 미국S&P500(H) (449780)",
        "VNQ": "KODEX 미국부동산리츠(H) (352560)",
        "PAVE": "KODEX 미국AI전력핵심인프라 (487230)",
        "SCHD": "TIGER 미국배당다우존스 (458730)",
        "SPYD": "KODEX 미국S&P500배당귀족커버드콜(합성H) (276970)",
        "SKYY": "TIGER 글로벌 클라우드컴퓨팅 INDXX (371450)",
        "SMH": "TIGER 미국 필라델피아 반도체 나스닥 (381180)",
        "VWO": "KODEX MSCI EM선물(H) (291890)",
        "QQQ": "KOSEF 미국나스닥100(H) (453080)",
        "IEF": "TIGER 미국채10년선물 (305080)",
        "BIL": "KOSEF 통안채1년 (122260)",
        "IAU": "KODEX 골드선물(H) (132030)",
        "HYG": "KODEX iShares미국하이일드액티브 (468380)"
    }
    
    # 데이터프레임 생성
    portfolio_data = {
        "자산": list(portfolio.keys()),
        "ETF 이름": [global_etf_mapping.get(asset, "N/A") for asset in portfolio],
        "국내 ETF 이름": [domestic_etf_mapping.get(asset, "N/A") for asset in portfolio],
        "비중": list(portfolio.values()),
        "기대수익률": [expected_returns[asset] * 100 for asset in portfolio],
        "변동성": [volatilities[asset] * 100 for asset in portfolio]
    }

    st.subheader("📊 추천 포트폴리오 구성")
    portfolio_df = pd.DataFrame(portfolio_data).reset_index(drop=True)
    
    st.dataframe(
    portfolio_df.style.format({
        "비중": "{:.2f}%",
        "기대수익률": "{:.2f}%",
        "변동성": "{:.2f}%"
    }).background_gradient(cmap="YlGnBu", subset=["비중"]),
    use_container_width=True
    )
    st.caption("미국 국고채 1년물은 국내 통안채 1년물로 대체")

    st.subheader("📚 ETF 상세 설명")
    for asset, info in portfolio_with_desc.items():
        with st.expander(f"{asset} - {global_etf_mapping.get(asset, 'N/A')}"):
            st.write(f"**비중:** {info['비중']}%")
            st.write(f"**설명:** {info['설명']}")
            domestic_etf = domestic_etf_mapping.get(asset, 'N/A')
            st.write(f"**국내 대체 ETF:** {domestic_etf}")
            
            global_etf_ticker_url = f"https://etfdb.com/etf/{asset}/#etf-ticker-profile"
            st.markdown(
            f"""
            <a href="{global_etf_ticker_url}" target="_blank" style="text-decoration:none;">
                <button style="
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    font-size: 14px;
                    margin: 4px 2px;
                    cursor: pointer;
                    border-radius: 8px;">
                    {asset} ETF 상세정보 보러가기
                </button>
            </a>
            """,
            unsafe_allow_html=True
        )

            if domestic_etf != 'N/A':
                domestic_etf_ticker_url = f"https://finance.naver.com/item/main.naver?code={domestic_etf[-7:-1]}"
                st.markdown(
                    f"""
                    <a href="{domestic_etf_ticker_url}" target="_blank" style="text-decoration:none;">
                        <button style="
                            background-color: #008CBA;
                            color: white;
                            border: none;
                            padding: 10px 20px;
                            text-align: center;
                            text-decoration: none;
                            display: inline-block;
                            font-size: 14px;
                            margin: 4px 2px;
                            cursor: pointer;
                            border-radius: 8px;">
                            {domestic_etf} ETF 상세정보 보러가기
                        </button>
                    </a>
                    """,
                    unsafe_allow_html=True
                )

    def create_portfolio_chart(portfolio):
        labels = list(portfolio.keys())
        values = list(portfolio.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values,
            textinfo='label+percent',
            insidetextorientation='radial',
            hole=.3,
            textfont=dict(size=16)
        )])
        
        fig.update_layout(
            showlegend=False,
            width=800,
            height=500
        )
        
        return fig

    st.subheader("🍰 포트폴리오 구성 비율")
    # portfolio_page() 함수 내에서 차트 생성 및 표시
    portfolio_pie_chart = create_portfolio_chart(portfolio)
    st.plotly_chart(portfolio_pie_chart, use_container_width=True)
    
    # 다음 페이지로 이동
    if st.button("📄 백테스트 결과 보기"):
        go_to_page("backtest")

    # 돌아가기 버튼
    if st.button("🔙 설문조사로 돌아가기"):
        go_to_page("survey")

    # 버튼 아래에 메시지 추가
    st.markdown("<small>버튼을 더블클릭해주세요</small>", unsafe_allow_html=True)

# 백테스트 결과 페이지
def backtest_page():
    st.title("📊 백테스트 결과")

    total_score = calculate_risk_score(
    st.session_state.user_goal,
    st.session_state.user_experience,
    st.session_state.user_market,
    st.session_state.user_risk
    )

    # 사용자 입력값
    risk = map_risk_level_by_score(total_score)
    horizon = st.session_state.user_horizon    

    # 백테스트 데이터 로드
    backtest_data = load_backtest_data(risk, horizon)
    if backtest_data.empty:
        st.error("백테스트 데이터를 불러올 수 없습니다.")
        return

    # 최종 수익률 계산
    initial_nav = backtest_data["NAV"].iloc[0]
    final_nav = backtest_data["NAV"].iloc[-1]
    cumulative_return = np.log(final_nav / initial_nav) 
    
    # MDD 계산
    max_drawdown = backtest_data["MDD"].min()

    # 최종 수익률 및 MDD 강조
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("누적 수익률", f"{cumulative_return:.2%}")
    with col2:
        st.metric("최대 낙폭(MDD)", f"{max_drawdown:.2%}")

    # 기간별 수익률 계산
    st.subheader("📅 기간별 수익률")
    backtest_data['Return'] = np.log(backtest_data['NAV'] / backtest_data['NAV'].shift(1))  # 일간 수익률 계산
    backtest_data['Date'] = pd.to_datetime(backtest_data['Date'])  # 날짜 형식 변환

    # 기간 설정
    date_ranges = [
        ("1개월", -30),
        ("3개월", -90),
        ("6개월", -180),
        ("1년", -365),
    ]

    period_returns = []
    for label, days in date_ranges:
        try:
            if len(backtest_data) > abs(days):  # 데이터가 충분히 있는지 확인
                start_date = backtest_data['Date'].iloc[days]
                start_nav = backtest_data[backtest_data['Date'] == start_date]['NAV'].iloc[0]
                period_return = np.log(final_nav / start_nav)  # 로그 수익률 계산
                period_returns.append({"기간": label, "기간 수익률": period_return})  # 숫자로 저장
            else:
                period_returns.append({"기간": label, "기간 수익률": None})  # None으로 저장
        except IndexError:
            period_returns.append({"기간": label, "기간 수익률": None})  # None으로 저장
    
    # DataFrame 생성
    period_return_df = pd.DataFrame(period_returns).reset_index(drop=True)
    
    # None 값 처리 및 포맷팅
    def format_returns(value):
        if pd.isna(value):  # None 처리
            return "데이터 부족"
        return f"{value:.2%}"  # 숫자 값에만 포맷 적용
    
    # DataFrame 표시
    st.dataframe(
        period_return_df.style.format({"기간 수익률": format_returns}).set_caption("기간별 누적 수익률"),
        use_container_width=True
    )

    # NAV 그래프 (다크 테마)
    st.subheader("📈 누적 NAV 추세")
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=backtest_data['Date'], 
        y=backtest_data['NAV'], 
        mode='lines+markers',
        name='NAV',
        line=dict(color='green', width=2),
        hovertemplate="날짜: %{x}<br>NAV: %{y:.2f}"
    ))
    
    fig1.update_layout(
        title='누적 NAV (수익률)',
        xaxis=dict(
            title="날짜",
            showgrid=True,
            zeroline=False,
            tickformat="%Y-%m-%d",
            tickangle=45,
        ),
        yaxis=dict(
            title="NAV",
            showgrid=True,
            zeroline=False,
        ),
        hovermode='x unified',
        template="plotly_white"  # 다크 테마
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # MDD 그래프 (다크 테마)
    st.subheader("📉 최대 낙폭(MDD)")
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=backtest_data['Date'], 
        y=backtest_data['MDD'], 
        mode='lines+markers',
        name='MDD',
        line=dict(color='red', width=2, dash="dash"),
        fill='tozeroy',
        fillcolor='rgba(255, 0, 0, 0.2)',
        hovertemplate="날짜: %{x}<br>MDD: %{y:.2%}"
    ))
    
    fig2.update_layout(
        title='MDD (Maximum Drawdown)',
        xaxis=dict(
            title="날짜",
            showgrid=True,
            zeroline=False,
            tickformat="%Y-%m-%d",
            tickangle=45,
        ),
        yaxis=dict(
            title="Drawdown",
            showgrid=True,
            zeroline=False,
        ),
        hovermode='x unified',
        template="plotly_white"  # 다크 테마
    )
    
    # Streamlit에 Plotly 차트 렌더링
    st.plotly_chart(fig2, use_container_width=False) 

    # 돌아가기 버튼
    if st.button("🔙 추천 포트폴리오로 돌아가기"):
        go_to_page("portfolio")

    # 돌아가기 버튼
    if st.button("🔙 설문조사로 돌아가기"):
        go_to_page("survey")

    # 버튼 아래에 메시지 추가
    st.markdown("<small>버튼을 더블클릭해주세요</small>", unsafe_allow_html=True)

# 화면 렌더링
if st.session_state.page == "survey":
    survey_page()
elif st.session_state.page == "portfolio":
    portfolio_page()
elif st.session_state.page == "backtest":
    backtest_page()
