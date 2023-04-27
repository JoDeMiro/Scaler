# cpu.py

import re
import csv
import time
import numpy
import datetime
import requests
import subprocess

import sys,os

from server_reset import restart
from termcolor import colored
from deadline import printTest, printToDo

print('---------------------------------------')
print('                RESTART                ')
print('---------------------------------------')

# restart()

print(colored('white', 'white'), colored('grey', 'grey'), colored('blue', 'blue'), colored('yellow', 'yellow'), colored('cyan', 'cyan'), colored('magenta', 'magenta'), colored('green', 'green'))

print('---------------------------------------')
print('                SET VMN                ')
print('---------------------------------------')

print_statavg_all_short = False

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



print('---------------------------------------')
print('                CONFIG                 ')
rt_limit_upper = 500
rt_limit_lower = 100
cpu_limit_upper = 70
cpu_limit_lower = 40
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
	# metriclog=open('./metric_rt_threshold%i_%i.log'%(rt_limit_lower,rt_limit_upper),'w', newline='')
	metriclog=open('./metric_cpu_threshold%i_%i.log'%(cpu_limit_lower,cpu_limit_upper),'w', newline='')

	# Ebben a sorrendben irom bele a metric.log-ba az adatokat
	# (idopont, response_time_95, response_time, worker_number, request_rate, metrics)
	metriclog.write('time, response_time_p95, response_time, worker_number, request_rate,')
	metriclog.write('CPU0User%, CPU0Idle%, CPU0Total%, CPU1User%, CPU1Idle%, CPU1Total%,')
	metriclog.write('[DSK:sda]Reads, [DSK:sda]RMerge, [DSK:sda]RKBytes, [DSK:sda]WaitR, [DSK:sda]Writes, [DSK:sda]WMerge, [DSK:sda]WKBytes, [DSK:sda]WaitW, [DSK:sda]Request, [DSK:sda]QueLen, [DSK:sda]Wait, [DSK:sda]SvcTim, [DSK:sda]Util,')
	metriclog.write('[NUMA:0]Used, [NUMA:0]Free, [NUMA:0]Slab, [NUMA:0]Mapped, [NUMA:0]Anon, [NUMA:0]AnonH, [NUMA:0]Inactive, [NUMA:0]Hits,')
	metriclog.write('[TCPD]InReceives, [TCPD]InDelivers, [TCPD]OutRequests, [TCPD]InSegs, [TCPD]OutSegs\n')
	metriclog.flush()
	mlog=csv.writer(metriclog)

	# Ebbe fogom tenni a skalazasi adatokat
	# scalelog=open('./scale_rt_threshold%i_%i.log'%(rt_limit_lower,rt_limit_upper),'w')
	scalelog=open('./scale_cpu_threshold%i_%i.log'%(cpu_limit_lower,cpu_limit_upper),'w')
	scalelog_header = 'time,notification,actual_vm_number_was,actual_vm_nuber_is\n'
	scalelog.write(scalelog_header)
	scalelog.flush()

	loglines=follow(accesslog)
	first=True    # hack to check if the script was just started
	print(first)
	cts=-1        # time-stamp we are looking to calculate response time for
	print(cts)
	RT_current=0          # RT keeps the total of response time
	print(RT_current)
	RTs=[]        # array to keep individual RT observations
	print(RTs)
	N=0           # number of requests arrived in cts
	print(N)


	timesSuggested=0
	entriesReceived=0
	workerStatus=workerInit()         # keeps track of which workers are up and running -> dict
	print('---------------------------------------')
	print(workerStatus)
	print('---------------------------------------')
	# print(workerStatus.values())
	# w=sum(workerStatus.values())    # number of acitve workers
	# print('Active workers = ', w)
	# ------------------------------

	for	line in loglines: # follow the apache accesslog file
		# print('---------------------------------------')
		# print('                    FOR                ')
		# print('---------------------------------------')
		entriesReceived += 1
		try:
			if first: # if script just started, initialize the necessary variables 
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)


				print('\n\n')
				print('------------------------------------------------------------------------------')
				print('------------------------------------------------------------------------------')
				# <re.Match object; span=(0, 143), match='193.225.250.30:80 80.95.82.243 - - [23/Apr/2022:1>
				# 193.225.250.30:80 80.95.82.243 - - [23/Apr/2022:19:10:47 +0000] "GET / HTTP/1.1" 200 14694 "-" "Apache-HttpClient/4.5.10 (Java/1.8.0_291)" 4238
				cts = matches.group(1)
				print('cts              = ', cts)
				print('matches.group(2) = ', matches.group(2))     # ez az utolso ertek a line-ban tehat a apache log response time (%D)
				RT_from_log = matches.group(2)                     # microsecundumban van megadva
				RT_current = float(matches.group(2))/1000.		   # millisecundumban van megadva
				cum_RT = 0
				cum_RT += RT_current
				print(colored('Response Time    = ', 'yellow'), colored(RT_current, 'green'))
				RTs.append(RT_current)
				print('RTs.append(RT_current)   =', RTs)
				N = 1
				first = False

				print('This was the first attempt')

				print('------------------------------------------------------------------------------')
				print('------------------------------------------------------------------------------')
				print('\n\n')

			else:
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)

				# print('\n\n')
				# print('------------------------------------------------------------------------------')
				# print('------------------------------------------------------------------------------')
				ts = matches.group(1) 				# extract the time stamp of request
				print('ts               = ', ts)		# timestamp from zulu.log
				print('cts              = ', cts)		# curent timestamp from zulu.log


				if cts==ts:					# if the timestamp is same, not changed then keep incrementing the variables
					RT_from_log = matches.group(2)				# microsecundumban van megadva
					RT_current = float(matches.group(2))/1000.		# millisecundumban van megadva

					RTs.append(RT_current)					# add to list for later analysis and check the mean
					print('RTs = ', RTs)

					running_stat = getStats(RTs)

					print('avg = {:.2f} min = {:.2f} max = {:.2f} std = {:.2f}'.format(running_stat['mean'], running_stat['minimum'], running_stat['maximum'], running_stat['std']))

					cum_RT += RT_current			# add to sum for mean
					N += 1

					# print('------------------------------------------------------------------------------')
					# print('------------------------------------------------------------------------------')
					# print('\n\n')

					# Ide kellene beillesztenem azt, hogy ha mar menet kozben azt latom, hogy az atlag kimegy a savbol akor
					# mivel egy sokkal kesobb beerkezo vlasz idobejege alapjan lepunk csak tovabb az 'else if' agra
					# ezert vagy ugy kene kivaltanom azt, hogy nem az beerkezo valasz idobejege alapjan ellenorzom az idobejeget
					# hanem nomrmalisan a 'time.time' alapjan
					# vagy mar itt beteszek egy olyan agat ami ha teljesul akkor skalaz
					# vagy csinalok egy olyan valtozot, aminek az erteket atallitva egy kesobbi feltelben kiadom a skalazast

					# Fejelesztes <--------------------
					# a running_statot mar korabban megcsinaltam
					if( running_stat['mean'] > 300 ):
						print(colored('discrepancia detected instide the sampling session', 'red'))



				elif cts<ts or (ts[0:7]=="00:00:0" and cts[0:7]=="23:59:5"): 		# case when the new request timestamp has changed -> interval passed

					print('--------------------------------')
					print('     SAMPLIG SESSION CLOSED     ')
					print('--------------------------------')

					print('--------------------------------')
					print('num of mesasurement in session = ', len(RTs))
					print('RTs                            = ', RTs)
					print('--------------------------------')


					stat = getStats(RTs)
					stat_violated = isViolatedStats(RTs, rt_limit_lower, rt_limit_upper)

					printTest(stat_violated)

					printToDo('Ezt kell meg betennem a metric.logba, hogy majdnem minden meglegyen')

					printToDo('betnni a metrika log vegere a kovetkezoket, _rt_lower, _rt_upper, az rt egyeb statisztikai mint min, max, std, med, tovabba a violatied statisztikakat')


					avgrt = stat['mean']

					rr = N                 						# request rate
					p_95 = numpy.percentile(RTs,95) 				# calculate percentile


					# Ez a print csak ellenorzes miatt van bent, de ugy latom, hogy minden jo, ugyan az az ertek itt is mint korabban.
					print('avg = {:.2f} min = {:.2f} max = {:.2f} std = {:.2f}'.format(stat['mean'], stat['minimum'], stat['maximum'], stat['std']))

					print('measured interval (cts) = ', cts)					# cts   = Current Time Stamp
					print('measured request        = ', rr)						# rr    = Request Rate / Num of inc. req.
					print('len(RTs)           = ', len(RTs))					# RTs   = list of Response Times
					print('measured avg response time (avgrt)  =  {:.2f}'.format(avgrt))		# avgrt = Average Response Time
					print('measured p95 response time (p_95)   =  {:.2f}'.format(p_95))		# p_95  = Average Response Time for 95%


					# -----------------------------------------------------------
					# Stats again - valamelyiket kibaszom a fenebe nem kell ketto

					# print('\n\n')

					print(colored('---------------------------------------', 'cyan'))
					print(colored('Response Time    = ', 'cyan'))
					print(colored('         RT Statistics                 ', 'cyan'))
					print(colored('---------------------------------------', 'cyan'))

					stat = getStats(RTs)

					print('avgrt   = {:.2f}'.format(avgrt))				# ez az egyik fo metrika a celvaltozo ha ugy tetszik
					print('average = {:.2f}'.format(stat['mean']))			# ez az RTso statisztikabol jon -> kettonek azonosnak kell lennie
					print('median  = {:.2f}'.format(stat['median']))
					print('minimum = {:.2f}'.format(stat['minimum']))
					print('maximum = {:.2f}'.format(stat['maximum']))
					print('std     = {:.2f}'.format(stat['std']))



					# -----------------------------------------------------------
					# Reset variables

					#					
					cts = ts 							# update the interval to current timestamp
					RT_from_log = float(matches.group(2))				# reinitialize RT, N and RTs for next interval
					RT = float(matches.group(2))/1000.
					N = 1								# reinitialize N
					RTso = RTs							# keep the RTs [list] for later
					RTs=[RT]							# reinitialize RTs [list] with RT



					# ----------------------------------------------------------->>>

					# -----------------------------------------------------------
					# Get the metric


					# Check the avalilable workers again
					workerStatus=workerInit()
					w=sum(workerStatus.values())


					# Most az egyszeruseg miatt csak egy workerbol olvasom ki a metrikat
					# Az utolso olyanon aki be van csatolva a terhelesbe
					# print('________________________')
					selectedWorker = ''
					for k, v in workerStatus.items():
						# print(k, v)
						if( v == True ):
							selectedWorker = k
					# print('------------------------')
					# print("selectedWorker = ", selectedWorker)
					# print('------------------------')

					# Ask the metric for a given worker
					# repWorker = '192.168.0.72'
					repWorker = selectedWorker
					repWorkerLogin = 'ubuntu@' + repWorker
					# print('------------------------')
					# print("repWorker= ", repWorker)
					# print('------------------------')



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


					# 1 - Date
					# 2 - Time
					# 3 - [CPU:0]User%
					# 5 - [CPU:0]Sys%
					# 


					# Ez az osszes metrikat visszaadja
					# statavgJO = subprocess.check_output(statcmd_all,shell=True)
					# statavgJO = subprocess.check_output(statcmd_all,shell=True,universal_newlines=True)

					# Ha latni akarom hogy mibol kesszult az atlag
					# statavg_all_short = subprocess.check_output(statcmd_all_short%("ubuntu@192.168.0.72"),shell=True,universal_newlines=True)
					if( print_statavg_all_short ):
						statavg_all_short = subprocess.check_output(statcmd_all_short%(repWorkerLogin),shell=True,universal_newlines=True)
						print('_______________________________________________________\n\n')
						print(statavg_all_short)

					# A tenyleges atlag a kivalasztott metrikakra
					# statavg_all_short = subprocess.check_output(statcmd_all_short_avg%("ubuntu@192.168.0.72"),shell=True,universal_newlines=True)
					statavg_all_short = subprocess.check_output(statcmd_all_short_avg%(repWorkerLogin),shell=True,universal_newlines=True)
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


					# -----------------------------------------------------------
					# Get Spring JVM Metrics from actuator/metrics

					stat_spring_jvm_given_worker = getSpringStatsGiven(repWorker)
					print('_______________________________________________________\n\n')
					print(stat_spring_jvm_given_worker)

