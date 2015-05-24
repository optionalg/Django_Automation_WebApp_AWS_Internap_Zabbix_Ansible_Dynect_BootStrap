#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dynec API

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
from pprint import pprint

import logging
logger = logging.getLogger(__name__)


class Dynect:

    def __init__(self):
        self.zone_list = []
        self.customer_name = 'xxxxx'
        self.user_name = 'xxxxx'
        self.password = 'xxxxx'
        self.TokenUrl = 'https://api.dynect.net/REST/Session/'
        self.NodeUrl = 'https://api.dynect.net/REST/NodeList/'
        self.ARecoardUrl = 'https://api.dynect.net/REST/ARecord/'
        self.ZoneUrl = 'https://api.dynect.net/REST/Zone/'
        self.CNameUrl = 'https://api.dynect.net/REST/CNAMERecord/'
        self.DSFUrl = "https://api.dynect.net/REST/DSFResponsePool/xxxxx/"
        self.token = ''

    def getToken(self):
        # Retrive a Auth-Token from Dynect via REST API
        payload = {'customer_name': self.customer_name,
                   'user_name': self.user_name, 'password': self.password}
        headers = {'content-type': 'application/json'}
        response = requests.post(
            self.TokenUrl, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            self.token = result["data"]["token"]
            return self.token
        else:
            logger.error("Can't get token")
            raise ValueError("Can't get token")

    def extractFQDN(self, fqdn):
        dots = []
        dns = []
        index = 0
        result = {}

        for dot in fqdn:
            if dot == ".":
                dots.append(index)
                index += 1
            else:
                index += 1

        for i in xrange(len(dots)):
            if i is 0:
                end = dots[i]
                dns.append(fqdn[:end])

            if i < (len(dots)):
                start = dots[i - 1] + 1
                end = dots[i]
                dns.append(fqdn[start:end])

            if i == (len(dots) - 1):
                start = dots[i] + 1
                dns.append(fqdn[start:])

        dns = filter(None, dns)
        zone = str(dns[-2]) + '.' + str(dns[-1])
        result["zone"] = zone
        node = ""

        for i in xrange(len(dns)):
            if i < (len(dns) - 2):
                node += (str(dns[i]) + '.')
        result["node"] = node[:-1]

        return result  # return dict

    def getZoneList(self):
        # Get all Zones via REST API
        zone_list = []
        url = self.ZoneUrl
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            for zone in result['data']:
                zone = zone[11:]
                zone = zone.strip("/")
                zone_list.append(zone)

            logger.debug("Get Zones successfully")

            return zone_list  # List

        else:
            logger.error("Can't get Zones")
            raise ValueError("Can't get Zones")

    def getNodeList(self, zone):
        # Get all nodes list from each Zone
        nodeList = []
        url = self.NodeUrl + zone + '/'
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            for node in result['data']:
                nodeList.append(node)

            logger.debug("Get Nodes successfully")

            return nodeList  # List

        else:
            logger.error("Can't get Nodes")
            raise ValueError("Can't get Nodes")

    def getNodeID(self, zone, node):
        nodeIDList = []
        url = self.ARecoardUrl + '%s/%s/' % (zone, node)
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            logger.debug("Get NodesID successfully")

            return result['data'][0]  # return nodeID (it's URL)

        else:
            logger.error("Can't get NodesID")
            raise ValueError("Can't get NodesID")

    def getArecord(self, id):
        url = 'https://api.dynect.net' + id + '/'
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.get(url, headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            logger.debug("Get Arecord successfully")

            # return ipAddress (it's URL)
            return result['data']['rdata']['address']

        else:
            logger.error("Can't get Arecord")
            raise ValueError("Can't get Arecord")

    def addRecoard(self, zone, node, ip, ttl):
        # Now that we have the session and token, add the A record for our zone
        # and fqdn
        recordParams = {}
        recordParams["rdata"] = {}
        recordParams["rdata"]["address"] = ip
        recordParams["ttl"] = ttl
        payload = recordParams
        zone = zone
        fqdn = node + "." + zone
        url = self.ARecoardUrl + '%s/%s/' % (zone, fqdn)
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.post(
            url, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            logger.debug("Add Record %s %s %s %s successfully" %
                         (zone, fqdn, ip, ttl))
        else:
            logger.error("Can't Publish")
            raise ValueError("Can't Publish")

    def updateCNAME(self, node, zone, cname, ttl):
        # Now that we have the session and token, update the CNAME record for
        # our zone and fqdn
        recordParams = {}
        recordParams["rdata"] = {}
        recordParams["rdata"]["cname"] = cname
        recordParams["ttl"] = ttl
        payload = recordParams
        zone = zone
        fqdn = node + "." + zone
        url = self.CNameUrl + '%s/%s/' % (zone, fqdn)
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        try:
            response = requests.put(
                url, data=json.dumps(payload), headers=headers)
            result = json.loads(response.text)
            if result["status"] == "success":
                logger.debug(
                    "Update CName %s %s %s %s successfully" % (zone, fqdn, cname, ttl))

        except Exception as e:
            logger.error("Can't update CName")
            logger.error(e)

    def getCName(self, zone, fqdn, record_id):
        url = self.CNameUrl + '%s/%s/%s/' % (zone, fqdn, record_id)
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        try:
            response = requests.get(url, headers=headers)
            result = json.loads(response.text)
            # pprint(result)

            if result["status"] == "success":
                rdata = result['data']['rdata']['cname']
                ttl = result['data']['ttl']
                logger.debug(
                    "Get CName %s %s point to %s ttl: %s successfully" % (zone, fqdn, rdata, ttl))

                return rdata, ttl

        except Exception as e:
            logger.error("Can't get CName")
            logger.error(e)

    def getDSF(self):
        url = self.DSFUrl
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        newResult = []

        try:
            response = requests.get(url, headers=headers)
            result = json.loads(response.text)
            # pprint(result)

            if result["status"] == "success":
                logger.debug(pprint(result))
                response_pool_id = []
                # print "Get CName %s %s point to %s ttl: %s successfully" %
                # (zone, fqdn, rdata, ttl)

                # Get all response pools ID as URI
                for i in xrange(len(result['data'])):
                    response_pool = result['data'][i]
                    response_pool_id.append(response_pool)

                # Get real response pool information
                for j in xrange(len(response_pool_id)):
                    url = "https://api.dynect.net" + response_pool_id[j]
                    headers = {
                        'Auth-Token': self.token, 'content-type': 'application/json'}
                    try:
                        response = requests.get(url, headers=headers)
                        result = json.loads(response.text)

                        if result["status"] == "success":
                            newResult.append(result)

                    except Exception as e:
                        logger.error("Can't get Response Pool info")
                        logger.error(e)

                    #result = json2html.convert(json = result)

                return newResult

        except Exception as e:
            logger.error("Can't get DSF")
            logger.error(e)

    def publish(self, zone):
        # Finally, if adding the A record was a success, let's publish the zone
        publishParams = {}
        publishParams["publish"] = 1
        payload = publishParams
        url = self.ZoneUrl + '%s/' % zone
        headers = {
            'Auth-Token': self.token, 'content-type': 'application/json'}
        response = requests.put(url, data=json.dumps(payload), headers=headers)
        result = json.loads(response.text)
        if result["status"] == "success":
            logger.debug("Publish Successful")
        else:
            logger.error("Can't Publish")
            raise ValueError("Can't Publish")
