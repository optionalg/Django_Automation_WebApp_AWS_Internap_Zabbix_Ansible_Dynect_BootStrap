from django.contrib import admin
from webapp.models import Devices, GroupList, TemplateList, ProxyList, Hosts, ResponsePools, Dns

# Register your models here.

admin.site.register(Devices)
admin.site.register(GroupList)
admin.site.register(TemplateList)
admin.site.register(ProxyList)
admin.site.register(Hosts)
admin.site.register(ResponsePools)
admin.site.register(Dns)
