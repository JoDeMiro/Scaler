# scale_by_none.py

import re
import csv
import time
import numpy
import datetime
import requests
import subprocess

import sys,os

from server_reset import restart

from cooler import printTest
from cooler import printColor
from cooler import printBlink

printTest('printTest')

printColor('cyan', 'cyan')
printColor('red', 'red')
printColor('green', 'green')
printColor('yellow', 'yellow')
printColor('blue', 'blue')
printColor('magenta', 'magenta')
printColor('white', 'white')
printBlink('red', 'red')


print('---------------------------------------')
print('                RESTART                ')
print('---------------------------------------')

# restart()

print('---------------------------------------')
print('                SET LOG                ')
print('---------------------------------------')

print_statavg_all_short = True

print('---------------------------------------')
print('                SETUP                  ')
print('---------------------------------------')

url = 'http://127.0.0.1/balancer-manager'

r = requests.get(url)
nonce = re.search(r'nonce=(.*?)">', r.text).group(1)

lb = '193.225.250.30'
usr='ubuntu'
# nonce='62c1d1d7-1c8a-152e-6b41-65bf544025c5'
log_file='zulu.log'
init_vm_number = 1
trigger_count = 1

metric_log_file_name = './Train/metric_train_by_none.log'
scale_log_file_name =  './Train/scaled_train_by_none.log'


print('---------------------------------------')
print('                CONFIG                 ')
rt_limit_upper = 500
rt_limit_lower = 200
# cpu_limit_upper = 70
# cpu_limit_lower = 40
print('---------------------------------------')


print('---------------------------------------')
print('                START                  ')
print('---------------------------------------')

def follow(thefile):
	thefile.seek(0,2)
	# print('\n\n\n')
	# print(thefile.seek(0,2))
	# print('\n\n\n')
	while True:
		line = thefile.readline()
		# print('\n\n\n')
		# print(line)
		# print('\n\n\n')
		if not line:
			time.sleep(0.1)
			continue
		# print(line)
		yield line


