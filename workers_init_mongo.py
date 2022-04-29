




# Reset all workers

import re
import csv
import time
import datetime
import subprocess

import sys,os

url = 'http://127.0.0.1/balancer-manager'
lb = '193.225.250.30'

#
mongodb_entities = 290000


def reset():
	print('reset')

	workerStatus= workerInit()

	print(workerStatus)

	for k, v in workerStatus.items():
		selectedWorker = k
		print(selectedWorker)

		print('---------------------------------------')
		print('              CLEAR MONGODB            ')
		print('---------------------------------------')

		clear_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no curl localhost:8080/mongodb/expense/clear'''
		clear = subprocess.check_output(clear_cmd%(selectedWorker),shell=True,universal_newlines=True)
		print(clear)

		print('---------------------------------------')
		print('              INIT MONGODB             ')
		print('---------------------------------------')

		init_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no curl -s localhost:8080/mongodb/expense/init/%s > /dev/null 2>&1 &'''

		subprocess.check_output(init_cmd%(selectedWorker, mongodb_entities),shell=True,universal_newlines=True)

	print('---------------------------------------')
	print('              FINISHED                 ')
	print('---------------------------------------')



def workerInit():
	d={}
	cmd= " curl -s http://%s/balancer-manager | grep 'Init' "%(lb)
	allW=subprocess.check_output(cmd,shell=True,universal_newlines=True).splitlines()
	workercmd=" curl -s http://%s/balancer-manager | grep 'Init Ok' "%(lb)
	# working = subprocess.check_output(workercmd,shell=True).splitlines()
	working = subprocess.check_output(workercmd,shell=True,universal_newlines=True).splitlines()
	# print('---------------------------------------')
	# print(allW)
	# print('---------------------------------------')
	# print(working)
	# print('---------------------------------------')
	# print('All Workers IP Addresses --------------')
	# iterate through all worker
	for line in allW:
		workerIP=re.search('.*http:\/\/([0-9]*.[0-9]*.[0-9]*.[0-9]*).*',line).group(1)
		d[workerIP]=False
	#	print(workerIP)
	# print('Init Ok Workers IP Addresses ----------')
	# iterate through all worker and if found in 'Init Ok' request than set it's valut True
	for line in working:
		workerIP=re.search('.*http:\/\/([0-9]*.[0-9]*.[0-9]*.[0-9]*).*',line).group(1)
		d[workerIP]=True
	#	print(workerIP)
	print('---------------------------------------')
	print(d)
	print('---------------------------------------')
	return d


if( __name__ == '__main__' ):
	reset()
