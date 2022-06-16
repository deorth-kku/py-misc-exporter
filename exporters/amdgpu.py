#!/bin/python3
import logging
from prometheus_client import Gauge
from typing import Any


def init(**_):
    import pyamdgpuinfo

    class gpu_info():
        def __init__(self, gpu_id: int) -> None:
            self.info_obj = pyamdgpuinfo.get_gpu(gpu_id)

        def __getattr__(self, __name: str) -> Any:
            return getattr(self.info_obj, __name)

        def get_metric_dict(self) -> dict:
            out_dict = {}
            available_methed = []
            for method_name in dir(self.info_obj):
                if hasattr(self, "available_methed"):
                    if method_name not in self.available_methed:
                        continue
                    method = getattr(self.info_obj, method_name)
                    result = method()
                else:
                    method = getattr(self.info_obj, method_name)
                    if not (method_name.startswith("query") and callable(method)):
                        continue
                    try:
                        result = method()
                        available_methed.append(method_name)
                    except RuntimeError:
                        logging.debug("%s is not supported on gpu_id %s" %
                                      (method_name, self.info_obj.gpu_id))
                        continue

                if type(result) == dict:
                    for key in result:
                        names = ("amdgpu", method_name.lstrip("query_"), key)
                        metirc_name = "_".join(names)
                        out_dict.update({
                            metirc_name: result[key]
                        })
                else:
                    names = ("amdgpu", method_name.lstrip("query_"))
                    metirc_name = "_".join(names)
                    out_dict.update({
                        metirc_name: result
                    })
            if not hasattr(self, "available_methed"):
                self.available_methed = available_methed
            return out_dict

    global gpus
    global amdgpu_metrics
    amdgpu_metrics = {}
    gpu_num = pyamdgpuinfo.detect_gpus()
    gpus = [gpu_info(gpu) for gpu in range(gpu_num)]
    for gpu_info_obj in gpus:
        result = gpu_info_obj.get_metric_dict()
        for metric_name in result:
            if metric_name in amdgpu_metrics:
                continue
            metric_obj = Gauge(metric_name, "", ["gpu_id"])
            amdgpu_metrics.update({
                metric_name: metric_obj
            })


def __main():
    for gpu in gpus:
        results = gpu.get_metric_dict()
        for metric_name in results:
            metric_obj = amdgpu_metrics[metric_name]
            metric_obj.labels(gpu_id=gpu.gpu_id).set(results[metric_name])


def main(**_):
    try:
        __main()
    except Exception as e:
        logging.exception(e)


if __name__ == "__main__":
    init()
