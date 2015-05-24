from django.shortcuts import render
from django.shortcuts import render_to_response
#from django.shortcuts import redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from webapp.models import Devices, GroupList, TemplateList, ResponsePools, Dns, ProxyList
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.http import HttpResponse
from django.template import loader, Context
import multiprocessing

import API.Internap as Internap
import API.Zabbix as Zabbix
import API.Dynect as Dynect
import API.Amazon as Amazon
import API.Ansible as Ansible
import os
import time
# import sys
# from pprint import pprint

import logging
logger = logging.getLogger(__name__)

url = '/webapp/accounts/login/'


def multi_dynect(context, node):

    try:
        host_name = (context["response"]["devices"][node]["label"])
        root_pass = (
            context["response"]["devices"][node]["access_methods"]["admin"]["password"])

        ip_address = (
            context["response"]["devices"][node]["ip_assignments"][0]["address"])
        checkpoint = ip_address.split('.')
        i = 0
        while int(checkpoint[0]) == 172:
            ip_address = (
                context["response"]["devices"][node]["ip_assignments"][i + 1]["address"])
            checkpoint = ip_address.split('.')
        status = (context["response"]["devices"][node]["status"])

        # time.sleep(1)
        logger.debug(
            "Dynect : {0} {1} {2}".format(host_name, root_pass, ip_address))
        obj = Devices.objects.create(
            fqdn=host_name, password=root_pass, ip=ip_address, status=status)
        obj.save()

    except IOError:
        pass


def multi_amazon(i):
    try:
        host_name = i.__dict__['tags']['Name']
        root_pass = i.__dict__['client_token']
        ip_address = i.__dict__['ip_address']
        status = str(i.__dict__['_state'])

        # time.sleep(1)
        logger.debug(
            "Amazon : {0} {1} {2}".format(host_name, root_pass, ip_address))

        obj = Devices.objects.create(
            fqdn=host_name, password=root_pass, ip=ip_address, status=status)
        obj.save()

    except IOError:
        pass


def multi_dns(zone, node):
    try:
        dynect2 = Dynect.Dynect()
        dynect2.getToken()
        url = ''
        url = dynect2.getNodeID(zone, node)
        logger.debug("URL : " + url)
        ip = dynect2.getArecord(url)
        logger.debug("IP : " + ip)
        # time.sleep(1)

        obj = Dns.objects.create(zone=zone, aRecord=node, ip=ip)
        obj.save()

    except IOError:
        pass


def multi_zabbix(num, lists, action):
    try:
        if action == "group":
            groupid = lists["result"][num]["groupid"]
            name = lists["result"][num]["name"]
            logger.debug("Add Group %s %s is Done" % (groupid, name))
            # time.sleep(1)
            obj = GroupList.objects.create(groupId=groupid, name=name)
            obj.save()

        if action == "template":
            templateid = lists["result"][num]["templateid"]
            name = lists["result"][num]["name"]
            logger.debug("Add Template %s %s is Done" % (templateid, name))
            # time.sleep(1)
            obj = TemplateList.objects.create(
                templateId=templateid, name=name)
            obj.save()

        if action == "proxy":
            proxyid = lists["result"][num]["proxyid"]
            host = lists["result"][num]["host"]
            logger.debug("Add Proxy %s %s is Done" % (proxyid, host))
            # time.sleep(1)
            obj = ProxyList.objects.create(proxyId=proxyid, name=host)
            obj.save()

    except IOError:
        pass


