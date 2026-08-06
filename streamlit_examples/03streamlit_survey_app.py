# streamlit run streamlit_examples/03streamlit_survey_app.py

import streamlit as st

st.set_page_config(page_title="간단한 설문조사 앱", layout="centered")
st.title("파이썬 학습자 설문조사")

st.write("안녕하세요! 아래 항목에 응답해 주세요.")

# 1. 이름과 학년
name = st.text_input("이름을 입력하세요")
grade = st.selectbox("학년을 선택하세요", ["1학년", "2학년", "3학년", "4학년", "졸업생"])

# 2. 학습 경험
experience = st.radio("파이썬을 학습한 경험이 있나요?", ["예", "아니오"])

# 3. 관심 분야
interests = st.multiselect(
    "관심 있는 분야를 모두 선택하세요:",
    ["웹 개발", "데이터 분석", "인공지능", "게임 개발", "모바일 앱", "자동화", "기타"]
)

# 4. 만족도
satisfaction = st.slider("이번 강의에 대한 기대 만족도는?", 1, 5, 3)

# 5. 의견
opinion = st.text_area("추가로 하고 싶은 말이 있다면 적어주세요.")

# 제출 버튼
if st.button("제출하기"):
    if name == "":
        st.warning("이름을 입력해 주세요!")
    else:
        st.success("설문이 제출되었습니다! 감사합니다 🙌")
        st.subheader("제출 내용 요약")
        st.write(f"**이름:** {name}")
        st.write(f"**학년:** {grade}")
        st.write(f"**파이썬 경험:** {experience}")
        st.write(f"**관심 분야:** {', '.join(interests) if interests else '없음'}")
        st.write(f"**만족도:** {satisfaction}점")
        if opinion:
            st.write(f"**기타 의견:** {opinion}")

