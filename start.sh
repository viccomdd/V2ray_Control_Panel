#!/bin/bash

[ $(id -u) != "0" ] && { echo "${CFAILURE}Error: You must be root to run this script${CEND}"; exit 1; }

cd /usr/local/V2ray_Control_Panel && pip3 install virtualenv && virtualenv venv && source venv/bin/activate
/usr/local/V2ray_Control_Panel/venv/bin/pip3 install -r requirements.txt
/usr/local/V2ray_Control_Panel/venv/bin/python3 /usr/local/V2ray_Control_Panel/app.py