# Todo. : ezt meg nem fejeztem be itt meg parsolni kell az adatokat
# Todo. : illetve van az, hogy nem errol hanem az actuator/prometheus vegpontrol kerem le az adatokat de azokat is parsolni kell




					# -----------------------------------------------------------
					# Scaling rule


					# Ki van olvasva a metrika es ki van olvasva az RT a response time.

					# Most el lehet donteni, hogy melyik alapjan akarunk skalazni.

					_cpu_user  = float(statavg_all_short.split()[0])
					_cpu_idle  = float(statavg_all_short.split()[1])
					_cpu_total = float(statavg_all_short.split()[2])


					k = 0
					if( _cpu_total > cpu_limit_upper ): # if _cpu_total is greater than the upper limit, consider scaling out
						print('---------------------------------------')
						print('         Testing for scale out         ')
						print('---------------------------------------')

						k+=1

					if( _cpu_total < cpu_limit_lower and w > 1): # if _cpu_total is less than lower limit, consider scaling in
						print('---------------------------------------')
						print('         Testing for scale in          ')
						print('---------------------------------------')

						k-=1


					# -----------------------------------------------------------
					# Log to file


					# print('---------------------------------------')
					# print('         Write Log metric file         ')
					# print('---------------------------------------')

					# Prepear data for statistic log files
					statarr=[float(i) for i in statavg_all_short.split()] 	# all the stats from collectl
					# print('statarr = ', statarr)
					carr=[rr/10]+statarr 					# calculated per second request rate since 10 second interval
					# print('carr \t= ', carr)
					# print(ts, p_95, avgrt, w)

					# mlog az mlog = csv.writer(metriclog)

					mlog.writerow([ts, p_95, avgrt, w]+carr) 		# add the timestamp, 95th percentile, avgrt, and number of workers to stats and log
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
					print('CPU Total                 =  {:.2f}'.format(_cpu_total))
					print('CPU Upper Limit           = ', cpu_limit_upper)
					print('CPU Lower Limit           = ', cpu_limit_lower)


					if k > 0: 								# if continous suggestion of scale out then scale out
						timesSuggested+=1
						print('timesSuggested out scale = ', timesSuggested)
						if timesSuggested >= trigger_count:  				# control continous suggestion number here
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
							removeWorker(workerStatus,repWorker,scalelog)	# remove only one worker
							print('\n\n   removeWorker   \n\n')
							workerStatus=workerInit()					
							w=sum(workerStatus.values())
					else:
						timesSuggested=0 					# if neither scale out nor scale in was suggested, reset the timesSuggested



					# -----------------------------------------------------------
					# End

					print('---------------------------------------')
					print('         End of Current Sessioon       ')
					print('---------------------------------------')


					
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
	return d

