# streamlit run streamlit_examples/09streamlit_local_search_nhncloud.py

import streamlit as st
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (streamlit_examples 의 상위)
import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="네이버 지역 검색 (NAVER API HUB)", layout="wide")
st.title("네이버 지역 검색 애플리케이션 (NAVER API HUB)")

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

# ------------------------------------------------------------------
# 참고: 지역(local) 검색 API 제약
#   - display: 1~5 (최대 5건, 기본 1)
#   - sort: random(기본, 정확도+거리) | comment(리뷰 많은 순)
#           ※ 블로그와 달리 sim/date는 사용하지 않음
#   - 응답 필드: title, link, category, description,
#                telephone, address, roadAddress, mapx, mapy
# ------------------------------------------------------------------


def get_headers():
    """NAVER API HUB 요청 헤더 생성"""
    return {
        'X-NCP-APIGW-API-KEY-ID': client_id,
        'X-NCP-APIGW-API-KEY': client_secret,
    }


def search_naver_api(endpoint, query, display=5, sort='random'):
    """NAVER API HUB 검색 함수

    Parameters:
        endpoint (str): 검색 유형 (여기서는 'local')
        query (str): 검색어
        display (int): 검색 결과 수 (지역 검색은 1~5)
        sort (str): 정렬 방법 ('random' | 'comment')
    Returns:
        list: 검색 결과 items 리스트
    """
    payload = {
        'query': query,
        'display': display,
        'sort': sort,
    }
    url = f'{DOMAIN_URL}/search/v1/{endpoint}'

    try:
        res = requests.get(url, params=payload, headers=get_headers())
        res.raise_for_status()
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


def clean_title(df):
    """title 필드의 <b> 태그 제거"""
    if df.empty or 'title' not in df.columns:
        return df
    df = df.copy()
    df['title'] = (
        df['title']
        .str.replace('<b>', '', regex=False)
        .str.replace('</b>', '', regex=False)
    )
    return df


def filter_by_category(df, category_name):
    """
    특정 카테고리가 포함된 업체만 필터링
    Parameters:
        df (DataFrame): 지역 검색 결과 데이터프레임
        category_name (str): 포함할 카테고리 (예: '음식점', '카페')
    Returns:
        DataFrame: 필터링된 결과
    """
    if df.empty or category_name == "":
        return pd.DataFrame()

    columns_to_show = [c for c in ['title', 'category', 'roadAddress', 'telephone']
                       if c in df.columns]

    return (
        df.loc[df['category'].str.contains(category_name, na=False), columns_to_show]
          .reset_index(drop=True)
    )


def filter_by_address(df, keyword):
    """
    도로명주소 또는 지번주소에 특정 지역 키워드가 포함된 업체만 필터링
    Parameters:
        df (DataFrame): 지역 검색 결과 데이터프레임
        keyword (str): 포함할 주소 키워드 (예: '강남구', '분당')
    Returns:
        DataFrame: 필터링된 결과
    """
    if df.empty or keyword == "":
        return pd.DataFrame()

    road = df['roadAddress'].str.contains(keyword, na=False) if 'roadAddress' in df.columns else False
    addr = df['address'].str.contains(keyword, na=False) if 'address' in df.columns else False
    mask = road | addr

    columns_to_show = [c for c in ['title', 'category', 'roadAddress', 'address', 'telephone']
                       if c in df.columns]

    return (
        df.loc[mask, columns_to_show]
          .reset_index(drop=True)
    )


# 사이드바에 검색 옵션 구성
st.sidebar.header("검색 옵션")
search_query = st.sidebar.text_input("검색어", "성남 맛집")
display_count = st.sidebar.slider("검색 결과 수", 1, 5, 5)  # 지역 검색은 최대 5
sort_option = st.sidebar.radio("정렬", ["random (정확도+거리)", "comment (리뷰순)"], index=0)
sort_value = "comment" if sort_option.startswith("comment") else "random"

