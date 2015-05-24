#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Amazon API

"""

__author__ = "Jash Lee"
__copyright__ = "Jan 14, 2015"
__credits__ = ["Site Reliability Engineers"]
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Jash Lee"
__email__ = "s905060@gmail.com"
__status__ = "Alpha"

import logging
logger = logging.getLogger(__name__)

from boto import ec2


class Amazon:

    def __init__(self):

        self.AWS_ACCESS_KEY_ID = 'xxxxx'
        self.AWS_SECRET_ACCESS_KEY = 'xxxxx'

    def getDevice(self):
        try:
            ec2conn = ec2.connection.EC2Connection(
                self.AWS_ACCESS_KEY_ID, self.AWS_SECRET_ACCESS_KEY)
            reservations = ec2conn.get_all_instances()
            instances = [i for r in reservations for i in r.instances]
            logger.debug("Get instances sucessfully")
            return instances

        except Exception as e:
            logger.error("Can't get Instances")
            logger.error(e)
