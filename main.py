import sys

from src import run, auth

if __name__ == "__main__":
    if "auth" in sys.argv:
        auth.selenium_auth()
    else:
        run.make_request()
