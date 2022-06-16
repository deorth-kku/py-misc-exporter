#!/bin/python3
import logging
from prometheus_client import start_http_server
import click
from utils import my_log_settings, JsonConfig
import exporters
import os
import sys
import time
from threading import Thread


def install_systemd_service(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    args = {p.name: p.default for p in ctx.command.params}
    args.update(ctx.params)
    my_log_settings(args.get("log"), args.get("log_level"))

    service_filename = "/etc/systemd/system/py-misc-exporter.service"
    env_filename = "/etc/default/py-misc-exporter"
    config_filename = "/etc/py-misc-exporter/pme.conf"

    python_path = sys.executable
    script_path = os.path.abspath(__file__)
    service_file_text = """[Unit]
Description=prometheus exporter for some of my devices written in python
Documentation=https://github.com/deorth-kku/py-misc-exporter
After=network.target nss-lookup.target
[Service]
EnvironmentFile=%s
User=root
ExecStart=%s %s
Restart=on-failure
[Install]
WantedBy=multi-user.target
""" % (env_filename, python_path, script_path)

    env_file_text = '''#configure command line args for systemd service here, run %s %s --help for more information
    PME_CONF="%s"
    PME_LOG_FILE="/var/log/pme.log"
    PME_LOG_LEVEL="INFO"
''' % (python_path, script_path, config_filename)

    if os.path.exists(service_filename):
        logging.error(
            "not overwriting exist service file %s, remove it first if you have to"%service_filename)
    else:
        with open(service_filename, "w") as f:
            f.write(service_file_text)
        logging.info("created service file %s"%service_filename)
        logging.warning("you need to run \"systemctl daemon-reload\" manually (for now)")

    
    if os.path.exists(env_filename):
        logging.error(
            "not overwriting exist env file %s, remove it first if you have to"%env_filename)
    else:
        with open(env_filename, "w") as f:
            f.write(env_file_text)
        logging.info("created env file %s"%env_filename)

    if os.path.exists(config_filename):
        logging.error(
            "not overwriting exist env file %s, remove it first if you have to"%config_filename)
    else:
        os.makedirs(os.path.dirname(config_filename),exist_ok=True)
        f=JsonConfig(config_filename)
        f.dumpconfig({
            "exporter":{}
        })
        logging.info("created config file %s"%config_filename)

    ctx.exit()


@click.command(context_settings=dict(auto_envvar_prefix="PME"))
@click.option('--install', is_flag=True, callback=install_systemd_service,
              expose_value=False, is_eager=True, help='install systemd service file to system')
@click.option('-c', "--conf", type=click.Path(exists=True), help='using specific config file', default="config.json", show_envvar=True)
@click.option('-l', "--log-file", type=click.Path(), help='using specific log file', default=None, show_envvar=True)
@click.option("--log-level", type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], case_sensitive=False), help='using specific log level', default="DEBUG", show_envvar=True)
def main(conf, log_file, log_level):
    my_log_settings(log_file, log_level)
    conf = JsonConfig(conf)
    start_http_server(conf.get("exporter", {}).get("port", 8900))

    for module_name in conf:
        if module_name == "exporter":
            continue
        try:
            module_init = eval("exporters.%s.init" % module_name)
            module_init(**conf.get(module_name, {}))
        except AttributeError:
            logging.warning(
                "cannot run init() in module %s, please check if module is correctly written" % module_name)

    while True:
        threads = []
        for module_name in conf:
            if module_name == "exporter":
                continue
            try:
                module_main = eval("exporters.%s.main" % module_name)
                t = Thread(target=module_main,
                           kwargs=conf.get(module_name, {}))
                t.start()
                threads.append(t)
            except AttributeError:
                logging.warning(
                    "cannot run main() in module %s, please check if module is correctly written" % module_name)
            except Exception as e:
                logging.exception(e)
                return 255
        t = Thread(target=time.sleep, args=(
            conf.get("exporter", {}).get("interval", 10),))
        t.start()
        threads.append(t)

        for t in threads:
            t.join()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.exception(e)
