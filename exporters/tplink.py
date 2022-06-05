#!/usr/bin/python3
#import os,sys
from requests.utils import unquote
import logging
from prometheus_client import Gauge, Info
if __package__ == '':
    from _tpapi import TPapi
else:
    from ._tpapi import TPapi


def only_str(input_dict: dict, convert: bool = False) -> dict:
    out_dict = {}
    for arg in input_dict:
        if type(input_dict[arg]) == str:
            out_dict.update({arg: input_dict[arg]})
        elif convert:
            vv = str(input_dict[arg])
            out_dict.update({arg: vv})
    return out_dict


def unquote_hostname(input: dict) -> dict:
    input.update({"hostname": unquote(input["hostname"])})
    return input


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
    'tplink_host_info_down_speed', 'tplink lan device download speed', ["ip", "hostname", "mac"])
tplink_host_info_up_speed = Gauge(
    'tplink_host_info_up_speed', 'tplink lan device upload speed', ["ip", "hostname", "mac"])
tplink_host_info_detail = None

tplink_realtime_push_msg = Gauge(
    "tplink_realtime_push_msg", "pushed messages", ["msgId", "eventType", "content", "encodeType", "time", "mac", "runtime"])

tplink_system_logs = Gauge(
    "tplink_system_logs", "tplink system log", ["text", "level", "name"])

tplink_port_manage_dev_info = Info(
    "tplink_port_manage_dev", "tplink route device info")
tplink_system_logs_uptime = 0
conn = None


def __main(**config) -> None:
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
            "table": "host_info",
            "name": "cap_host_num"
        },
        "system": {
            "table": "realtime_push_msg"
        },
        "port_manage": {
            "table": "dev_info",
        },
        "dhcpd": {
            "table": "dhcp_clients"
        },
        "upnpd": {
            "table": "upnp_lease"
        }
    }
    try:
        result = conn.apipost(data)
    except Exception as e:
        if str(e) == "ESYSTEM":
            data["network"]["name"].remove("wanv6_status")
            result = conn.apipost(data)
        else:
            logging.exception(e)
            conn = None
            return
    # add route info
    tplink_port_manage_dev_info.info(
        only_str(result["port_manage"]["dev_info"][0]))

    # add wired lan port info
    global tplink_port_manage_phy_info
    try:
        tplink_port_manage_phy_info.clear()
    except NameError:
        info_template = result["port_manage"]["dev_info"][0]["phy_info"][0]
        info_keys = list(info_template.keys())
        info_keys.remove("status")
        tplink_port_manage_phy_info = Gauge(
            "tplink_port_manage_phy_info", "tplink wired lan port info", info_keys)
    for port in result["port_manage"]["dev_info"][0]["phy_info"]:
        status = int(port.pop("status"))
        tplink_port_manage_phy_info.labels(**port).set(status)

    # add dhcp clients info
    global tplink_dhcpd_dhcp_clients
    try:
        tplink_dhcpd_dhcp_clients.clear()
    except NameError:
        info_template = list(result["dhcpd"]["dhcp_clients"][0].values())[0]
        info_keys = list(info_template.keys())
        info_keys.remove("expires")
        tplink_dhcpd_dhcp_clients = Gauge(
            "tplink_dhcpd_dhcp_clients", "tplink dhcp clients expires time in seconds", info_keys)
    for client in result["dhcpd"]["dhcp_clients"]:
        info = list(client.values())[0]
        info = unquote_hostname(info)
        expires = int(info.pop("expires"))
        tplink_dhcpd_dhcp_clients.labels(**info).set(expires)

    # add upnp lease info
    global tplink_upnpd_upnp_lease
    try:
        tplink_upnpd_upnp_lease.clear()
    except NameError:
        info_template = list(result["upnpd"]["upnp_lease"][0].values())[0]
        info_keys = list(info_template.keys())
        info_keys.remove("enable")
        tplink_upnpd_upnp_lease = Gauge(
            "tplink_upnpd_upnp_lease", "tplink upnp lease info", info_keys)
    for port in result["upnpd"]["upnp_lease"]:
        info = list(port.values())[0]
        enable = info.pop("enable")
        tplink_upnpd_upnp_lease.labels(**info).set(enable)

    # add wan/wanv6 status info
    tplink_wan_status_up_time.set(result["network"]["wan_status"]["up_time"])
    tplink_wan_status_down_speed.set(
        result["network"]["wan_status"]["down_speed"])
    tplink_wan_status_up_speed.set(result["network"]["wan_status"]["up_speed"])

    tplink_wan_status.info(only_str(result["network"]["wan_status"]))

    tplink_wanv6_status_up_time.set(
        result["network"].get("wanv6_status", {}).get("up_time", 0))

    tplink_wanv6_status.info(
        only_str(result["network"].get("wanv6_status", {})))

    # add host/guest host count
    tplink_cap_host_num.set(result["hosts_info"]["cap_host_num"]["host_num"])
    tplink_cap_guest_num.set(result["hosts_info"]["cap_host_num"]["guest_num"])

    # add push msg
    tplink_realtime_push_msg.clear()
    if len(result["system"]["realtime_push_msg"]) > 0:
        msg_dict = result["system"]["realtime_push_msg"][0]['realtime_push_msg_1']['attribute']
        msg_dict = only_str(msg_dict)
        content = unquote(msg_dict["content"])
        msg_dict.update({"content": content})
        tplink_realtime_push_msg.labels(**msg_dict).set(1)

    # add syslog
    tplink_system_logs.clear()
    syslog = conn.getsyslog(num_per_page=150)
    global tplink_system_logs_uptime

    for line in syslog:
        if line["uptime"] > tplink_system_logs_uptime or line["name"] != vars().get("last_name", line["name"]):
            uptime = line["uptime"]
            tplink_system_logs.labels(**only_str(line)).set(uptime)
            tplink_system_logs_uptime = uptime
            last_name = line["name"]
    if "last_name" in dir():
        del last_name

    # add lan hosts info
    tplink_host_info_down_speed.clear()
    tplink_host_info_up_speed.clear()
    global tplink_host_info_detail
    if tplink_host_info_detail:
        tplink_host_info_detail.clear()
    else:
        info_template = only_str(
            result["hosts_info"]["host_info"][-1]["host_info_1"])
        info_keys = list(info_template.keys())
        tplink_host_info_detail = Gauge(
            'tplink_host_info_detail', "detailed host info", info_keys)
    for host in result["hosts_info"]["host_info"]:
        info = list(host.values())[0]
        info = unquote_hostname(info)

        tplink_host_info_down_speed.labels(
            ip=info["ip"],
            hostname=info["hostname"],
            mac=info["mac"]
        ).set(info["down_speed"])
        tplink_host_info_up_speed.labels(
            ip=info["ip"],
            hostname=info["hostname"],
            mac=info["mac"]
        ).set(info["up_speed"])

        tplink_host_info_detail.labels(**only_str(info)).set(1)

def main(**config):
    try:
        return __main(**config)
    except Exception as e:
        logging.exception(e)
        raise


if __name__ == "__main__":
    pass
