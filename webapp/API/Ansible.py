#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Ansible API

"""

__author__ = "Jash Lee"
__copyright__ = "Jan 14, 2015"
__credits__ = ["Site Reliability Engineers"]
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Jash Lee"
__email__ = "s905060@gmail.com"
__status__ = "Alpha"

import shlex
import subprocess

import logging
logger = logging.getLogger(__name__)


class Ansible:

    def __init__(self):
        self.svn_path = 'xxxxx.yml'
        self.forks = 30

    def runAnsible(self):
        # os.chdir(../svn/Internap/)
        cmd = "ansible-playbook -i .xxxxx %s -e 'hosts=xxxxx --forks=%s'" % (
            self.svn_path, self.forks)
        logger.debug(cmd)
        args = shlex.split(cmd)
        output = subprocess.Popen(args)
        return output
