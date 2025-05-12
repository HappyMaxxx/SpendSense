import requests
from django.conf import settings
from datetime import datetime, timedelta
import time

class MonobankAPI:
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
        url = f"https://api.monobank.ua/personal/statement/{account_id}/{from_date}/{to_date}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def get_all_transactions(token, account_id):
        headers = {'X-Token': token}

        now = datetime.now()
        from_time = int((now - timedelta(days=30)).timestamp())
        to_time = int(now.timestamp())

        url = f'https://api.monobank.ua/personal/statement/{account_id}/{from_time}/{to_time}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()