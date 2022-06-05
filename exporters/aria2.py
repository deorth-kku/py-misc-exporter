#!/bin/python3
from utils import Aria2Rpc
from prometheus_client import Gauge,Info
import os
import logging

aria2_task_metrics={}
aria2_global_metrics={}
conn=None

def __main(**config):
    global conn
    if not conn:
        conn = Aria2Rpc(**config)
    sel_para = ["gid", "totalLength", "completedLength", "uploadSpeed", "downloadSpeed", "connections", "numSeeders", "files", "bittorrent"]
    active_stat = conn.tellActive(sel_para)
    global_stat = conn.getGlobalStat()
    for task in active_stat:
        if "bittorrent" in task:
            bittorrent="1"
            if "info" in task["bittorrent"]:
                name=task["bittorrent"]["info"]["name"]
            else:
                name=task["files"][0]["path"]
            task.pop("bittorrent")
            
        else:
            bittorrent="0"
            logging.debug("set task name from filename %s ,gid %s"%(task["files"][0]["path"],task["gid"]))
            name=os.path.basename(task["files"][0]["path"])
            
            
            
        gid=task.pop("gid")
        for arg in task:
            metric_name="aria2_task_"+arg
            if metric_name in aria2_task_metrics:
                metric_obj=aria2_task_metrics[metric_name]
            else:
                logging.debug("add metric %s"%metric_name)
                metric_obj=Gauge(metric_name,"",["gid","name","bittorrent"])
                aria2_task_metrics.update({metric_name:metric_obj})
            try:
                value=float(task[arg])
            except (ValueError,TypeError):
                continue
            metric_obj.labels(gid,name,bittorrent).set(value)

    for arg in global_stat:
        metric_name="aria2_global_"+arg
        if metric_name in aria2_global_metrics:
            metric_obj=aria2_global_metrics[metric_name]
        else:
            logging.debug("add metric %s"%metric_name)
            metric_obj=Gauge(metric_name,"")
            aria2_global_metrics.update({metric_name:metric_obj})
        try:
            value=float(global_stat[arg])
        except (ValueError,TypeError):
            continue
        metric_obj.set(value)

def main(**config):
    try:
        return __main(**config)
    except Exception as e:
        logging.exception(e)
        raise

if __name__ == "__main__":
    pass
