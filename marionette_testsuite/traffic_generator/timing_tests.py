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

import argparse
import marionette_tg.conf


def execute(cmd):
    os.system(cmd)


def exec_download(param):
    mar_socksproxy_ip = marionette_tg.conf.get("client.client_ip")
    mar_socksproxy_port = marionette_tg.conf.get("client.client_port")
    direct_socksproxy_ip = marionette_tg.conf.get("server.proxy_ip")
    direct_socksproxy_port = marionette_tg.conf.get("server.proxy_port")

    http_server = param.http_server
    iterations = param.iterations
    outfile = param.outfile
    powers = param.powers
    fp = open(outfile, "w")

    print

    fp.write("Power\tDirection\tMarionette min\tMarionette median\tMarionette average\tMarionette max\tDirect min    \tDirect median\tDirect average\tDirect max\tSlowdown\n")
    for p in powers:

        (mar_speed_results, direct_speed_results, mar_latency_results, direct_latency_results) = httpclient.getAverageTransferSpeed(
                http_server, 
                mar_socksproxy_ip, 
                mar_socksproxy_port, 
                direct_socksproxy_ip, 
                direct_socksproxy_port, 
                length=p, 
                direction="down", 
                iterations=iterations)
        fp.write("%-5s\t%-9s\t%-14s\t%-17s\t%-18s\t%-14s\t%-14s\t%-14s\t%-14s\t%-10s\t%s\n" % (
            p, "down", mar_speed_results[0], mar_speed_results[1], mar_speed_results[2], mar_speed_results[3],
            direct_speed_results[0], direct_speed_results[1], direct_speed_results[2], direct_speed_results[3], 
            direct_speed_results[2]/mar_speed_results[2]))

        (mar_speed_results, direct_speed_results, mar_latency_results, direct_latency_results) = httpclient.getAverageTransferSpeed(
                http_server, 
                mar_socksproxy_ip, 
                mar_socksproxy_port, 
                direct_socksproxy_ip, 
                direct_socksproxy_port, 
                length=p, 
                direction="up", 
                iterations=iterations)
        fp.write("%-5s\t%-9s\t%-14s\t%-17s\t%-18s\t%-14s\t%-14s\t%-14s\t%-14s\t%-10s\t%s\n" % (
            p, "down", mar_speed_results[0], mar_speed_results[1], mar_speed_results[2], mar_speed_results[3],
            direct_speed_results[0], direct_speed_results[1], direct_speed_results[2], direct_speed_results[3], 
            direct_speed_results[2]/mar_speed_results[2]))

    fp.write("\n\nLatency Results (in ms):\n")
    fp.write("Marionette min\tMarionette median\tMarionette average\tMarionette max\tDirect min    \tDirect median\tDirect average\tDirect max\n")
    (mar_speed_results, direct_speed_results, mar_latency_results, direct_latency_results) = httpclient.getAverageTransferSpeed(
            http_server, 
            mar_socksproxy_ip, 
            mar_socksproxy_port, 
            direct_socksproxy_ip, 
            direct_socksproxy_port, 
            length=1,
            direction="down",
            iterations=iterations)

    fp.write("%-14s\t%-17s\t%-18s\t%-14s\t%-14s\t%-14s\t%-14s\t%-10s\n" % (
        mar_latency_results[0], mar_latency_results[1], mar_latency_results[2], mar_latency_results[3],
        direct_latency_results[0], direct_latency_results[1], direct_latency_results[2], direct_latency_results[3]))

    fp.close()


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
        client_port = marionette_tg.conf.get("client.client_port")
        server_ip = marionette_tg.conf.get("server.server_ip")

        execute("marionette_client --client_ip %s --client_port %s --server_ip %s --format %s &" %
                (client_ip, client_port, server_ip, format))
        time.sleep(5)

    def stopservers(self):
        execute("pkill -9 -f marionette_client")

    def dodownload(self, param):
        exec_download(param)

    def test_cli_curl(self):
        if self.param:
            try:
                format = self.param.format
                self.startservers(format)
                self.dodownload(self.param)
                sys.stdout.write(format+' ')
                sys.stdout.flush()
            except Exception as e:
                self.assertFalse(True, e)
            finally:
                self.stopservers()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Respond to HTTP requests with integer strings.')
    parser.add_argument('--http_server', '-s', dest='http_server', required=False,
        default="127.0.0.1:8080", help='HTTP Server addres')
    parser.add_argument('--powers', '-p', dest='powers', required=True, 
        action='append', help='Power of 2 to generate power string length (between 1-25)')
    parser.add_argument('--socksproxy_server', '-sp', dest='socksproxy_server', required=False,
        help='Socks proxy server address')
    parser.add_argument('--socksproxy_port', '-spport', dest='socksproxy_port', required=False,
        help='Socks proxy server port')
    parser.add_argument('--direct_socksproxy_server', '-dsp', dest='direct_socksproxy', required=False,
        help='Direct socks proxy server address (without Marionette layer)')
    parser.add_argument('--direct_socksproxy_port', '-dspport', dest='direct_socksproxy_port', required=False,
        help='Direct socks proxy server port')
    parser.add_argument('--iterations', '-i', dest='iterations', required=False,
        type=int, default=5, help='Number of iterations to average over')
    parser.add_argument('--format', '-f', dest='format', required=False,
        default="dummy", help="Format for Marionette to load")
    parser.add_argument('--write', '-w', dest='outfile', required=False,
        default="/tmp/timing_test.out", help="Write outout to file")
    args = parser.parse_args()

    if args.direct_socksproxy != None:
        marionette_tg.conf.set('server.proxy_ip', str(args.direct_socksproxy))
    if args.direct_socksproxy_port != None:
        marionette_tg.conf.set('server.proxy_port', int(args.direct_socksproxy_port))
    if args.socksproxy_server != None:
        marionette_tg.conf.set('client.client_ip', str(args.socksproxy_server))
    if args.socksproxy_port != None:
        marionette_tg.conf.set('client.client_port', int(args.socksproxy_port))
    if args.format != None:
        marionette_tg.conf.set('general.format', str(args.format))



    # Configure the tests suite
    suite = unittest.TestSuite()
    suite.addTest(ParametrizedTestCase.parametrize(CliTest, param=args))
    unittest.TextTestRunner(verbosity=2).run(suite)
