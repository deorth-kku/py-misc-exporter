#!/bin/python3
import sys
if __package__=="":
    from _tpapi import *

if __name__ == "__main__":
    conn = TPapi("http://tplogin.cn/", stok=open("/mnt/temp/tpapi_stok","r").read())
    data = {
        "method": "get",
        "dhcpd": {
           "table":"dhcp_clients"
        },
        "upnpd":{
            "table":"upnp_lease"
        }
    }

    data={
        "method": "set",
        "custom_multi_ssid":{
            "wlan_multi_ssid_5g_2":{
                "enable":1
            }
        }
    }
    po = conn.apipost(data)
    sys.exit()
