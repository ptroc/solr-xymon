#!/usr/bin/env python3
# file location: /usr/lib/xymon/client/ext/solr.py
import datetime
import logging
import os

import requests
from xymon import Xymon


class XymonSolr:
    def __init__(self, hostname: str, service: str, core_list: dict,
                 solr_admin_url: str, log_level: int = logging.INFO):
        self._core_dict = core_list
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
                if core in self._core_dict:
                    core_settings = self._core_dict[core]
                    report_text += (
                        f"Core: {core}\n\n"
                        f"Conditions for Yellow: Number of documents < {core_settings['yellow_count']} or \n"
                        f"last modified date is older than {core_settings['yellow_time']} minutes\n"
                        f"Conditions for Red: Number of documents < {core_settings['red_count']} or \n"
                        f"last modified date is older than {core_settings['red_time']} minutes\n\n"

                    )
                    if num_docs < core_settings['red_count']:
                        color_check = "red"
                        report_text += f"Number of Documents: {num_docs} {self._red_icon()}\n"
                    elif num_docs < core_settings['yellow_count']:
                        if color_check != "red":
                            color_check = "yellow"
                        report_text += f"Number of Documents: {num_docs} {self._yellow_icon()}\n"
                    else:
                        report_text += f"Number of Documents: {num_docs} {self._green_icon()}\n"

                    if not last_modified or last_modified < datetime.datetime.now() - datetime.timedelta(minutes=core_settings['red_time']):
                        color_check = "red"
                        report_text += f"Last Modified Date: {last_modified} {self._red_icon()}\n\n"
                    elif last_modified < datetime.datetime.now() - datetime.timedelta(minutes=core_settings['yellow_time']):
                        if color_check != "red":
                            color_check = "yellow"
                        report_text += f"Last Modified Date: {last_modified} {self._yellow_icon()}\n\n"
                    else:
                        report_text += f"Last Modified Date: {last_modified} {self._green_icon()}\n\n"

                    report_text += "--------------------------------\n\n"
                report_text += "\nVersion: 1.0\n"
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
    cores = {
        'core_1': {'yellow_time': 1500, 'red_time': 1900, 'yellow_count': 50, 'red_count': 5},
        'core_2': {'yellow_time': 120, 'red_time': 720, 'yellow_count': 50, 'red_count': 5},
        'core_3': {'yellow_time': 1500, 'red_time': 1900, 'yellow_count': 50, 'red_count': 5},
        'core_4': {'yellow_time': 120, 'red_time': 720, 'yellow_count': 50, 'red_count': 5}
    }

    xymon = XymonSolr(hostname=os.getenv("MACHINE"), service="solr",
                      core_list=cores,
                      solr_admin_url="http://localhost:8983/solr/admin/cores?action=STATUS&wt=json")
    xymon.check_solr_state()
