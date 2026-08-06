# python selenium_infinite_scroll.py
#
# Selenium으로 '무한 스크롤(infinite scroll)' 페이지를 자동 수집하는 예제
# - 대상: https://quotes.toscrape.com/scroll (스크래핑 연습용 사이트)
# - 스크롤을 내릴 때마다 AJAX로 명언이 추가 로드되는 동적 페이지
# - requests로는 초기 화면만 얻을 수 있어 Selenium이 필요한 대표 사례
#
# 사전 준비:
#   pip install selenium pandas
#   Selenium 4.6+ 는 드라이버(chromedriver)를 자동 관리하므로 별도 설치 불필요

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

TARGET_URL = "https://quotes.toscrape.com/scroll"


def create_driver(headless=True):
    """크롬 드라이버를 생성한다.

    Parameters:
        headless (bool): True면 브라우저 창을 띄우지 않고 백그라운드 실행
    Returns:
        webdriver.Chrome: 설정이 적용된 드라이버
    """
    options = Options()
    if headless:
        options.add_argument("--headless=new")  # 창 없이 실행
    options.add_argument("--window-size=1200,900")
    options.add_argument("--disable-gpu")
    # 자동화 탐지 회피용 옵션(연습 목적)
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)


def scroll_and_collect(driver, max_scrolls=15, pause=1.0):
    """페이지 끝까지 스크롤하며 모든 명언을 수집한다.

    Parameters:
        driver: Selenium 드라이버
        max_scrolls (int): 최대 스크롤 시도 횟수 (무한루프 방지)
        pause (float): 스크롤 후 로딩 대기 시간(초)
    Returns:
        list[dict]: 명언/작가/태그 정보 리스트
    """
    driver.get(TARGET_URL)
    time.sleep(pause)

    # 스크롤 전 페이지 높이 기록
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(max_scrolls):
        # 페이지 맨 아래로 스크롤 → 새 콘텐츠 로드 유발
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)  # AJAX 로딩 대기

        new_height = driver.execute_script("return document.body.scrollHeight")
        loaded = len(driver.find_elements(By.CSS_SELECTOR, "div.quote"))
        print(f"[스크롤 {i + 1}] 현재 {loaded}개 로드됨")

        # 더 이상 높이가 늘지 않으면 끝에 도달한 것으로 판단
        if new_height == last_height:
            print("페이지 끝에 도달했습니다.")
            break
        last_height = new_height

    # 최종 로드된 모든 명언 요소 파싱
    quotes = []
    for card in driver.find_elements(By.CSS_SELECTOR, "div.quote"):
        text = card.find_element(By.CSS_SELECTOR, "span.text").text
        author = card.find_element(By.CSS_SELECTOR, "small.author").text
        tags = [t.text for t in card.find_elements(By.CSS_SELECTOR, "a.tag")]
        quotes.append({"text": text, "author": author, "tags": ", ".join(tags)})

    return quotes


def main():
    driver = create_driver(headless=True)
    try:
        quotes = scroll_and_collect(driver)
    finally:
        driver.quit()  # 예외가 나도 브라우저는 반드시 종료

    df = pd.DataFrame(quotes)
    print(f"\n총 {len(df)}개 명언 수집 완료")
    print(df.head())

    # 결과 저장 (엑셀 호환 인코딩)
    out_path = "data/scraped_quotes.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"저장 완료: {out_path}")

    # 작가별 명언 수 집계 (간단 분석)
    print("\n작가별 명언 수 Top 5")
    print(df["author"].value_counts().head(5))


if __name__ == "__main__":
    main()
