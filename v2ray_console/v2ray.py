#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import platform
import re
import uuid
import json
import time
import logging
import subprocess
import socket
import requests
import urllib.request

logid = {"console": "logs/v2ray_console.log", "access": "/var/log/v2ray/access.log",
         "error": "/var/log/v2ray/error.log", }


def loadconfig(path):
	with open(path, 'r') as load_f:
		try:
			load_dict = json.load(load_f)
			return load_dict
		except Exception as ex:
			logging.error(str(ex))

def saveconfig(path, data):
	# print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
	with open(path, 'w') as f:
		try:
			json.dump(data, f, indent=4, separators=(',', ':'))
		except Exception as ex:
			logging.error(str(ex))
	with open(path, 'r') as load_f:
		load_dict = json.load(load_f)
		return load_dict

def alterfile(file, old_str, new_str):
	# if os.path.exists("v2ray_console/new-v2rayTproxy.sh"):
	# 	os.remove("v2ray_console/new-v2rayTproxy.sh")
	with open(file, "r", encoding="utf-8") as f1, open("new-%s" % file, "w", encoding="utf-8") as f2:
		for line in f1:
			f2.write(re.sub(old_str, new_str, line))

def get_ip():
	"""
	获取本地ip
	"""
	my_ip = ""
	try:
		my_ip = urllib.request.urlopen('http://api.ipify.org').read()
	except Exception:
		my_ip = urllib.request.urlopen('http://icanhazip.com').read()
	return bytes.decode(my_ip).strip()


def is_ipv4(ip):
	try:
		socket.inet_pton(socket.AF_INET, ip)
	except AttributeError:  # no inet_pton here, sorry
		try:
			socket.inet_aton(ip)
		except socket.error:
			return False
		return ip.count('.') == 3
	except socket.error:  # not a valid ip
		return False
	return True


def is_ipv6(ip):
	try:
		socket.inet_pton(socket.AF_INET6, ip)
	except socket.error:  # not a valid ip
		return False
	return True


def check_ip(ip):
	return is_ipv4(ip) or is_ipv6(ip)


def port_is_use(port):
	"""
	判断端口是否占用
	"""
	tcp_use, udp_use = False, False
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	u = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.settimeout(3)
	tcp_use = s.connect_ex(('127.0.0.1', int(port))) == 0
	try:
		u.bind(('127.0.0.1', int(port)))
	except:
		udp_use = True
	finally:
		u.close()
	return tcp_use or udp_use


def GetReleases(author, repo, filename):
	# url = "https://api.github.com/repos/idorecall/selection-menu/releases/latest"
	browser_download_url = None
	url = "https://api.github.com/repos/" + author + '/' + repo + "/releases/latest"
	try:
		r = requests.get(url, timeout=6)
		# print(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ':')))
		if r and r.status_code == 200:
			# print(json.dumps(r.json(), sort_keys=True, indent=4, separators=(',', ':')))
			files = r.json()
			if files.get('assets'):
				for file in files.get('assets'):
					# print(json.dumps(file, sort_keys=True, indent=4, separators=(',', ':')))
					if file.get('name') == filename:
						browser_download_url = file.get('browser_download_url')
						break
	except Exception as ex:
		logging.exception(str(ex))
	finally:
		return browser_download_url

def GetReleases_longtime(author, repo, filename, count=5):
	r = None
	while not r and count > 0:
		r = GetReleases(author, repo, filename)
		count = count - 1
		if r:
			break
		time.sleep(2)
	return r


