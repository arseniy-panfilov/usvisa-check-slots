import logging
from json import JSONDecodeError

import requests

from src.auth import USER_AGENT, delete_cookie, get_cookies, set_cookie
from src.check_results import check_results
from src.config import ACCOUNT_ID, SESSION_COOKIE

headers = {
    "Connection": "keep-alive",
    "sec-ch-ua": '"Chromium";v="108", " Not A;Brand";v="99", "Google Chrome";v="108"',
    "Accept": "*/*",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": USER_AGENT,
    "X-Requested-With": "XMLHttpRequest",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": f"https://ais.usvisa-info.com/en-ca/niv/schedule/{ACCOUNT_ID}/appointment",
    "Accept-Language": "en-US,en;q=0.9",
}

CITIES_TO_CHECK = [(92, "Ottawa"), (93, "Quebec")]


def make_request():
    cookies = get_cookies()
    for key, name in CITIES_TO_CHECK:
        r = requests.get(
            f"https://ais.usvisa-info.com/en-ca/niv/schedule/{ACCOUNT_ID}/appointment/days/{key}.json?appointments[expedite]=false",
            cookies=cookies,
            headers=headers,
        )
        if r.ok:
            set_cookie(r.cookies.get(SESSION_COOKIE))
        else:
            logging.info(f"Deleting cookie: response status was {r.status_code}")
            return delete_cookie()

        try:
            result = r.json()
        except JSONDecodeError as err:
            logging.info(f"Deleting cookie: got json encoding error {err}")
            return delete_cookie()

        check_results(name, result)


if __name__ == "__main__":
    make_request()
