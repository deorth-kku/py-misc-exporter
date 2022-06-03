#!/usr/bin/python3
#import os,sys
from requests.utils import unquote
import logging
from prometheus_client import Gauge, Info
if __package__=='':
    from _tpapi import TPapi
else:
    from ._tpapi import TPapi

def only_str(input_dict: dict) -> dict:
    out_dict = {}
    for arg in input_dict:
        if type(input_dict[arg]) == str:
            out_dict.update({arg: input_dict[arg]})
    return out_dict



tplink_cap_host_num = Gauge('tplink_cap_host_num', 'tplink online device num')
tplink_cap_guest_num = Gauge(
    'tplink_cap_guest_num', 'tplink online guest device num')
tplink_wan_status_up_time = Gauge(
    'tplink_wan_status_up_time', 'tplink wan uptime')
tplink_wan_status_up_speed = Gauge(
    'tplink_wan_status_up_speed', 'tplink wan upload speed (KB)')
tplink_wan_status_down_speed = Gauge(
    'tplink_wan_status_down_speed', 'tplink wan download speed (KB)')
tplink_wan_status = Info("tplink_wan_status", "tplink full wan status")

tplink_wanv6_status_up_time = Gauge(
    'tplink_wanv6_status_up_time', 'tplink wan ipv6 uptime')
tplink_wanv6_status = Info("tplink_wanv6_status",
                           "tplink full wan ipv6 status")

tplink_host_info_down_speed = Gauge(
    'tplink_host_info_down_speed', 'tplink lan device download speed', ["ip", "hostname", "mac", "ipv6", "type"])
tplink_host_info_up_speed = Gauge(
    'tplink_host_info_up_speed', 'tplink lan device upload speed', ["ip", "hostname", "mac", "ipv6", "type"])

conn = None


def main(**config) -> None:
    logging.debug("start refresh tp-link explorer")
    global conn
    url = "http://%s/" % config.get("host", "tplogin.cn")
    if not conn:
        conn = TPapi(url, config["password"])
    data = {
        "method": "get",
        "network": {
            "name": [
                "wan_status",
                "wanv6_status"
            ]
        },
        "hosts_info": {
            "table": "online_host",
            "name": "cap_host_num"
        }
    }
    try:
        result = conn.apipost(data)
    except Exception as e:
        if str(e).endswith("-40101"):
            data["network"]["name"].remove("wanv6_status")
            result = conn.apipost(data)
        else:
            logging.exception(e)
            conn = None
            return
    tplink_wan_status_up_time.set(result["network"]["wan_status"]["up_time"])
    tplink_wan_status_down_speed.set(
        result["network"]["wan_status"]["down_speed"])
    tplink_wan_status_up_speed.set(result["network"]["wan_status"]["up_speed"])

    tplink_wan_status.info(only_str(result["network"]["wan_status"]))

    tplink_wanv6_status_up_time.set(
        result["network"].get("wanv6_status", {}).get("up_time", 0))

    tplink_wanv6_status.info(
        only_str(result["network"].get("wanv6_status", {})))

    tplink_cap_host_num.set(result["hosts_info"]["cap_host_num"]["host_num"])
    tplink_cap_guest_num.set(result["hosts_info"]["cap_host_num"]["guest_num"])

    tplink_host_info_down_speed.clear()
    tplink_host_info_up_speed.clear()

    for host in result["hosts_info"]["online_host"]:
        info = list(host.values())[0]

        device_types = ["wired", "wifi_2.4g", "wifi_5g"]
        device_type = device_types[int(info["type"])+int(info["wifi_mode"])]

        tplink_host_info_down_speed.labels(
            ip=info["ip"],
            hostname=unquote(info["hostname"]),
            ipv6=info.get("ipv6", "::"),
            mac=info["mac"],
            type=device_type
        ).set(info["down_speed"])
        tplink_host_info_up_speed.labels(
            ip=info["ip"],
            hostname=unquote(info["hostname"]),
            ipv6=info.get("ipv6", "::"),
            mac=info["mac"],
            type=device_type
        ).set(info["up_speed"])


if __name__ == "__main__":
    pass
