#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Zabbix API

"""

__author__ = "Jash Lee"
__copyright__ = "Jan 14, 2015"
__credits__ = ["Site Reliability Engineers"]
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Jash Lee"
__email__ = "s905060@gmail.com"
__status__ = "Alpha"

import requests
import json

import logging
logger = logging.getLogger(__name__)


class Zabbix:

    def __init__(self):
        #proxyId       = raw_input('Please typ proxyID (lookup proxyIds.txt) :')
        self.user_name = 'xxxxx'
        self.password = 'xxxxx'
        self.url = 'http://zabbix.exelator.com/zabbix/api_jsonrpc.php'
        self.headers = {'content-type': 'application/json'}
        self.token = ''

    def getToken(self):
        # Retrive a Auth-Token from Zabbix via API
        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.user_name,
                "password": self.password
            },
            "id": 0
        }

        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)
        self.token = result["result"]
        return self.token

    def getTemplateId(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": ["templateid", "name"]
            },
            "auth": self.token,
            "id": 1
        }
        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)
        return result

    def getGroupId(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": ["groupid", "name"],
            },
            "auth": self.token,
            "id": 1
        }
        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)
        return result

    def getProxyId(self):
        payload = {
            "jsonrpc": "2.0",
            "method": "proxy.get",
            "params": {
                "output": ["proxyid", "host"]
            },
            "auth": self.token,
            "id": 1
        }
        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)
        return result

    def getHost(self, hostname):
        payload = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "filter": {
                    "host": [hostname]
                }
            },
            "auth": self.token,
            "id": 1
        }
        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)
        return result

    def addHost(self, hostName, hostIp, groups, templates):
        # Add each host ips into Zabix
        hostName = hostName
        hostIp = hostIp
        hostGroup_List = []
        template_List = []

        for group in groups:  # list
            var = {}
            var['groupid'] = group
            hostGroup_List.append(var)

        for template in templates:  # list
            var = {}
            var['templateid'] = template
            template_List.append(var)

        payload = {
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostName,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostIp,
                        "dns": hostName,
                        "port": "10050"
                    }
                ],
                "groups": hostGroup_List,
                "templates": template_List,
            },
            "auth": self.token,
            "id": 1
        }

        response = requests.post(
            self.url, data=json.dumps(payload), headers=self.headers)
        result = json.loads(response.text)

        logger.debug("Add Host %s %s is Done" % (hostName, hostIp))
        return result
