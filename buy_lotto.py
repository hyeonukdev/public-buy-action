import re
import sys
import time
from datetime import datetime, timedelta
import telebot

from requests import post, Response
from playwright.sync_api import Playwright, sync_playwright

# 동행복권 아이디와 패스워드를 설정
USER_ID = sys.argv[1]
USER_PW = sys.argv[2]

# 구매 개수를 설정
COUNT = sys.argv[3]

# 텔레그램 설정
BOT_TOKEN = sys.argv[4]
CHAT_ID = sys.argv[5]
bot = telebot.TeleBot(BOT_TOKEN)


class BalanceError(Exception):
    def __init__(self, message="An error occurred", code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} - Code: {self.code}" if self.code else self.message

def __get_now() -> datetime:
    now_utc = datetime.utcnow()
    korea_timezone = timedelta(hours=9)
    now_korea = now_utc + korea_timezone
    return now_korea

def send_message(text):
    bot.send_message(CHAT_ID, text)


def run(playwright: Playwright) -> None:

    print(f"{COUNT}개 자동 복권 구매 시작합니다!")
    send_message(f"{COUNT}개 자동 복권 구매 시작합니다!")
    
    try:
        browser = playwright.chromium.launch(headless=True)  # chrome 브라우저를 실행, False인 경우 테스트 실행
        context = browser.new_context()

        page = context.new_page()
        page.goto("https://dhlottery.co.kr/user.do?method=login")
        page.click('[placeholder="아이디"]')
        page.fill('[placeholder="아이디"]', USER_ID)
        page.press('[placeholder="아이디"]', "Tab")
        page.fill('[placeholder="비밀번호"]', USER_PW)
        page.press('[placeholder="비밀번호"]', "Tab")

        # Press Enter
        # with page.expect_navigation(url="https://ol.dhlottery.co.kr/olotto/game/game645.do"):
        with page.expect_navigation():
            page.press('form[name="jform"] >> text=로그인', "Enter")
        time.sleep(4)

        # 로그인 이후 기본 정보 체크 & 예치금 알림
        page.goto("https://dhlottery.co.kr/common.do?method=main")
        money_info = page.query_selector("ul.information").inner_text()
        money_info: str = money_info.split("\n")
        user_name = money_info[0]
        money_info: int = int(money_info[2].replace(",", "").replace("원", ""))

        print(f"로그인 사용자: {user_name}, 예치금: {money_info}")
        send_message(f"로그인 사용자: {user_name}, 예치금: {money_info}")

        # 예치금 잔액 부족 미리 exception
        if 1000 * int(COUNT) > money_info:
            raise BalanceError()

        page.goto(url="https://ol.dhlottery.co.kr/olotto/game/game645.do")
        # "비정상적인 방법으로 접속하였습니다. 정상적인 PC 환경에서 접속하여 주시기 바랍니다." 우회하기
        # 아래코드는 action하면서필요하고 테스트일 땐 주석해야함.
        page.locator("#popupLayerAlert").get_by_role("button", name="확인").click()
        page.click("text=자동번호발급")

        # 구매할 개수를 선택
        page.select_option("select", str(COUNT))  # Select 1
        page.click("text=확인")
        page.click('input:has-text("구매하기")')  # Click input:has-text("구매하기")
        time.sleep(2)
        page.click(
            'text=확인 취소 >> input[type="button"]'
        )  # Click text=확인 취소 >> input[type="button"]
        page.click('input[name="closeLayer"]')
        assert page.url == "https://el.dhlottery.co.kr/game/TotalGame.jsp?LottoId=LO40"

        print(f"{COUNT}개 복권 구매 성공! \n자세하게 확인하기: https://dhlottery.co.kr/myPage.do?method=notScratchListView")
        send_message(f"{COUNT}개 복권 구매 성공! \n자세하게 확인하기: https://dhlottery.co.kr/myPage.do?method=notScratchListView")

        # 오늘 구매한 복권 결과
        now_date = __get_now().date().strftime("%Y%m%d")
        page.goto(
            url=f"https://dhlottery.co.kr/myPage.do?method=lottoBuyList&searchStartDate={now_date}&searchEndDate={now_date}&lottoId=&nowPage=1"
        )
        a_tag_href = page.query_selector(
            "tbody > tr:nth-child(1) > td:nth-child(4) > a"
        ).get_attribute("href")
        detail_info = re.findall(r"\d+", a_tag_href)
        page.goto(
            url=f"https://dhlottery.co.kr/myPage.do?method=lotto645Detail&orderNo={detail_info[0]}&barcode={detail_info[1]}&issueNo={detail_info[2]}"
        )
        result_msg = ""
        for result in page.query_selector_all("div.selected li"):
            result_msg += ", ".join(result.inner_text().split("\n")) + "\n"

        print(f"이번주 나의 행운의 번호는?!\n{result_msg}")
        send_message(f"이번주 나의 행운의 번호는?!\n{result_msg}")

    except BalanceError:
        print("BalanceError")
        send_message(BalanceError)

    except Exception as exc:
        print(exc)
        send_message(exc)

    finally:
        # End of Selenium
        context.close()
        browser.close()


with sync_playwright() as playwright:
    run(playwright)