class V2ray:

	@staticmethod
	def run(command, keyword):
		try:
			subprocess.check_output(command, shell=True)
			logging.info("{}ing v2ray...".format(keyword))
			time.sleep(2)
			if subprocess.check_output("systemctl is-active v2ray|grep active", shell=True) or keyword == "stop":
				logging.info("v2ray {} success !".format(keyword))
				return True
			else:
				raise subprocess.CalledProcessError
		except subprocess.CalledProcessError:
			logging.info("v2ray {} fail !".format(keyword))
			return False

	@staticmethod
	def status():
		statusStr = bytes.decode(
			subprocess.check_output("systemctl status v2ray|grep Active: | awk '{print $3}'", shell=True))
		if 'running' in statusStr:
			return 'running'
		else:
			return 'stopped'

	@staticmethod
	def version():
		v2ray_version = bytes.decode(
			subprocess.check_output("/usr/bin/v2ray/v2ray -version | head -n 1 | awk '{print $2}'", shell=True))
		return v2ray_version

	@staticmethod
	def update():
		logging.info("start v2ray update!")
		subprocess.Popen("curl -L -s https://install.direct/go.sh|bash", shell=True).wait()
		logging.info("v2ray update completely!")

	@staticmethod
	def cleanLog():
		subprocess.call("cat /dev/null > /var/log/v2ray/access.log", shell=True)
		subprocess.call("cat /dev/null > /var/log/v2ray/error.log", shell=True)
		logging.info("clean v2ray log success!")

	@staticmethod
	def logs(pathid):
		path = logid.get(pathid)
		if not os.path.exists(path):
			logging.info(path + " is nonexistent,")
			return None
		cmd_str = "tail -100 " + path
		codemethod = 'utf-8'
		pattern = r'[\r\n]+'
		if (platform.system() != "Linux"):
			codemethod = 'gbk'
		logs_ret = bytes.decode(
			subprocess.check_output(cmd_str, shell=True), encoding=codemethod).strip()
		result = re.split(pattern, logs_ret)
		if type(result) == list:
			result = json.dumps(result)
		return result

	@staticmethod
	def rtlog():
		cmd_list = ['tail', '-f', '-n', '100', 'logs/v2ray_console.log']
		cmd_str = " ".join(cmd_list)
		f = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		log_ret = bytes.decode(f.stdout.readline().strip())
		find_processid = """ps -ef | grep '""" + cmd_str + """' | grep -v grep | awk '{print $2}'"""
		processid_list = bytes.decode(subprocess.check_output(find_processid, shell=True)).strip()
		for processid in processid_list:
			subprocess.call("kill " + processid, shell=True)
		return log_ret

	@staticmethod
	def v2rayStats():
		v2ray_stats = []
		v2ray_stats_str = bytes.decode(subprocess.check_output("v2ctl api --server=127.0.0.1:10085  StatsService.QueryStats 'pattern: \"\" reset: false'", shell=True))
		for i, v in enumerate(re.split(r'stat:', v2ray_stats_str)):
			if len(v) > 0:
				rr = re.split(r'[\r\n]+', v.strip())
				a = rr[1].strip().replace("\"", "")
				b = rr[2].strip()
				vlist = a.split(': ')[1].split(">>>")
				vlist.append(b.split(": ")[1])
				v2ray_stats.append(vlist)
		return v2ray_stats

	@staticmethod
	def v2rayApps_fileurl(v2rayApps):
		v2rayAppsPath = "v2ray_console/v2rayApps.json"
		v2rayAppsFiles = []
		remoteRead = True
		saveFlag = True
		if os.path.exists(v2rayAppsPath):
			v2rayAppsdict = loadconfig(v2rayAppsPath)
			if v2rayAppsdict:
				lasttime = v2rayAppsdict.get('timestamp')
				if lasttime and int(time.time()) - lasttime < 186400:
					v2rayAppsFiles = v2rayAppsdict.get('data')
					remoteRead = False
			else:
				logging.error("v2ray_console/v2rayApps.json read error")
				os.remove(v2rayAppsPath)
		if remoteRead:
			for app in v2rayApps:
				if (app[0] == 'tablet_mac'):
					file = {"platform": app[0], "appName": app[1], "author": app[2], "repo": app[3], "filename": app[4]}
					v2rayAppsFiles.append(file)
				else:
					r = GetReleases_longtime(app[2], app[3], app[4])
					if r:
						file = {"platform": app[0], "appName": app[1], "author": app[2], "repo": app[3], "filename": r}
						v2rayAppsFiles.append(file)
					else:
						saveFlag = False
						v2rayAppsFiles = []
						break

			# print(json.dumps(v2rayAppsFiles, sort_keys=True, indent=4, separators=(',', ':')))
			if saveFlag:
				v2rayAppsdict = {"timestamp": int(time.time()), "data": v2rayAppsFiles}
				saveconfig(v2rayAppsPath, v2rayAppsdict)
		return v2rayAppsFiles

	@classmethod
	def restart(cls):
		return cls.run("systemctl restart v2ray", "restart")

	@classmethod
	def start(cls):
		return cls.run("systemctl start v2ray", "start")

	@classmethod
	def stop(cls):
		return cls.run("systemctl stop v2ray", "stop")

	@classmethod
	def check(cls):
		if not os.path.exists("/usr/bin/v2ray/v2ray"):
			logging.info("check v2ray no install, auto install v2ray..")
			if is_ipv6(get_ip()):
				subprocess.Popen("curl -Ls https://install.direct/go.sh -o v2raytemp.sh", shell=True).wait()
				subprocess.Popen("bash v2raytemp.sh --source jsdelivr && rm -f v2raytemp.sh", shell=True).wait()
			else:
				cls.update()
