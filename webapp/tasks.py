from __future__ import absolute_import
from celery import shared_task
from celery.task import periodic_task
from pprint import pprint
from webapp.models import Devices, GroupList, TemplateList, ProxyList, Hosts, ResponsePools

import webapp.API.Internap as Internap
import webapp.API.Zabbix as Zabbix
import webapp.API.Dynect as Dynect
import webapp.API.Amazon as Amazon
import webapp.API.Ansible as Ansible
import os
import sys

import logging
logger = logging.getLogger(__name__)

#@periodic_task(ignore_result=True, run_every=1800)


@shared_task
def updateDB():

    Devices.objects.all().delete()
    ResponsePools.objects.all().delete()
    # Update Internap Device list via their API
    internap = Internap.Internap()
    internap.getToken()
    context = internap.getDeviceList()
    nodes_num = len(context["response"]["devices"])

    for node in xrange(nodes_num):
        try:
            host_name = (context["response"]["devices"][node]["label"])
            root_pass = (
                context["response"]["devices"][node]["access_methods"]["admin"]["password"])
            ip_address = (
                context["response"]["devices"][node]["ip_assignments"][0]["address"])
            status = (context["response"]["devices"][node]["status"])
            #device = Devices.objects.update_or_create(fqdn=host_name, password=root_pass ,ip=ip_address)
            # device.save()

            obj, created = Devices.objects.update_or_create(
                fqdn=host_name, defaults={'fqdn': host_name, 'password': root_pass, 'ip': ip_address, 'status': status})
            obj.save()

        except Exception as e:
            logger.error(e)
            print e

    # Update Zabbix Group and Template and Proxy list
    zabbix = Zabbix.Zabbix()
    zabbix_token = zabbix.getToken()
    zabbix_templates = zabbix.getTemplateId()

    zabbix.updateDB(zabbix_templates, "template")
    zabbix_groups = zabbix.getGroupId()
    zabbix.updateDB(zabbix_groups, "group")
    zabbix_proxys = zabbix.getProxyId()
    zabbix.updateDB(zabbix_proxys, "proxy")

    dynect = Dynect.Dynect()
    dynect_token = dynect.getToken()

    # Update Amazon instance
    amazon = Amazon.Amazon()
    instances = amazon.getDevice()
    for i in instances:
        # pprint(i.__dict__)
        try:
            host_name = i.__dict__['tags']['Name']
            root_pass = i.__dict__['client_token']
            ip_address = i.__dict__['ip_address']
            status = str(i.__dict__['_state'])
            logger.debug("token : " + i.__dict__['client_token'])
            logger.debug("Host name :" + i.__dict__['tags']['Name'])
            logger.debug("Ip address : " + i.__dict__['ip_address'])
            logger.debug("status : " + str(i.__dict__['_state']))

            obj, created = Devices.objects.update_or_create(fqdn=host_name, defaults={
                                                            'fqdn': host_name, 'password': root_pass, 'ip': ip_address, 'status': status})
            obj.save()

        except Exception as e:

            print "Can't update instance"
            print e
            logger.error("Can't update instance")
            logger.error(e)

    # Update Dynec Pesponse pool
    dynect = Dynect.Dynect()
    dynect.getToken()
    context = dynect.getDSF()

    for i in xrange(len(context)):
        print "RESPONSE POOLS : " + context[i]['data']['label']
        logger.debug("RESPONSE POOLS : " + context[i]['data']['label'])
        pools = context[i]['data']['label']

        # print out all info
        for k in xrange(int(len(context[i]['data']['rs_chains'][0]['record_sets'][0]['records']))):

            print "Label : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['label']
            logger.debug(
                "Label : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['label'])
            label = context[i]['data']['rs_chains'][0][
                'record_sets'][0]['records'][k]['label']

            print "Address : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['master_line']
            logger.debug(
                "Address : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['master_line'])
            address = context[i]['data']['rs_chains'][0][
                'record_sets'][0]['records'][k]['master_line']

            print "Weight : " + str(context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['weight'])
            logger.debug(
                "Weight : " + str(context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['weight']))
            weight = str(
                context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['weight'])

            print "Status : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['status']
            logger.debug(
                "Status : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['status'])
            status = context[i]['data']['rs_chains'][0][
                'record_sets'][0]['records'][k]['status']

            print "Mode : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['automation']
            logger.debug(context[i]['data']['rs_chains'][0][
                         'record_sets'][0]['records'][k]['automation'])
            mode = context[i]['data']['rs_chains'][0][
                'record_sets'][0]['records'][k]['automation']

            print "Eligible: " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['eligible']
            logger.debug(
                context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['eligible'])
            eligible = context[i]['data']['rs_chains'][0][
                'record_sets'][0]['records'][k]['eligible']

            tag = pools + " : " + label

            obj, created = ResponsePools.objects.update_or_create(
                tag=tag, defaults={'pools': pools, 'label': label, 'address': address, 'weight': weight, 'status': status, 'mode': mode, 'eligible': eligible, 'tag': tag})
            obj.save()

updateDB.delay()
