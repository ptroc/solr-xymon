#!/usr/bin/env python3
# file location: /usr/lib/xymon/client/ext/solr.py
import datetime
import logging
import os

import requests
from xymon import Xymon


class XymonSolr:
    def __init__(self, hostname: str, service: str, yellow_time: int, red_time: int, core_list: list,
                 solr_admin_url: str,
                 log_level: int = logging.INFO, yellow_count: int = 10, red_count: int = 5):
        self.yellow_time = yellow_time
        self.red_time = red_time
        self.yellow_count = yellow_count
        self.red_count = red_count
        self.core_list = core_list
        self.log_level = log_level
        self.logger = logging
        self.hostname = hostname
        self.service = service
        self.solr_admin_url = solr_admin_url
        self.server = Xymon()
        self.logger.basicConfig(
            format='[%(asctime)s] %(levelname)s %(process)d --- [%(threadName)s] %(funcName)s: %(message)s',
            level=self.log_level
        )

    def check_solr_state(self):
        self.logger.info(f"Checking Solr status")
        try:
            response = requests.get(self.solr_admin_url)
            response.raise_for_status()
            cores_info = response.json().get("status", {})
            report_text = ""
            color_check = "green"
            for core, info in cores_info.items():
                num_docs = info["index"].get("numDocs", 0)
                last_modified_str = info["index"].get("lastModified")
                last_modified = datetime.datetime.strptime(last_modified_str,
                                                           '%Y-%m-%dT%H:%M:%S.%fZ') if last_modified_str else None
                if core in self.core_list:
                    if num_docs < self.red_count or not last_modified or last_modified < datetime.datetime.now() - datetime.timedelta(
                            minutes=self.red_time):
                        color_check = "red"
                        report_text += f"Core: {core} {self._red_icon()}\nNumber of Documents: {num_docs}\nLast Modified Date: {last_modified}\n\n"
                    elif num_docs < self.yellow_count or last_modified < datetime.datetime.now() - datetime.timedelta(
                            minutes=self.yellow_time):
                        color_check = "yellow"
                        report_text += f"Core: {core} {self._yellow_icon()}\nNumber of Documents: {num_docs}\nLast Modified Date: {last_modified}\n\n"
                    else:
                        report_text += f"Core: {core} {self._green_icon()}\nNumber of Documents: {num_docs}\nLast Modified Date: {last_modified}\n\n"
                self.server.report(host=self.hostname, test=self.service, color=color_check, message=report_text)
                self.logger.debug(report_text)
        except requests.RequestException as e:
            self.logger.error("Error fetching data from Solr:", e)
            self._send_red_status(f"Error fetching data from Solr: {e}")

    def _send_red_status(self, message):
        self.server.report(host=self.hostname, test=self.service, color="red", message=message)

    def _send_yellow_status(self, message):
        self.server.report(host=self.hostname, test=self.service, color="yellow", message=message)

    def _send_green_status(self, message):
        self.server.report(host=self.hostname, test=self.service, color="green", message=message)

    def _green_icon(self):
        return '<img src="/xymon/gifs/static/green.gif" alt="green" height="16" width="16" border="0">'

    def _yellow_icon(self):
        return '<img src="/xymon/gifs/static/yellow.gif" alt="yellow" height="16" width="16" border="0">'

    def _red_icon(self):
        return '<img src="/xymon/gifs/static/red.gif" alt="red" height="16" width="16" border="0">'


if __name__ == "__main__":
    # get $MACHINE bash environment variable
    cores = ["core1", "core2"]
    xymon = XymonSolr(hostname=os.getenv("MACHINE"), service="solr",
                      red_time=720,
                      yellow_time=120,
                      yellow_count=50,
                      red_count=5,
                      core_list=cores,
                      solr_admin_url="http://localhost:8984/solr/admin/cores?action=STATUS&wt=json")
    xymon.check_solr_state()
