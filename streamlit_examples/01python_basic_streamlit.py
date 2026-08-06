# ============================================================
# 08. 파이썬 기초 - Streamlit 입문
# ============================================================
# Streamlit 은 파이썬 코드만으로 웹 앱(대시보드)을 만드는 라이브러리입니다.
# HTML/CSS/JavaScript 를 몰라도 되고, 위→아래로 실행되는 스크립트가 그대로 웹 화면이 됩니다.
# 이 프로젝트의 streamlit_*.py 파일들이 모두 이 방식으로 만들어졌습니다.
#
# ▶ 실행 방법 (터미널에서):
#     pip install streamlit
#     streamlit run streamlit_examples/01python_basic_streamlit.py
#
# 실행하면 브라우저가 자동으로 열립니다. 코드를 저장할 때마다 화면이 자동 갱신됩니다.
# (Jupyter 노트북에서는 st.* 명령이 동작하지 않으므로 반드시 streamlit run 으로 실행하세요.)
# ============================================================

import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 1. 페이지 기본 설정 (반드시 다른 st 명령보다 먼저 호출)
# ------------------------------------------------------------
st.set_page_config(page_title="Streamlit 입문", page_icon="🎈", layout="centered")

# ------------------------------------------------------------
# 2. 텍스트 출력 — 가장 기본
# ------------------------------------------------------------
st.title("🎈 Streamlit 입문")               # 큰 제목
st.header("1. 텍스트 출력")                  # 중간 제목
st.subheader("여러 가지 글쓰기 방법")         # 작은 제목

st.write("st.write() 는 거의 모든 것을 화면에 출력합니다. (숫자, 표, 그래프 등)")
st.markdown("**마크다운**도 사용할 수 있어요. `코드`, *기울임*, 목록 등")
st.info("정보 메시지")
st.success("성공 메시지")
st.warning("경고 메시지")
st.error("오류 메시지")

st.divider()  # 구분선

# ------------------------------------------------------------
# 3. 입력 위젯 — 사용자와 상호작용
# ------------------------------------------------------------
# 위젯은 사용자가 값을 바꾸면 스크립트가 '처음부터 다시 실행' 되면서
# 그 변수에 새 값이 담깁니다. 이것이 Streamlit 의 핵심 동작 방식입니다.
st.header("2. 입력 위젯")

name = st.text_input("이름을 입력하세요", "홍길동")     # 텍스트 입력
age = st.slider("나이", 0, 100, 25)                      # 슬라이더 (최소, 최대, 기본값)
city = st.selectbox("도시 선택", ["서울", "부산", "대구", "광주"])  # 드롭다운
agree = st.checkbox("동의합니다")                        # 체크박스

# 입력값을 즉시 화면에 반영
st.write(f"👤 {name} / {age}세 / {city} / 동의: {agree}")

st.divider()

# ------------------------------------------------------------
# 4. 버튼 — 클릭 시 특정 코드 실행
# ------------------------------------------------------------
st.header("3. 버튼")

# 버튼은 클릭된 그 순간의 실행에서만 True 를 반환한다
if st.button("인사하기"):
    st.write(f"안녕하세요, {name}님! 👋")

st.divider()

# ------------------------------------------------------------
# 5. 데이터 표시 — DataFrame 과 차트
# ------------------------------------------------------------
st.header("4. 데이터와 차트")

# 04편에서 배운 DataFrame 을 그대로 화면에 표시
df = pd.DataFrame({
    "company": ["SM", "JYP", "FNC", "Starship", "YG"],
    "count": [58, 56, 52, 44, 41],
})

st.subheader("표 (dataframe)")
st.dataframe(df, use_container_width=True)   # 정렬 가능한 인터랙티브 표

st.subheader("막대 차트 (bar_chart)")
# 인덱스를 company 로 두면 x축이 회사명이 된다
st.bar_chart(df.set_index("company"))

st.divider()

# ------------------------------------------------------------
# 6. 사이드바 — 옵션을 왼쪽에 모으기
# ------------------------------------------------------------
# st.sidebar.xxx 로 넣으면 화면 왼쪽 사이드바에 배치된다
st.sidebar.header("⚙️ 사이드바")
min_count = st.sidebar.slider("최소 인원 필터", 0, 60, 45)

# 필터링 (04편의 조건 필터) 후 결과 표시
filtered = df[df["count"] >= min_count]
st.write(f"인원 {min_count}명 이상인 소속사: {len(filtered)}개")
st.table(filtered)   # st.table 은 고정 크기 표

st.divider()

# ------------------------------------------------------------
# 7. 레이아웃 — columns 와 tabs
# ------------------------------------------------------------
st.header("5. 레이아웃")

# 화면을 좌우로 나누기
col1, col2 = st.columns(2)
col1.metric("총 소속사", f"{len(df)}개")
col2.metric("총 인원", f"{df['count'].sum()}명")

# 탭으로 내용 나누기
tab1, tab2 = st.tabs(["표 보기", "차트 보기"])
with tab1:
    st.dataframe(df, use_container_width=True)
with tab2:
    st.bar_chart(df.set_index("company"))

st.divider()

# ------------------------------------------------------------
# 8. 캐싱과 세션 상태 (심화 개념 맛보기)
# ------------------------------------------------------------
st.header("6. 캐싱과 세션 상태")

# @st.cache_data : 오래 걸리는 작업의 결과를 저장해두고 재사용 (성능 향상)
# 실제 프로젝트에서 CSV 로드/API 호출에 붙입니다.
@st.cache_data
def load_sample():
    """무거운 데이터 로드를 흉내낸 함수 (결과가 캐시됨)."""
    return pd.DataFrame({"x": range(5), "y": [v ** 2 for v in range(5)]})

st.line_chart(load_sample().set_index("x"))

# st.session_state : 위젯이 바뀌어 스크립트가 다시 실행돼도 값을 '기억' 하는 저장소
# (Streamlit 은 상호작용마다 전체를 재실행하므로, 누적 값은 여기에 보관)
if "click_count" not in st.session_state:
    st.session_state.click_count = 0   # 최초 1회 초기화

if st.button("카운트 증가"):
    st.session_state.click_count += 1

st.write("버튼을 누른 횟수:", st.session_state.click_count)

# ------------------------------------------------------------
# 정리
# ------------------------------------------------------------
# - st.title/header/write/markdown : 텍스트 출력
# - st.text_input/slider/selectbox/checkbox/button : 입력 위젯
# - st.dataframe/table/bar_chart/line_chart : 데이터·차트
# - st.sidebar / st.columns / st.tabs : 레이아웃
# - @st.cache_data : 결과 캐싱 (성능)
# - st.session_state : 재실행에도 값 유지
#
# 이제 streamlit_basic.py, streamlit_book_search.py,
# streamlit_netflix_dashboard.py 코드를 읽을 수 있습니다! 🎉
st.divider()
st.caption("이 파일은 학습용 예제입니다. streamlit run streamlit_examples/01python_basic_streamlit.py 로 실행하세요.")
