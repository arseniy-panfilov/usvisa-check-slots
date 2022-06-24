import logging
from datetime import datetime

from src.config import TARGET_DATE


def check_results(name, results):
    logging.info(f"Inspecting dates for {name}...")
    dates = [
        datetime.strptime(record["date"], "%Y-%m-%d").date()
        for record in results
    ]
    dates.sort()
    if not dates:
        return

    earliest = dates[0]
    if earliest < TARGET_DATE:
        logging.info(f"Found better date in {name}: {earliest}.")
        notify_new_slot(name, earliest)
    else:
        logging.warning("Nothing new.")


def notify_new_slot(name, slot_date):
    """
    Do whatever you want with the new slot.
    E.g. you can create a Slack org and send yourself a notification:

        msg = f"<@U01234567> NEW SLOT AVAILABLE!\n\n*{name}: {slot_date}*"
        logging.warning(msg)
        requests.post(
            "https://hooks.slack.com/services/FOO/BAR/YOUR_ENDPOINT",
            json={"text": msg},
        )

    Or send an SMS to yourself?
    Or maybe even make the bot book the slot automatically?

    Your choice.
    """
    raise NotImplementedError
