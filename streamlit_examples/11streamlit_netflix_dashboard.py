# streamlit run streamlit_examples/11streamlit_netflix_dashboard.py
#
# 넷플릭스 콘텐츠 인터랙티브 대시보드
# - 기본 데이터: data/netflix_titles.csv
# - 사이드바에서 유형/연도/국가로 필터링하고 결과를 차트와 표로 확인
# - CSV 업로드 기능으로 다른 데이터셋도 분석 가능

import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (streamlit_examples 의 상위)
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(page_title="넷플릭스 대시보드", page_icon="🎬", layout="wide")
st.title("🎬 넷플릭스 콘텐츠 대시보드")

DATA_PATH = BASE_DIR / "data" / "netflix_titles.csv"


@st.cache_data  # 동일 입력이면 재계산하지 않고 캐시된 결과 재사용 (성능 향상)
def load_data(path_or_buffer):
    """CSV를 읽어 전처리한 DataFrame을 반환한다.

    Parameters:
        path_or_buffer: 파일 경로 문자열 또는 업로드된 파일 객체
    Returns:
        pd.DataFrame: 전처리 완료된 데이터
    """
    df = pd.read_csv(path_or_buffer)

    # date_added를 날짜형으로 변환하고 추가 연도 컬럼 생성
    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(
            df["date_added"].astype(str).str.strip(), errors="coerce"
        )
        df["year_added"] = df["date_added"].dt.year

    # country 결측 처리
    if "country" in df.columns:
        df["country"] = df["country"].fillna("Unknown")

    return df


# --- 데이터 소스 선택: 업로드 파일이 있으면 우선 사용 ---
st.sidebar.header("데이터 소스")
uploaded = st.sidebar.file_uploader("CSV 업로드 (선택)", type=["csv"])

if uploaded is not None:
    df = load_data(uploaded)
    st.sidebar.success("업로드한 파일을 사용합니다.")
elif os.path.exists(DATA_PATH):
    df = load_data(DATA_PATH)
    st.sidebar.info(f"기본 데이터 사용: {DATA_PATH}")
else:
    st.error(f"기본 데이터 파일이 없습니다: {DATA_PATH}\n좌측에서 CSV를 업로드해주세요.")
    st.stop()  # 데이터가 없으면 이후 코드 실행 중단


# --- 사이드바 필터 ---
st.sidebar.header("필터")

# 유형 필터 (Movie / TV Show)
if "type" in df.columns:
    types = st.sidebar.multiselect(
        "유형", options=sorted(df["type"].dropna().unique()),
        default=list(df["type"].dropna().unique()),
    )
    df = df[df["type"].isin(types)]

# 연도 슬라이더
if "year_added" in df.columns and df["year_added"].notna().any():
    min_y = int(df["year_added"].min())
    max_y = int(df["year_added"].max())
    year_range = st.sidebar.slider("추가 연도 범위", min_y, max_y, (min_y, max_y))
    df = df[df["year_added"].between(*year_range)]

# 국가 텍스트 검색
if "country" in df.columns:
    country_kw = st.sidebar.text_input("국가 검색어", "")
    if country_kw:
        df = df[df["country"].str.contains(country_kw, case=False, na=False)]


# --- 상단 요약 지표 ---
col1, col2, col3 = st.columns(3)
col1.metric("전체 콘텐츠", f"{len(df):,}개")
if "type" in df.columns:
    col2.metric("영화", f"{(df['type'] == 'Movie').sum():,}개")
    col3.metric("TV 프로그램", f"{(df['type'] == 'TV Show').sum():,}개")


# --- 차트 영역 ---
tab1, tab2, tab3 = st.tabs(["연도별 추이", "인기 장르", "원본 데이터"])

with tab1:
    if "year_added" in df.columns and df["year_added"].notna().any():
        yearly = df.dropna(subset=["year_added"]).groupby("year_added").size()
        st.subheader("연도별 추가 콘텐츠 수")
        st.line_chart(yearly)  # Streamlit 내장 차트 (별도 matplotlib 불필요)
    else:
        st.info("연도 정보가 없어 추이를 표시할 수 없습니다.")

with tab2:
    if "listed_in" in df.columns:
        genre = (
            df["listed_in"].str.split(", ").explode().str.strip()
            .value_counts().head(10)
        )
        st.subheader("인기 장르 Top 10")
        st.bar_chart(genre)
    else:
        st.info("장르(listed_in) 컬럼이 없습니다.")

with tab3:
    st.subheader(f"필터 결과 ({len(df):,}행)")
    # 너무 긴 설명 컬럼은 제외하고 표시
    show_cols = [c for c in df.columns if c not in ("description",)]
    st.dataframe(df[show_cols], use_container_width=True)

    # 필터링된 결과 다운로드 버튼
    csv = df[show_cols].to_csv(index=False, encoding="utf-8-sig")
    st.download_button("결과 CSV 다운로드", csv, "netflix_filtered.csv", "text/csv")
