#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import httplib
import unittest
import threading

sys.path.append('.')

import marionette_tg.conf


def execute(cmd):
    os.system(cmd)


def exec_download():
    client_client_ip = marionette_tg.conf.get("client.client_ip")
    conn = httplib.HTTPConnection(
        client_client_ip, 18079, False, timeout=30)
    conn.request("GET", "/")
    response = conn.getresponse()
    actual_response = response.read()
    conn.close()

    expected_response = ''
    for x in range(2**18):
        expected_response += '_' + str(x)

    assert actual_response == expected_response

    return actual_response


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
        client_client_ip = marionette_tg.conf.get("client.client_ip")
        server_proxy_ip = marionette_tg.conf.get("server.proxy_ip")

        execute("marionette_client --client_ip %s --client_port 18079 --format %s &" %
                (client_client_ip, format))
        time.sleep(5)

    def stopservers(self):
        execute("pkill -9 -f marionette_client")

    def dodownload_serial(self):
        exec_download()

    def dodownload_parallel(self):
        simultaneous = 2
        threads = []
        for j in range(simultaneous):
            t = threading.Thread(target=exec_download)
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    def test_cli_curl(self):
        if self.param:
            try:
                format = self.param
                #self.startservers(format)
                self.dodownload_serial()
                self.dodownload_parallel()
                sys.stdout.write(format+' ')
                sys.stdout.flush()
            except Exception as e:
                self.assertFalse(True, e)
            finally:
                self.stopservers()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("format",
                        nargs='?',
                        help="Format for Marionette to load",
                        default="dummy")
    args = parser.parse_args()
    # Configure the tests suite
    suite = unittest.TestSuite()
    suite.addTest(ParametrizedTestCase.parametrize(CliTest, param=args.format))
    unittest.TextTestRunner(verbosity=2).run(suite)
