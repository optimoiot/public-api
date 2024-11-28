#
# pip install pycognito

import datetime
import json
import math
import requests

class OptimoApi(object):
    API_ENDPOINT = "https://prod.api.optimoiot.it"

    def __init__(self, api_key, app_id, app_secret) -> None:
        self.api_key = api_key
        self.app_id = app_id
        self.app_secret = app_secret


    def do_post_request(self, endpoint, payload):
        r = requests.post(f"{OptimoApi.API_ENDPOINT}/{endpoint}", data=json.dumps(payload), timeout=60, headers={
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'APP_ID': self.app_id,
            'APP_SECRET': self.app_secret,
        })
        r.raise_for_status()
        return r.json()

    def get_latest_values(self, variable_ids):
        payload = list(map(lambda variable_id: {"variable_id": variable_id, "limit": 1}, variable_ids))
        response = self.do_post_request("timeseries", payload)
        response_dict = {}
        for i, variable_id in enumerate(variable_ids):
            if len(response[i]["values"]) == 0:
                response_dict[variable_id] = None
            else:
                response_dict[variable_id] = response[i]["values"][0]
        return response_dict
    
    def get_latest_value(self, variable_id):
        return self.get_latest_values([variable_id])[variable_id]

    def get_values_in_range(self, variable_ids, from_unix_ms_timestamp, to_unix_ms_timestamp, limit=10000):
        payload = list(map(lambda variable_id: {
            "variable_id": variable_id,
            "forward": False,
            "limit": limit,
            "from": from_unix_ms_timestamp,
            "to": to_unix_ms_timestamp,
        }, variable_ids))
        response = self.do_post_request("timeseries", payload)
        response_dict = {}
        next_pages = []
        for i, variable_id in enumerate(variable_ids):
            response_dict[variable_id] = response[i]["values"]
            if response[i].get("next"):
                next_pages.append({
                    "variable_id": variable_id,
                    "query": response[i]["next"]
                })
        
        while len(next_pages) > 0:
            response = self.do_post_request("timeseries", list(map(lambda page: page["query"], next_pages)))
            next_next_pages = []
            for i, next_page in enumerate(next_pages):
                response_dict[next_page["variable_id"]] += response[i]["values"]
                if response[i]["next"]:
                    next_next_pages.append({
                        "variable_id": next_page["variable_id"],
                        "query": response[i]["next"]
                    })
            next_pages = next_next_pages

        return response_dict

    def set_value(self, variable_id, value):
        payload = {
                "value": value,
            }
        response = self.do_post_request(f"setpoint/{variable_id}", payload)
        return response