def multi_dsf(pools, context, i, k):
    try:
        logger.debug(
            "Label : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['label'])

        label = context[i]['data']['rs_chains'][0][
            'record_sets'][0]['records'][k]['label']

        logger.debug(
            "Address : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['master_line'])

        address = context[i]['data']['rs_chains'][0][
            'record_sets'][0]['records'][k]['master_line']

        logger.debug(
            "Weight : " + str(context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['weight']))
        weight = str(
            context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['weight'])

        logger.debug(
            "Status : " + context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['status'])
        status = context[i]['data']['rs_chains'][0][
            'record_sets'][0]['records'][k]['status']

        logger.debug(context[i]['data']['rs_chains'][0][
                     'record_sets'][0]['records'][k]['automation'])

        mode = context[i]['data']['rs_chains'][0][
            'record_sets'][0]['records'][k]['automation']

        logger.debug(
            context[i]['data']['rs_chains'][0]['record_sets'][0]['records'][k]['eligible'])

        eligible = context[i]['data']['rs_chains'][0][
            'record_sets'][0]['records'][k]['eligible']

        tag = pools + " : " + label
       # time.sleep(1)
        obj = ResponsePools.objects.create(
            pools=pools, label=label, address=address, weight=weight, status=status, mode=mode, eligible=eligible, tag=tag)
        obj.save()

    except IOError:
        pass

# Create your views here.


def index(request):
    context = "Site Reliability Engineers!!!"

    return render(request, 'webapp/index.html', {'context': context})


@login_required(login_url=url)
def dsf(request):
    context = ResponsePools.objects.all().order_by('pools')

    # return HttpResponse(context)
    return render(request, 'webapp/dsf.html', {'context': context})


@login_required(login_url=url)
def console(request):

    lastLines = os.popen("tail -n 1 AIT.webapp.log").read()
    context = lastLines

    # return HttpResponse(context)
    return render(request, 'webapp/console.html', {'context': context})


@login_required(login_url=url)
def failover(request):

    context = ''
    dynect = Dynect.Dynect()
    dynect.getToken()
    rdata, ttl = dynect.getCName(
        'xxx.com', 'xxx.xxxxx.com', xxxxx)

    if request.method == 'POST':
        dynect = Dynect.Dynect()
        dynect.getToken()
        node = 'xxxxx'
        zone = 'xxxxx.com'
        ttl = 60
        cname = ''

        try:
            if request.POST.get('optionsRadios', '') == 'prod':
                cname = 'prod.xxxxx.com'

            if request.POST.get('optionsRadios', '') == 'fail':
                cname = 'failover.xxxxx.com'
            # Update the CName
            dynect.updateCNAME(node, zone, cname, ttl)
            dynect.publish(zone)

            context = "Success"
            return render_to_response('webapp/failover.html', {'context': context}, context_instance=RequestContext(request))

        except:
            context = "Failed"
            return render_to_response('webapp/failover.html', {'context': context}, context_instance=RequestContext(request))

    return render_to_response('webapp/failover.html', {'rdata': rdata, 'ttl': ttl}, context_instance=RequestContext(request))


@login_required(login_url=url)
def updateDB(request):
    processes = multiprocessing.cpu_count()
    if request.GET.get("db", "") == "inventory":
        Devices.objects.all().delete()
        GroupList.objects.all().delete()
        TemplateList.objects.all().delete()
        ProxyList.objects.all().delete()

        # Update Internap Device list via their API
        internap = Internap.Internap()
        internap.getToken()
        context = internap.getDeviceList()
        nodes_num = len(context["response"]["devices"])
        pool = multiprocessing.Pool(processes)
        for node in xrange(nodes_num):
            pool.apply_async(multi_dynect, args=(context, node, ))
        pool.close()
        pool.join()

        # Update Zabbix Group and Template and Proxy list
        zabbix = Zabbix.Zabbix()
        zabbix.getToken()

        zabbix_templates = zabbix.getTemplateId()
        total_num = len(zabbix_templates["result"])
        pool = multiprocessing.Pool(processes)
        for num in xrange(total_num):
            pool.apply_async(
                multi_zabbix, args=(num, zabbix_templates, "template", ))
        pool.close()
        pool.join()

        zabbix_groups = zabbix.getGroupId()
        total_num = len(zabbix_groups["result"])
        pool = multiprocessing.Pool(processes)
        for num in xrange(total_num):
            pool.apply_async(
                multi_zabbix, args=(num, zabbix_groups, "group", ))
        pool.close()
        pool.join()

        zabbix_proxys = zabbix.getProxyId()
        pool = multiprocessing.Pool(processes)
        total_num = len(zabbix_proxys["result"])
        for num in xrange(total_num):
            pool.apply_async(
                multi_zabbix, args=(num, zabbix_proxys, "proxy", ))
        pool.close()
        pool.join()

        # Update Amazon instance
        amazon = Amazon.Amazon()
        instances = amazon.getDevice()
        pool = multiprocessing.Pool(processes)
        for i in instances:
            pool.apply_async(multi_amazon, args=(i, ))
        pool.close()
        pool.join()

    if request.GET.get("db", "") == "dsf":
        ResponsePools.objects.all().delete()
        dynect = Dynect.Dynect()
        dynect.getToken()
        context = dynect.getDSF()

        for i in xrange(len(context)):
            logger.debug("RESPONSE POOLS : " + context[i]['data']['label'])
            pools = context[i]['data']['label']
            pool = multiprocessing.Pool(processes)
            # print out all info
            for k in xrange(int(len(context[i]['data']['rs_chains'][0]['record_sets'][0]['records']))):
                pool.apply_async(multi_dsf, args=(pools, context, i, k, ))
            pool.close()
            pool.join()

    if request.GET.get("db", "") == "dns":
        Dns.objects.all().delete()
        # Update Dynec aRecord and Pesponse pool list
        dynect = Dynect.Dynect()
        dynect.getToken()

        zones = []
        zones = dynect.getZoneList()

        for zone in zones:
            nodes = []
            nodes = dynect.getNodeList(zone)
            logger.debug("Zone : " + zone)

            pool = multiprocessing.Pool(processes)
            for node in nodes:
                logger.debug("Node : " + node)
                pool.apply_async(multi_dns, args=(zone, node, ))
            pool.close()
            pool.join()

    context = "Database is UP-TO-DATE!"
    # return redirect('/webapp/updateDB/')
    return render(request, 'webapp/updateDB.html', {'context': context})


@login_required(login_url=url)
def inventory(request):
    # Acquire device list from Sqlite3
    context = Devices.objects.all().order_by('fqdn')

    if request.GET.get('page') == "all":
        return render(request, 'webapp/inventory.html', {'context': context})

    else:
        paginator = Paginator(context, 25)  # Show 25 contacts per page
        page = request.GET.get('page')
        try:
            context = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            context = paginator.page(paginator.num_pages)

        return render(request, 'webapp/inventory.html', {'context': context})


@login_required(login_url=url)
def exportCSV(request):
    if request.method == 'GET':
        if request.GET.get("data", "") == "inventory":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response[
                'Content-Disposition'] = 'attachment; filename="inventory.csv"'
            context = Devices.objects.all().order_by('fqdn')
            allrows = []
            header = []
            # Defaulf header
            header.append("Hostname")
            header.append("Root password")
            header.append("Public IP Address")
            allrows.append(header)

            for device in context:
                row = []
                row.append(device.fqdn)
                row.append(device.password)
                row.append(device.ip)
                allrows.append(row)

            csv_data = (allrows)

            t = loader.get_template('webapp/inventory.template')
            c = Context({
                'data': csv_data,
            })

        if request.GET.get("data", "") == "dns":
            # Create the HttpResponse object with the appropriate CSV header.
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="dns.csv"'
            context = Dns.objects.all().order_by('zone')
            allrows = []
            header = []
            # Defaulf header
            header.append("Zone")
            header.append("aRecord")
            header.append("IP address")
            allrows.append(header)

            for device in context:
                row = []
                row.append(device.zone)
                row.append(device.aRecord)
                row.append(device.ip)
                allrows.append(row)

            csv_data = (allrows)

            t = loader.get_template('webapp/dns.template')
            c = Context({
                'data': csv_data,
            })

        response.write(t.render(c))
        return response


@login_required(login_url=url)
def dns(request):
    # Acquire device list from Sqlite3
    context = Dns.objects.all().order_by('zone')

    if request.GET.get('page') == "all":
        return render(request, 'webapp/dns.html', {'context': context})

    else:
        paginator = Paginator(context, 25)  # Show 25 contacts per page
        page = request.GET.get('page')
        try:
            context = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            context = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of
            # results.
            context = paginator.page(paginator.num_pages)

        return render(request, 'webapp/dns.html', {'context': context})


@login_required(login_url=url)
def mojo(request):
    if request.method == 'POST':
        hosts = []
        ttl = ''
        # group         = []
        templates = []
        # Dealing with the FQDN to Zone and Node
        text_area_value = request.POST["hosts"]
        # Split lines from front-end textarea line-by-line
        hosts = [x for x in text_area_value.splitlines()]

        try:
            f = open('.xxxxx', 'w')
            f.write('[xxxxx]\n')  # python will convert \n to os.linesep
        except Exception as e:
            logger.error(e)

        # Get root password from Internap
        for host in hosts:
            # Dynect Add Arecords
            dynect = Dynect.Dynect()
            dynect.getToken()
            device_list = Devices.objects.filter(fqdn=host)
            password_list = device_list.values('password')
            ip_list = device_list.values('ip')

            root_password = password_list[0]["password"]
            hostIp = ip_list[0]["ip"]
            hostName = host

            try:
                if request.POST.get("ttl", ""):
                    ttl = request.POST.get("ttl", "")
                    # Break FQDN in to node and zone
                    result = dynect.extractFQDN(host)
                    node = result['node']
                    zone = result['zone']
                    logger.debug("Dynect: Add ARecord node: %s zone: %s IP: %s ttl: %s \n" % (
                        node, zone, hostIp, ttl))
                    try:
                        # Add Record
                        dynect.addRecoard(zone, node, hostIp, ttl)
                        # Publish Record
                        dynect.publish(zone)
                    except:
                        pass
            except Exception as e:
                logger.error(e)

            try:
                if request.POST.getlist("group") and request.POST.getlist("templates"):
                    try:
                        # Add Zabbix host, groups, templates
                        zabbix = Zabbix.Zabbix()
                        zabbix.getToken()
                        # from frontend select
                        groups = request.POST.getlist("group")
                        # from frontend multi-select
                        templates = request.POST.getlist("templates")
                        logger.debug("Zabbix: Add Host: %s IP: %s Groups: %s Templates: %s \n" % (
                            hostName, hostIp, groups, templates))
                        # Add Zabbix host
                        zabbix.addHost(hostName, hostIp, groups, templates)
                    except:
                        pass
            except Exception as e:
                logger.error(e)

            try:
                if (request.POST.get("ttl", "") and request.POST.getlist("group") and request.POST.getlist("templates")) or request.POST.get("internap", ""):
                    cmd = '%s ansible_ssh_pass="%s"\n' % (
                        hostName, root_password)
                    logger.debug("Ansible: %s " % cmd)
                    f.write(cmd)
            except Exception as e:
                logger.error(e)

        f.close()

        try:
            if (request.POST.get("ttl", "") and request.POST.getlist("group") and request.POST.getlist("templates")) or request.POST.get("internap", ""):
                ansible = Ansible.Ansible()
                result = ansible.runAnsible()
                logger.debug(result)
        except Exception as e:
            logger.error(e)

        response = "DONE"
        return render_to_response('webapp/mojo.html', {'response': response}, context_instance=RequestContext(request))

    # List all groups and templates and return to fronend
    groupList = GroupList.objects.all().order_by('name')
    templateList = TemplateList.objects.all().order_by('name')

    return render_to_response('webapp/mojo.html', {'groupList': groupList, 'templateList': templateList}, context_instance=RequestContext(request))
