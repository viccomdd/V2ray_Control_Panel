#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.security import APIKeyCookie
from pydantic import BaseModel
from starlette.responses import Response, HTMLResponse, FileResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette import status
from jose import jwt
import uvicorn
import json
import re
import chardet
import os, sys, platform
import subprocess
import requests
import logging
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler
from v2ray_console.v2rayCrypto import appconfigLoad, appconfigSave, V2rayCryp
from v2ray_console.v2ray import V2ray


formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
log_level = 'INFO'
log_filenum = 9
log_maxsize = 4
level = logging.getLevelName(log_level)
logging.basicConfig(level=level, format=formatter)
if not os.path.exists("logs"):
	os.mkdir("logs")
log = logging.getLogger()
# 输出到文件
fh = RotatingFileHandler('./logs/v2ray_console.log', mode='a+', maxBytes=log_maxsize * 1024 * 1024,
                         backupCount=log_filenum, delay=True)
fh.setFormatter(logging.Formatter(formatter))
log.addHandler(fh)

v2rayApps = [['desktop_windows', 'v2rayN', '2dust', 'v2rayN', 'v2rayN-Core.zip'],
             ['android', 'v2rayNG', '2dust', 'v2rayNG', 'v2rayNG_1.2.4.apk'],
             ['desktop_mac', 'V2RayX', 'Cenmrev', 'V2RayX', 'V2RayX.app.zip'],
             ['tablet_mac', 'Kitsunebi', 'noppefoxwolf', 'Kitsunebi',
              'https://www.apple.com/us/search/Kitsunebi?src=globalnav']]

class v2rayItems(BaseModel):
	config: dict

class UserItems(BaseModel):
	UserItems: dict

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory='static'), name='static')
cookie_sec = APIKeyCookie(name="session")
v2raydata = appconfigLoad('v2ray_console/v2ray.ini')
secret_key = v2raydata.get('key2')
vaes = V2rayCryp(v2raydata.get('key1'))
users = json.loads(vaes.decrypt(v2raydata.get('users')))


def turnfile(file):
	with open(file, 'rb') as f:
		data = f.read()
		encoding = chardet.detect(data)['encoding']
		data_str = data.decode(encoding)
		tp = 'LF'
		if '\r\n' in data_str:
			tp = 'CRLF'
			data_str = data_str.replace('\r\n', '\n')
		if encoding not in ['utf-8', 'ascii'] or tp == 'CRLF':
			with open(file, 'w', newline='\n', encoding='utf-8') as f:
				f.write(data_str)

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

def alter(file, old_str, new_str):
	if os.path.exists("v2ray_console/new-v2rayTproxy.sh"):
		os.remove("v2ray_console/new-v2rayTproxy.sh")
	with open("v2ray_console/" + file, "r", newline='\n', encoding="utf-8") as f1, open("v2ray_console/" + "new-%s" % file, "w", encoding="utf-8") as f2:
		for line in f1:
			f2.write(re.sub(old_str, new_str, line))
	turnfile("v2ray_console/new-v2rayTproxy.sh")


def get_current_user(session: str = Depends(cookie_sec)):
	try:
		payload = jwt.decode(session, secret_key)
		user = payload["user"]
		if payload.get('timesec'):
			if 0 <= int(time.time()) - int(payload.get('timesec')) < 86400:
				# print(payload)
				return user
			else:
				raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="session out of date")
		else:
			raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="session out of date")
	except Exception:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authentication")


@app.get("/")
async def index(request: Request):
	# print(request.body())
	return templates.TemplateResponse('index.html', {'request': request})


@app.get("/user")
async def index(request: Request):
	# print(request.body())
	return templates.TemplateResponse('user.html', {'request': request})


@app.get("/logs")
async def index(request: Request):
	# print(request.body())
	return templates.TemplateResponse('logs.html', {'request': request})


@app.get("/login")
async def login(request: Request):
	return templates.TemplateResponse('signin.html', {'request': request})


@app.post("/login")
def login(request: Request, response: Response, username: str = Form(...), password: str = Form(...),
          extracode: str = Form(...)):
	if username not in users:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user")
	db_password = users[username]["password"]
	if not password == db_password:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid password")
	token = jwt.encode({"user": username, "timesec": int(time.time())}, secret_key)
	response.set_cookie("session", token)
	response.set_cookie("username", username)
	if extracode:
		response.set_cookie("extracode", extracode)
	log.info(username + ' login ok')
	return {"result": True, "message": 'ok'}


