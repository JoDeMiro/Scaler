




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
max_threads = 40


def reset():
	print('reset')

	workerStatus= workerInit()

	print(workerStatus)

	for k, v in workerStatus.items():
		selectedWorker = k
		print(selectedWorker)

		print('---------------------------------------')
		print('              STOP JAVA                ')
		print('---------------------------------------')

		stop_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no killall -9 java'''
		# stop = subprocess.check_output(stop_cmd%(selectedWorker),shell=True,universal_newlines=True)

		stop = subprocess.call(stop_cmd%(selectedWorker),shell=True,universal_newlines=True)
		print(stop)

		print('---------------------------------------')
		print('              RESTART JAVA             ')
		print('---------------------------------------')

		# restart_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no nohup java -Xms1024m -Xmx2048m -jar Micado-Optimizer-Test/target/file-demo-0.0.1-SNAPSHOT.jar --server.port=8080 --name="MyBean is multiplied" --server.tomcat.max-threads=%s --wavefront.application.service="JVMSpring" --management.metrics.export.wavefront.api-token=a9653b2f-79ce-4ea2-9475-d5913006533d > /dev/null &'''
		# restart_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no nohup java -Xms1024m -Xmx2048m -jar Micado-Optimizer-Test/target/file-demo-0.0.1-SNAPSHOT.jar --server.port=8080 --name="MyBean is multiplied" --server.tomcat.max-threads=%s --server.tomcat.connection-timeout=3600 --server.tomcat.accept-count=200000 --server.tomcat.keep-alive-timeout=-1 --server.tomcat.max-connections=8192 --server.tomcat.max-keep-alive-requests=-1 --server.tomcat.threads.min-spare=1 --wavefront.application.service="JVMSpring" --management.metrics.export.wavefront.api-token=c5e7ec91-0fd0-4db0-8b77-25b8572950c8 > /dev/null &'''
		# restart_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no nohup java -Xms1024m -Xmx2048m -jar Micado-Optimizer-Test/target/file-demo-0.0.1-SNAPSHOT.jar --server.port=8080 --name="MyBean is multiplied" --server.tomcat.max-threads=%s --server.tomcat.connection-timeout=3600 --server.tomcat.accept-count=200000 --server.tomcat.keep-alive-timeout=-1 --server.tomcat.max-connections=8192 --server.tomcat.max-keep-alive-requests=-1 --server.tomcat.threads.min-spare=1 --wavefront.application.service="JVMSpring" --management.metrics.export.wavefront.api-token=c5e7ec91-0fd0-4db0-8b77-25b8572950c8 --management.endpoints.web.exposure.include=httptrace > /dev/null &'''
		# restart_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no nohup java -Xms1024m -Xmx2048m -jar Micado-Optimizer-Test/target/file-demo-0.0.1-SNAPSHOT.jar --server.port=8080 --name="MyBean is multiplied" --server.tomcat.max-threads=%s --server.tomcat.connection-timeout=3600 --server.tomcat.accept-count=200000 --server.tomcat.keep-alive-timeout=-1 --server.tomcat.max-connections=8192 --server.tomcat.max-keep-alive-requests=-1 --server.tomcat.threads.min-spare=1 --wavefront.application.service="JVMSpring" --management.metrics.export.wavefront.api-token=c5e7ec91-0fd0-4db0-8b77-25b8572950c8 --management.endpoints.web.exposure.include=httptrace --server.tomcat.accesslog.enabled=true > /dev/null &'''

		restart_cmd = '''ssh -A ubuntu@%s -oStrictHostKeyChecking=no nohup java -Xms1024m -Xmx2048m -jar Micado-Optimizer-Test/target/file-demo-0.0.1-SNAPSHOT.jar --server.port=8080 --name="MyBean is multiplied" --server.tomcat.max-threads=%s --server.tomcat.connection-timeout=3600 --server.tomcat.accept-count=200000 --server.tomcat.keep-alive-timeout=-1 --server.tomcat.max-connections=8192 --server.tomcat.max-keep-alive-requests=-1 --server.tomcat.threads.min-spare=1 --wavefront.application.service="JVMSpring" --management.metrics.export.wavefront.api-token=c5e7ec91-0fd0-4db0-8b77-25b8572950c8 --management.endpoints.web.exposure.include=httptrace --server.tomcat.accesslog.enabled=true server.tomcat.accesslog.pattern=common server.tomcat.basedir=/home/ubuntu/ server.tomcat.accesslog.directory=logiks > /dev/null &'''

		subprocess.check_output(restart_cmd%(selectedWorker, max_threads),shell=True,universal_newlines=True)

		# subprocess.call(restart_cmd%(selectedWorker, max_threads),shell=True,universal_newlines=True)

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
