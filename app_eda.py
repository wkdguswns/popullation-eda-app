import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    class Home:
        def __init__(self, login_page, register_page, findpw_page):
            st.title("🏠 Home")
            if st.session_state.get("logged_in"):
                st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

            # 데이터 소개
            st.markdown("""
                ---
                **지역별 인구 추이 데이터셋 소개**  
                - 출처: [KOSIS 지역통계](https://kosis.kr)  
                - 설명: 연도별 각 지역(시·도)의 인구, 출생아 수, 사망자 수 등을 포함한 데이터  
                - 주요 변수:
                - `연도`: 기준 연도  
                - `지역`: 시·도 이름  
                - `인구`: 해당 연도 인구 수  
                - `출생아수(명)`, `사망자수(명)`: 해당 연도 출생 및 사망 수  
                - 그 외 기타 통계
            """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
    def __init__(self):
        st.title("📊 지역별 인구 분석 EDA")

        uploaded_file = st.file_uploader("population_trends.csv 파일을 업로드하세요", type="csv")
        if uploaded_file is None:
            st.info("분석을 시작하려면 population_trends.csv 파일을 업로드하세요.")
            return

        df = pd.read_csv(uploaded_file)

        # 세종 지역 '-' 값을 0으로 치환
        df.loc[df['지역'] == '세종'] = df.loc[df['지역'] == '세종'].replace('-', 0)

        # 필요한 열 숫자로 변환
        cols_to_convert = ['인구', '출생아수(명)', '사망자수(명)']
        for col in cols_to_convert:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # 연도 정수형으로 변환
        df['연도'] = pd.to_numeric(df['연도'], errors='coerce').astype(int)

        tabs = st.tabs([
            "기초 통계", "연도별 추이", "지역별 분석", "변화량 분석", "시각화"
        ])

        # 1. 기초 통계
        with tabs[0]:  # "기초 통계" 탭
            st.header("📌 Basic Statistics & Preprocessing")

            uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file)

                # '세종' 지역의 모든 열에서 '-' → 0으로 치환
                df.loc[df['지역'] == '세종'] = df.loc[df['지역'] == '세종'].replace('-', 0)

                # 숫자형 변환 대상 열
                cols_to_convert = ['인구', '출생아수(명)', '사망자수(명)']
                for col in cols_to_convert:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

                # 연도 정수화
                df['연도'] = pd.to_numeric(df['연도'], errors='coerce').astype(int)

                st.subheader("1. DataFrame Info (`df.info()`)")
                buffer = io.StringIO()
                df.info(buf=buffer)
                st.text(buffer.getvalue())

                st.subheader("2. Descriptive Statistics (`df.describe()`)")
                st.dataframe(df.describe())

                st.subheader("3. Sample Data")
                st.dataframe(df.head())
            else:
                st.info("Please upload the population_trends.csv file.")

        # 2. 연도별 추이
        with tabs[1]:  # "연도별 추이" 탭
            st.header("📈 Nationwide Population Trend")

            if uploaded_file is not None:
                df_national = df[df['지역'] == '전국'].sort_values('연도')

                # 최근 3년 평균 출생아수 및 사망자수
                recent = df_national.tail(3)
                birth_avg = recent['출생아수(명)'].mean()
                death_avg = recent['사망자수(명)'].mean()
                net_change = birth_avg - death_avg

                # 2035년 인구 예측
                last_year = df_national['연도'].max()
                last_pop = df_national['인구'].iloc[-1]
                projected_year = 2035
                years_to_project = projected_year - last_year
                projected_pop = int(last_pop + net_change * years_to_project)

                # 연도 및 인구 리스트
                years = df_national['연도'].tolist() + [projected_year]
                pops = df_national['인구'].tolist() + [projected_pop]

                # 그래프 그리기
                fig, ax = plt.subplots()
                ax.plot(years[:-1], pops[:-1], marker='o', label='Actual')
                ax.plot(years[-2:], pops[-2:], linestyle='--', color='red', marker='x', label='Projected')
                ax.set_title("Population Trend")
                ax.set_xlabel("Year")
                ax.set_ylabel("Population")
                ax.legend()
                st.pyplot(fig)

                st.markdown(f"""
                > **2035년 예측 인구:** 약 {projected_pop:,}명  
                > 최근 3년간 평균 출생자: {birth_avg:,.0f}, 평균 사망자: {death_avg:,.0f} → 연간 순증가 {net_change:,.0f}
                """)
            else:
                st.info("Please upload the population_trends.csv file to view the graph.")

        # 3. 지역별 분석
        with tabs[2]:  
            st.header("📊 Regional Population Change (Last 5 Years)")

            if uploaded_file is not None:
                latest_years = sorted(df['연도'].unique())[-5:]
                recent_df = df[df['연도'].isin(latest_years) & (df['지역'] != '전국')]

                # 지역-연도 pivot → 변화량 계산
                pivot_df = recent_df.pivot(index='지역', columns='연도', values='인구')
                pivot_df = pivot_df.dropna()
                pivot_df['Change'] = pivot_df[latest_years[-1]] - pivot_df[latest_years[0]]
                pivot_df['Rate (%)'] = (pivot_df['Change'] / pivot_df[latest_years[0]]) * 100

                # 한글 → 영어 지역명 맵핑
                region_en = {
                    '서울': 'Seoul', '부산': 'Busan', '대구': 'Daegu', '인천': 'Incheon',
                    '광주': 'Gwangju', '대전': 'Daejeon', '울산': 'Ulsan', '세종': 'Sejong',
                    '경기': 'Gyeonggi', '강원': 'Gangwon', '충북': 'Chungbuk', '충남': 'Chungnam',
                    '전북': 'Jeonbuk', '전남': 'Jeonnam', '경북': 'Gyeongbuk', '경남': 'Gyeongnam',
                    '제주': 'Jeju'
                }
                pivot_df = pivot_df.rename(index=region_en)
                pivot_df = pivot_df.sort_values('Change', ascending=False)

                # 수평 막대그래프 (변화량)
                st.subheader("Change in Population (Last 5 Years, Unit: Thousand)")
                fig1, ax1 = plt.subplots(figsize=(8, 6))
                sns.barplot(x=pivot_df['Change'] / 1000, y=pivot_df.index, ax=ax1, palette="Blues_d")
                for i, v in enumerate(pivot_df['Change'] / 1000):
                    ax1.text(v, i, f"{v:.1f}", color='black', va='center')
                ax1.set_xlabel("Change (thousand)")
                ax1.set_ylabel("Region")
                ax1.set_title("Population Change by Region")
                st.pyplot(fig1)

                # 변화율 그래프
                st.subheader("Change Rate Compared to 5 Years Ago (%)")
                fig2, ax2 = plt.subplots(figsize=(8, 6))
                sns.barplot(x=pivot_df['Rate (%)'], y=pivot_df.index, ax=ax2, palette="Greens_d")
                for i, v in enumerate(pivot_df['Rate (%)']):
                    ax2.text(v, i, f"{v:.1f}%", color='black', va='center')
                ax2.set_xlabel("Change Rate (%)")
                ax2.set_ylabel("Region")
                ax2.set_title("Population Change Rate by Region")
                st.pyplot(fig2)

                st.markdown("""
                > **해석:** 상단 그래프는 최근 5년간 지역별 인구 순증감량을 나타내며,  
                > 하단 그래프는 기준 연도 대비 인구 증가율을 시각화한 것입니다.  
                > 이 그래프들을 통해 특정 지역의 인구 유입 및 유출 경향을 비교 분석할 수 있습니다.
                """)
        # 4. 변화량 분석
        with tabs[3]:  # 변화량 분석
            st.header("📉 Top 100 Population Changes by Region-Year")

            if uploaded_file is not None:
                diff_df = df[df['지역'] != '전국'].sort_values(['지역', '연도'])
                diff_df['증감'] = diff_df.groupby('지역')['인구'].diff()

                top100 = diff_df.dropna().sort_values('증감', ascending=False).head(100).copy()
                top100['증감'] = top100['증감'].astype(int)

                # 천단위 콤마
                top100['증감'] = top100['증감'].map('{:,}'.format)

                st.dataframe(
                    top100.style.background_gradient(
                        subset=['증감'], cmap='RdBu', axis=0, low=0.5, high=0.5
                    ).format({'증감': lambda x: f"{x}"})
                )

                st.markdown("""
                > **해석:**  
                > 연도별로 각 지역의 인구 증가 또는 감소 수치를 계산하여 상위 100개 사례를 추출했습니다.  
                > 배경색은 증감 방향을 시각적으로 강조하며, 빨강(감소), 파랑(증가)을 나타냅니다.
                """)

        # 5. 시각화
        with tabs[4]:  # 시각화
            st.header("🗺 Stacked Area Chart of Regional Population")

            if uploaded_file is not None:
                pivot = df[df['지역'] != '전국'].pivot(index='연도', columns='지역', values='인구')
                pivot = pivot.rename(columns=region_en)
                pivot = pivot.fillna(0).astype(int)

                fig, ax = plt.subplots(figsize=(12, 6))
                pivot.plot.area(ax=ax, colormap='tab20')
                ax.set_title("Regional Population by Year (Stacked Area)")
                ax.set_xlabel("Year")
                ax.set_ylabel("Population")
                ax.legend(title="Region", bbox_to_anchor=(1.05, 1), loc='upper left')
                st.pyplot(fig)

                st.markdown("""
                > **해석:**  
                > 이 누적 영역 그래프는 연도별로 지역 간 인구 분포를 시각화한 것입니다.  
                > 면적이 넓은 지역은 전체 인구 비중이 크며, 면적의 기울기 변화로 인구 추세도 파악할 수 있습니다.
                """)


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()