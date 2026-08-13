# 실행: 
# streamlit run streamlit_basic/05_레이아웃.py
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title='레이아웃', layout='wide')
st.title('05. 레이아웃')

# 실행 위치와 무관하게 동작하도록 __file__ 기준 절대경로 사용
CSV_PATH = Path(__file__).resolve().parents[2] / 'data' / 'netflix_titles.csv'


@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)


df = load_data()

print("df['release_year'].min():", df['release_year'].min())
print("df['release_year'].max():", df['release_year'].max())
print("df['type'].dropna().unique():", df['type'].dropna().unique())

# ---------- 사이드바: 필터 ----------
with st.sidebar:
    st.header('🔍 필터')
    kind = st.selectbox('종류', ['전체'] + df['type'].dropna().unique().tolist())
    year_min, year_max = st.slider(
        '제작 연도',
        int(df['release_year'].min()), int(df['release_year'].max()),
        (2015, 2021),
    )

# ---------- 본문: 필터 적용 결과 ----------
filtered = df[df['release_year'].between(year_min, year_max)]
if kind != '전체':
    filtered = filtered[filtered['type'] == kind]

# columns: 숫자 카드를 가로로 배치
c1, c2, c3 = st.columns(3)
c1.metric('전체 작품', f'{len(df):,}')
c2.metric('필터 결과', f'{len(filtered):,}')
c3.metric('비율', f'{len(filtered) / len(df) * 100:.1f}%')

st.divider()

# tabs: 같은 데이터를 여러 관점으로
tab1, tab2, tab3 = st.tabs(['📋 목록', '📊 연도별', '🎬 장르'])

with tab1:
    st.dataframe(
        filtered[['type', 'title', 'release_year', 'listed_in']].head(100),
        use_container_width=True,
    )

with tab2:
    by_year = filtered['release_year'].value_counts().sort_index()
    st.bar_chart(by_year)

with tab3:
    # 08편에서 배운 split → explode
    genres = filtered['listed_in'].str.split(', ').explode()
    st.bar_chart(genres.value_counts().head(10))

with st.expander('원본 데이터 정보'):
    st.write('행 x 열:', df.shape)
    st.write('컬럼:', list(df.columns))