@app.get("/logout")
def logout(request: Request, response: Response):
	return {"result": False, "message": 'must use post method'}


@app.post("/logout")
def logout(request: Request, response: Response, username: str = Depends(get_current_user)):
	response.delete_cookie("session")
	response.delete_cookie("username")
	return {"result": True, "message": 'ok'}


@app.get("/tproxydown")
def tproxydown():
	return RedirectResponse("/tproxyshell?" + str(int(time.time())))

@app.get("/tproxyshell")
def tproxyshell():
	# ext = os.path.basename(file_path).split('.')[-1].lower()
	# response = FileResponse(open(file_path, 'rb'))
	# # cannot be used to download py, db and sqlite3 files.
	# if ext not in ['py', 'db', 'sqlite3']:
	alter("v2rayTproxy.sh", "a39c3628-191c-4d0a-8a5b-47d1464b976b", "633134f5-d004-0fcf-766f-3da738a9d5d4")
	response = FileResponse("v2ray_console/new-v2rayTproxy.sh")
	response.media_type = "application/octet-stream"
	response.filename = "v2rayTproxy.sh"
	return response


@app.get("/private")
def read_private(username: str = Depends(get_current_user)):
	return {"result": True, "username": username, "private": "get some private data"}


@app.get("/api/ping")
async def api_ping(response: Response, username: str = Depends(get_current_user)):
	token = jwt.encode({"user": username, "timesec": int(time.time())}, secret_key)
	response.set_cookie("session", token)
	response.set_cookie("username", username)
	return {"result": True, "message": username}


@app.get("/api/defaultConfig")
async def api_defaultConfig(username: str = Depends(get_current_user)):
	if not os.path.exists("config.json"):
		logging.info("config.json is nonexistent,")
		return {"result": False, "message": None}
	serverConfig: dict = loadconfig("config.json")
	return {"result": True, "message": serverConfig}


@app.get("/api/serverConfig")
async def api_serverConfig(username: str = Depends(get_current_user)):
	if not os.path.exists("/etc/v2ray/config.json"):
		logging.info("/etc/v2ray/config.json is nonexistent,")
		return {"result": False, "message": None}
	serverConfig: dict = loadconfig("/etc/v2ray/config.json")
	stats = V2ray.v2rayStats()
	return {"result": True, "message": serverConfig, "stats": stats}


@app.post("/api/serverConfig")
async def api_serverConfig(items: v2rayItems, username: str = Depends(get_current_user)):
	if not os.path.exists("/etc/v2ray/config.json"):
		logging.info("/etc/v2ray/config.json is nonexistent,")
		return {"result": False, "message": None}
	items_dict = items.dict().get('config')
	# print(items_dict)
	if items_dict:
		serverConfig: dict = saveconfig("/etc/v2ray/config.json", items_dict)
	return {"result": True, "message": serverConfig}


@app.post("/api/applyConfig")
async def api_applyConfig(items: v2rayItems, username: str = Depends(get_current_user)):
	if not os.path.exists("/etc/v2ray/config.json"):
		logging.info("/etc/v2ray/config.json is nonexistent,")
		return {"result": False, "message": None}
	items_dict = items.dict().get('config')
	# print(items_dict)
	if items_dict:
		serverConfig: dict = saveconfig("/etc/v2ray/config.json", items_dict)
	cmdr = V2ray.restart()
	log.info('restart ' + str(cmdr))
	if cmdr:
		return {"result": True, "message": {"save": 'successful', "apply": 'successful'}}
	else:
		return {"result": False, "message": {"save": 'successful', "apply": 'failed'}}


@app.get("/api/vpspublicip")
def api_vpsPublicIp(username: str = Depends(get_current_user)):
	r = None
	try:
		r = requests.get("http://api.ipify.org", timeout=2)
		if r and r.status_code == 200:
			return {"result": True, "message": r.text}
	except Exception:
		r = requests.get("http://ifconfig.me/ip", timeout=2)
		if r and r.status_code == 200:
			return {"result": True, "message": r.text}
	return {"result": False, "message": r}


@app.get("/api/v2rayVersion")
def api_v2rayVersion(username: str = Depends(get_current_user)):
	v2ray_version = bytes.decode(
		subprocess.check_output("/usr/bin/v2ray/v2ray -version | head -n 1 | awk '{print $2}'", shell=True))
	if v2ray_version:
		return {"result": True, "message": v2ray_version}
	else:
		return {"result": True, "message": None}


