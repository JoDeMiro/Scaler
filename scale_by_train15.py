# scale_by_none.py

import os
import re
import csv
import time
import numpy
import pickle
import datetime
import requests
import subprocess

import sys,os

from server_reset import restart

from cooler import printTest
from cooler import printColor
from cooler import printBlink

from termcolor import colored

printTest('printTest')

printColor('cyan', 'cyan')
printColor('red', 'red')
printColor('green', 'green')
printColor('yellow', 'yellow')
printColor('blue', 'blue')
printColor('magenta', 'magenta')
printColor('white', 'white')
printBlink('red', 'red')

print(colored('---------------------------------------', 'yellow'))
print(colored('---------------------------------------', 'red'))
print(colored('---------------------------------------', 'blue'))
print(colored('---------------------------------------', 'green'))
print(colored('---------------------------------------', 'magenta'))
print(colored('---------------------------------------', 'cyan'))

print(colored('--------------', color='red', on_color='on_grey'))
print(colored('--------------', color='red', on_color='on_grey', attrs=['bold']))
print(colored('--------------', color='red', on_color='on_grey', attrs=['bold', 'reverse']))
print(colored('--------------', color='red', on_color='on_grey', attrs=['bold', 'concealed']))

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from termcolor import colored

from sklearn.linear_model import LinearRegression




print('---------------------------------------')
print('                RESTART                ')
print('---------------------------------------')

# restart()

print('---------------------------------------')
print('                SET LOG                ')
print('---------------------------------------')

print_statavg_all_short = False

print('---------------------------------------')
print('                SETUP                  ')
print('---------------------------------------')

url = 'http://127.0.0.1/balancer-manager'

r = requests.get(url)
nonce = re.search(r'nonce=(.*?)">', r.text).group(1)

metricWorker = '192.168.0.6'

VCPU = 1 # A metrika gépen a VCPU száma

lb = '193.225.250.30'
usr='ubuntu'
# nonce='62c1d1d7-1c8a-152e-6b41-65bf544025c5'
log_file='zulu.log'
init_vm_number = 1
trigger_count = 1

metric_log_file_name = './Optimizer/metric_train_by_15_after_trained.log'
scale_log_file_name =  './Optimizer/scaled_train_by_15_after_trained.log'


# ----------------------------------------------------------------------
# melyik train folder
trained_folder = '/Train/Train15/'
# melyik train file
trained_metric_file_name = './Train/Train15/metric_train_by_none.log'
# mik az input változók (egyeznie kell a betöltött neurális hálóval)
input_variables = ['request_rate', 'CPU0User%', '[TCPD]OutSegs']

MIN_VM = 1
MAX_VM = 9
# ----------------------------------------------------------------------


print('---------------------------------------')
print('                CONFIG                 ')
RT_LIMIT_UPPER = 500
RT_LIMIT_LOWER = 200
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

def read_trained_csv(trained_metric_file_name):
	df = pd.read_csv(trained_metric_file_name, sep=',', header=0)
	# df.head()
	# ebből csak az utolsó sor kell
	last_df = df.iloc[[-1]]
	return last_df

def get_current_worker_number(last_df):
	# worker az kell a számításokhoz
	current_worker_number = last_df['worker_number'].values[0]
	return current_worker_number

def get_train_features(last_df, input_variables):
	# csak azok az oszlop kellenek amelyek bemenetei a neurális hálónak
	train_features = last_df[input_variables]
	train_features.head()
	print(train_features)
	return train_features

def load_tf_model(trained_folder):
	model = keras.models.load_model(os.getcwd() + trained_folder)
	return model

def pred_rt(model, train_features):
	predicted_labels = model.predict(train_features)
	return predicted_labels

def get_last_df_info(last_df):
	# pár egyéb dolgot ellenőrzéshez kiolvasok
	wcsv = last_df['write_to_csv_time']
	tper = last_df['time']
	c_rt = last_df['response_time']
	print(colored('wcsv -> \t' + str(wcsv), 'red'))
	print(colored('tper -> \t' + str(tper), 'red'))
	print(colored('c_rt -> \t' + str(c_rt), 'red'))


# ------------------------------------------------
# get_advice
# függvényhez szükséges függvéynek

def create_term_for_prediction(value: float, w: int, k: int):
	__metric_term1 = value * w/(w+k)
	__metric_term2 = value * k/(w+k)
	__metric_term = np.array([[__metric_term1, __metric_term2]])
	return __metric_term

