import logging
import os
import os.path
import os.path
import random
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait

from src.config import (CHROMEDRIVER_PATH, COOKIE_PATH, PASSWORD, SESSION_COOKIE,
                        AUTO_REFRESH_AUTH, USER)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
logging.basicConfig(format="[%(asctime)s] %(message)s", level=logging.INFO)


def get_cookies():
    if not os.path.exists(COOKIE_PATH):
        if AUTO_REFRESH_AUTH:
            selenium_auth()
        else:
            logging.warning("cookie is gone")
            exit(0)

    with open(COOKIE_PATH, "r") as cookie:
        return {
            SESSION_COOKIE: cookie.read().strip()
        }


def set_cookie(cookie):
    with open(COOKIE_PATH, "w") as cookie_file:
        logging.info("update cookie")
        cookie_file.write(cookie)


def delete_cookie():
    logging.info("DELETE cookie")
    os.remove(COOKIE_PATH)


def get_csrf(response):
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.find("meta", attrs={"name": "csrf-token"}).get("content")


def selenium_auth():
    driver = get_driver()

    # Bypass reCAPTCHA
    driver.get("https://ais.usvisa-info.com/en-ca/niv")
    time.sleep(1)
    a = driver.find_element_by_xpath('//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    logging.info("start sign")
    href = driver.find_element_by_xpath(
        '//*[@id="header"]/nav/div[2]/div[1]/ul/li[3]/a'
    )
    href.click()
    time.sleep(1)
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    logging.info("click bounce")
    a = driver.find_element_by_xpath('//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(1)

    do_login_action(driver)


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1440,794")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f'user-agent={USER_AGENT}')
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)


def do_login_action(driver):
    logging.info("input email")
    user = driver.find_element_by_id("user_email")
    user.send_keys(USER)
    time.sleep(random.randint(1, 3))

    logging.info("input pwd")
    pw = driver.find_element_by_id("user_password")
    pw.send_keys(PASSWORD)
    time.sleep(random.randint(1, 3))

    logging.info("click privacy")
    box = driver.find_element_by_class_name("icheckbox")
    box.click()
    time.sleep(random.randint(1, 3))

    logging.info("commit")
    btn = driver.find_element_by_name("commit")
    btn.click()
    time.sleep(random.randint(1, 3))

    cookie = driver.get_cookie(SESSION_COOKIE)["value"]
    if len(cookie) > 400:
        logging.info("Login successful!")

        set_cookie(driver.get_cookie(SESSION_COOKIE)["value"])
        driver.quit()
        return

    else:
        driver.quit()
        logging.error("Couldn't obtain cookie, better luck next time")
        exit()


if __name__ == "__main__":
    selenium_auth()
