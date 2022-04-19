# cpu.py

import re
import csv
import time
import numpy
import datetime
import subprocess

import sys,os

usr='ubuntu'

print('---------------------------------------')
print('                START                  ')
print('---------------------------------------')

def follow(thefile):
	thefile.seek(0,2)
	while True:
		line = thefile.readline()
		if not line:
			time.sleep(0.1)
			continue
		yield line


def main():
	print('---------------------------------------')
	print('                  MAIN                 ')
	print('---------------------------------------')
	# accesslog=open('/var/log/apache2/access.log','r')
	accesslog=open('/var/log/apache2/other_vhosts_access.log','r')
	# Ez a kurva mas neven tarolja le nem access.log hanem ebbe pakolja a cuccost

	loglines=follow(accesslog)
	print('fuk')
	first=True # hack to check if the script was just started
	print(first)
	cts=-1 # time-stamp we are looking to calculate response time for
	print(cts)
	RT=0 # RT keeps the total of response time
	print(RT)
	RTs=[] # array to keep individual RT observations
	print(RTs)
	N=0 # number of requests arrived in cts
	print(N)

	for	line in loglines: # follow the apache accesslog file
		# print('---------------------------------------')
		# print('                    FOR                ')
		# print('---------------------------------------')
		try:
			if first: # if script just started, initialize the necessary variables 
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)
				cts=matches.group(1)
				RT=float(matches.group(2))/1000.
				RTs.append(RT)
				N=1
				first=False
				print('This was the first attempt')
			else:
				# print(line)
				matches=re.search('.*:([0-9]*:[0-9]*:[0-9])[0-9] .* ([0-9]*)',line)
				ts=matches.group(1) # extract the time stamp of request
				if cts==ts: # if the timestamp is same, not changed then keep incrementing the variables
					RTs.append(float(matches.group(2))/1000.) # add to list for percentile
					RT+=float(matches.group(2))/1000. # add to sum for mean
					N+=1 
				elif cts<ts or (ts[0:7]=="00:00:0" and cts[0:7]=="23:59:5"): # case when the new request timestamp has changed -> interval passed
					rt=float(RT/N) # calculate averate rt
					avgrt=rt
					rr=N # request rate 
					p_95=numpy.percentile(RTs,95) # calculate percentile
					print("====== Average RT for ten second interval %s is %f, 95th percentile is: %f and RC is %d ======"%(cts,rt,p_95,rr))
					cts=ts # update the interval to current timestamp
					RT=float(matches.group(2))/1000. # reinitialize RT, N , RTs variables for next interval
					N=1
					RTs=[RT]
				
					
		except Exception as e:
			print(line)
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			print(exc_type, fname, exc_tb.tb_lineno)

main()