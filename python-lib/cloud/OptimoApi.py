from dataclasses import dataclass
import json
import requests

@dataclass
class Sample:
    timestamp: int
    value: float

@dataclass
class VariableData:
    variable_id: str
    samples: list[Sample]


class OptimoApi(object):
    API_ENDPOINT = "https://prod.api.optimoiot.it"

    def __init__(self, api_key: str, app_id: str, app_secret: str) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        if not api_key.startswith("apik_"):
            raise ValueError("api_key must start with 'apik_'")
        if not app_id:
            raise ValueError("app_id is required")
        if not app_id.startswith("app_id_"):
            raise ValueError("app_id must start with 'app_id_'")
        if not app_secret:
            raise ValueError("app_secret is required")
        if not app_secret.startswith("secret_"):
            raise ValueError("app_secret must start with 'secret_'")
        self.api_key = api_key
        self.app_id = app_id
        self.app_secret = app_secret


    def _do_post_request(self, endpoint, payload):
        r = requests.post(f"{OptimoApi.API_ENDPOINT}/{endpoint}", data=json.dumps(payload), timeout=60, headers={
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'APP_ID': self.app_id,
            'APP_SECRET': self.app_secret,
        })
        r.raise_for_status()
        return r.json()

    def get_latest_values(self, variable_ids: list[str]) -> dict[str, Sample]:
        """
        Get the latest value of a list of variables
        """
        payload = list(map(lambda variable_id: {"variable_id": variable_id, "limit": 1}, variable_ids))
        response = self._do_post_request("timeseries", payload)
        response_dict = {}
        for i, variable_id in enumerate(variable_ids):
            if len(response[i]["values"]) == 0:
                response_dict[variable_id] = None
            else:
                response_dict[variable_id] = response[i]["values"][0]
        return response_dict
    
    def get_latest_value(self, variable_id: str) -> Sample | None:
        """
        Get the latest value of a single variable
        """
        return self.get_latest_values([variable_id])[variable_id]

    def get_values_in_range(self, variable_ids: list[str], from_unix_ms_timestamp: float, to_unix_ms_timestamp: float, limit: float = 10000) -> dict[str, list[Sample]]:
        """
        Get the values of a list of variables in a specific time range.
        Pagination is handled automatically.
        """
        payload = list(map(lambda variable_id: {
            "variable_id": variable_id,
            "forward": False,
            "limit": limit,
            "from": from_unix_ms_timestamp,
            "to": to_unix_ms_timestamp,
        }, variable_ids))
        response = self._do_post_request("timeseries", payload)
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
            response = self._do_post_request("timeseries", list(map(lambda page: page["query"], next_pages)))
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

    def set_value(self, variable_id: str, value: float):
        """
        Send a command to the gateway to set the value of a variable
        """
        payload = {
                "value": value,
            }
        response = self._do_post_request(f"setpoint/{variable_id}", payload)
        return response

    def injest_values(self, data: list[VariableData]):
        """
        Injest samples to the cloud DB. Only applicable for variables marked as "injestable"
        """
        response = self._do_post_request(f"injest", data)
        return response

    def delete_injested_values(self, variable_ids: list[str], from_unix_ms_timestamp: float, to_unix_ms_timestamp: float):
        """
        Delete injested values in a specific time range
        """
        response = self._do_post_request(f"injest", {
            "variable_ids": variable_ids,
            "from": from_unix_ms_timestamp,
            "to": to_unix_ms_timestamp,
        })
        return response