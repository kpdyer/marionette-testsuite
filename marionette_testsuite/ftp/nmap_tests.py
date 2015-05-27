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

    def test_active_probing_ftp_nmap(self):
        try:
            self.startservers("active_probing/ftp_pureftpd_10")
            remote_host = '127.0.0.1'
            remote_port = '2121'

            nm = nmap.PortScanner()
            nm.scan(remote_host, remote_port)
            tcp_obj = nm[remote_host].tcp(int(remote_port))

            print tcp_obj
            self.assertEqual(tcp_obj['name'],    'ftp')
            self.assertEqual(tcp_obj['product'], 'Pure-FTPd')
            self.assertEqual(tcp_obj['version'], '')
            self.assertEqual(tcp_obj['cpe'],     'cpe:/a:pureftpd:pure-ftpd')
        finally:
            self.stopservers()

if __name__ == '__main__':
    unittest.main()