def get_advice(w, train_features, model, scale=None):
	print(MIN_VM, MAX_VM)
	MAX = MAX_VM - w + 1
	MIN = MIN_VM - w
	# A = [x for x in range(MIN, MAX)]
	if scale == 'OUT':
		A = [x for x in range(1, MAX)]
	if scale == 'IN':
		A = [x for x in range(MIN, 0)]
	print(A)

	print('---------------------------------------')
	print('train_features -> azaz current metrics ')
	with np.printoptions(precision=2, suppress=True):
		print(train_features)
	print('---------------------------------------')
    
	# Pandas.Series -> nd.array
	train_features = train_features.values
	train_features = train_features[0]
	print('train_features ......', train_features)

	# aps ebbe pakolom az [a, __predicted_response_time] értékeket
	aps = []   
    
	for a in A:

		# 0.
		# inicializálni egy üres tömböt az input_variable változónak
		_new_train_features = np.zeros((1, train_features.shape[0]))
        
		# 1.
		# minden metrikára kiszámolni
		for i, metric in enumerate(input_variables):
			print(i, metric)
			if metric != 'worker_number':
            
                # Systematicly load
                # Minden egyes alkalommal betölteni elég nagy luxus de most így hagyom (később pedig kiszervezem egy külön
                # függvénybe és az elején beolvasom, letárolom őket egy listában aztán onnan töltöm be de most itt hagyom)
				f = 'lr/'
				f = os.getcwd() + trained_folder + f
				print('----------------------- pickle folder', f)
                # file name, I'm using *.pickle as a file extension
				filename = f + str(metric) + '.pickle'
                # load model
				__lr_model = pickle.load(open(filename, "rb"))
				print(__lr_model.coef_, __lr_model.intercept_)

				feature = train_features[i]
				#print(feature)

				# 3.
				# az előbbi model alapján egy becslés egy konkrét értékre (value, w, k)
				print(f'feature: {feature} w: {w} a: {a}')
				__metric_term = create_term_for_prediction(feature, w, a)
                
				# print('---a metrica értékének becsése (value, w, k alapján ---')
				# print(__metric_term.shape)
				# __metric_term  = np.squeeze(__metric_term, -1)
                
				__pred_metric = __lr_model.predict(__metric_term)

				# 4.
				# adott becsült metrikát bele kell helyezni a neurális háló bemeneti változójához
				_new_train_features[0, i] = __pred_metric

		# 5.
		# megvan az új a-hoz tartozó metika tömb, ez alapján becsüjük meg a válaszidőt
		with np.printoptions(precision=2, suppress=True):
			print(_new_train_features)
                
		# 6.
		# a neurális háló model segítségével megbecsülöm a válaszidőt
		__predicted_response_time = model.predict(_new_train_features, verbose = 0)

		with np.printoptions(precision=2, suppress=True):
			print('action = ', a, ' --> rt --> ', __predicted_response_time, '\n')

		aps.append([a, __predicted_response_time.flatten()[0]])

	return aps

def chose_action(aps, scale):
	# Keressük meg hol a legjobb a becslés
	# fps = pd.DataFrame(aps, columns=['delta_vm', 'pred_rt'])
	# fps
	print(colored('---------------------------------------', 'cyan'))
	print(colored('RT_LIMIT_UPPER  ' + str(RT_LIMIT_UPPER) , 'cyan'))
	print(colored('RT_LIMIT_LOWER  ' + str(RT_LIMIT_LOWER) , 'cyan'))
	print(colored('---------------------------------------', 'cyan'))

	# Kerresük meg hoa legjobb a becslés
	UPPER_LIMIT = 90
	LOWER_LIMIT = 30
	UPPER_LIMIT = RT_LIMIT_UPPER
	LOWER_LIMIT = RT_LIMIT_LOWER

	chosen_delta_vm_out = 19
	chosen_delta_vm_in  = -20
    
	chosen_delta_vm = None

	# scale out (felfelés skálázás)
	if scale == 'OUT':
		print('SCALE OUT')
		for row in aps:
			print(row)
			print(row[1])
			if row[1] < UPPER_LIMIT:
				chosen_delta_vm_out = row[0]
				print(chosen_delta_vm_out)
				break
		chosen_delta_vm = chosen_delta_vm_out

	# scale in (lefelés skálázás)
	if scale == 'IN':
		print('SCALE IN')
		for row in aps:
			print(row)
			print(row[1])
			if row[1]  < UPPER_LIMIT:
				chosen_delta_vm_in = row[0]
				print(chosen_delta_vm_in)
				break
		chosen_delta_vm = chosen_delta_vm_in

	print(colored('---------------------------------------', 'cyan'))
	print(chosen_delta_vm_out)
	print(chosen_delta_vm_in)
	print(chosen_delta_vm)
	print(colored('---------------------------------------', 'cyan'))

	return chosen_delta_vm

