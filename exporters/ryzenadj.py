#!/bin/python3
import logging
from prometheus_client import Gauge


def init(**_):
    from ryzen_ppd.cpu import RyzenAdj
    global ryzenadj_obj
    global ryzenadj_metrics

    ryzenadj_obj = RyzenAdj()
    ryzenadj_metrics = {}
    arg_list = (
        'stapm_limit',
        'stapm_value',
        'fast_limit',
        'fast_value',
        'slow_limit',
        'slow_value',
        'apu_slow_limit',
        'apu_slow_value',
        'vrm_current',
        'vrm_current_value',
        'vrmsoc_current',
        'vrmsoc_current_value',
        'vrmmax_current',
        'vrmmax_current_value',
        'vrmsocmax_current',
        'vrmsocmax_current_value',
        'tctl_temp',
        'tctl_temp_value',
        'apu_skin_temp_limit',
        'apu_skin_temp_value',
        'dgpu_skin_temp_limit',
        'dgpu_skin_temp_value',
        'psi0_current',
        'psi0soc_current',
        'stapm_time',
        'slow_time',
        'cclk_setpoint',
        'cclk_busy_value',
        'core_clk',
        'core_volt',
        'core_power',
        'core_temp',
        'l3_clk',
        'l3_logic',
        'l3_vddm',
        'l3_temp',
        'gfx_clk',
        'gfx_temp',
        'gfx_volt',
        'mem_clk',
        'fclk',
        'soc_power',
        'soc_volt',
        'socket_power'
    )
    ryzenadj_obj.refresh()
    # detect args available on current platform, not available args wont be created as metric
    for arg in arg_list:
        if ryzenadj_obj.get(arg) != None:
            metric = Gauge("ryzenadj_"+arg, "")
            ryzenadj_metrics.update({
                arg: metric
            })


def __main():
    ryzenadj_obj.refresh()
    for metric_name in ryzenadj_metrics:
        metric = ryzenadj_metrics[metric_name]
        metric.set(ryzenadj_obj.get(metric_name))


def main(**_):
    try:
        __main()
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    pass
