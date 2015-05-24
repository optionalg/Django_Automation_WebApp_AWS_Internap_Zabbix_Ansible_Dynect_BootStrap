from django.db import models

# Create your models here.


class Devices(models.Model):
    fqdn = models.CharField(max_length=50, primary_key=True)
    ip = models.CharField(max_length=20)
    ttl = models.IntegerField(default=0)
    password = models.CharField(max_length=30)
    status = models.CharField(max_length=10)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s %s %s %s %s' % (self.fqdn, self.ip, self.ttl, self.password, self.status, self.date)


class GroupList(models.Model):
    groupId = models.IntegerField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s' % (self.name, self.groupId)


class TemplateList(models.Model):
    templateId = models.IntegerField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s' % (self.name, self.templateId)


class ProxyList(models.Model):
    proxyId = models.IntegerField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s' % (self.name, self.proxyId)


class Hosts(models.Model):
    fqdn = models.ForeignKey(Devices)
    groupId = models.ManyToManyField(GroupList)
    templateId = models.ManyToManyField(TemplateList)
    proxyId = models.ManyToManyField(ProxyList)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s %s %s' % (self.fqdn, self.groupId, self.templateId, self.proxyId)


class Dns(models.Model):
    zone = models.CharField(max_length=100)
    aRecord = models.CharField(max_length=100)
    ip = models.CharField(max_length=20)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s %s' % (self.zone, self.aRecord, self.ip)


class ResponsePools(models.Model):
    pools = models.CharField(max_length=50)
    label = models.CharField(max_length=50)
    address = models.CharField(max_length=20)
    weight = models.CharField(max_length=2)
    mode = models.CharField(max_length=6)
    eligible = models.CharField(max_length=5)
    status = models.CharField(max_length=4)
    tag = models.CharField(max_length=10)

    def __str__(self):              # __unicode__ on Python 2
        return '%s %s %s %s %s %s %s %s' % (self.pools, self.label, self.address, self.weight, self.mode, self.eligible, self.status, self.tag)