def read_metric_csv(metric_log_file_name):
	df = pd.read_csv(metric_log_file_name, sep=',', header=0)
	# df.head()
	# ebből csak az utolsó sor kell
	last_df = df.iloc[[-1]]
	return last_df


def main():
    
	print('---------------------------------------')
	print('                TEST DB                ')
	print('---------------------------------------')
    
	last_df = read_trained_csv(trained_metric_file_name)

	print('---------------------------------------')
	print('                TEST TF                ')
	print('---------------------------------------')
    
	train_features = get_train_features(last_df, input_variables)

	print('---------------------------------------')
	print('                TEST WN                ')
	print('---------------------------------------')

	current_worker_number = get_current_worker_number(last_df)

	print('---------------------------------------')
	print('                TEST IN                ')
	print('---------------------------------------')

	get_last_df_info(last_df)
    
	print('---------------------------------------')
	print('                TEST NN                ')
	print('---------------------------------------')
    
	model = load_tf_model(trained_folder)

	print('---------------------------------------')
	print('                TEST PR                ')
	print('---------------------------------------')
    
	predicted_labels = pred_rt(model, train_features)
	print(predicted_labels)

	print('---------------------------------------')
	print('                TEST AD                ')
	print('---------------------------------------')

	# aps = get_advice(w = 3, train_features = train_features, model = model, scale = 'OUT')
	aps = get_advice(w = current_worker_number, train_features = train_features, model = model, scale = 'OUT')

	print('---------------------------------------')
	print('                TEST CA                ')
	print('---------------------------------------')

	chosen_delta_vm = chose_action(aps, scale = 'OUT')
    
    # ------------------------------------------------------------------------------ ITT TARTOK 2023.05.15 19:03

	print('---------------------------------------')
	print('                TEST VARIABLES         ')
	print('---------------------------------------')

	print(train_features)
	print(current_worker_number)


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
	# metriclog=open('./metric_rt_threshold%i_%i.log'%(RT_LIMIT_LOWER,RT_LIMIT_UPPER),'w', newline='')
	# metriclog=open('./metric_cpu_threshold%i_%i.log'%(cpu_limit_lower,cpu_limit_upper),'w', newline='')

	# Ebben a sorrendben irom bele a metric.log-ba az adatokat
	# (idopont, response_time_95, response_time, worker_number, request_rate, metrics)
	metriclog.write('worker_give_metrics,')
	metriclog.write('write_to_csv_time,')
	metriclog.write('time,response_time_p95,response_time,worker_number,request_rate,')
	if VCPU == 1:
		metriclog.write('CPU0User%,CPU0Idle%,CPU0Total%,')
	if VCPU == 2:
		metriclog.write('CPU0User%,CPU0Idle%,CPU0Total%,CPU1User%,CPU1Idle%,CPU1Total%,')
	metriclog.write('[DSK:sda]Reads,[DSK:sda]RMerge,[DSK:sda]RKBytes,[DSK:sda]WaitR,[DSK:sda]Writes,[DSK:sda]WMerge,[DSK:sda]WKBytes,[DSK:sda]WaitW,[DSK:sda]Request,[DSK:sda]QueLen,[DSK:sda]Wait,[DSK:sda]SvcTim,[DSK:sda]Util,')
	metriclog.write('[NUMA:0]Used,[NUMA:0]Free,[NUMA:0]Slab,[NUMA:0]Mapped,[NUMA:0]Anon,[NUMA:0]AnonH,[NUMA:0]Inactive,[NUMA:0]Hits,')
	metriclog.write('[TCPD]InReceives,[TCPD]InDelivers,[TCPD]OutRequests,[TCPD]InSegs,[TCPD]OutSegs\n')
	metriclog.flush()
	mlog=csv.writer(metriclog)

	# Ebbe fogom tenni a skalazasi adatokat
	scalelog=open(scale_log_file_name,'w')
	# scalelog=open('./train_by_none.log','w')
	# scalelog=open('./scale_rt_threshold%i_%i.log'%(RT_LIMIT_LOWER,RT_LIMIT_UPPER),'w')
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
					metWorker = metricWorker
					metWorkerLogin = 'ubuntu@' + metWorker

					# Get the metrics command
					statcmd = '''ssh -A ubuntu@192.168.0.72 -oStrictHostKeyChecking=no tail -n 10 mylog.log | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '2-5,8-' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%f ", a[i]/NR;}}' '''

					statcmd_all = '''ssh -A ubuntu@192.168.0.72 -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '2-5,8-' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%f ", a[i]/NR;}}' '''

					statcmd_ido = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '1,2' '''

					statcmd_all_short_2VCPU     = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' '''

					statcmd_all_short_avg_2VCPU = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%%f ", a[i]/NR;}}' '''

					statcmd_all_short_ori_2VCPU = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]*:[0-9]*:[0-9]*' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,15,22,23,28-40,41-48,51,57,58,77,78' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%%f ", a[i]/NR;}}' '''

					statcmd_all_short_1VCPU     = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,16-28,29-36,39,45,46,65,66' '''

					statcmd_all_short_avg_1VCPU = '''ssh -A %s -oStrictHostKeyChecking=no 'tail -n 10 mylog.log' | grep '[0-9]' | sed 's/ \+/ /g' | cut -d ' ' -f '3,10,11,16-28,29-36,39,45,46,65,66' | awk '{for (i=1;i<=NF;i++){a[i]+=$i;}} END {for (i=1;i<=NF;i++){printf "%%f ", a[i]/NR;}}' '''


					# Természetesen ha Több VCPU van akkor elcsúszik az egész számozás és rossz lesz az egész (!)
                    
					if VCPU == 1:
						statcmd_all_short     = statcmd_all_short_1VCPU
						statcmd_all_short_avg = statcmd_all_short_avg_1VCPU
					elif VCPU == 2:
						statcmd_all_short     = statcmd_all_short_2VCPU
						statcmd_all_short_avg = statcmd_all_short_avg_2VCPU
					else:
						break
                    

					# 1 - Date
					# 2 - Time
					# 3 - [CPU:0]User%
					# 5 - [CPU:0]Sys%
					#
                    
					# Természetesen ha Több VCPU van akkor elcsúszik az egész számozás és rossz lesz az egész (!)


					# Ez az osszes metrikat visszaadja
					# statavgJO = subprocess.check_output(statcmd_all,shell=True)
					# statavgJO = subprocess.check_output(statcmd_all,shell=True,universal_newlines=True)

					# Ha latni akarom hogy mibol kesszult az atlag
					if( print_statavg_all_short ):
						statavg_all_short = subprocess.check_output(statcmd_all_short%(metWorkerLogin),shell=True,universal_newlines=True)
						print('_______________________________________________________\n\n')
						print(statavg_all_short)

					# A tenyleges atlag a kivalasztott metrikakra
					start_time = time.time()
					statavg_all_short = subprocess.check_output(statcmd_all_short_avg%(metWorkerLogin),shell=True,universal_newlines=True)
					end_time   = time.time()
					printTest('KI A metWorker AKITŐL LE FOGJUK KÉRNI A METRIKÁT')
					print(metWorker)
					print(metWorkerLogin)
					print('get metric took: {:.3f} sec'.format(end_time - start_time))
					if( print_statavg_all_short ):
						print('_______________________________________________________\n\n')
						print(statavg_all_short)

					print(colored('---------------------------------------', 'cyan'))
					print(colored('EZEN A PONTON EL VAN KÉRVE A METRIKA   ', 'cyan'))
					print(colored('---------------------------------------', 'cyan'))
					print(statavg_all_short)
                    
					__start_time = time.time()

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
					# if( rt > RT_LIMIT_UPPER ): # if response time is greater than the upper limit, consider scaling out
					if( rnd > 0.5 ): # véletlenszerűen skáláz fel, vag le.

						print('---------------------------------------')
						print('         Testing for scale out         ')
						print('---------------------------------------')

                        # Csak egyet adunk hozzá (fix)
						# k+=1
                        
                        # Random
						rnd1 = numpy.random.rand()
						delta = 1 if rnd1 < 0.5 else 2
						delta = 1 if rnd1 < 0.33 else 2 if rnd1 < 0.66 else 3
						k += delta
						print('-------------------------UP-------------------------------------------> k =', k)
                        
                        

					# if( rt < RT_LIMIT_LOWER and w > 1): # if response time is less than lower limit, consider scaling in
					if( rnd < 0.5 and w > 1): # véletlenszerűen skáláz fel,v agy le.
						print('---------------------------------------')
						print('         Testing for scale in          ')
						print('---------------------------------------')


                        # Csak egyet veszünk el (fix)
						# k-=1
                        
                        # Random
						rnd1 = numpy.random.rand()
						delta = 1 if rnd1 < 0.5 else 2
						delta = 1 if rnd1 < 0.33 else 2 if rnd1 < 0.66 else 3
						k -= delta
						print('-------------------------LE-------------------------------------------> k =', k)

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

