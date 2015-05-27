#!/usr/bin/env python
# coding: utf-8

import os
import unittest
import time

import marionette_tg.conf
import marionette_testsuite.nessus


def execute(cmd):
    os.system(cmd)


class Tests(unittest.TestCase):

    def startservers(self, format):
        server_proxy_iface = marionette_tg.conf.get("server.proxy_iface")

        execute("marionette_server %s 8888 %s &" %
                (server_proxy_iface, format))
        time.sleep(0.25)

    def stopservers(self):
        execute("pkill -9 -f marionette_server")

    def test_active_probing_ftp_nessus(self):
        global token
        try:
            self.startservers("active_probing/ftp_pureftpd_10")
            data = marionette_testsuite.nessus.do_scan('127.0.0.1')
            success = marionette_testsuite.nessus.eval_plugin_output(
                data, 10092, 'tcp', 2121, 'ftp', 'Welcome to Pure-FTPd')
            self.assertTrue(success)
        finally:
            self.stopservers()


if __name__ == '__main__':
    unittest.main()
