#!/usr/bin/env python
# coding: utf-8

import os
import unittest
import time

import nessrest.ness6rest as nessrest

import marionette.conf

def execute(cmd):
    os.system(cmd)

class Tests(unittest.TestCase):

    def startservers(self, format):
        server_proxy_iface = marionette.conf.get("server.proxy_iface")

        execute("marionette_server %s 8888 %s &" %
                (server_proxy_iface, format))
        time.sleep(0.25)

    def stopservers(self):
        execute("pkill -9 -f marionette_server")

    def test_active_probing1(self):
        print 'hi'
        #try:
        #    self.startservers("nmap/kpdyer.com")
        #remote_host = '127.0.0.1'
        #remote_port = '8080'

        # Connecting to a server
        server = '127.0.0.1'
        port = 8834
        username = 'admin'
        password = 'admin'

        print 'scanner'
        scan = nessrest.Scanner(url="https://"+server+":"+str(port),
                                login=username, password=password,
                                insecure=True)
        print 'add'
        scan.scan_add(targets=server)
        scan.policy_add(name="Scripted Scan", plugins="10107") # plugin to check for webservers
        print 'start run'
        scan.scan_run()
        print 'done run'
        print scan.scan_results()
        kbs = scan.download_kbs()

        for hostname in kbs.keys():
            f = open(hostname, "w")
            f.write(kbs[hostname])
            f.close()
        #finally:
        #    self.stopservers()

if __name__ == '__main__':
    unittest.main()
