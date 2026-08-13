# 실행: 
# streamlit run streamlit_basic/06_차트.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc
from pathlib import Path

# 한글 폰트 설정 (06편과 동일)
rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

st.title('06. 차트')

# 실행 위치와 무관하게 동작하도록 __file__ 기준 절대경로 사용
CSV_PATH = Path(__file__).resolve().parents[2] / 'data' / 'netflix_titles.csv'


@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)


df = load_data()
by_year = df[df['release_year'] >= 2010]['release_year'].value_counts().sort_index()

# ---------- 방법 1: streamlit 내장 차트 (간단) ----------
st.subheader('내장 차트 - st.bar_chart')
st.bar_chart(by_year)

st.divider()

# ---------- 방법 2: matplotlib (세밀한 제어 가능) ----------
st.subheader('matplotlib - st.pyplot')

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(by_year.index, by_year.values, color='#E50914')
ax.set_title('연도별 넷플릭스 콘텐츠 수')
ax.set_xlabel('제작 연도')
ax.set_ylabel('작품 수')
ax.grid(axis='y', alpha=0.3)

st.pyplot(fig)      # Figure 객체를 그대로 넘긴다

st.caption('matplotlib 은 제목·색·격자 등을 세밀하게 제어할 수 있다.')
