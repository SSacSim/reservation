import sys
import os
sys.path.append(os.path.abspath("../"))  # .. = project 루트 폴더

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import yaml
import random
import re 
from datetime import datetime

from telegram_util import telegram_utils


options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("start-maximized")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")

# 로컬PC
# driver = webdriver.Chrome(options=options)

# 가상 UI
driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options
)

## util def

def is_valid_date(date_str: str) -> bool:
    '''
        return : year , month , day -> int 
    '''
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        split_day = date_str.split("-")

        return int(split_day[0]), int(split_day[1]), int(split_day[2])
    except ValueError:
        raise "날짜 형식이 맞지 않습니다. 2025-11-07 형태로 넣어주세요."
    

# localhost:4444로 들어가야 함. -> 오른쪽 카메라 버튼
# pwd : secret 

def read_info(private_path : str = "./config/private_config.yaml", public_path : str = "./config/public_config.yaml"):
    try:
        with open(private_path, "r", encoding="utf-8") as f:
            userInfo =  yaml.safe_load(f)
    except:
        raise "사용자 정보가 없습니다. private_config.yaml 파일을 만들어 주세요."
    
    try:
        with open(public_path, "r", encoding="utf-8") as f:
            public_info =  yaml.safe_load(f)
    except:
        raise "사용자 정보가 없습니다. private_config.yaml 파일을 만들어 주세요."

    return userInfo, public_info

def pageLogin(driver , userInfo):
    '''
        로그인 
    '''
    driver.get("https://www.korail.com/ticket/login") # login page 접속
    


    ## ID 입력 
    input_id = driver.find_element(By.ID, "id")
    input_id.click()
    input_id.clear()
    for ch in str(userInfo['userNumber']):
        input_id.send_keys(ch)
        time.sleep(random.uniform(0.05, 0.2))

    ## pwd 입력 
    input_pwd = driver.find_element(By.ID, "password")
    input_pwd.click()
    input_pwd.clear()
    for ch in str(userInfo['pwd']):
        input_pwd.send_keys(ch)
        time.sleep(random.uniform(0.05, 0.2))

    
    ## 입력 후 로그인 클릭 
    time.sleep(random.uniform(1, 2))

    element = driver.switch_to.active_element
    ## 로그인때 오류 나오는 경우 있음.
    ## Enter 기준으로 진행해야 오류창 한번 뜨고 가능 
    while True:
        time.sleep(random.uniform(1,2))
        element.send_keys(Keys.ENTER)
        time.sleep(random.uniform(1,2))
        isError = driver.find_elements(By.CLASS_NAME,"layerWrap")
        if len(isError) != 0 :
            driver.find_element(By.CLASS_NAME,"btn_pop-close").click()
        else:
            break
    print("============= login finish =============")


def selectPort(driver , desti : str = "서울", start = True):
    if start:
        driver.find_element(By.CLASS_NAME,"start").click()
    else:
        driver.find_element(By.CLASS_NAME,"end").click()
        
    port = driver.find_element(By.NAME,"searchTxt")
    port.click()
    port.send_keys(desti)
    port_list = driver.find_elements(By.CLASS_NAME,"sch_wrap")[0]
    port_list.click()

# 달력에서 선택 
# 달력에서 선택 
def selectCalendar(driver , settings):

    # 달력 열기 
    driver.find_element(By.CLASS_NAME , "btn_pop.btn_d-day").click()

    target_day = settings["targetdate"]
    target_time = "10"
    year, month , day = is_valid_date(target_day) 

    time.sleep(2)
    # 현재 년,월 추출 
    now_day  = driver.find_element(By.CLASS_NAME,'date').text.split(". ")
    now_year = int(re.findall(r"\d+", now_day[0])[0])
    now_month = int(re.findall(r"\d+", now_day[1])[0])

    # 년도가 바뀌면 
    if now_month > month :
        month += 12
    
    if (month - now_month) >=3:
        raise "3개월 이상 미리 예매할 수 없습니다."

    # 원하는 달로 이동 
    for i in range(month - now_month):
        driver.find_element(By.CLASS_NAME,"slick-arrow.slick-next").click()
        time.sleep(2)
        
    # 선택 가능한 날짜 총 수가 나옴.
    CSS_SELECTOR = "tbody a[aria-disabled='false']"
    enabled_elements = driver.find_elements(By.CSS_SELECTOR, CSS_SELECTOR)
    # 출발일 선택 
    enabled_elements[day - int(enabled_elements[0].text.split("\n")[0])].click()
    time.sleep(2)
    # 달력 적용 선택 
    driver.find_element(By.CLASS_NAME,"btn_wrap").find_element(By.CLASS_NAME,"btn_bn-blue").click()

