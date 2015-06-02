#!/bin/bash

cd /root/pxegui
export HWADDR=`ifconfig eth0 | grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}'`
python pxegui.py