# 검색/저장 버튼
search_button = st.sidebar.button("검색하기")
save_button = st.sidebar.button("결과 저장하기")

# 필터링 옵션
st.sidebar.header("필터링 옵션")
category_filter = st.sidebar.text_input("카테고리 필터", "")
address_filter = st.sidebar.text_input("지역(주소) 필터", "")

st.sidebar.caption("ⓘ 지역 검색은 최대 5건까지만 반환됩니다 (API 제약).")

# 메인 영역
tab1, tab2, tab3 = st.tabs(["전체 결과", "카테고리 필터링", "지역 필터링"])

# 데이터를 저장할 상태 변수
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
    st.session_state.local_df = pd.DataFrame()

# 검색 버튼 클릭
if search_button and client_id and client_secret:
    with st.spinner('검색 중...'):
        st.session_state.search_results = search_naver_api(
            'local', search_query, display_count, sort_value
        )
        if st.session_state.search_results:
            st.session_state.local_df = clean_title(pd.DataFrame(st.session_state.search_results))
            st.success(f"{len(st.session_state.search_results)}개의 업체를 찾았습니다.")
        else:
            st.warning("검색 결과가 없습니다.")

# 저장 버튼 클릭
if save_button and st.session_state.search_results:
    filepath = BASE_DIR / "data" / f"{search_query}_local.json"
    save_json(st.session_state.search_results, filepath)

# 탭 1: 전체 결과
with tab1:
    if not st.session_state.local_df.empty:
        st.write("전체 검색 결과")
        cols = [c for c in ['title', 'category', 'roadAddress', 'telephone', 'description']
                if c in st.session_state.local_df.columns]
        st.dataframe(st.session_state.local_df[cols], use_container_width=True)

        # 지도 표시 (mapx, mapy가 있으면 좌표 변환하여 표시)
        # 네이버 지역 검색의 mapx/mapy는 KATECH(카텍) 좌표가 아니라
        # WGS84 경위도에 10^7을 곱한 정수값입니다. (예: 1270123456 -> 127.0123456)
        map_df = st.session_state.local_df.copy()
        if 'mapx' in map_df.columns and 'mapy' in map_df.columns:
            try:
                map_df['lon'] = pd.to_numeric(map_df['mapx'], errors='coerce') / 1e7
                map_df['lat'] = pd.to_numeric(map_df['mapy'], errors='coerce') / 1e7
                map_points = map_df[['lat', 'lon']].dropna()
                if not map_points.empty:
                    st.write("지도")
                    st.map(map_points)
            except Exception as e:
                st.info(f"지도를 표시할 수 없습니다: {e}")
    else:
        st.info("검색 결과가 없습니다. 검색 버튼을 클릭하여 결과를 불러오세요.")

# 탭 2: 카테고리 필터링
with tab2:
    if not st.session_state.local_df.empty and category_filter:
        filtered_by_category = filter_by_category(st.session_state.local_df, category_filter)
        if not filtered_by_category.empty:
            st.write(f"카테고리에 '{category_filter}'가 포함된 업체")
            st.dataframe(filtered_by_category, use_container_width=True)
        else:
            st.info(f"카테고리에 '{category_filter}'가 포함된 업체가 없습니다.")
    else:
        st.info("검색 결과가 없거나 카테고리 필터가 입력되지 않았습니다.")

# 탭 3: 지역 필터링
with tab3:
    if not st.session_state.local_df.empty and address_filter:
        filtered_by_address = filter_by_address(st.session_state.local_df, address_filter)
        if not filtered_by_address.empty:
            st.write(f"주소에 '{address_filter}'가 포함된 업체")
            st.dataframe(filtered_by_address, use_container_width=True)
        else:
            st.info(f"주소에 '{address_filter}'가 포함된 업체가 없습니다.")
    else:
        st.info("검색 결과가 없거나 지역(주소) 필터가 입력되지 않았습니다.")
