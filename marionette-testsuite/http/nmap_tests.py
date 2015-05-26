#!/usr/bin/env python
# coding: utf-8

import os
import unittest
import time

import nmap

import marionette_tg.conf

def execute(cmd):
    os.system(cmd)

class Tests(unittest.TestCase):

    def startservers(self, format):
        server_proxy_iface = marionette_tg.conf.get("server.proxy_iface")

        execute("marionette_server %s 8888 %s &" %
                (server_proxy_iface, format))
        time.sleep(1)

    def stopservers(self):
        execute("pkill -9 -f marionette_server")

    def test_active_probing1(self):
            try:
                self.startservers("nmap/kpdyer.com")
                remote_host = '127.0.0.1'
                remote_port = '8080'

                nm = nmap.PortScanner()
                nm.scan(remote_host, remote_port)
                tcp_obj = nm[remote_host].tcp(int(remote_port))

                self.assertEqual(tcp_obj['name'],    'http')
                self.assertEqual(tcp_obj['product'], 'Apache httpd')
                self.assertEqual(tcp_obj['version'], '2.4.7')
                self.assertEqual(tcp_obj['cpe'],     'cpe:/a:apache:http_server:2.4.7')

            finally:
                self.stopservers()

if __name__ == '__main__':
    unittest.main()