def startReservation(driver , settings):
    find_flag = 0 
    while True: 
        # 오류 wrap창 확인
        # if len(driver.find_elements(By.CLASS_NAME, 'layerWrap')) != 0:
        #     driver.refresh()
        #     time.sleep(1)
        #     continue
        # time.sleep(2)
        no_seat = 0
        top1 = driver.find_element(By.CLASS_NAME,"tckWrap")
        top2 = top1.find_elements(By.CLASS_NAME,"tck_inner")

        for content in top2:
            find_train_number = content.find_element(By.CLASS_NAME, 'info_inner.fl-l').text.split("\n")[1]
            
            if find_train_number == settings['trainNumber']:
                normal_seat = content.find_elements(By.CLASS_NAME, "price_box.fl-l")[0].text

                if "일반실" in normal_seat:
                    print("예매 가능!")

                    ## 예매 일반실 클릭 
                    content.find_elements(By.CLASS_NAME, "price_box.fl-l")[0].click()

                    ## ~~ 거쳐가는 곳입니다. / 시스템 통신 대기 .... 등 있음 
                    
                    # 혹시 close popup버튼 이 있다면 클릭
                    # if driver.find_element(By.CLASS_NAME,"btn_pop-close").click()

                    time.sleep(0.5)
                    # 예매버튼 누르기
                    wait = WebDriverWait(driver, 15)  # 최대 15초 기다림
                    if len(driver.find_elements(By.CLASS_NAME,"btn_pop-close")) != 0 :
                        driver.find_element(By.CLASS_NAME,"btn_pop-close").click()
                    # 예: 버튼이 클릭 가능해질 때까지 대기
                    
                    # 예: 버튼이 클릭 가능해질 때까지 대기
                    btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"btn_bn-blue02.reservbtn")))
                    btn.click() 
                    # driver.find_element(By.CLASS_NAME,"btn_bn-blue02.reservbtn").click()

                    time.sleep(0.5)
                    # 잔여석 없을때 
                    if len(driver.find_elements(By.CLASS_NAME,"btn_pop-close")) != 0 :
                        driver.find_element(By.CLASS_NAME,"btn_pop-close").click()
                        time.sleep(2)
                        no_seat = 1 
                        break
                    find_flag = 1
                    break
                else:
                    print("일반실이 없습니다. refresh!")
                    no_seat = 1 
                    break
        if find_flag == 1:
            print("======= 예매 완료!!!!!!!!!!!!!")
            telegram_utils.send_message("예매가 완료됐습니다. 결제 진행해주세요.")
            break
        if no_seat == 1 :
            driver.refresh()
            time.sleep(1)
            continue

        element = driver.find_element(By.TAG_NAME, "body")
        # 왼쪽 → 오른쪽 이동
        for x in range(0, 400, 100):
            ActionChains(driver).move_to_element_with_offset(element, x, 200).perform()
            time.sleep(0.2)


        # 여러 번에 나눠서 천천히 스크롤
        for _ in range(4):
            ActionChains(driver).scroll_by_amount(0, 200).perform()  # (x, y) 만큼 스크롤
            time.sleep(1)
        time.sleep(1)
        try:
            driver.find_element(By.CLASS_NAME,'page_group').click()
            time.sleep(1)
        except:
            print("정확한 열차 번호를 입력해주세요.")
            break


def run():
    
    ################# run ###################3
    userInfo ,settings = read_info() # user , settings 

    # login 시도
    pageLogin(driver ,userInfo )
    time.sleep(2)
    # 예매 페이지로 이동
    driver.get("https://www.korail.com/ticket/search/general")
    time.sleep(2)

    # 출발 <-> 도착 선택
    selectPort(driver, settings["start"] , True)
    selectPort(driver, settings["end"] , False)

    time.sleep(2)
    ############################# 달력에서 원하는 날 선택
    # selectCalendar(driver , settings) #-> Server에서는 조금 문제 존재함

    # 예매하기 클릭 
    driver.find_element(By.CLASS_NAME , "btn_lookup").click()
    time.sleep(2)
    # 매크로 알림창 예방 
    driver.refresh()

    ########################## 예매창 Scroll.... -> 기차 번호를 기준으로 진행함.
    print("################# 실제 예매 서칭 .... ##########################")


    user , settings = read_info()
    startReservation(driver , settings)
    ## 20분 이내의 열차는 온라인으로 예매 불가능 -> 창구에서 해야함 
    driver.quit()