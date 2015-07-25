#!/usr/bin/env python
# coding: utf-8

import os
import unittest
import time

import argparse
import marionette_tg.conf

def execute(cmd):
    os.system(cmd)

def startservers(format):
    server_proxy_iface = marionette_tg.conf.get("server.proxy_iface")
    httpserver = os.path.join(os.path.dirname(os.path.realpath(__file__)), "httpserver")
    execute("%s 18081 &" % httpserver)
    execute("marionette_server %s 18081 %s &" %
            (server_proxy_iface, format))
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
