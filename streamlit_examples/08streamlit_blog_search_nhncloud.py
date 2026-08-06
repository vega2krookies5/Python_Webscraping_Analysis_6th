# streamlit run streamlit_examples/08streamlit_blog_search_nhncloud.py

import streamlit as st
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (streamlit_examples 의 상위)
import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="네이버 블로그 검색 (NAVER API HUB)", layout="wide")
st.title("네이버 블로그 검색 애플리케이션 (NAVER API HUB)")

# .env 파일에서 환경 변수 로드
load_dotenv(BASE_DIR / '.env')
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# 환경 변수가 없다면 사이드바에서 입력받도록 함
if not client_id or not client_secret:
    st.sidebar.header("API 키 설정")
    client_id = st.sidebar.text_input("CLIENT_ID 입력", type="password")
    client_secret = st.sidebar.text_input("CLIENT_SECRET 입력", type="password")

    if not client_id or not client_secret:
        st.warning("NAVER API HUB 사용을 위해 CLIENT_ID와 CLIENT_SECRET을 입력해주세요.")

# NAVER API HUB 공통 도메인
DOMAIN_URL = 'https://naverapihub.apigw.ntruss.com'


def get_headers():
    """NAVER API HUB 요청 헤더 생성"""
    return {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }


def search_naver_api(endpoint, query, display=50, sort='sim'):
    """NAVER API HUB 검색 함수

    Parameters:
        endpoint (str): 검색 유형 (여기서는 'blog')
        query (str): 검색어
        display (int): 검색 결과 수 (1~100)
        sort (str): 정렬 방법 ('sim' 정확도 | 'date' 날짜)
    Returns:
        list: 검색 결과 items 리스트
    """
    payload = {
        'query': query,
        'display': display,
        'sort': sort,
    }
    url = f'{DOMAIN_URL}/search/v1/{endpoint}'
    print(url)

    try:
        res = requests.get(url, params=payload, headers=get_headers())
        res.raise_for_status()
        print(len(res.json()))
        print(res.json())
        return res.json().get('items', [])
    except requests.exceptions.RequestException as e:
        detail = ""
        if e.response is not None:
            try:
                detail = f" / 응답: {e.response.json()}"
            except Exception:
                detail = f" / 응답: {e.response.text}"
        st.error(f"API 요청 중 오류가 발생했습니다: {e}{detail}")
        return []


def save_json(data, filepath):
    """JSON 파일 저장 함수"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.success(f"데이터가 {filepath}에 저장되었습니다.")


def filter_by_blogger(df, blogger_name):
    """
    특정 블로거명이 포함된 글만 필터링 (link 컬럼 제외)
    Parameters:
        df (DataFrame): 블로그 검색 결과 데이터프레임
        blogger_name (str): 포함할 블로거명
    Returns:
        DataFrame: 필터링된 결과
    """
    if df.empty or blogger_name == "":
        return pd.DataFrame()

    columns_to_show = [c for c in df.columns if c != 'link']

    return (
        df.loc[df['bloggername'].str.contains(blogger_name, na=False), columns_to_show]
          .reset_index(drop=True)
    )


def filter_and_sort_by_date(df, start_date=""):
    """
    작성일(postdate)이 start_date 이상인 글만 필터링 후 최신순 정렬
    Parameters:
        df (DataFrame): 블로그 검색 결과 데이터프레임
        start_date (str): 기준 날짜 (YYYYMMDD 형식 문자열, 빈 문자열이면 전체)
    Returns:
        DataFrame: 필터링 및 정렬된 결과
    """
    if df.empty or 'postdate' not in df.columns:
        return pd.DataFrame()

    result = df.copy()
    if start_date:
        result = result.loc[result['postdate'] >= start_date]

    columns_to_show = ['title', 'bloggername', 'postdate', 'link']
    columns_to_show = [c for c in columns_to_show if c in result.columns]

    return (
        result[columns_to_show]
        .sort_values(by='postdate', ascending=False)
        .reset_index(drop=True)
    )


# 사이드바에 검색 옵션 구성
st.sidebar.header("검색 옵션")
search_query = st.sidebar.text_input("검색어", "파이썬")
display_count = st.sidebar.slider("검색 결과 수", 10, 100, 50)
sort_option = st.sidebar.radio("정렬", ["sim (정확도)", "date (날짜)"], index=0)
sort_value = "date" if sort_option.startswith("date") else "sim"

# 검색/저장 버튼
search_button = st.sidebar.button("검색하기")
save_button = st.sidebar.button("결과 저장하기")

# 필터링 옵션
st.sidebar.header("필터링 옵션")
date_filter = st.sidebar.text_input("작성일 기준 (YYYYMMDD 이상)", "")
blogger_filter = st.sidebar.text_input("블로거명 필터", "")

# 메인 영역
tab1, tab2, tab3 = st.tabs(["전체 결과", "작성일 필터링", "블로거 필터링"])

# 데이터를 저장할 상태 변수
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
    st.session_state.blog_df = pd.DataFrame()

# 검색 버튼 클릭
if search_button and client_id and client_secret:
    with st.spinner('검색 중...'):
        st.session_state.search_results = search_naver_api(
            'blog', search_query, display_count, sort_value
        )
        if st.session_state.search_results:
            st.session_state.blog_df = pd.DataFrame(st.session_state.search_results)
            st.success(f"{len(st.session_state.search_results)}개의 블로그 글을 찾았습니다.")
        else:
            st.warning("검색 결과가 없습니다.")

# 저장 버튼 클릭
if save_button and st.session_state.search_results:
    filepath = BASE_DIR / "data" / f"{search_query}_blog.json"
    save_json(st.session_state.search_results, filepath)

# 탭 1: 전체 결과
with tab1:
    if not st.session_state.blog_df.empty:
        st.write("전체 검색 결과")
        cols = [c for c in ['title', 'bloggername', 'postdate', 'description']
                if c in st.session_state.blog_df.columns]
        st.dataframe(st.session_state.blog_df[cols], use_container_width=True)
    else:
        st.info("검색 결과가 없습니다. 검색 버튼을 클릭하여 결과를 불러오세요.")

# 탭 2: 작성일 필터링
with tab2:
    if not st.session_state.blog_df.empty:
        filtered_by_date = filter_and_sort_by_date(st.session_state.blog_df, date_filter)
        if not filtered_by_date.empty:
            label = f"{date_filter} 이후 작성 글" if date_filter else "작성일 최신순 정렬"
            st.write(label)
            st.dataframe(filtered_by_date, use_container_width=True)
        else:
            st.info("해당 조건의 글이 없습니다.")
    else:
        st.info("검색 결과가 없습니다. 검색 버튼을 클릭하여 결과를 불러오세요.")

# 탭 3: 블로거 필터링
with tab3:
    if not st.session_state.blog_df.empty and blogger_filter:
        filtered_by_blogger = filter_by_blogger(st.session_state.blog_df, blogger_filter)
        if not filtered_by_blogger.empty:
            st.write(f"블로거명에 '{blogger_filter}'가 포함된 글")
            st.dataframe(filtered_by_blogger, use_container_width=True)
        else:
            st.info(f"블로거명에 '{blogger_filter}'가 포함된 글이 없습니다.")
    else:
        st.info("검색 결과가 없거나 블로거명 필터가 입력되지 않았습니다.")