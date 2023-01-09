import logging
from datetime import datetime

from src.config import TARGET_DATE, TWILIO_CONFIG
from src.twilio import TwilioClient


def check_results(name, results):
    logging.info(f"Inspecting dates for {name}...")
    dates = [datetime.strptime(record["date"], "%Y-%m-%d").date() for record in results]
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
    client = TwilioClient(TWILIO_CONFIG)
    client.send_message(f"NEW SLOT AVAILABLE!\n{name}: {slot_date}")
