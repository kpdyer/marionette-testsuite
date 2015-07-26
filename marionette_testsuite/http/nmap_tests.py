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
        server_proxy_ip = marionette_tg.conf.get("server.proxy_ip")

        execute("marionette_server --proxy_ip %s --proxy_port 8888 --format %s &" %
                (server_proxy_ip, format))
        time.sleep(1)

    def stopservers(self):
        execute("pkill -9 -f marionette_server")

    def test_active_probing_http_nmap(self):
        try:
            self.startservers("active_probing/http_apache_247")
            remote_host = '127.0.0.1'
            remote_port = '8080'

            nm = nmap.PortScanner()
            nm.scan(remote_host, remote_port)
            tcp_obj = nm[remote_host].tcp(int(remote_port))

            self.assertEqual(tcp_obj['name'],    'http')
            self.assertEqual(tcp_obj['product'], 'Apache httpd')
            self.assertEqual(tcp_obj['version'], '2.4.7')
        finally:
            self.stopservers()

if __name__ == '__main__':
    unittest.main()
