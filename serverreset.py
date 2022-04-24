import re
import csv
import time
import numpy
import datetime
import subprocess


import sys,os

def restart():

	print('---------------------------------------')
	print('              DELETE LOGS              ')
	print('---------------------------------------')

	# delete_cmd = '''sudo rm /var/log/apache2/other_vhosts_access.log'''

	delete_cmd = '''sudo rm -rf /var/log/apache2/*.log'''

	delete = subprocess.check_output(delete_cmd,shell=True,universal_newlines=True)

	print(delete)

	print('---------------------------------------')
	print('              RESTART A2               ')
	print('---------------------------------------')


	restart_cmd = '''sudo systemctl restart apache2'''

	restart = subprocess.check_output(restart_cmd,shell=True,universal_newlines=True)

	print(restart)


	print('---------------------------------------')
	print('              FINISHED                 ')
	print('---------------------------------------')


if( __name__ == '__main__' ):
	restart()
