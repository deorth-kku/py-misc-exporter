#!/usr/bin/python3
#import os,sys
import requests
from requests.utils import quote, unquote
import logging
from prometheus_client import Gauge, Info


def only_str(input_dict: dict) -> dict:
    out_dict = {}
    for arg in input_dict:
        if type(input_dict[arg]) == str:
            out_dict.update({arg: input_dict[arg]})
    return out_dict


class TPapi:
    @staticmethod
    def passwdEncryption(PassWd):
        Secret_key = "RDpbLfCPsJZ7fiv"
        Encrypted_string = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"

        L_PassWd = len(PassWd)
        L_Secret_Ket = len(Secret_key)
        L_Encrypted_string = len(Encrypted_string)
        e = max(L_PassWd, L_Secret_Ket)

        result = []
        for l in range(e):
            m = chr(187)
            k = chr(187)
            if l >= L_PassWd:
                m = Secret_key[l]
            else:
                if l >= L_Secret_Ket:
                    k = PassWd[l]
                else:
                    k = PassWd[l]
                    m = Secret_key[l]
            k = ord(k)
            m = ord(m)
            result.append(Encrypted_string[(k ^ m) % L_Encrypted_string])

        return "".join(result)

    @staticmethod
    def ruleConvert(rule):
        name = list(rule.keys())[0]
        attr = list(rule.values())[0]
        return name, attr

    def __init__(self, url, passwd, encrypted=False):
        self.url = url
        if not encrypted:
            passwd = TPapi.passwdEncryption(passwd)
        data = {"method": "do", "login": {"password": passwd}}
        req = requests.post(url=self.url, json=data)
        try:
            stok = req.json()["stok"]
        except KeyError:
            raise ValueError("Incorrect password")

        self.apiurl = self.url+"stok=%s/ds" % stok

    def apipost(self, data):
        req = requests.post(url=self.apiurl, json=data)
        ret = req.json()
        if ret["error_code"] != 0:
            raise RuntimeError("TP api return error code %s" %
                               ret["error_code"])
        return ret

    def __getattr__(self, name):
        if name.startswith("get"):
            self.methodname = name.lstrip("get")
            return self.__defaultMethod

    def __defaultMethod(self, *args):
        data = {"network": {"name": self.methodname}, "method": "get"}
        return self.apipost(data)

    def reconnectv6(self):
        logging.info("reconnet ipv6 now")
        data = {"network": {"change_wanv6_status": {
            "proto": "pppoev6", "operate": "connect"}}, "method": "do"}
        return self.apipost(data)

    def reconnectv4(self):
        logging.info("reconnet ipv4 now")
        data = {"network": {"change_wan_status": {
            "proto": "pppoe", "operate": "connect"}}, "method": "do"}
        return self.apipost(data)

    def setv6dns(self, dns1, dns2="::1"):
        logging.info("set ipv6 dns %s" % dns1)
        dns1 = quote(dns1)
        dns2 = quote(dns2)
        data = {
            "protocol": {
                "pppoev6": {"pri_dns": dns1, "snd_dns": dns2}}, "method": "set"
        }
        return self.apipost(data)

    def getfwrules(self):
        data = {"firewall": {"table": "redirect"}, "method": "get"}
        return self.apipost(data)["firewall"]["redirect"]

    def gethostinfo(self):
        data = {"hosts_info": {"table": "host_info",
                               "name": "cap_host_num"}, "method": "get"}
        return self.apipost(data)

    def getcurhostinfo(self):
        hosts = self.gethostinfo()["hosts_info"]["host_info"]
        for host in hosts:
            info = list(host.values())[0]
            if info["is_cur_host"] == "1":
                return info

    def gethostinfobymac(self, mac):
        mac = mac.lower()
        mac = mac.replace(":", "-")
        hosts = self.gethostinfo()["hosts_info"]["host_info"]
        for host in hosts:
            info = list(host.values())[0]
            if info["mac"] == mac:
                return info
        logging.warning("cannot find host by mac %s" % mac)

    def delfwrule(self, rule_name):
        data = {"firewall": {"name": [rule_name]}, "method": "delete"}
        return self.apipost(data)

    def addfwrule(self, port, ipv4="", ipv6="", proto="all", name=None):
        logging.debug("add rule %s %s %s %s" % (ipv4, ipv6, port, proto))
        if name == None:
            num = 0
            for rule in self.getfwrules():
                rulename, _ = TPapi.ruleConvert(rule)
                if rulename.startswith("redirect"):
                    num = int(rulename.split("_")[1])
            name = "redirect_%d" % (num+1)

        if ipv4 == "" and ipv6 == "":
            raise ValueError("you must input at lease one ip")

        ipv6 = quote(ipv6)
        port = str(port)
        data0 = {
            "firewall": {
                "table": "redirect",
                "name": name,
                "para": {
                    "proto": proto,
                    "src_dport_start": port,
                    "src_dport_end": port,
                    "dest_port": port,
                    "wan_port": 0,
                    "dest_ip": ipv4,
                    "dest_ip6": ipv6
                }
            },
            "method": "add"}
        return self.apipost(data0)

    def reboot(self):
        logging.warning("reboot router now")
        data = {"system": {"reboot": None}, "method": "do"}
        return self.apipost(data)


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
    'tplink_host_info_down_speed', 'tplink lan device download speed', ["ip", "hostname", "mac", "ipv6","type"])
