# 실행: 
# streamlit run streamlit_basic/02_위젯.py
import streamlit as st

st.title('02. 위젯 - 입력값 받기')

# 각 위젯은 '사용자가 고른 값' 을 반환한다
name = st.text_input('이름을 입력하세요', value='홍길동')
age = st.slider('나이', min_value=0, max_value=100, value=25)
city = st.selectbox('도시', ['서울', '부산', '대구'])
hobbies = st.multiselect('취미', ['독서', '운동', '게임', '음악'])
agree = st.checkbox('약관에 동의합니다')
gender = st.radio('성별', ['남', '여'], horizontal=True)

st.divider()

# 위젯을 하나라도 건드리면 스크립트가 처음부터 재실행되고
# 아래 내용이 새 값으로 다시 그려진다
st.subheader('입력 결과')
st.write(f'**{name}** / {age}세 / {city} / {gender}')
st.write('취미:', ', '.join(hobbies) if hobbies else '(없음)')

if not agree:
    st.warning('약관에 동의해야 제출할 수 있습니다.')
elif st.button('제출'):
    # button 은 눌린 그 순간의 재실행에서만 True 다
    st.success(f'{name}님 제출 완료!')
    st.balloons()
