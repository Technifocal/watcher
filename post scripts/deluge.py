#!/usr/bin/env python
import sys

f = open('/opt/watcher/delugepost.txt', 'a+')
print >> f, 'ARGV'
print >> f, sys.argv

f.close()
