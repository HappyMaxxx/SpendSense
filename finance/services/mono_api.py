import requests
from django.conf import settings
from datetime import datetime, timedelta
import time

class MonobankAPI:
    BASE_URL = "https://api.monobank.ua"

    @staticmethod
    def get_client_info(token):
        url = "https://api.monobank.ua/personal/client-info"
        headers = {"X-Token": token}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def get_statement(token, account_id, from_date, to_date=None):
        headers = {"X-Token": token}
        if not to_date:
            to_date = int(time.time())
        from_date = int(from_date.timestamp())
        url = f"{MonobankAPI.BASE_URL}/personal/statement/{account_id}/{from_date}/{to_date}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()