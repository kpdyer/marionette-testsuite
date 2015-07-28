#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
import unittest
import time

import argparse
import marionette_tg.conf

def execute(cmd):
    subprocess.Popen(["nohup", "python", cmd])

def startservers(format):
    proxy_ip = marionette_tg.conf.get("server.proxy_ip")
    server_ip = marionette_tg.conf.get("server.server_ip")
    httpserver = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "httpserver --local_port 18081 &")
    execute(httpserver)
    execute("marionette_server  --proxy_ip %s --proxy_port 18081 --server_ip %s --format %s &" %
            (proxy_ip, server_ip, format))
    time.sleep(1)

def stopservers():
    execute("pkill -9 -f marionette_server")
    execute("pkill -9 -f httpserver")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices=('start', 'stop', 'restart'))
    parser.add_argument("format",
                        nargs='?',
                        help="Format for Marionette to load",
                        default="dummy")
    args = parser.parse_args()
    if args.action == "start":
        startservers(args.format)
    elif args.action == "stop":
        stopservers()
    elif args.action == "restart":
        stopservers()
        time.sleep(5)
        startservers(args.format)
