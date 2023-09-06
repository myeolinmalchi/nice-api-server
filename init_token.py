import json
import requests

from requests.auth import HTTPBasicAuth

if __name__ == "__main__":
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    session = requests.Session()

    auth = session.post(f"{config['NICE']['API_URL']}/digital/niceid/oauth/oauth/token")

    res = requests.post(
        f"{config['NICE']['API_URL']}/digital/niceid/oauth/oauth/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "grant_type": "client_credentials",
            "scope": "default"
        },
        auth=HTTPBasicAuth(config['NICE']['CLIENT_ID'], config['NICE']['SECRET_KEY'])
    )

    if res.status_code != 200:
        body = res.json()
        dataBody = body["dataBody"]

        config['NICE']['API_KEY'] = dataBody["access_token"]

    with open("config.json", "w") as f:
        json.dump(config, f)
