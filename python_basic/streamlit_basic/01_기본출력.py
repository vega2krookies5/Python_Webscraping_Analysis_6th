# 실행: 
# streamlit run streamlit_basic/01_기본출력.py
import streamlit as st
import pandas as pd

# set_page_config 는 반드시 '가장 먼저' 호출해야 한다
st.set_page_config(page_title='기본 출력', layout='wide')

st.title('01. 기본 출력')
st.header('헤더')
st.subheader('서브헤더')

# write 는 만능이다 - 문자열, 숫자, DataFrame, 그래프 모두 알아서 처리
st.write('일반 텍스트입니다.')
st.write({'딕셔너리도': '표로 보여준다', 'key': 'value'})

st.divider()   # 가로 구분선

df = pd.DataFrame({
    '이름': ['지민', '수진', '태양'],
    '점수': [90, 85, 78],
})

st.subheader('표 출력')
st.dataframe(df, use_container_width=True)   # 정렬·검색 가능한 표
st.table(df)                                  # 정적인 표

st.divider()

# metric: 대시보드의 숫자 카드
col1, col2 = st.columns(2)
col1.metric('평균 점수', f"{df['점수'].mean():.1f}", delta='2.3')
col2.metric('최고 점수', df['점수'].max())

st.divider()

# 알림 상자 4종
st.info('정보 메시지')
st.success('성공 메시지')
st.warning('경고 메시지')
st.error('에러 메시지')