tplink_host_info_up_speed = Gauge(
    'tplink_host_info_up_speed', 'tplink lan device upload speed', ["ip", "hostname", "mac", "ipv6","type"])

tplink_host_info_wired_count = Gauge(
    'tplink_host_info_wired_count', 'tplink lan wired device count')
tplink_host_info_wifi_2_4g_count = Gauge(
    'tplink_host_info_wifi_2_4g_count', 'tplink lan 2.4g wifi device count')
tplink_host_info_wifi_5g_count = Gauge(
    'tplink_host_info_wifi_5g_count', 'tplink lan 5g wifi device count')

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
        result["network"].get("wanv6_status",{}).get("up_time",0))

    tplink_wanv6_status.info(only_str(result["network"].get("wanv6_status",{})))

    tplink_cap_host_num.set(result["hosts_info"]["cap_host_num"]["host_num"])
    tplink_cap_guest_num.set(result["hosts_info"]["cap_host_num"]["guest_num"])

    tplink_host_info_down_speed.clear()
    tplink_host_info_up_speed.clear()

    wired_count = 0
    wifi_2_4g_count = 0
    wifi_5g_count = 0
    for host in result["hosts_info"]["online_host"]:
        info = list(host.values())[0]

        if info["type"] == "0":
            wired_count += 1
            device_type="wired"
        elif info["wifi_mode"] == "0":
            wifi_2_4g_count += 1
            device_type="wifi_2.4g"
        else:
            wifi_5g_count += 1
            device_type="wifi_5g"


        tplink_host_info_down_speed.labels(
            ip=info["ip"],
            hostname=unquote(info["hostname"]),
            ipv6=info.get("ipv6","::"),
            mac=info["mac"],
            type=device_type
        ).set(info["down_speed"])
        tplink_host_info_up_speed.labels(
            ip=info["ip"],
            hostname=unquote(info["hostname"]),
            ipv6=info.get("ipv6","::"),
            mac=info["mac"],
            type=device_type
        ).set(info["up_speed"])
        
    tplink_host_info_wired_count.set(wired_count)
    tplink_host_info_wifi_2_4g_count.set(wifi_2_4g_count)
    tplink_host_info_wifi_5g_count.set(wifi_5g_count)


if __name__ == "__main__":
    url = "http://%s/" %"tplogin.cn"
    conn = TPapi(url, "Huawei12#$").apipost({
        "method": "get",
        "network": {
            "name": [
                "wan_status",
                "wanv7_status"
            ]
        },
    })