@app.post("/api/v2rayUpdate")
def api_v2rayUpdate(username: str = Depends(get_current_user)):
	V2ray.update()
	return {"result": True}


@app.get("/api/v2rayStatus")
def api_v2rayStatus(username: str = Depends(get_current_user)):
	cmd = """ps -ef | grep "v2ray" | grep -v grep | awk '{print $2}'"""
	output = subprocess.getoutput(cmd)
	if output == "":
		return {"result": True, "message": 'stopped'}
	else:
		return {"result": True, "message": 'running'}


@app.get("/api/v2rayInfo")
def api_v2rayInfo(username: str = Depends(get_current_user)):
	v2ray_version = None
	v2ray_statusStr = None
	vps_publicIP = None
	try:
		v2ray_version = bytes.decode(
			subprocess.check_output("/usr/bin/v2ray/v2ray -version | head -n 1 | awk '{print $2}'", shell=True))
	except Exception:
		pass
	try:
		v2ray_statusStr = bytes.decode(
			subprocess.check_output("systemctl status v2ray|grep Active: | awk '{print $3}'", shell=True))
	except Exception:
		pass
	finally:
		if v2ray_statusStr and 'running' in v2ray_statusStr:
			v2ray_statusStr = 'running'
		elif v2ray_version:
			v2ray_statusStr = 'stopped'
		else:
			v2ray_statusStr = 'unknown'
	try:
		r = requests.get("http://api.ipify.org", timeout=2)
		if r and r.status_code == 200:
			vps_publicIP = r.text
	except Exception:
		r = requests.get("http://ifconfig.me/ip", timeout=2)
		if r and r.status_code == 200:
			vps_publicIP = r.text
	return {"result": True, "message": {"version": v2ray_version, "status": v2ray_statusStr, "publicip": vps_publicIP}}


@app.post("/api/v2rayStart")
def api_v2rayStart(username: str = Depends(get_current_user)):
	cmdr = V2ray.start()
	if cmdr:
		return {"result": True, "message": 'successful'}
	else:
		return {"result": False, "message": 'failed'}


@app.post("/api/v2rayStop")
def api_v2rayStop(username: str = Depends(get_current_user)):
	cmdr = V2ray.stop()
	if cmdr:
		return {"result": True, "message": 'successful'}
	else:
		return {"result": False, "message": 'failed'}


@app.post("/api/v2rayRestart")
def api_v2rayRestart(username: str = Depends(get_current_user)):
	cmdr = V2ray.restart()
	if cmdr:
		return {"result": True, "message": 'successful'}
	else:
		return {"result": False, "message": 'failed'}


@app.put("/api/user")
async def api_user(response: Response, UserItems: UserItems, username: str = Depends(get_current_user)):
	UserItems = UserItems.dict().get('UserItems')
	if UserItems.get('userid') == username:
		if UserItems.get('lastpass') == users[username]["password"]:
			users[username]["password"] = UserItems.get('newpass')
			secstr = vaes.encrypt(json.dumps(users))
			v2raydata['users'] = secstr
			appconfigSave('v2ray_console/v2ray.ini', v2raydata)
			return {"result": True, "message": "successful"}
		else:
			return {"result": False, "message": "failed, lastpass is incorrect"}
	else:
		return {"result": False, "message": "error, current user is not " + str(UserItems.get('userid'))}


@app.get("/api/v2rayApps")
def api_v2rayApps_fileurl():
	r = V2ray.v2rayApps_fileurl(v2rayApps)
	if r:
		return {"result": True, "message": r}
	else:
		return {"result": False, "message": None}


@app.get("/api/rtlog")
def api_rtlog():
	logstr = V2ray.rtlog()
	return {"result": True, "message": logstr}


@app.get("/api/logs/{id}")
async def api_logs(id):
	logstr = V2ray.logs(id)
	return {"result": True, "message": logstr}


if __name__ == '__main__':
	debug = False
	# logging.info("启动参数:" + str(sys.argv))
	if len(sys.argv) > 1 and sys.argv[1] == '--debug':
		# (arguments, value) = sys.argv[1].split('=')
		debug = True
	if (platform.system() != "Linux"):
		debug = True
	else:
		V2ray.check()
	logging.info("当前工作路径：" + str(os.getcwd()) + ",启动参数:debug=" + str(debug))
	time.sleep(1)
	(filename, extension) = os.path.splitext(os.path.basename(__file__))
	appStr = filename + ':app'
	uvicorn.run(appStr, host="127.0.0.1", port=8000, reload=debug)
