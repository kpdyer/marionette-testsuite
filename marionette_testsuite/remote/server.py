#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
import unittest
import time

import argparse

def startservers(format):
    httpserver = [os.path.join(os.path.dirname(os.path.realpath(__file__)),"httpserver"),
                  "--local_port", "18081"]
    subprocess.Popen(httpserver)
    time.sleep(1)
    marionetteserver = ["marionette_server",
                       "--proxy_ip", "127.0.0.1",
                       "--proxy_port", "18081",
                       "--server_ip", "0.0.0.0",
                       "--format", format]
    subprocess.Popen(marionetteserver)

def stopservers():
    subprocess.Popen(["pkill", "-9", "-f", "marionette_server"])
    subprocess.Popen(["pkill", "-9", "-f", "httpserver"])

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
