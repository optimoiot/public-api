import os
from OptimoApi import OptimoApi

API_KEY = os.environ.get("OPTIMO_API_KEY") # e.g. "apik_****"
APP_ID = os.environ.get("OPTIMO_APP_ID") # e.g. "app_id_****"
APP_SECRET = os.environ.get("OPTIMO_APP_SECRET") # e.g. "secret_****"

api = OptimoApi(api_key=API_KEY, app_id=APP_ID, app_secret=APP_SECRET)

variable_id = "XXXXX_YYYYY"
response = api.get_latest_value(variable_id)
print(response)
"""
{
    "timestamp": 1612137600000,
    "value": 1
}
"""
response = api.get_latest_values(["XXXXX_YYYYY", "XXXXX_ZZZZZ"])
print(response)
"""
{
    "XXXXX_YYYYY": {
        "timestamp": 1612137600000,
        "value": 1
    },
    "XXXXX_ZZZZZ": {
        "timestamp": 1612137600000,
        "value": 2
    }
}
"""
response = api.get_values_in_range(["XXXXX_YYYYY"], from_unix_ms_timestamp=1612137600000, to_unix_ms_timestamp=1612137600000)
print(response)
"""
{
    "XXXXX_YYYYY": [
        {
            "timestamp": 1612137600000,
            "value": 1
        },
        {
            "timestamp": 1612137660000,
            "value": 1
        }
    }
]
"""


# Set value of variable to 1
api.set_value("XXXXX_YYYYY", 1)