# Ellenőrzés
# Mi a faszom itt az rt?
# Megynugodtam az avgrt és az rt ezen a ponton ugyan az
					print(colored('---------------------------------------', 'red'))
					print('    rt -----------> ', rt)
					print(' avgrt -----------> ', avgrt)
					print(colored('---------------------------------------', 'red'))
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

					__end_time = time.time()
					__met_time = __end_time - __start_time

					print(colored('---------------------------------------', 'cyan'))
					print(colored('ENNYI IDŐBE TELT KIIRNI A METRIKÁKAT   ', 'cyan'))
					print(colored(__met_time, 'cyan'))
					print(colored('---------------------------------------', 'cyan'))
                    
                    # Most kiszámolom a k értékét
                    #
                    # Korábban is megtettem, de most a metrikák alapján az ML segítségével
                    
                    # 1
                    # --> olvassuk ki a metrika filéből a szükséges adatokat
					last_metric_df = read_metric_csv(metric_log_file_name)
					print(last_metric_df)
                    #
                    # 2
                    # --> ez alapján mi a current_worker_number (by the way ezt máshonnan is megtudhatnám)
					current_worker_number = get_current_worker_number(last_metric_df)
					print(current_worker_number)
                    #
                    # 3
                    # --> előállítani a pred_feature-oket
					pred_features = get_train_features(last_metric_df, input_variables)
					print(pred_features)
                    #
                    # 4
                    # --> pred_features alapján megcsinálni az a/lr/nn becslést
                    #
                    # --> kiviből megnézem, hogy a pred
                    #
                    #     ez azt jelenti, hogy a jelenlegi értékek alapján ilyen becslést adna RT-re a háló
                    #
                    #     olyan minthhta (a = 0) lenne
                    #
                    #     <-- ez a rész kiiktatható, kivehető, ha gyorsítani akarom, debug-ra jó --> 

					predicted_labels = pred_rt(model, pred_features)
					print(predicted_labels)
					print(colored('---------------------------------------', 'cyan'))

                    #
                    # 5
                    # --> kiszámolom a lehetséges a-kra a metrikákat
                    #
                    # --> ellenőrzés
					print(current_worker_number)
					aps = get_advice(w = current_worker_number, train_features = pred_features, model = model, scale = 'OUT')
					print(colored('---------------------------------------', 'cyan'))
                    #
                    # Na ez a fenti rész az (5) az ami bekerülhet a skálázáshoz
                    #
                    







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
					print('Response Time Upper Limit = ', RT_LIMIT_UPPER)
					print('Response Time Lower Limit = ', RT_LIMIT_LOWER)


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

                    # ez rész régen így volt megírva, s csak egyet skálázott le
                    
					# elif k < 0: 							# if continous suggestion to scale in, then scale in
					#	timesSuggested+=1
					#	print('timesSuggested in scale = ', timesSuggested)
					#	if timesSuggested >= trigger_count: 				# control continous suggestion number here
					#		timesSuggested=0
					#		# for t in range(0,-k):
					#		#	print "Removing worker",t+1
					#		removeWorker(workerStatus,repWorker,scalelog)	# remove only one worker
					#		print('\n\n   removeWorker   \n\n')
					#		workerStatus=workerInit()
					#		w=sum(workerStatus.values())
                    
                    # vége

					elif k < 0: 							# if continous suggestion to scale in, then scale in
						timesSuggested+=1
						print('timesSuggested in scale = ', timesSuggested)
						if timesSuggested >= trigger_count: 				# control continous suggestion number here
							timesSuggested=0
							for t in range(0,-k):
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
