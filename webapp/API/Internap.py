#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Internap API

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
import hashlib
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class Internap:

    def __init__(self):
        self.username = 'xxxxx'
        self.password = 'xxxxx'
        self.url = 'https://api.voxel.net/version/1.5/'
        self.format = 'json'
        self.auth = {}

    def getToken(self):
        now = datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S+0000")
        payload = {'method': 'voxel.hapi.authkeys.read', 'format': self.format}
        response = requests.get(
            self.url, auth=(self.username, self.password), params=payload)
        result = json.loads(response.text)
        if result["response"]["status"] == "ok":
            self.auth["format"] = self.format
            self.auth["key"] = result["response"]["authkey"]["key"]
            self.auth["secrect"] = result["response"]["authkey"]["secret"]
            self.auth["timestamp"] = timestamp
            return self.auth
        else:
            logger.error("Can't get token")
            raise ValueError("Can't get token")

    def getApiSig(self):
        string = []
        secret = self.auth["secrect"]
        del self.auth["secrect"]
        m = hashlib.md5()
        for key in sorted(self.auth.iterkeys()):
            string.append(key)
            string.append(self.auth[key])
        string = ''.join(string)
        apiSig = secret + string
        m.update(apiSig)
        self.auth["api_sig"] = m.hexdigest()
        return self.auth

    def getDeviceList(self):
        self.auth["method"] = "devices.list"
        payload = self.getApiSig()
        response = requests.get(self.url, params=payload)
        json_response = json.loads(response.text)
        return json_response
