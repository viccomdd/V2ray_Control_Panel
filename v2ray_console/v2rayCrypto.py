#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import base64
import json
import random
from Crypto.Cipher import AES
from configparser import ConfigParser


def randomstr():
	return ''.join(random.sample('123456890abcdefghijklmnopqrstuvwxyzABCDEDFGHIJKLMNOPQRSTUVWXYZ@#', 16))


def appconfigLoad(path):
	data = {}
	config = ConfigParser()
	defaultUsers = {"admin": {"password": "v2rayadmin"}, "viccom": {"password": "v2rayviccom"},
	                "dajiji": {"password": "v2raydajiji"}}
	if os.access(path, os.F_OK):
		config.read(path)
		if config.get('system', 'users'):
			data["users"] = config.get('system', 'users')
		if config.get('system', 'key1'):
			data["key1"] = config.get('system', 'key1')
		if config.get('system', 'key2'):
			data["key2"] = config.get('system', 'key2')
	else:
		config.read(path)
		config.add_section("system")
		data['key1'] = randomstr()
		data['key2'] = randomstr()
		vcp = V2rayCryp(data['key1'])
		secstr = vcp.encrypt(json.dumps(defaultUsers))
		data['users'] = secstr
		# print(json.dumps(data, sort_keys=True, indent=4, separators=(',', ':')))
		config.set("system", 'key1', data.get('key1'))
		config.set("system", 'key2', data.get('key2'))
		config.set("system", 'users', data.get('users'))
		config.write(open(path, 'w'))
	return data


def appconfigSave(path, data):
	config = ConfigParser()
	config.read(path)
	config.set("system", 'key1', data.get('key1'))
	config.set("system", 'key2', data.get('key2'))
	config.set("system", 'users', data.get('users'))
	config.write(open(path, 'w'))


class V2rayCryp:
	def __init__(self, key=None, ):
		self.__key = key or "V2ray@GWF**USA**"  # 密钥（长度必须为16、24、32）

	def add_to_16(self, value):
		while len(value) % 16 != 0:
			value += '\0'
		return str.encode(value)

	def encrypt(self, plainStr):
		aes = AES.new(self.add_to_16(self.__key), AES.MODE_ECB)
		encrypt_aes = aes.encrypt(self.add_to_16(plainStr))
		encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')
		return encrypted_text

	def decrypt(self, securityStr):
		aes = AES.new(self.add_to_16(self.__key), AES.MODE_ECB)
		base64_decrypted = base64.decodebytes(securityStr.encode(encoding='utf-8'))
		decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
		return decrypted_text


if __name__ == '__main__':
	v2raydata = appconfigLoad('v2ray.ini', {})
	print(json.dumps(v2raydata, sort_keys=True, indent=4, separators=(',', ':')))
