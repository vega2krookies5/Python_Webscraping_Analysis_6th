# streamlit run streamlit_examples/10streamlit_netflix_actor_search.py

import streamlit as st
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (streamlit_examples 의 상위)
import pandas as pd

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv(BASE_DIR / 'data' / 'netflix_titles.csv')
    df['cast'] = df['cast'].fillna('No Data')
    return df

df = load_data()

st.title("Netflix 배우 검색 앱")
st.write("배우 이름을 입력하면 해당 배우의 출연작 목록을 보여줍니다.")

# 배우 이름 입력
actor_name = st.text_input(" 배우 이름을 입력하세요 (예: Shah Rukh Khan)")

if actor_name:
    # 해당 배우가 포함된 행 필터링
    results = df[df['cast'].str.contains(actor_name, case=False, na=False)]

    if not results.empty:
        st.success(f"🔎 {actor_name}이(가) 출연한 콘텐츠 {len(results)}개가 검색되었습니다.")
        st.dataframe(results[['title','type', 'release_year', 'listed_in']]\
                     .sort_values(by='release_year', ascending=False)\
                     .reset_index(drop=True))
    else:
        st.warning(f" {actor_name} 출연작이 없습니다.")
