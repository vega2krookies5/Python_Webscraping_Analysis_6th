"""
추가 설치 필요함
pip install streamlit-aggrid
pip show streamlit-aggrid

streamlit run streamlit_examples/07streamlit_korea_aggrid.py

"""

import streamlit as st
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent  # 프로젝트 루트 (streamlit_examples 의 상위)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# GridUpdateMode 는 deprecated 되어 더 이상 import 하지 않는다 (아래 update_on 참고)
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode

# 데이터 로드
@st.cache_data
def load_data():
    data = pd.read_csv(BASE_DIR / 'data' / 'data_draw_korea.csv')
    if 'Unnamed: 0' in data.columns:
        data.drop('Unnamed: 0', axis=1, inplace=True)
    return data

data = load_data()
plt.rc('font', family="Malgun Gothic")

# Streamlit UI 구성
st.title("🇰🇷 대한민국 광역시도 데이터 분석 (AgGrid)")

# 광역시도 목록
sido_list = data['광역시도'].unique()
sido_name = st.selectbox("조회할 광역시도를 선택하세요", sido_list)

# 데이터 필터링
sido_df = data[data['광역시도'] == sido_name][['행정구역', '인구수', '면적']].reset_index(drop=True)

if sido_df.empty:
    st.error("해당 광역시도의 데이터를 찾을 수 없습니다.")
else:
    # --- AgGrid 설정 ---
    st.subheader(f"📊 {sido_name} 데이터 그리드")
    st.info("💡 열 제목을 클릭하여 정렬하거나, 필터 아이콘을 눌러 데이터를 검색해보세요.")

    gb = GridOptionsBuilder.from_dataframe(sido_df)
    gb.configure_default_column(editable=True, groupable=True, value=True, enableRowGroup=True) # 편집 가능 설정
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10) # 페이지네이션
    gb.configure_side_bar() # 측면 필터 바 추가
    gb.configure_selection('single') # 행 선택 기능
    grid_options = gb.build()

    # AgGrid 실행
    #
    # [update_on 이란]
    #   "그리드에서 어떤 일이 일어났을 때 Streamlit 을 재실행할 것인가" 를 지정한다.
    #   여기에 적힌 이벤트가 발생해야 파이썬 쪽으로 변경된 데이터가 돌아온다.
    #   (즉, 아래 updated_df 가 갱신되고 그래프가 다시 그려진다)
    #
    # [예전 방식이 사라진 이유]
    #   과거에는 update_mode=GridUpdateMode.MODEL_CHANGED 처럼
    #   '미리 정해진 묶음(enum)' 중에서 고르는 방식이었다.
    #   하지만 AG Grid 가 제공하는 이벤트는 수십 가지인데 enum 으로는 일부만 쓸 수 있어,
    #   이벤트 이름을 문자열로 직접 나열하는 update_on 방식으로 바뀌었다.
    #
    # [MODEL_CHANGED 와 동일한 설정]
    #   MODEL_CHANGED = VALUE_CHANGED | SELECTION_CHANGED | FILTERING_CHANGED | SORTING_CHANGED
    #   이 4가지가 아래 4개 문자열로 1:1 대응되므로 동작은 완전히 같다.
    #
    # [응답 속도 조절]
    #   ('columnResized', 300) 처럼 튜플로 주면 300ms 디바운스가 걸린다.
    #   (연속으로 발생하는 이벤트가 재실행을 과도하게 일으키는 것을 막는다)
    grid_response = AgGrid(
        sido_df,
        gridOptions=grid_options,
        height=300,
        width='100%',
        update_on=[
            'cellValueChanged',   # 셀 값을 수정했을 때  (편집 반영 → 그래프 갱신)
            'selectionChanged',   # 행을 선택했을 때
            'filterChanged',      # 필터를 걸었을 때
            'sortChanged',        # 정렬을 바꿨을 때
        ],
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        theme='material' # 또는 'alpine', 'balham', 'material'
    )

    # AgGrid에서 수정한 데이터를 그래프에 반영하기 위해 데이터 가져오기
    updated_df = pd.DataFrame(grid_response['data'])

    # --- 그래프 영역 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"👥 인구수 현황")
        fig, ax = plt.subplots(figsize=(10, 8))

        # seaborn 0.13 부터 palette 는 반드시 hue 와 함께 써야 한다.
        #   - palette 는 '무엇에 따라 색을 나눌지(hue)' 에 색을 배정하는 규칙이다.
        #   - hue 없이 palette 만 주면 '기준' 이 없으므로 v0.14 에서 제거 예정(FutureWarning).
        # 막대마다 색을 다르게 하려면 x 와 같은 열을 hue 에 넣고,
        # 범례는 x축 라벨과 중복되므로 legend=False 로 끈다.
        sns.barplot(
            x='행정구역',
            y='인구수',
            hue='행정구역',      # x 와 동일한 열 → 막대별로 다른 색
            data=updated_df.sort_values(by='인구수', ascending=False),
            ax=ax,
            palette='viridis',
            legend=False,        # 범례가 x축 라벨과 중복되므로 숨김
        )

        # tick_params 를 쓰면 '현재 figure' 가 아니라 이 ax 에 확실히 적용된다
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        plt.close(fig)   # 재실행 때마다 figure 가 쌓이지 않도록 닫아준다

    with col2:
        st.subheader(f"🗺️ 면적 현황")
        fig, ax = plt.subplots(figsize=(10, 8))

        # 위와 동일한 이유로 hue='행정구역' + legend=False 를 지정한다
        sns.barplot(
            x='행정구역',
            y='면적',
            hue='행정구역',
            data=updated_df.sort_values(by='면적', ascending=False),
            ax=ax,
            palette='magma',
            legend=False,
        )

        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
        plt.close(fig)