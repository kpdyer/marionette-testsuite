#!/usr/bin/env python
# coding: utf-8

import sys
import argparse

import pycurl
from StringIO import StringIO
import time
import itertools
import tempfile
import filecmp
import os

sys.path.append('.')

def getMsgYield(requested_length):
    retval = ''
    try:
        power = int(requested_length)
        if power > 25:
            raise Exception("Too large")
    except:
        power = 18
    for x in xrange(2**power):
        yield '_'
        for ch in str(x):
            yield ch


def httpGet(http_server, proxy, proxy_port, length):

    fp = tempfile.NamedTemporaryFile(delete=False)
    url = "http://" + http_server + "/" + str(length)
    buf = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(c.WRITEDATA, fp)
    c.setopt(pycurl.PROXY, proxy)
    c.setopt(pycurl.PROXYPORT, proxy_port)
    c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
    try:
        c.perform()
    except pycurl.error, e:
        #TODO: Why is this failing??
        print "pycurl error tries", str(e.args)
        if e[1] == 'Failed to receive SOCKS4 connect request ack.':
            print 'could not connect to proxy sleeping 5 seconds'
            time.sleep(3)
            c.perform()
    c.close()
    fp.close()

    validfile = tempfile.NamedTemporaryFile(delete=False)
    msgGen = getMsgYield(length)
    for ch in msgGen:
        validfile.write(ch)
    validfile.close()
    retval = filecmp.cmp(fp.name, validfile.name)
    os.unlink(validfile.name)
    os.unlink(fp.name)
    return retval

def httpPost(http_server, proxy, proxy_port, length):

    validfile = tempfile.NamedTemporaryFile(delete=False)
    msgGen = getMsgYield(length)
    for ch in msgGen:
        validfile.write(ch)
    validfile.close()
    url = "http://" + http_server + "/" + str(length)
    buf = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.CONNECTTIMEOUT, 30)
    c.setopt(c.WRITEDATA, buf)
    c.setopt(pycurl.PROXY, proxy)
    c.setopt(pycurl.PROXYPORT, proxy_port)
    c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS4)
    c.setopt(c.HTTPPOST, [("posted", (c.FORM_FILE, validfile.name))])
    c.perform()
    c.close()
    os.unlink(validfile.name)

    responseData = buf.getvalue()

    if responseData == "OK":
        return True
    else:
        print "FAILURE"
        return False

def getAverageTransferTime(http_server, mar_proxy, mar_proxy_port, direct_proxy, direct_proxy_port, length=18, direction='down', iterations=10):
    direct_times = []
    mar_times = []
    print "Running iterations",
    for i in range(iterations):
        # Direct Connection
        direct_start = time.time()
        if direction == 'up':
            direct = httpPost(http_server, direct_proxy, direct_proxy_port, length)
        else:
            direct = httpGet(http_server, direct_proxy, direct_proxy_port, length)
        direct_end = time.time()
        if direct:
            direct_times.insert(i, direct_end - direct_start)
        else:
            print "ERROR: 999999"
            direct_times.insert(i, 999999)
        print ".",
        sys.stdout.flush()

        # Marionette Connection
        mar_start = time.time()
        if direction == 'up':
            mar = httpPost(http_server, mar_proxy, mar_proxy_port, length)
        else:
            mar = httpGet(http_server, mar_proxy, mar_proxy_port, length)
        mar_end = time.time()
        if mar:
            mar_times.insert(i, mar_end - mar_start)
        else:
            print "ERROR: 999999"
            mar_times.insert(i, 999999)
        print ".",
        sys.stdout.flush()
    print

    direct_times.sort()
    mar_times.sort()
    direct_avg = 0
    mar_avg = 0
    # Throw out fastest and slowest
    for i in range(1, iterations-1):
        direct_avg += direct_times[i]
        mar_avg += mar_times[i]
    direct_avg = direct_avg/(iterations-2)
    mar_avg = mar_avg/(iterations-2)
    return (mar_avg, direct_avg)

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Respond to HTTP requests with integer strings.')
    parser.add_argument('--server', '-s', dest='server', required=False,
        default="127.0.0.1:8080", help='HTTP Server addres')
    parser.add_argument('--length', '-l', dest='length', required=False,
        default="18", help='local port to listen on for HTTP requests')
    parser.add_argument('--proxy_server', '-p', dest='proxy', required=False,
        default="127.0.0.1", help='Proxy server address')
    parser.add_argument('--proxy_port', '-pport', dest='proxy_port', required=False,
        default="8079", help='Proxy server port')
    parser.add_argument('--direct_proxy_server', '-dp', dest='direct_proxy', required=False,
        default="127.0.0.1", help='Direct proxy server address (without Marionette layer)')
    parser.add_argument('--direct_proxy_port', '-dpport', dest='direct_proxy_port', required=False,
        default="8081", help='Direct proxy server port')
    parser.add_argument('--direction', '-d', dest='direction', required=False,
        default="down", help='Direction of traffic "up"/"down" for HTTP requests')
    parser.add_argument('--iterations', '-i', dest='iterations', required=False,
        type=int, default=10, help='Number of iterations to average over')
    args = parser.parse_args()

    (mar_avg, direct_avg) = getAverageTransferTime(args.server, args.proxy, int(args.proxy_port), args.direct_proxy, int(args.direct_proxy_port), args.length, args.direction, int(args.iterations))
    print "Average Direct connection GET time:\t", direct_avg
    print "Average Marionette connection GET time:\t", mar_avg
    print "Slowdown =", mar_avg/direct_avg

    (mar_avg, direct_avg) = getAverageTransferTime(args.server, args.proxy, int(args.proxy_port), args.direct_proxy, int(args.direct_proxy_port), args.length, "up", int(args.iterations))
    print "Average Direct connection POST time:\t", direct_avg
    print "Average Marionette connection POST time:\t", mar_avg
    print "Slowdown =", mar_avg/direct_avg
    #httpGet(args.server, args.proxy, int(args.proxy_port), args.length)
    #httpPost(args.server, args.proxy, int(args.proxy_port), args.length)