def printActiveWorkers(d):
	print(len(d))
	for worker in d:
	#	print(worker)
	#	print(type(worker))
	#	print(worker.get(0))
	#	print(worker.get(1))
		yield

def isViolatedStats(RTs, rt_lower_threshold, rt_upper_threshold):
	total_number_in_session = len(RTs)
	RTs_array = numpy.array(RTs)
	upper_violation = numpy.count_nonzero(RTs_array > rt_upper_threshold)
	lower_violation = numpy.count_nonzero(RTs_array < rt_lower_threshold)
	if( total_number_in_session > 0 ):
		upper_violation_ratio = upper_violation / total_number_in_session * 1.0
		lower_violation_ratio = lower_violation / total_number_in_session * 1.0
	result = {'lower_violation_number': lower_violation, 'upper_violation_number': upper_violation, 'lower_violation_ratio': lower_violation_ratio, 'upper_violation_ratio': upper_violation_ratio, 'total_number_in_session': total_number_in_session}
	return result


def getStats(RTs):
	RTs_array = numpy.array(RTs)
	mean = RTs_array.mean()
	median = numpy.median(RTs_array)
	maximum = RTs_array.max()
	minimum = RTs_array.min()
	std = RTs_array.std()
	stat = {'mean': mean, 'median': median, 'minimum': minimum, 'maximum': maximum, 'std': std}
	return stat

def getSpringStatsGiven(repWorker):
	'''Get Spring JVM Metrics from actuator/metrics'''

	print('Selected worker = ', repWorker)

	statcmd_spring_jvm = '''curl -s http://%s:8080/actuator/metrics'''

	stat_spring_jvm_given_worker = subprocess.check_output(statcmd_spring_jvm%(repWorker),shell=True,universal_newlines=True)
	return stat_spring_jvm_given_worker

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


def removeWorker(workerStatus,repWorker,scalelog):
	print('\n------------ removeWorker function ----------- \n')
	workerIP=-1
	for worker in workerStatus:
		print('worker  =', worker)
		print('repWorker = ', repWorker)
		if( workerStatus[worker] == True and worker != repWorker ):
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