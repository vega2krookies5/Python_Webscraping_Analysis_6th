# 실행: 
# streamlit run streamlit_basic/03_session_state.py
import streamlit as st

st.title('03. session_state - 값 유지하기')

# ---------------------------------------------------------
# 잘못된 예: 매 재실행마다 0 으로 초기화되어 절대 늘지 않는다
# ---------------------------------------------------------
bad_count = 0
if st.button('❌ 잘못된 카운터'):
    bad_count += 1
st.write('잘못된 카운터:', bad_count, '← 아무리 눌러도 0 또는 1')

st.divider()

# ---------------------------------------------------------
# 올바른 예: session_state 에 보관하면 재실행돼도 살아남는다
# ---------------------------------------------------------
# 이 if 문이 '최초 1회만 초기화' 를 보장한다
if 'count' not in st.session_state:
    st.session_state.count = 0

col1, col2 = st.columns(2)
if col1.button('⭕ 올바른 카운터 +1'):
    st.session_state.count += 1
if col2.button('초기화'):
    st.session_state.count = 0

st.write('올바른 카운터:', st.session_state.count, '← 계속 누적된다')

st.divider()

# 실전 패턴: 검색 결과를 보관해 두면
# 다른 위젯을 건드려도 결과가 사라지지 않는다
if 'history' not in st.session_state:
    st.session_state.history = []

keyword = st.text_input('검색어')
if st.button('검색') and keyword:
    st.session_state.history.append(keyword)

st.subheader('검색 기록')
st.write(st.session_state.history)

# 디버깅용: 현재 보관 중인 전체 상태 확인
with st.expander('session_state 전체 보기'):
    st.write(dict(st.session_state))
