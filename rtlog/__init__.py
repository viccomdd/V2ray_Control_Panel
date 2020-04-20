#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import time
import threading
import subprocess
import random
import string


class RTLOG(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self._thread_stop = False
		self.logContent = None

	def start(self):
		threading.Thread.start(self)

	def run(self):
		f = subprocess.Popen(['tail', '-f', '-n', '10', 'logs/v2ray_console.log'], stdout=subprocess.PIPE,
		                     stderr=subprocess.PIPE)
		while not self._thread_stop:
			self.logContent = bytes.decode(f.stdout.readline().strip())
			# self.logContent = ''.join(random.sample(string.ascii_letters + string.digits, 32))
			time.sleep(1)
		logging.warning("Close rtlog!")

	def stop(self):
		self._thread_stop = True
		self.join()
