#!/bin/python3
import requests
import logging
from requests.utils import quote,unquote


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

    def __init__(self, url: str, passwd: str = None, encrypted: str = False, stok: str = None) -> None:
        self.url = url
        if stok == None:
            if not encrypted:
                passwd = TPapi.passwdEncryption(passwd)
            data = {"method": "do", "login": {"password": passwd}}
            req = requests.post(url=self.url, json=data)
            try:
                stok = req.json()["stok"]
            except KeyError:
                raise ValueError("Incorrect password")
        self.stok = stok
        self.apiurl = self.url+"stok=%s/ds" % stok

    def apipost(self, data: dict):
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

    def getsyslog(self, page:int=1, num_per_page:int=20):
        data = {
            "system": {
                "read_logs": {
                    "page": page,
                    "num_per_page": num_per_page
                }
            },
            "method": "do"}
        syslog=self.apipost(data)["syslog"]
        out=[]
        log_levels=["","DEBUG","INFO","NOTICE","WARNING","ERROR","CRITICAL"]
        for line in syslog:
            name=list(line.keys())[0]    

            text=unquote(line[name])
            level=log_levels[int(text[1])]
            text=text[3:]
            text=text.split(",")
            days_str=text[0]
            hour_str,min_str,sec_str=text[1].split(":")
            text=",".join(text[2:])
            days:int=int(days_str.rstrip("days"))
            hour:int=int(hour_str.lstrip(" "))
            minute:int=int(min_str)
            second:int=int(sec_str)
            uptime=days*86400+hour*3600+minute*60+second
            out.append({
                "name":name,
                "text":text,
                "level":level,
                "uptime":uptime
                })
        return out

        

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


if __name__ == "__main__":
    pass
