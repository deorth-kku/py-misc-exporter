#!/bin/python3
from s_tui.sources.util_source import UtilSource
from s_tui.sources.freq_source import FreqSource
from s_tui.sources.temp_source import TempSource
from s_tui.sources.rapl_power_source import RaplPowerSource
from s_tui.sources.fan_source import FanSource
import logging
from prometheus_client import Gauge


def init(**_):
    global s_tui_metrics
    global sources
    s_tui_metrics={}
    sources = [FreqSource(), TempSource(),
                    UtilSource(),
                    RaplPowerSource(),
                    FanSource()]
    
    for source in sources:
        source_name = source.get_source_name()
        metric_obj=Gauge("s_tui_sensors_"+source_name,"",["device"])
        s_tui_metrics.update({source_name:metric_obj})


def __main():
    global s_tui_metrics
    for source in sources:
        source.update()
        source_name = source.get_source_name()
        metric_obj=s_tui_metrics[source_name]
        result=source.get_sensors_summary()
        for device_name in result:
            value=float(result[device_name])
            metric_obj.labels(device_name).set(value)

def main(**_):
    try:
        __main()
    except Exception as e:
        logging.exception(e)
    
    

if __name__ == "__main__":
    pass
