# 실행: 
# streamlit run streamlit_basic/04_cache.py
import streamlit as st
import pandas as pd
import time
from pathlib import Path

st.title('04. cache_data - 다시 읽지 않기')

# streamlit run 은 '명령을 실행한 폴더' 가 기준(cwd)이 된다. 스크립트 위치가 아니다.
# 따라서 './../data' 같은 상대경로는 어디서 실행하느냐에 따라 깨진다.
# __file__(이 스크립트의 위치) 기준으로 절대경로를 만들면 어디서 실행해도 안전하다.
#   streamlit_basic/04_cache.py → parents[0]=streamlit_basic
#                                 parents[1]=python_basic
#                                 parents[2]=프로젝트 루트
CSV_PATH = Path(__file__).resolve().parents[2] / 'data' / 'netflix_titles.csv'


@st.cache_data
def load_data(path):
    """CSV 를 읽어 DataFrame 으로 돌려준다.

    @st.cache_data 덕분에 같은 path 로 호출되면
    실제 읽기는 최초 1회만 수행되고, 이후에는 저장된 결과를 반환한다.
    """
    time.sleep(2)               # 느린 작업을 흉내
    return pd.read_csv(path)


start = time.time()
df = load_data(CSV_PATH)
elapsed = time.time() - start

st.metric('로딩 시간', f'{elapsed:.2f} 초')
st.info('처음에는 2초 이상, 이후 재실행에서는 0초에 가깝게 나온다.')

st.dataframe(df.head(20), use_container_width=True)

# 슬라이더를 움직여 재실행시켜 보자 - 로딩 시간이 0초가 된다
n = st.slider('표시할 행 수', 5, 50, 20)
st.write(f'상위 {n}개 행')
st.dataframe(df.head(n), use_container_width=True)

if st.button('캐시 지우기'):
    st.cache_data.clear()
    st.rerun()      # 스크립트를 강제로 다시 실행
