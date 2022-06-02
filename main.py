#!/bin/python3
import logging
from prometheus_client import start_http_server
import click
from utils import my_log_settings,JsonConfig
import explorers
import sys
import time

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
    start_http_server(conf.get("explorer",{}).get("port",8900))
    while True:
        for module_name in conf:
            if module_name=="explorer":
                continue
            try:
                explorer_main=eval("explorers.%s.main"%module_name)
                explorer_main(**conf.get(module_name,{}))
            except AttributeError:
                logging.warning("cannot run main() in module %s, please check if module is correctly written"%module_name)
            except Exception as e:
                logging.exception(e)
                return 255
        time.sleep(conf.get("explorer",{}).get("interval",10))

if __name__ == "__main__":
    sys.exit(main())
