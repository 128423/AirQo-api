import os
import traceback

import requests


class AirQoApi:
    def __init__(self):
        self.AIRQO_BASE_URL = os.getenv("AIRQO_BASE_URL")
        self.AIRQO_API_KEY = f"JWT {os.getenv('AIRQO_API_KEY')}"

    def get_events(self, tenant, start_time, end_time, device):
        headers = {'Authorization': self.AIRQO_API_KEY}

        params = {
            "tenant": tenant,
            "frequency": 'raw',
            "device": device,
            "startTime": start_time,
            "endTime": end_time
        }

        try:
            api_request = requests.get(
                '%s%s' % (self.AIRQO_BASE_URL, 'devices/events'),
                params=params,
                headers=headers,
                verify=False
            )

            if api_request.status_code == 200 and "measurements" in api_request.json():
                return api_request.json()["measurements"]

            print(api_request.request.url)
            print(api_request.request.body)
            print(api_request.content)
            return []
        except:
            traceback.print_exc()
            return []

    def get_devices(self, tenant):
        headers = {'Authorization': self.AIRQO_API_KEY}

        params = {
            "tenant": tenant,
            "active": 'yes',
        }

        try:
            api_request = requests.get(
                '%s%s' % (self.AIRQO_BASE_URL, 'devices'),
                params=params,
                headers=headers,
                verify=False
            )

            if api_request.status_code == 200 and "devices" in api_request.json():
                return api_request.json()["devices"]

            print(api_request.request.url)
            print(api_request.request.body)
            print(api_request.content)
            return []
        except:
            traceback.print_exc()
            return []