def main():


	print('---------------------------------------')
	print('                SET VMN                ')
	print('---------------------------------------')


	set_init_vm_number(init_vm_number)




	print('---------------------------------------')
	print('                  MAIN                 ')
	print('---------------------------------------')
	# Ebbol olvasom ki a response timot
	# accesslog=open('/var/log/apache2/other_vhosts_access.log','r')
	accesslog=open('/var/log/apache2/'+log_file,'r')

	# Ebbe fogom irni a metikakat
	metriclog=open(metric_log_file_name,'w', newline='')
	# metriclog=open('./metric_train_by_none.log','w', newline='')
	# metriclog=open('./metric_rt_threshold%i_%i.log'%(rt_limit_lower,rt_limit_upper),'w', newline='')
	# metriclog=open('./metric_cpu_threshold%i_%i.log'%(cpu_limit_lower,cpu_limit_upper),'w', newline='')

	# Ebben a sorrendben irom bele a metric.log-ba az adatokat
	# (idopont, response_time_95, response_time, worker_number, request_rate, metrics)
	metriclog.write('worker_give_metrics,')
	metriclog.write('write_to_csv_time,')
	metriclog.write('time,response_time_p95,response_time,worker_number,request_rate,')
	metriclog.write('CPU0User%,CPU0Idle%,CPU0Total%,CPU1User%,CPU1Idle%,CPU1Total%,')
	metriclog.write('[DSK:sda]Reads,[DSK:sda]RMerge,[DSK:sda]RKBytes,[DSK:sda]WaitR,[DSK:sda]Writes,[DSK:sda]WMerge, [DSK:sda]WKBytes,[DSK:sda]WaitW,[DSK:sda]Request,[DSK:sda]QueLen,[DSK:sda]Wait,[DSK:sda]SvcTim,[DSK:sda]Util,')
	metriclog.write('[NUMA:0]Used,[NUMA:0]Free,[NUMA:0]Slab,[NUMA:0]Mapped,[NUMA:0]Anon,[NUMA:0]AnonH,[NUMA:0]Inactive, [NUMA:0]Hits,')
	metriclog.write('[TCPD]InReceives,[TCPD]InDelivers,[TCPD]OutRequests,[TCPD]InSegs,[TCPD]OutSegs\n')
	metriclog.flush()
	mlog=csv.writer(metriclog)

	# Ebbe fogom tenni a skalazasi adatokat
	scalelog=open(scale_log_file_name,'w')
	# scalelog=open('./train_by_none.log','w')
	# scalelog=open('./scale_rt_threshold%i_%i.log'%(rt_limit_lower,rt_limit_upper),'w')
	# scalelog=open('./scale_cpu_threshold%i_%i.log'%(cpu_limit_lower,cpu_limit_upper),'w')
	scalelog_header = 'time,notification,actual_vm_number_was,actual_vm_number_is\n'
	scalelog.write(scalelog_header)
	scalelog.flush()

	loglines=follow(accesslog)
	first=True    # hack to check if the script was just started
	print(first)
	cts=-1        # time-stamp we are looking to calculate response time for
	print(cts)
	RT=0          # RT keeps the total of response time
	print(RT)
	RTs=[]        # array to keep individual RT observations
	print(RTs)
	N=0           # number of requests arrived in cts
	print(N)


	# Most itt tartok
	timesSuggested=0
	workerStatus=workerInit()       # keeps track of which workers are up and running -> dict
	# print('workerStatus = ')
	# print(workerStatus.values())
	# w=sum(workerStatus.values())    # number of acitve workers
	# print('Active workers = ', w)
	# ------------------------------

	for	line in loglines: # follow the apache accesslog file
		# print('---------------------------------------')
		# print('                    FOR                ')
		# print('---------------------------------------')
		try:
			if first: # if script just started, initialize the necessary variables 
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)


				print('\n\n')
				print('------------------------------------------------------------------------------')
				print('------------------------------------------------------------------------------')
				# print(matches)
				# <re.Match object; span=(0, 143), match='193.225.250.30:80 80.95.82.243 - - [23/Apr/2022:1>
				# 193.225.250.30:80 80.95.82.243 - - [23/Apr/2022:19:10:47 +0000] "GET / HTTP/1.1" 200 14694 "-" "Apache-HttpClient/4.5.10 (Java/1.8.0_291)" 4238
				cts=matches.group(1)
				print('cts = ', cts)
				print('matches.group(2) = ', matches.group(2))     # ez az utolso ertek a line-ban
				# 4238
				RT=float(matches.group(2))/1000.
				print('RT = float(matches.group(2))/1000. = ', RT)
				RTs.append(RT)
				print('RTs.append(RT) =', RTs)
				N=1
				first=False
				print('------------------------------------------------------------------------------')
				print('------------------------------------------------------------------------------')
				print('\n\n')

				print('This was the first attempt')
			else:
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)

				# print('\n\n')
				# print('------------------------------------------------------------------------------')
				# print('------------------------------------------------------------------------------')
				# print(matches)
				ts=matches.group(1) # extract the time stamp of request
				# print('ts = matches.group(1) extract the time stamp of request = ', ts)
				# print('cts = curent time stamp = ', cts)


				if cts==ts: # if the timestamp is same, not changed then keep incrementing the variables
					RTs.append(float(matches.group(2))/1000.) # add to list for percentile
					# print('RTs = ', RTs)

					RTs_array = numpy.array(RTs)
					mean = RTs_array.mean()
					median = numpy.median(RTs_array)
					maximum = RTs_array.max()
					minimum = RTs_array.min()
					std = RTs_array.std()
					n = RTs_array.size
					# print('mean = {:.2f}, med = {:.2f}, min = {:.2f}, max = {:.2f}, std = {:.2f}'.format(mean, median, minimum, maximum, std, n))
					# print('------------------------------------------------------------------------------')
					# print('------------------------------------------------------------------------------')
					# print('\n\n')

					RT+=float(matches.group(2))/1000. # add to sum for mean
					N+=1
				elif cts<ts or (ts[0:7]=="00:00:0" and cts[0:7]=="23:59:5"): # case when the new request timestamp has changed -> interval passed
					rt=float(RT/N)       # calculate average rt
					avgrt=rt
					rr=N                 # request rate
					p_95=numpy.percentile(RTs,95) # calculate percentile
					print('--------------------------------')
					print('len(RTs) = ', len(RTs))
					print(RTs)
					print('--------------------------------')

					RTs_array = numpy.array(RTs)
					mean = RTs_array.mean()
					median = numpy.median(RTs_array)
					maximum = RTs_array.max()
					minimum = RTs_array.min()
					std = RTs_array.std()
					n = RTs_array.size
					# print('mean = {:.2f}, med = {:.2f}, min = {:.2f}, max = {:.2f}, std = {:.2f}'.format(mean, median, minimum, maximum, std, n))

					print('-------------------------------------')
					print('\n\n')

					# The measured values are the follow
					# rr    = Request Rate
					# rt    = Response Time
					# avgrt = Average Response Time
					# p_95  = Average Response Time for 95%
					# cts   = Current Time Stamp

					print('rr     = ', rr)
					print('rt     =  {:.2f}'.format(rt))
					print('p_95   =  {:.2f}'.format(p_95))
					print('avgrt  =  {:.2f}'.format(avgrt))
					print('cts    = ', cts)
					# print('len(RTso)', len(RTso))
					# print('RTso', RTso)

					# debug
					print('_______BEFORE_REINITIALIZATION______')
					print('cts', cts)
					# print('RTso', RTso)
					# Reinitialize cuclis

					cts=ts # update the interval to current timestamp
					RT=float(matches.group(2))/1000. # reinitialize RT, N , RTs variables for next interval
					N=1
					RTso = RTs
					RTs=[RT]


					# debug
					print('_______AFTER_REINITIALIZATION_______')
					print('cts', cts)
					# print('RTso', RTso)                    # Ha látni akarom az egyes válaszidőket az összeset



					# Check the avalilable workers again
					workerStatus=workerInit()
					w=sum(workerStatus.values())

