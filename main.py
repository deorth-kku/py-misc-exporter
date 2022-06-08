#!/bin/python3
import logging
from prometheus_client import start_http_server
import click
from utils import my_log_settings,JsonConfig
import exporters
import sys
import time
from threading import Thread

def install():
    service_file_text="""
    
    """


@click.command(context_settings=dict(auto_envvar_prefix="PME"))
@click.option('-c', "--conf", type=click.Path(exists=True), help='using specific config file', default="config.json",show_envvar=True)
@click.option('-l', "--log-file", type=click.Path(), help='using specific log file', default=None,show_envvar=True)
@click.option("--log-level", type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False), help='using specific log level', default="DEBUG",show_envvar=True)
def main(conf,log_file,log_level):
    my_log_settings(log_file,log_level)
    conf=JsonConfig(conf)
    start_http_server(conf.get("exporter",{}).get("port",8900))

    for module_name in conf:
        if module_name=="exporter":
            continue
        try:
            module_init=eval("exporters.%s.init"%module_name)
            module_init(**conf.get(module_name,{}))
        except AttributeError:
            logging.warning("cannot run init() in module %s, please check if module is correctly written"%module_name)

    while True:
        threads=[]
        for module_name in conf:
            if module_name=="exporter":
                continue
            try:
                module_main=eval("exporters.%s.main"%module_name)
                t=Thread(target=module_main,kwargs=conf.get(module_name,{}))
                t.start()
                threads.append(t)
            except AttributeError:
                logging.warning("cannot run main() in module %s, please check if module is correctly written"%module_name)
            except Exception as e:
                logging.exception(e)
                return 255
        t=Thread(target=time.sleep,args=(conf.get("exporter",{}).get("interval",10),))
        t.start()
        threads.append(t)

        for t in threads:
            t.join()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.exception(e)
