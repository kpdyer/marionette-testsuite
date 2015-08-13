#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import httplib
import unittest
import threading
import httpclient

sys.path.append('.')
#TODO: For local testing
#sys.path.append('/Users/charlietanzini/work/tmp/marionette')

import argparse
import marionette_tg.conf


def execute(cmd):
    os.system(cmd)

def exec_timing_test():
    server_ip = marionette_tg.conf.get("server.server_ip")
    http_server_ip = server_ip + ":18080"
    proxy_ip = marionette_tg.conf.get("server.proxy_ip")
    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=8, direction='down', iterations=5)
    print "Direction: down"
    print "\tLength: 8\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg
    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=10, direction='down', iterations=5)
    print "\tLength: 16\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg
    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=18, direction='down', iterations=5)
    print "\tLength: 20\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg

    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=8, direction='up', iterations=5)
    print "Direction: up"
    print "\tLength: 8\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg
    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=10, direction='up', iterations=5)
    print "\tLength: 16\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg
    (mar_avg, direct_avg) = httpclient.getAverageTransferTime(
            http_server_ip, proxy_ip, 18079, server_ip, 18081, length=18, direction='up', iterations=5)
    print "\tLength: 20\tMarionette average: %s\tDirect average: %s" % (mar_avg, direct_avg)
    print "\tSlowdown:", mar_avg/direct_avg


class ParametrizedTestCase(unittest.TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """
    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


class CliTest(ParametrizedTestCase):

    def startservers(self, format):
        client_ip = marionette_tg.conf.get("client.client_ip")
        server_ip = marionette_tg.conf.get("server.server_ip")
        proxy_ip = marionette_tg.conf.get("server.proxy_ip")

        #TODO: Should some of these be started using ansible?
        execute("./httpserver -lport 18080 &")
        execute("socksserver -lport 18081 &")
        execute("marionette_server --server_ip %s --proxy_ip %s --proxy_port 18081 --format %s &" %
                (server_ip, proxy_ip, format))
        time.sleep(5)
        execute("marionette_client --client_ip %s --client_port 18079 --server_ip %s --format %s &" %
                (client_ip, server_ip, format))
        time.sleep(5)

    def stopservers(self):
        execute("pkill -9 -f marionette_client")
        execute("pkill -9 -f marionette_server")
        execute("pkill -9 -f socksserver")
        execute("pkill -9 -f httpserver")
    
        #print "Sleeping 5..."
        time.sleep(5)

    def do_timing_test(self):
        exec_timing_test()

    def test_cli_curl(self):
        if self.param:
            try:
                format = self.param
                self.startservers(format)
                self.do_timing_test()
                sys.stdout.write(format+' ')
                sys.stdout.flush()
            except Exception as e:
                self.assertFalse(True, e)
            finally:
                self.stopservers()

#TODO: ftp_simple_blocking is hanging after ~50MB
suite = unittest.TestSuite()
for param in [
        #'ftp_simple_blocking',
        'http_simple_blocking',
        'http_simple_blocking:20150701', # tests in-band nego.
        'http_simple_blocking:20150702', # tests in-band nego.
        'dummy',
        'http_squid_blocking',
        'http_timings',
        'http_probabilistic_blocking',
        'http_simple_nonblocking',
        'ssh_simple_nonblocking',
        'smb_simple_nonblocking',
        'http_simple_blocking_with_msg_lens',
        'http_active_probing',
        'http_active_probing2',
        'active_probing/http_apache_247',
        'active_probing/ssh_openssh_661',
        'active_probing/ftp_pureftpd_10']:
        suite.addTest(ParametrizedTestCase.parametrize(CliTest, param=param))
unittest.TextTestRunner(verbosity=2).run(suite)

