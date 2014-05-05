#!/usr/bin/env python
__author__ = 'babnik'
from pynginxconfig import NginxConfig
import argparse
import subprocess
parser = argparse.ArgumentParser(description='Test editor for nginx host')
parser.add_argument('-b', '--backend', metavar=' ip:port', type=str, help='Add backend servers to pool', nargs='+')
args=parser.parse_args()
val=[]
for host in args.backend:
    val.append(('server', host))

nc = NginxConfig()
nc.load('')
nc.append({'name': 'upstream', 'param': 'backend', 'value': val}, position=1)
f1 = open("/etc/nginx/sites-available/default", 'a')
f1.write(str(nc.gen_config()))
f1.close()
