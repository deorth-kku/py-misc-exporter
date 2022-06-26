#!/bin/python3
import os
from utils import JsonConfig
from utils import Url
import requests
from slugify import slugify


class Grafana:
    def __init__(self, site: str, apikey: str) -> None:
        self.site = site
        self.apikey = apikey
        headers = {
            "Authorization": "Bearer %s" % apikey,
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(headers)

    def get_dashboard(self, uid: str) -> dict:
        url = Url.join(self.site, "api/dashboards/uid/", uid)
        req = self.session.get(url)
        return req.json()


def main():
    working_dir = os.path.dirname(__file__)
    os.chdir(working_dir)
    conf = JsonConfig("dashboards.json")
    G = Grafana(conf["site"], conf["apikey"])
    for uid in conf["dashboards"]:
        dashboard_json = G.get_dashboard(uid)
        title = dashboard_json["dashboard"]["title"]
        jfile = JsonConfig("dashboards/%s.json" % slugify(title))
        jfile.dumpconfig(dashboard_json["dashboard"])


if __name__ == "__main__":
    main()