# --------------------------------------------
# na ezen dolgozom most
#
# másik parám::: biztos, hogy az elmúlt 10 időpont átlagát kérem el?

					# Most az egyszeruseg miatt csak egy workerbol olvasom ki a metrikat
					# Az utolso olyanon aki be van csatolva a terhelesbe
					# print('________________________')
					selectedWorker = ''
					selectedWorkers = []
					for k, v in workerStatus.items():
						# print(k, v)
						# printTest('printTest')
						if( v == True ):
							selectedWorker = k
							selectedWorkers.append(k)
					# print('------------------------')
					# print("selectedWorker = ", selectedWorker)
					# print('------------------------')

					# Ask the metric from the last worker (it can be change over time)
					# repWorker = '192.168.0.72'
					repWorker = selectedWorker
					repWorkerLogin = 'ubuntu@' + repWorker


					# Ask the metric always the same worker (should be the first wich is always on)
					metWorker = '192.168.0.170'
					metWorkerLogin = 'ubuntu@' + metWorker

					# Get the metrics command
					statcmd = '''ssh -A ubuntu@192.168.0.72 -oStrictHostKeyChecking=no tail -n 10 mylog.log | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '2-5,8-' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%f ", a[i]/NR;}}' '''

					statcmd_all = '''ssh -A ubuntu@192.168.0.72 -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '2-5,8-' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%f ", a[i]/NR;}}' '''

					statcmd_rossz = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' '''

					statcmd_rossz = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' '''

					statcmd_rossz = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' '''

					statcmd_ido = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '1,2' '''

					statcmd_cpu = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23' '''

					statcmd_hdd = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '28-40' '''

					statcmd_ram = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '41-48' '''

					statcmd_tcp = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '49-117' '''

					statcmd_tcp_short = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '51,57,58,77,78' '''

					statcmd_all_short     = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' '''

					statcmd_all_short_avg = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%%f ", a[i]/NR;}}' '''

					statcmd_all_short_ori = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]*:[0-9]*:[0-9]*' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%%f ", a[i]/NR;}}' '''


					# 1 - Date
					# 2 - Time
					# 3 - [CPU:0]User%
					# 5 - [CPU:0]Sys%
					#


					# Ez az osszes metrikat visszaadja
					# statavgJO = subprocess.check_output(statcmd_all,shell=True)
					# statavgJO = subprocess.check_output(statcmd_all,shell=True,universal_newlines=True)

					# Ha latni akarom hogy mibol kesszult az atlag
					if( print_statavg_all_short ):
						# ha a repWorker (mindíg az utolsó)
						# statavg_all_short = subprocess.check_output(statcmd_all_short%(repWorkerLogin),shell=True,universal_newlines=True)
						# ha a metWorker (mindíg egy általam megadott)
						statavg_all_short = subprocess.check_output(statcmd_all_short%(metWorkerLogin),shell=True,universal_newlines=True)
						print('_______________________________________________________\n\n')
						print(statavg_all_short)

					# A tenyleges atlag a kivalasztott metrikakra
					start_time = time.time()
					# statavg_all_short = subprocess.check_output(statcmd_all_short_avg%(repWorkerLogin),shell=True,universal_newlines=True)
					statavg_all_short = subprocess.check_output(statcmd_all_short_avg%(metWorkerLogin),shell=True,universal_newlines=True)
					end_time   = time.time()
					printTest('KI A metWorker AKITŐL LE FOGJUK KÉRNI A METRIKÁT')
					print(metWorker)
					print(metWorkerLogin)
					print('get metric took: {:.3f} sec'.format(end_time - start_time))
					if( print_statavg_all_short ):
						print('_______________________________________________________\n\n')
						print(statavg_all_short)



					# Ebben a visszakapott stringben a metrikak a kovetkezoek
					# 0 - 3  - CPU0User%
					# 1 - 10 - CPU0Idle%
					# 2 - 11 - CPU0Total%
					# 3 - 15 - CPU1User%
					# 4 - 22 - CPU1Idle%
					# 5 - 23 - CPU1Total%

					# 6 - 28 - [DSK:sda]Reads
					# 7 - 29 - [DSK:sda]RMerge
					# 8 - 30 - [DSK:sda]RKBytes
					# 9 - 31 - [DSK:sda]WaitR
					# 10- 32 - [DSK:sda]Writes
					# 11- 33 - [DSK:sda]WMerge
					# 12- 34 - [DSK:sda]WKBytes
					# 13- 35 - [DSK:sda]WaitW
					# 14- 36 - [DSK:sda]Request
					# 15- 37 - [DSK:sda]QueLen
					# 16- 38 - [DSK:sda]Wait
					# 17- 39 - [DSK:sda]SvcTim
					# 18- 40 - [DSK:sda]Util

					# 19- 41 [NUMA:0]Used
					# 20- 42 [NUMA:0]Free
					# 21- 43 [NUMA:0]Slab
					# 22- 44 [NUMA:0]Mapped
					# 23- 45 [NUMA:0]Anon
					# 24- 46 [NUMA:0]AnonH
					# 25- 47 [NUMA:0]Inactive
					# 26- 48 [NUMA:0]Hits

					# 27- 51 [TCPD]InReceives
					# 28- 57 [TCPD]InDelivers
					# 29- 58 [TCPD]OutRequests
					# 30- 77 [TCPD]InSegs
					# 31- 78 [TCPD]OutSegs

					#

					# Ki van olvasva a metrika es ki van olvasva az RT a response time.

					# Most el lehet donteni, hogy melyik alapjan akarunk skalazni.

					_cpu_user  = float(statavg_all_short.split()[0])
					_cpu_idle  = float(statavg_all_short.split()[1])
					_cpu_total = float(statavg_all_short.split()[2])
                    
                    # A tanításhoz használt skálázás
                    # Proba.: 0.1


					k = 0
					rnd = numpy.random.rand()
					if( rt > rt_limit_upper ): # if response time is greater than the upper limit, consider scaling out
					# if( rnd > 0.5 ): # véletlenszerűen skáláz fel, vag le.

						print('---------------------------------------')
						print('         Testing for scale out         ')
						print('---------------------------------------')

						k+=1

					if( rt < rt_limit_lower and w > 1): # if response time is less than lower limit, consider scaling in
					# if( rnd < 0.5 and w > 1): # véletlenszerűen skáláz fel,v agy le.
						print('---------------------------------------')
						print('         Testing for scale in          ')
						print('---------------------------------------')

						k-=1

					# -----------------------------------------------------------
					# Log to file

					print('\n\n')

					print('---------------------------------------')
					print('         RT Statistics                 ')
					print('---------------------------------------')

					stat = getStats(RTso)

					print('average = {:.2f}'.format(stat['mean']))
					print('median  = {:.2f}'.format(stat['median']))
					print('minimum = {:.2f}'.format(stat['minimum']))
					print('maximum = {:.2f}'.format(stat['maximum']))
					print('std     = {:.2f}'.format(stat['std']))
					print('n       = {}'.format(stat['n']))

					rt = avgrt 						# average Response Time for last interval
					print('rt      = {:.2f}'.format(rt))

					# print('---------------------------------------')
					# print('         Write Log metric file         ')
					# print('---------------------------------------')

					# Prepear data for statistic log files
					statarr=[float(i) for i in statavg_all_short.split()] 	# all the stats from collectl
					# print('statarr = ', statarr)
					carr=[rr/10]+statarr 					# calculated per second request rate since 10 second interval
					# print('carr \t= ', carr)
					# print(ts, p_95, rt, w)

					# mlog az mlog = csv.writer(metriclog)
                    
					write_to_csv_time = time.strftime("%H:%M:%S", time.gmtime())
					write_to_csv_time = datetime.datetime.now().strftime("%H:%M:%S")

					mlog.writerow([metWorker, write_to_csv_time, ts, p_95, rt, w]+carr) 	# add the timestamp, 95th percentile, avg rt, and number of workers to stats and log
					# metriclog az egy open context manager
					metriclog.flush()




					# Ok Log file is ki van irva benne van minden amit akarok
					# (idopont, response_time_95, response_time, worker_number, request_rate, metrics)



					# -----------------------------------------------------------
					# Scale

					print('---------------------------------------')
					print('         Actual Scaling Logic          ')
					print('---------------------------------------')

					print('Actual Worker Number      = ', w)
					print('k (Control the action)    = ', k)
					print('Response Time             =  {:.2f}'.format(rt))
					print('Response Time Upper Limit = ', rt_limit_upper)
					print('Response Time Lower Limit = ', rt_limit_lower)


					if k > 0: 								# if continous suggestion of scale out then scale out
						timesSuggested+=1
						print('timesSuggested out scale = ', timesSuggested)
						if timesSuggested >= trigger_count: 				# control continous suggestion number here
							print('\n\n  Scale Out \n\n')
							timesSuggested=0
							for t in range(0,k): 			# add k workers one by one
								addWorker(workerStatus,scalelog)
								print('\n\n   addWorker   \n\n')
								workerStatus=workerInit()
							w=sum(workerStatus.values())

					elif k < 0: 							# if continous suggestion to scale in, then scale in
						timesSuggested+=1
						print('timesSuggested in scale = ', timesSuggested)
						if timesSuggested >= trigger_count: 				# control continous suggestion number here
							timesSuggested=0
							# for t in range(0,-k):
							#	print "Removing worker",t+1
							removeWorker(workerStatus,metWorker,scalelog)	# remove only one worker
							print('\n\n   removeWorker   \n\n')
							workerStatus=workerInit()
							w=sum(workerStatus.values())
					else:
						timesSuggested=0 					# if neither scale out nor scale in was suggested, reset the timesSuggested



		except Exception as e:
			print(line)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)




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

	print('')
	print('---------------------------------------')
	print(d)
	print('---------------------------------------')
	return d

def printActiveWorkers(d):
	print(len(d))
	for worker in d:
	#	print(worker)
	#	print(type(worker))
	#	print(worker.get(0))
	#	print(worker.get(1))
		yield

def getStats(RTs):
	RTs_array = numpy.array(RTs)
	mean = RTs_array.mean()
	median = numpy.median(RTs_array)
	maximum = RTs_array.max()
	minimum = RTs_array.min()
	std = RTs_array.std()
	n = RTs_array.size
	stat = {'mean': mean, 'median': median, 'minimum': minimum, 'maximum': maximum, 'std': std, 'n': n}
	return stat

def set_init_vm_number(init_vm_number):
	workerStatus = workerInit()
	w = sum(workerStatus.values())
	print(workerStatus)
	counter = 0
	for worker in workerStatus:
		# if counter == 0:
		if counter < init_vm_number:
			enable_worker_ip = worker
			print('enable_worker_ip =', enable_worker_ip)
			enablecmd= 'curl -s -o /dev/null -XPOST "http://%s/balancer-manager?" -H "Referer: http://%s/balancer-manager?b=backend-cluster&w=http://%s:8080&nonce=%s" -d b="backend-cluster" -d w="http://%s:8080" -d nonce="%s" -d w_status_D=0'%(lb,lb,enable_worker_ip,nonce,enable_worker_ip,nonce)
			print(enablecmd)
			subprocess.check_output(enablecmd,shell=True)
			counter += 1
		else:
			disable_worker_ip = worker
			print('disable_worker_ip =', disable_worker_ip)
			disablecmd= 'curl -s -o /dev/null -XPOST "http://%s/balancer-manager?" -H "Referer: http://%s/balancer-manager?b=backend-cluster&w=http://%s:8080&nonce=%s" -d b="backend-cluster" -d w="http://%s:8080" -d nonce="%s" -d w_status_D=1'%(lb,lb,disable_worker_ip,nonce,disable_worker_ip,nonce)
			print(disablecmd)
			subprocess.check_output(disablecmd,shell=True)
			counter += 1


def addWorker(workerStatus,scalelog):
	print('\n------------ addWorker function ----------- \n')
	workerIP=-1
	for worker in workerStatus:
		if workerStatus[worker]==False:
			workerIP=worker
			print('------------ ot fogjuk hozzaadni ---------- ')
			print('workerIP = ', workerIP)
			break
	if workerIP!=-1:
		print('Adding worker: ' + workerIP)

		enablecmd= 'curl -s -o /dev/null -XPOST "http://%s/balancer-manager?" -H "Referer: http://%s/balancer-manager?b=backend-cluster&w=http://%s:8080&nonce=%s" -d b="backend-cluster" -d w="http://%s:8080" -d nonce="%s" -d w_status_D=0'%(lb,lb,workerIP,nonce,workerIP,nonce)

		# print(enablecmd)

		subprocess.check_output(enablecmd,shell=True)

		_w = sum(workerStatus.values())
		_w_next = _w + 1

		scalelog.write(datetime.datetime.now().strftime("%H:%M:%S")+",\"Worker "+workerIP+" added.\"," + str(_w) + "," + str(_w_next) + "\n")
		scalelog.flush()
	else:
		print('\n\n ------------- No workers left ------------- \n\n')


def removeWorker(workerStatus,metWorker,scalelog):
	print('\n------------ removeWorker function ----------- \n')
	workerIP=-1
	for worker in workerStatus:
		print('worker  =', worker)
		print('metWorker = ', metWorker)
		if( workerStatus[worker] == True and worker != metWorker ):
			workerIP=worker
			print('------------ ot fogjuk elvenni ----------- ')
			print('workerIP = ', workerIP)
			break
	if workerIP!=-1:
		print('Removing worker: ' + workerIP)

		disablecmd= 'curl -s -o /dev/null -XPOST "http://%s/balancer-manager?" -H "Referer: http://%s/balancer-manager?b=backend-cluster&w=http://%s:8080&nonce=%s" -d b="backend-cluster" -d w="http://%s:8080" -d nonce="%s" -d w_status_D=1'%(lb,lb,workerIP,nonce,workerIP,nonce)

		# print(disablecmd)

		subprocess.check_output(disablecmd,shell=True)

		_w = sum(workerStatus.values())
		_w_next = _w - 1

		scalelog.write(datetime.datetime.now().strftime("%H:%M:%S")+",\"Worker "+workerIP+" removed.\"," + str(_w) + "," + str(_w_next) + "\n")
		scalelog.flush()
	else:
		print('\n\n ------------- This else branch should not run ------------- \n\n')



main()
