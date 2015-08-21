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
        print "pycurl error tries", str(e.args)
        if e[1] == 'Failed to receive SOCKS4 connect request ack.':
            print 'could not connect to proxy sleeping 3 seconds'
            time.sleep(3)
            c.perform()
    latency = c.getinfo(pycurl.STARTTRANSFER_TIME)*1000 - c.getinfo(pycurl.PRETRANSFER_TIME)*1000
    download_speed = c.getinfo(pycurl.SPEED_DOWNLOAD)*8
    c.close()
    fp.close()

    validfile = tempfile.NamedTemporaryFile(delete=False)
    msgGen = getMsgYield(length)
    for ch in msgGen:
        validfile.write(ch)
    validfile.close()
    valid = filecmp.cmp(fp.name, validfile.name)
    os.unlink(validfile.name)
    os.unlink(fp.name)
    retval = None
    if valid:
        retval = (download_speed, latency)
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
    latency = c.getinfo(pycurl.STARTTRANSFER_TIME)*1000 - c.getinfo(pycurl.PRETRANSFER_TIME)*1000
    upload_speed = c.getinfo(pycurl.SPEED_UPLOAD)*8
    c.close()

    responseData = buf.getvalue()

    if responseData == "OK":
        retval = (upload_speed, latency)
    else:
        retval = None
        print "FAILURE"
    os.unlink(validfile.name)
    return retval
    
#item == 0 speed, item == 1 latency
def getMinMedAvgMax(results, item=0):

    results.sort(key=lambda tup: tup[item])
    iterations = len(results)
    avg = sum([pair[item] for pair in results])/iterations

    if not iterations % 2:
        median = (results[iterations / 2][item] + results[iterations / 2 - 1][item]) / 2.0
    else:
        median = results[iterations / 2][item]

    minimum = results[0][item]
    maximum = results[iterations-1][item]

    return (minimum, median, avg, maximum)
 

def getAverageTransferSpeed(http_server, mar_proxy, mar_proxy_port, direct_proxy, direct_proxy_port, length=18, direction='down', iterations=10):
    direct_results = []
    mar_results = []
    print "Running iterations",
    for i in range(iterations):
        # Direct Connection
        if direction == 'up':
            direct = httpPost(http_server, direct_proxy, direct_proxy_port, length)
        else:
            direct = httpGet(http_server, direct_proxy, direct_proxy_port, length)
        if direct is not None:
            direct_results.insert(i, direct)
        else:
            print "ERROR: Direct transfer: -1"
            direct_results.insert(i, (-1, -1))
        print ".",
        sys.stdout.flush()

        # Marionette Connection
        if direction == 'up':
            mar = httpPost(http_server, mar_proxy, mar_proxy_port, length)
        else:
            mar = httpGet(http_server, mar_proxy, mar_proxy_port, length)
        if mar is not None:
            mar_results.insert(i, mar)
        else:
            print "ERROR: Marionette transfer: -1"
            mar_results.insert(i, (-1, -1))
        print ".",
        sys.stdout.flush()
    print
    return_direct_speed = getMinMedAvgMax(direct_results, 0)
    return_mar_speed = getMinMedAvgMax(mar_results, 0)
    return_direct_latency = getMinMedAvgMax(direct_results, 1)
    return_mar_latency = getMinMedAvgMax(mar_results, 1)

    return (return_mar_speed, return_direct_speed, return_mar_latency, return_direct_latency)


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

    (mar, direct) = getAverageTransferSpeed(args.server, args.proxy, int(args.proxy_port), args.direct_proxy, int(args.direct_proxy_port), args.length, args.direction, int(args.iterations))
    (mar_min, mar_median, mar_avg, mar_max) = mar
    (direct_min, direct_median, direct_avg, direct_max) = direct
    print "Min Direct connection GET time:\t", direct_min
    print "Median Direct connection GET time:\t", direct_median
    print "Average Direct connection GET time:\t", direct_avg
    print "Max Direct connection GET time:\t", direct_max
    print "Min Marionette connection GET time:\t", mar_min
    print "Median Marionette connection GET time:\t", mar_median
    print "Average Marionette connection GET time:\t", mar_avg
    print "Max Marionette connection GET time:\t", mar_max
    print "Average Slowdown =", direct_avg/mar_avg

    (mar, direct) = getAverageTransferSpeed(args.server, args.proxy, int(args.proxy_port), args.direct_proxy, int(args.direct_proxy_port), args.length, "up", int(args.iterations))
    (mar_min, mar_median, mar_avg, mar_max) = mar
    (direct_min, direct_median, direct_avg, direct_max) = direct
    print "Min Direct connection POST time:\t", direct_min
    print "Median Direct connection POST time:\t", direct_median
    print "Average Direct connection POST time:\t", direct_avg
    print "Max Direct connection POST time:\t", direct_max
    print "Min Marionette connection POST time:\t", mar_min
    print "Median Marionette connection POST time:\t", mar_median
    print "Average Marionette connection POST time:\t", mar_avg
    print "Max Marionette connection POST time:\t", mar_max
    print "Average Slowdown =", direct_avg/mar_avg

