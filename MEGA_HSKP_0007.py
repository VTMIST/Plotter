###usage: MEGA_HSKP_0007.py -S all -r -s 2017_10_24 -e 2018_03_01
# you can put any system, or any number of systems separated by commas (i.e. 2,4,8) you can also put dates in yyyy-mm-dd or yyyy_mm_dd format

import time
start_time = time.time()
import sys, getopt, os
from datetime import datetime, timedelta
import glob, gzip, zipfile, csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as tckr
import matplotlib.dates as mdates
from matplotlib import dates, gridspec
import math

def main(argv):
	input = handle_input(argv)
	system_input = input.get('system')
	date_range = input.get('date_range')
	if input['season']:
		# season_dates = seas(int(input['season']))
		range_start = input.get('range_start')
		range_end = input.get('range_end')
	elif date_range:
		range_start = input.get('range_start')
		range_end = input.get('range_end')
	
	delta_days = range_end - range_start
	days_in_range = delta_days.days+1

	print 'Range of Dates: ',date_range
	if date_range:
		print '     Number of Days in Range: ',days_in_range		# these lines just show the user what they've asked for
		print '     Start: ',range_start.strftime('%B %d, %Y')
		print '       End: ',range_end.strftime('%B %d, %Y')
		print

	if input['ticker_override']:
		days_in_range = input['ticker_override']
		if days_in_range == 1:
			print 'Ticker settings configured to',days_in_range,'day format.\n'
		else:
			print 'Ticker settings configured to',days_in_range,'days format.\n'
	else:
		pass

	if input['equipment']:
		if equip_to_row(input['equipment']) in [8,9]:
			sysdata = []
			for system in [3,4,5,6]:
				sysdata.append(sysx_file_handler(list_sysx(range_start,range_end,str(system)),input['equipment']))
			sysdata[0] = equip_separator(np.asarray(sysdata[0][1],dtype=np.float32),np.asarray(sysdata[0][0]),3)
			sysdata[1] = equip_separator(np.asarray(sysdata[1][1],dtype=np.float32),np.asarray(sysdata[1][0]),2)
			sysdata[2] = equip_separator(np.asarray(sysdata[2][1],dtype=np.float32),np.asarray(sysdata[2][0]),1)
			sysdata[3] = equip_separator(np.asarray(sysdata[3][1],dtype=np.float32),np.asarray(sysdata[3][0]),0)
			CASES_plotter(sysdata[0],sysdata[1],sysdata[2],sysdata[3],days_in_range,input['output_filename'],[range_start,range_end],input['tickdelta'],input['equipment'])
		else:

			### FINISH THIS

#equip_plotter(sys2,sys3,sys4,sys5,sys6,sys8,length,out_fname,title_days,tickdelta,equipment):

			sysdata = []
			for system in [2,3,4,5,6,8]:
				sysdata.append(sysx_file_handler(list_sysx(range_start,range_end,str(system)),input['equipment']))
			sysdata[0] = equip_separator(np.asarray(sysdata[0][1],dtype=np.float32),np.asarray(sysdata[0][0]),5)
			sysdata[1] = equip_separator(np.asarray(sysdata[1][1],dtype=np.float32),np.asarray(sysdata[1][0]),4)
			sysdata[2] = equip_separator(np.asarray(sysdata[2][1],dtype=np.float32),np.asarray(sysdata[2][0]),3)
			sysdata[3] = equip_separator(np.asarray(sysdata[3][1],dtype=np.float32),np.asarray(sysdata[3][0]),2)
			sysdata[4] = equip_separator(np.asarray(sysdata[0][1],dtype=np.float32),np.asarray(sysdata[0][0]),1)
			sysdata[5] = equip_separator(np.asarray(sysdata[0][1],dtype=np.float32),np.asarray(sysdata[0][0]),0)

			equip_plotter(sysdata[0],sysdata[1],sysdata[2],sysdata[3],sysdata[4],sysdata[5],days_in_range,input['output_filename'],[range_start,range_end],input['tickdelta'],input['equipment'])


	else:
		for system_plot in input['system']:
			if system_plot == 1:
				sysdata = sys1_file_handler(list_sys1(range_start,range_end))
				sys1_plotter(sysdata,days_in_range,str(system_plot),input['output_filename'],input['tickdelta'])
				sysdata = False
			else:
				try:
					sysdata = sysx_file_handler(list_sysx(range_start,range_end,str(system_plot)),input['equipment'])
					sysx_plotter(sysdata,days_in_range,str(system_plot),input['output_filename'],input['tickdelta'])
					sysdata = False
				except IndexError:
					print('No data for Sys_'+str(system_plot)+'/PG_'+sysnum_to_pgnum(system_plot)+' for given dates.\n')
					pass

def file_patherator(option,O_S,year,date):
	if O_S == 'win32':
		if option == '1A':
			return str('.\data\\'+year+'\sys_1\PG1_PEN_HSKP_DATA_'+date+'.csv.zip')
		elif option == '1B':
			return str('.\data\\'+year+'\sys_1\SYS_1_PEN_HSKP_DATA_'+date+'.csv.zip')
		else:
			return str('.\data\\'+year+'\sys_'+option+'\hskp\\'+date)
	else:
		if option == '1A':
			return str('./data/'+year+'/sys_1/PG1_PEN_HSKP_DATA_'+date+'.csv.zip')
		elif option == '1B':
			return str('./data/'+year+'/sys_1/SYS_1_PEN_HSKP_DATA_'+date+'.csv.zip')
		else:
			return str('./data/'+year+'/sys_'+option+'/hskp/'+date)
def list_sys1(start,end):		# generates a file list from a list of dates
	date_list = []
	year_list = []
	for single_date in daterange(start,end):
		date_list.append(single_date.strftime('%Y_%m_%d'))
	for y in date_list:
		year_list.append(y[:4])
	lister = range(len(date_list))
	file_list = []
	sys_time_option = False
	for i in lister:
		if int(year_list[i]) < 2012:
			sys_time_option = '1A'
		else:	
			sys_time_option = '1B'
		file_name = os.path.abspath(file_patherator(sys_time_option,sys.platform,year_list[i],date_list[i]))
		file_list.append(file_name)
	return file_list
def sys1_csv_namer(filepath):
	return filepath.split('\\')[-1].strip('.zip')
def sys1_file_handler(zip_list):
		#	initializing variables, first line is for ALL columns
	# file_list, dtg, gps_sync_age, gps_time_error_sec, gps_on_sync, gps_on_heat, int_modem_on_comm, int_modem_on_heat, int_modem_overtemp, ext_modem_on_comm, latitude_deg, longitude_deg, min_x_null, max_x_null, avg_x_null, min_z_null, max_z_null, avg_z_null, min_batt_temp, max_batt_temp, avg_batt_temp, min_cpu_board_temp, max_cpu_board_temp, avg_cpu_board_temp, min_batt_voltage, max_batt_voltage, avg_batt_voltage, int_modem_rf, ext_modem_rf = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]	#use if all fields are turned on
	file_list, dtg, gps_on_sync, gps_on_heat, int_modem_on_comm, int_modem_on_heat, ext_modem_on_comm, min_batt_temp, max_batt_temp, avg_batt_temp, min_cpu_board_temp, max_cpu_board_temp, avg_cpu_board_temp, min_batt_voltage, max_batt_voltage, avg_batt_voltage, int_modem_rf, ext_modem_rf = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
	for single_zip in zip_list:
		try:
			with zipfile.ZipFile(single_zip) as zipped_file:
				with zipped_file.open(sys1_csv_namer(single_zip), 'r') as csv_file:
					data = csv.reader(csv_file, delimiter=',')
					next(data, None) # iterates over the first line immediately
					
					for row in data:	# keeping extra data columns for ease in adding them later
						dtg.append(datetime(int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5]),int(row[6])))
						# gps_sync_age.append(int(row[7]))
						# gps_time_error_sec.append(float(row[8]))
						gps_on_sync.append(float(row[9]))
						gps_on_heat.append(float(row[10]))
						int_modem_on_comm.append(float(row[11]))
						int_modem_on_heat.append(float(row[12]))
						# int_modem_overtemp.append(float(row[13]))
						ext_modem_on_comm.append(float(row[14]))
						# latitude_deg.append(float(row[15]))
						# longitude_deg.append(float(row[16]))
						# min_x_null.append(float(row[17]))
						# max_x_null.append(float(row[18]))
						# avg_x_null.append(float(row[19]))
						# min_z_null.append(float(row[20]))
						# max_z_null.append(float(row[21]))
						# avg_z_null.append(float(row[22]))
						min_batt_temp.append(float(row[23]))
						max_batt_temp.append(float(row[24]))
						avg_batt_temp.append(float(row[25]))
						min_cpu_board_temp.append(float(row[26]))
						max_cpu_board_temp.append(float(row[27]))
						avg_cpu_board_temp.append(float(row[28]))
						min_batt_voltage.append(float(row[29]))
						max_batt_voltage.append(float(row[30]))
						avg_batt_voltage.append(float(row[31]))
						int_modem_rf.append(float(row[38]))
						ext_modem_rf.append(float(row[39]))
		except IOError:
			pass
	datas = {'dtg':dtg, 'gps_on_sync':gps_on_sync, 'gps_on_heat':gps_on_heat, 'int_modem_on_comm':int_modem_on_comm, 'int_modem_on_heat':int_modem_on_heat, 'ext_modem_on_comm':ext_modem_on_comm, 'min_batt_temp':min_batt_temp, 'max_batt_temp':max_batt_temp, 'avg_batt_temp':avg_batt_temp, 'min_cpu_board_temp':min_cpu_board_temp, 'max_cpu_board_temp':max_cpu_board_temp, 'avg_cpu_board_temp':avg_cpu_board_temp, 'min_batt_voltage':min_batt_voltage, 'max_batt_voltage':max_batt_voltage, 'avg_batt_voltage':avg_batt_voltage, 'int_modem_rf':int_modem_rf, 'ext_modem_rf':ext_modem_rf}
	sorted_indices = np.argsort(datas['dtg'])
	for this_key in datas.keys():
		datas[this_key] = [datas[this_key][sorted_ix] for sorted_ix in sorted_indices]
 	return datas
def list_sysx(start,end,system_input):
	date_list = []
	year_list = []
	for single_date in daterange(start,end):
		date_list.append(single_date.strftime('%Y_%m_%d'))
	for y in date_list:
		year_list.append(y[:4])
	lister = range(len(date_list))
	folder_list = []
	for i in lister:
		file_name = os.path.abspath(file_patherator(system_input,sys.platform,year_list[i],date_list[i]))
		folder_list.append(file_name)
	return folder_list
def sysx_file_handler(folder_list,equip):
#	initializing variables
	if equip:
		file_list, dtg, equipment = [],[],[]
		for single_folder in folder_list:
			pathy = single_folder+'\*.gz'
			for i in glob.glob(pathy):
				file_list.append(i)
		for single_file in file_list:
			with gzip.open(single_file, 'rb') as zipped_file:
				data = csv.reader(zipped_file, delimiter=',')
				next(data, None) # iterates over the first line immediately
				for row in data:
					dtg.append(datetime(int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])))
					equipment.append(int(row[equip_to_row(equip)]))
		datas = {'dtg':dtg, 'equipment':equipment}
		sorted_indices = np.argsort(datas['dtg'])
		for this_key in datas.keys():
			datas[this_key] = [datas[this_key][sorted_ix] for sorted_ix in sorted_indices]
	 	return [datas['dtg'],datas['equipment']]

	else:
		file_list, dtg, voltage,input_current,input_power, cpu_load_1, cpu_load_5, cpu_load_15, t_batt_1, t_batt_2, t_batt_3, t_fg_elec, t_fg_sensor, t_router, modem_on, fg_on, sc_on, cases_on, hf_on, htr_on, gps_on, overcurrent_on = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]
		for single_folder in folder_list:
			pathy = single_folder+'\*.gz'
			for i in glob.glob(pathy):
				file_list.append(i)
		for single_file in file_list:
			with gzip.open(single_file, 'rb') as zipped_file:
				data = csv.reader(zipped_file, delimiter=',')
				next(data, None) # iterates over the first line immediately
				for row in data:
					dtg.append(datetime(int(row[0]),int(row[1]),int(row[2]),int(row[3]),int(row[4]),int(row[5])))
					voltage.append(float(row[20]))
					input_current.append(float(row[23]))
					input_power.append(float(row[24]))
					cpu_load_1.append(float(row[30]))
					cpu_load_5.append(float(row[31]))
					cpu_load_15.append(float(row[32]))
					t_batt_1.append(float(row[14]))
					t_batt_2.append(float(row[15]))
					t_batt_3.append(float(row[16]))
					t_fg_elec.append(float(row[17]))
					t_fg_sensor.append(float(row[18]))
					t_router.append(float(row[19]))
					modem_on.append(int(row[6]))
					fg_on.append(int(row[7]))
					sc_on.append(int(row[8]))
					cases_on.append(int(row[9]))
					hf_on.append(int(row[10]))
					htr_on.append(int(row[11]))
					gps_on.append(int(row[12]))
					overcurrent_on.append(int(row[13]))
		i=0
		while i < len(modem_on):
			if modem_on[i] != 0:
				modem_on[i] = (modem_on[i] + 7)
			else:
				modem_on[i] = np.nan
			if fg_on[i] != 0:
				fg_on[i] = (fg_on[i] + 6)
			else:
				fg_on[i] = np.nan
			if sc_on[i] != 0:
				sc_on[i] = (sc_on[i] + 5)
			else:
				sc_on[i] = np.nan
			if cases_on[i] != 0:
				cases_on[i] = (cases_on[i] + 4)
			else:
				cases_on[i] = np.nan
			if hf_on[i] != 0:
				hf_on[i] = (hf_on[i] + 3)
			else:
				hf_on[i] = np.nan
			if htr_on[i] != 0:
				htr_on[i] = (htr_on[i] + 2)
			else:
				htr_on[i] = np.nan
			if gps_on[i] != 0:
				gps_on[i] = (gps_on[i] + 1)
			else:
				gps_on[i] = np.nan
			if overcurrent_on[i] != 0:
				pass
			else:
				overcurrent_on[i] = np.nan
			i+=1
		datas = {'dtg':dtg, 'voltage':voltage,'input_current':input_current,'input_power':input_power, 'cpu_load_1':cpu_load_1, 'cpu_load_5':cpu_load_5, 'cpu_load_15':cpu_load_15, 't_batt_1':t_batt_1, 't_batt_2':t_batt_2, 't_batt_3':t_batt_3, 't_fg_elec':t_fg_elec, 't_fg_sensor':t_fg_sensor, 't_router':t_router, 'modem_on':modem_on, 'fg_on':fg_on, 'sc_on':sc_on, 'cases_on':cases_on, 'hf_on':hf_on, 'htr_on':htr_on, 'gps_on':gps_on, 'overcurrent_on':overcurrent_on}

		sorted_indices = np.argsort(datas['dtg'])
		for this_key in datas.keys():
			datas[this_key] = [datas[this_key][sorted_ix] for sorted_ix in sorted_indices]
	 	return datas


def handle_input(argv):		# handles user input
	date_range = False
	sysnum = 'none'
	range_start = ''
	range_end = ''
	showplot = False
	verb = False
	season = False
	ticker_override = False
	output_filename = False
	tickdelta = False
	equipment = False
	voltage = False
	system_number = False

# ^^initializing variables^^

	try:
		# place the option and its respective filenames into opts and args
		opts, args = getopt.getopt(argv,'hS:rs:e:pvY:O:o:dE:V')#,'input_filename=')
	except getopt.GetoptError:		# if we're given an incorrect option
		print '\n***You have input an unsupported option/argument***\nUsage: python sysx_plotter.py -d <system number [2-6]> -r -s <YYYY_MM_DD> -e <YYYY_MM_DD> -p -v\n   -d          Specifies what system to pull data for. This program is for sys 2-6.\n   -r          Plots between a range of dates (using -s and -e)\n   -s          First date to be included (YYYY_MM_DD)\n   -e          Last date to be included (YYYY_MM_DD)\n   -p          Show plot in python\n   -v          Verbose: shows missing and corrupted files\n\nFor a single date plot, start and end dates should be the same.'
		sys.exit()
	if len(argv) == 0:
		print '\nUsage: python sysx_plotter.py -d <system number [2-6]> -r -s <YYYY_MM_DD> -e <YYYY_MM_DD> -p -v\n   -d          Specifies what system to pull data for. This program is for sys 2-6.\n   -r          Plots between a range of dates (using -s and -e)\n   -s          First date to be included (YYYY_MM_DD)\n   -e          Last date to be included (YYYY_MM_DD)\n   -p          Show plot in python\n   -v          Verbose: shows missing and corrupted files\n\nFor a single date plot, start and end dates should be the same.'
		sys.exit()
	else:
		for opt, arg in opts:	# taking our options and handling inputs
			if opt == '-h':		# -h to show proper arguments/options
				print '\nUsage: python sysx_plotter.py -d <system number [2-6]> -r -s <YYYYMMDD> -e <YYYYMMDD> -p -v\n   -d          Specifies what system to pull data for. This program is for sys 2-6.\n   -r          Plots between a range of dates (using -s and -e)\n   -s          First date to be included (YYYY_MM_DD)\n   -e          Last date to be included (YYYY_MM_DD)\n   -p          Show plot in python\n   -v          Verbose: shows missing and corrupted files\n\nFor a single date plot, start and end dates should be the same.'
				sys.exit()
			elif opt == '-S':	# device to plot (sys1, sys2, etc.)
				sysnum = arg
			elif opt == '-r':	# plot a range of days
				date_range = True
			elif opt == '-s':	# first date included in plot
				range_start = arg
			elif opt == '-e': 	# last date included in plot
				range_end = arg
			elif opt == '-p': 	# plot to screen after saving
				showplot = True
			elif opt == '-v': 	# verbose
				verb = True
			elif opt == '-Y':	# use predefined season dates
				season = arg
			elif opt == '-O':	# gives the option to override ticker settings by using settings for a specific number of days
				ticker_override = int(arg)
			elif opt == '-o':	# gets optional output filename
				output_filename = arg
			elif opt == '-d':	# allows you to optionally place major ticks at the start and end of the plot, if they arent already there
				tickdelta = True
			elif opt == '-E':	# makes an equipment on/off plot
				equipment = arg
				voltage = False
			elif opt == '-V':	# makes a voltage plot
				if equipment:
					print("\nThis program can't plot voltage and equipment plots at the same time.")
					sys.exit()
				equipment = False
				voltage = True
	if date_range:
		if range_start == '' or range_end == '':
			print '\nThis program requires both a start and end date using "-r -s <YYYY_MM_DD> -e <YYYY_MM_DD>".\nYou could also opt for the predefined dates in the program using "-Y <YYYY>".'
		else:
			pass
	else:
		pass

	if equipment:
		pass
	elif voltage:
		pass
	else:
		if sysnum == 'none':
			print '\nThis program requires a system number using the -S option.\nUse "-S <system number>" or "-S all" or "-S <2,3,4>. '
			sys.exit()
		elif sysnum == 'all' or sysnum == 'All' or sysnum == 'ALL':
			system_number = [1,2,3,4,5,6,8]
		elif isinstance(sysnum,str): # checks to see if the input is some other string
			if len(sysnum) == 1:
				system_number = [int(sysnum)]
				if system_number[0] in range(1,9):
					pass
				else:
					print('\nSys_'+str(system_number[0])+' is not a valid system number.')
					sys.exit()
			else:
				system_number = []
				try:
					for system in sysnum.split(','):
						system_number.append(int(system))
				except ValueError: # catches invalid sysnum lists
					print('\nInvalid system number input. Input system numbers with a comma between each number (e.g. "-S 2,4,8").\n')
					sys.exit()
				for system in system_number:
					if system in range(1,9):
						pass
					else:
						print('\nSys_'+str(system)+' is not a valid system number.')
						system_number.remove(system)
						if len(system_number) == 1:
							print('\nNow plotting Sys_'+str(system_number[0])+'.')
						elif len(system_number) > 1:
							print('\nNow plotting:')
							for sys in system_number:
								print('Sys_'+str(sys))
							print
						else:
							print 'Check system inputs. Unhandled exceptions.'
							sys.exit()

	if date_range:	 		# taking in user defined dates and getting them into datetime format
		try: # creates start date datetime object. allows for users putting in date in YYYY_MM_DD or YYYY-MM-DD format
			start_date = datetime.strptime(range_start, '%Y_%m_%d')
		except ValueError:
			try:
				start_date = datetime.strptime(range_start, '%Y-%m-%d')
			except ValueError:
				print '\nFor future reference, this program requires start and end dates to be in YYYY_MM_DD format.' # if the user doesn't put in the date in either of these formats we will ask them for a new date
				try:
					start_date = datetime.strptime(raw_input('\nInput a new start date in YYYY_MM_DD format: '), '%Y_%m_%d')
				except ValueError:
					print '\nCOULD NOT RESOLVE START DATE!\n\nENDING PROGRAM!'
					sys.exit()
		try:	# creates end date datetime object. allows for users putting in date in YYYY_MM_DD or YYYY-MM-DD format
			end_date = datetime.strptime(range_end, '%Y_%m_%d')
		except ValueError:
			try:
				end_date = datetime.strptime(range_end, '%Y-%m-%d')
			except ValueError:
				print '\nFor future reference, this program requires start and end dates to be in YYYY_MM_DD format.'
				try:
					end_date = datetime.strptime(raw_input('\nInput a new end date in YYYY_MM_DD format: '), '%Y_%m_%d')
				except ValueError:
					print '\nCOULD NOT RESOLVE END DATE!\n\nENDING PROGRAM!'
					sys.exit()
	if season:
		start_end = seas(int(season))
		start_date = datetime.strptime(start_end['starter'], '%Y_%m_%d')
		end_date = datetime.strptime(start_end['ender'], '%Y_%m_%d')
	else:
		pass
	return {'system':system_number,'output_filename':output_filename, 'date_range':date_range, 'range_start':start_date, 'range_end':end_date, 'showplot':showplot, 'verb':verb, 'season':season,'ticker_override':ticker_override,'tickdelta':tickdelta,'equipment':equipment} # set to be returned

# generates a file list from a list of dates


# finds the range of real days between the start and end dates
def daterange(start_date, end_date):
	for n in range(int((end_date - start_date).days)+1):
		yield start_date + timedelta(n)

# provides dates for the -k flag
def seas(season):
	dates = {}
	if season == 2006:
		dates = {'starter':'2005_10_01','ender':'2006_09_01'}
	elif season == 2007:
		dates = {'starter':'2006_10_01','ender':'2007_09_01'}
	elif season == 2008:
		dates = {'starter':'2007_10_01','ender':'2008_09_01'}
	elif season == 2009:
		dates = {'starter':'2008_10_01','ender':'2009_09_01'}
	elif season == 2010:
		dates = {'starter':'2009_10_01','ender':'2010_09_01'}
	elif season == 2011:
		dates = {'starter':'2010_10_01','ender':'2011_09_01'}
	elif season == 2012:
		dates = {'starter':'2011_10_01','ender':'2012_09_01'}
	elif season == 2013:
		dates = {'starter':'2012_10_01','ender':'2013_09_01'}
	elif season == 2014:
		dates = {'starter':'2013_10_01','ender':'2014_09_01'}
	elif season == 2015:
		dates = {'starter':'2014_10_01','ender':'2015_09_01'}
	elif season == 2016:
		dates = {'starter':'2015_10_01','ender':'2016_08_01'}
	elif season == 2017:
		dates = {'starter':'2016_10_01','ender':'2017_09_01'}
	elif season == 2018:
		dates = {'starter':'2017_10_01','ender':'2018_09_01'}
	else:
		print('\nInvalid Season Input! Attempting to plot last 7 days.\n')
		dates = {'starter':(datetime.now()-timedelta(days=8)).strftime('%Y_%m_%d'),'ender':datetime.now().strftime('%Y_%m_%d')}
	return dates

def range_to_tickers(days):
	if days > 365:
		major_locator = mdates.DayLocator(bymonthday=1, interval=3)
		major_formatter = mdates.DateFormatter(fmt='%Y-%m-%d')
		minor_locator = mdates.DayLocator(bymonthday=(1,15))
		minor_formatter = mdates.DateFormatter(fmt='')
		major_size = '5'
		minor_size = '4'
		linewidth = 0.5
	elif days > 180: # up to 365 days
		major_locator = mdates.DayLocator(bymonthday=1, interval=1)
		major_formatter = mdates.DateFormatter(fmt='%Y-%m-%d')
		minor_locator = mdates.DayLocator(bymonthday=15)
		minor_formatter = mdates.DateFormatter(fmt='%m-%d')
		major_size = '5'
		minor_size = '4'
		linewidth = 0.5
	elif days > 90: # up to 180 days
		major_locator = mdates.DayLocator(bymonthday=(1),interval=1)
		major_formatter = mdates.DateFormatter(fmt='%Y\n%m-%d')
		minor_locator = mdates.DayLocator(bymonthday=(8,15,22,29),interval=1)
		minor_formatter = mdates.DateFormatter(fmt='%m-%d')
		major_size = '9'
		minor_size = '6'
		linewidth = 0.5
	elif days > 30: # up to 90 days
		major_locator = mdates.HourLocator(byhour=(0),interval=7)
		major_formatter = mdates.DateFormatter(fmt='%Y\n%m-%d')
		minor_locator = mdates.HourLocator(byhour=(0),interval=1)
		minor_formatter = mdates.DateFormatter(fmt='')
		major_size = '10'
		minor_size = '5'
		linewidth = 0.5
	elif days > 7: # up to 30 days
		major_locator = mdates.HourLocator(byhour=0,interval=1)
		major_formatter = mdates.DateFormatter(fmt='%Y\n%m-%d')
		minor_locator = mdates.HourLocator(byhour=(0,6,12,18),interval=1)
		minor_formatter = mdates.DateFormatter(fmt='')
		major_size = '9'
		minor_size = '4'
		linewidth = 1
	elif days > 3: # up to 7 days
		major_locator = mdates.HourLocator(byhour=0,interval=1)
		major_formatter = mdates.DateFormatter(fmt='%Y\n%m-%d')
		minor_locator = mdates.HourLocator(byhour=(6,12,18),interval=1)
		minor_formatter = mdates.DateFormatter(fmt='%H')
		major_size = '10'
		minor_size = '8'
		linewidth = 1
	else: # up to 3 days
		major_locator = mdates.HourLocator(byhour=(0,12),tz=None,interval=1)
		major_formatter = mdates.DateFormatter(fmt='%Y\n%m-%d')
		minor_locator = mdates.HourLocator(byhour=(2,4,6,8,10,14,16,18,20,22),interval=1)
		minor_formatter = mdates.DateFormatter(fmt='%H:%M')
		major_size = '6.5'
		minor_size = '4'
		linewidth = 1
	
	return {'mj_loc':major_locator,'mj_fmt':major_formatter,'mn_loc':minor_locator,'mn_fmt':minor_formatter,'major_size':major_size,'minor_size':minor_size,'linewidth':linewidth}

def sys1_plotter(data,length,sysnum,out_fname,tickdelta):
	pgnum = sysnum_to_pgnum(sysnum) # finds the PG number for the system number
	ticker_settings = range_to_tickers(length) # pulls ticker settings based on number of days in plot

	date_0 = data['dtg'][0]	# pulling the first date from the data, for title and filenames
	date_n = data['dtg'][-1] # pulling the last date from the data, for title and filenames


	
	f, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(nrows=6, ncols=1, sharex='col', sharey=False) #also facecolor='burlywood' sets background colors for the plots
	f.set_size_inches(16,9) # setting the size of the entire figure (f) (originally used 14,9.5)

	ax1 = plt.subplot2grid((6,1),(0,0),rowspan=2)	# sets position of each subplot
	ax2 = plt.subplot2grid((6,1),(2,0),rowspan=1)	# 
	ax3 = plt.subplot2grid((6,1),(3,0),rowspan=1)	# 
	ax4 = plt.subplot2grid((6,1),(4,0),rowspan=1)	# 
	ax5 = plt.subplot2grid((6,1),(5,0),rowspan=1)	# 

	ax1.set_title(plot_titler(sysnum,length,date_0,date_n), fontsize=16, fontweight='bold')		# label for plot based on day

	ax1.plot(data['dtg'], data.get('int_modem_on_comm'), linestyle='-', linewidth=ticker_settings['linewidth'], color='blue', label='Internal Modem\n On for Comm (%)') 		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('ext_modem_on_comm'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='External Modem\n On for Comm (%)') 		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('int_modem_on_heat'), linestyle='-', linewidth=ticker_settings['linewidth'], color='orange', label='Internal Modem\n On for Heat (%)') 		#sets plotted data, line properties, and label for legend

	ax2.plot(data['dtg'], data.get('gps_on_sync'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='GPS on for Sync (%)') 		#sets plotted data, line properties, and label for legend
	ax2.plot(data['dtg'], data.get('gps_on_heat'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='GPS on for Heat (%)') 		#sets plotted data, line properties, and label for legend

	ax3.plot(data['dtg'], data.get('avg_batt_voltage'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='Battery Voltage (Avg)') 		#sets plotted data, line properties, and label for legend
	ax3.plot(data['dtg'], data.get('min_batt_voltage'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='Battery Voltage (Min)') 		#sets plotted data, line properties, and label for legend
	ax3.plot(data['dtg'], data.get('max_batt_voltage'), linestyle='-', linewidth=ticker_settings['linewidth'], color='blue', label='Battery Voltage (Max)') 		#sets plotted data, line properties, and label for legend

	ax4.plot(data['dtg'], data.get('avg_batt_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='Battery Temp (Avg)') 		#sets plotted data, line properties, and label for legend
	ax4.plot(data['dtg'], data.get('min_batt_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='Battery Temp (Min)') 		#sets plotted data, line properties, and label for legend
	ax4.plot(data['dtg'], data.get('max_batt_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='blue', label='Battery Temp (Max)') 		#sets plotted data, line properties, and label for legend

	ax5.plot(data['dtg'], data.get('avg_cpu_board_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='CPU Board Temp (Avg)')		#sets plotted data, line properties, and label for legend
	ax5.plot(data['dtg'], data.get('min_cpu_board_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='CPU Board Temp (Min)')		#sets plotted data, line properties, and label for legend
	ax5.plot(data['dtg'], data.get('max_cpu_board_temp'), linestyle='-', linewidth=ticker_settings['linewidth'], color='blue', label='CPU Board Temp (Max)')		#sets plotted data, line properties, and label for legend

	x_min, x_max = date_0, date_n	# setting the first and last dates to be used as x-axis min and max values	

	for subplot in [ax1,ax2,ax3,ax4,ax5]:
		subplot.set_xlim([x_min, x_max])		# restricting x-axis to data points, preventing an extra left and right xtick
		subplot.xaxis.set_major_locator(ticker_settings['mj_loc'])	# sets xaxis major locator
		subplot.xaxis.set_major_formatter(ticker_settings['mj_fmt'])	# sets xaxis major formatter
		subplot.xaxis.set_minor_locator(ticker_settings['mn_loc'])	# sets xaxis minor locator
		subplot.xaxis.set_minor_formatter(ticker_settings['mn_fmt'])	# sets xaxis minor formatter
		subplot.grid(which='major',axis='x',linewidth=.2,color='black')
		subplot.grid(which='minor',axis='x',linewidth=.1,color='grey')
	for subplot in [ax2,ax3,ax4,ax5]:
		subplot.grid(which='major',axis='y',linewidth=.2,color='black')

	for subplot in [ax1,ax2,ax3,ax4]:
		plt.setp(subplot.get_xticklabels(), visible=False)

		### Sets up y axis labels for plots
	ylabel_size=9
	ylabel_weight='bold'
	ax1.set_ylabel('Modem\nPercent On',fontsize=ylabel_size,fontweight=ylabel_weight)					# Sets Y axis labels
	ax2.set_ylabel('GPS\nPercent On',fontsize=ylabel_size,fontweight=ylabel_weight)			# Sets Y axis labels
	ax3.set_ylabel('Battery\nVoltage (V)',fontsize=ylabel_size,fontweight=ylabel_weight)				# Sets Y axis labels
	ax4.set_ylabel('Battery\nTemp (C)',fontsize=ylabel_size,fontweight=ylabel_weight)	# Sets Y axis labels
	ax5.set_ylabel('CPU Board\nTemp (C)',fontsize=ylabel_size,fontweight=ylabel_weight)				# Sets Y axis labels

		### Sets up the x_axis label for the whole figure on the bottom plot
	ax5.set_xlabel('Date/Time (UTC)',fontsize=ylabel_size,fontweight=ylabel_weight,labelpad=1)			# sets label of x axis

	if tickdelta:
		print 'Start:',start_end[0].strftime('%Y-%m-%d_%H_%M_%S'),'\nEnd:',start_end[1].strftime('%Y-%m-%d_%H_%M_%S'),'\n'
		startdelta = int(raw_input('Start ticker delta (minutes)? '))
		enddelta = int(raw_input('End ticker delta (minutes)? '))
		print '\nNew Start:',(start_end[0]+timedelta(minutes=startdelta)).strftime('%Y-%m-%d_%H_%M_%S'),'\n New End:',(start_end[1]+timedelta(minutes=enddelta)).strftime('%Y-%m-%d_%H_%M_%S')
		locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(minutes=enddelta))]
		# locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(seconds=15))]
		locator= tckr.FixedLocator(locs)
		ax.xaxis.set_major_locator(locator)	
	else:
		pass

		### Automatically resizes the subplots to eliminate whitespace before we resize in next step
	plt.autoscale(enable=True,axis='x',tight=True)
	plt.tight_layout(pad=3.5) # defines the amount of space between the outer text and the outside of the figure, based on text size (according to source documentation)

		### places the legends
	leg1,leg2,leg3,leg4,leg5=0,0,0,0,0
	for subplot,leg in zip([ax1,ax2,ax3,ax4,ax5],[leg1,leg2,leg3,leg4,leg5]):
		leg = subplot.legend(bbox_to_anchor=(1,.5), loc='center left', ncol=1)		# sets the position of our legends
		subplot.get_yaxis().set_label_coords(-0.04,.5)		# sets position of y axis labels

		### rotates the x-tick labels
	plt.setp(ax5.xaxis.get_majorticklabels(),rotation=90,horizontalalignment='center',size=ticker_settings['major_size'])		# rotates x-ticks on the last subplot (for space and legibility purposes), and centers them
	plt.setp(ax5.xaxis.get_minorticklabels(), rotation=90,size=ticker_settings['minor_size'])
	
		### adjusts spacing to get everything into the figure
	f.subplots_adjust(left=0.06,right=0.86,hspace=0.05) # moves the sides of the plots and pushes them together

		### saves the figure with the name given by plotfile_namer or the given output filename
	plt.savefig(plotfile_namer(sysnum,pgnum,out_fname,date_0,date_n,length),dpi=500)

def sysx_plotter(data,length,sysnum,out_fname,tickdelta):
	pgnum = sysnum_to_pgnum(sysnum) # finds the PG number for the system number
	ticker_settings = range_to_tickers(length) # pulls ticker settings based on number of days in plot

	date_0 = data['dtg'][0]	# pulling the first date from the data, for title and filenames
	date_n = data['dtg'][-1] # pulling the last date from the data, for title and filenames


	
	f, (ax1, ax2, ax3, ax4, ax5, ax6) = plt.subplots(nrows=6, ncols=1, sharex='col', sharey=False) #also facecolor='burlywood' sets background colors for the plots
	f.set_size_inches(16,9) # setting the size of the entire figure (f) (originally used 14,9.5)

	ax1 = plt.subplot2grid((6,1),(0,0),rowspan=1)	# sets position of each subplot
	ax2 = plt.subplot2grid((6,1),(1,0),rowspan=1)	# 
	ax3 = plt.subplot2grid((6,1),(2,0),rowspan=1)	# 
	ax4 = plt.subplot2grid((6,1),(3,0),rowspan=1)	# 
	ax5 = plt.subplot2grid((6,1),(4,0),rowspan=1)	# 
	ax6 = plt.subplot2grid((6,1),(5,0),rowspan=1)	# 

	ax1.set_title(plot_titler(sysnum,length,date_0,date_n), fontsize=16, fontweight='bold')		# label for plot based on day

	ax1.plot(data['dtg'], data.get('modem_on'), linestyle='-', linewidth=2, color='blue', label='Modem On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('fg_on'), linestyle='-', linewidth=2, color='green', label='Fluxgate On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('sc_on'), linestyle='-', linewidth=2, color='black', label='Searchcoil On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('cases_on'), linestyle='-', linewidth=2, color='blue', label='Cases On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('hf_on'), linestyle='-', linewidth=2, color='green', label='HF On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('htr_on'), linestyle='-', linewidth=2, color='black', label='Heater On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('gps_on'), linestyle='-', linewidth=2, color='blue', label='GPS On')		#sets plotted data, line properties, and label for legend
	ax1.plot(data['dtg'], data.get('overcurrent_on'), linestyle='-', linewidth=4, color='r', label='Overcurrent')		#sets plotted data, line properties, and label for legend
	ax2.plot(data['dtg'], data.get('cpu_load_1'), linestyle='-', linewidth=ticker_settings['linewidth'], color='yellow', label='CPU Load (1 min)')		#sets plotted data, line properties, and label for legend
	ax2.plot(data['dtg'], data.get('cpu_load_5'), linestyle='-', linewidth=ticker_settings['linewidth'], color='green', label='CPU Load (5 min)')		#sets plotted data, line properties, and label for legend
	ax2.plot(data['dtg'], data.get('cpu_load_15'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='CPU Load (15 min)')		#sets plotted data, line properties, and label for legend
	ax3.plot(data['dtg'], data.get('voltage'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='Battery Voltage (V)')		#sets plotted data, line properties, and label for legend
	ax4.plot(data['dtg'], data.get('input_current'), linestyle='-', linewidth=ticker_settings['linewidth'], color='r', label='Input Current (A)')		#sets plotted data, line properties, and label for legend
	ax4.plot(data['dtg'], data.get('input_power'), linestyle='-', linewidth=ticker_settings['linewidth'], color='b', label='Input Power (V)')		#sets plotted data, line properties, and label for legend	
	ax5.plot(data['dtg'], data.get('t_batt_1'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='Battery 1 Temp (C)')		#sets plotted data, line properties, and label for legend
	ax5.plot(data['dtg'], data.get('t_fg_sensor'), linestyle='-', linewidth=ticker_settings['linewidth'], color='r', label='FG Sensor Temp (C)')		#sets plotted data, line properties, and label for legend
	# ax5.plot(data['dtg'], data.get('t_batt_2'), linestyle='-', linewidth=ticker_settings['linewidth'], color='r', label='Battery 2 Temp (C)')		#sets plotted data, line properties, and label for legend
	# ax5.plot(data['dtg'], data.get('t_batt_3'), linestyle='-', linewidth=ticker_settings['linewidth'], color='b', label='Battery 3 Temp (C)')		#sets plotted data, line properties, and label for legend
	ax6.plot(data['dtg'], data.get('t_fg_elec'), linestyle='-', linewidth=ticker_settings['linewidth'], color='black', label='FG Electronics\nTemp (C)')		#sets plotted data, line properties, and label for legend
	ax6.plot(data['dtg'], data.get('t_router'), linestyle='-', linewidth=ticker_settings['linewidth'], color='red', label='Router Temp (C)')		#sets plotted data, line properties, and label for legend

	x_min, x_max = date_0, date_n	# setting the first and last dates to be used as x-axis min and max values	

	for subplot in [ax1,ax2,ax3,ax4,ax5,ax6]:
		subplot.set_xlim([x_min, x_max])		# restricting x-axis to data points, preventing an extra left and right xtick
		subplot.xaxis.set_major_locator(ticker_settings['mj_loc'])	# sets xaxis major locator
		subplot.xaxis.set_major_formatter(ticker_settings['mj_fmt'])	# sets xaxis major formatter
		subplot.xaxis.set_minor_locator(ticker_settings['mn_loc'])	# sets xaxis minor locator
		subplot.xaxis.set_minor_formatter(ticker_settings['mn_fmt'])	# sets xaxis minor formatter
		subplot.grid(which='major',axis='x',linewidth=.2,color='black')
		subplot.grid(which='minor',axis='x',linewidth=.1,color='grey')
	for subplot in [ax2,ax3,ax4,ax5,ax6]:
		subplot.grid(which='major',axis='y',linewidth=.2,color='black')

	for subplot in [ax1,ax2,ax3,ax4,ax5]:
		plt.setp(subplot.get_xticklabels(), visible=False)


		### Sets grid and y axis settings for the On/Off Plot
	ax1.set_ylim([.5,8.5])				# (optional) sets upper and lower limits of y axis
	ax1.yaxis.set_major_locator(tckr.MultipleLocator(base=1.0))
	ax1.yaxis.set_minor_locator(tckr.FixedLocator((1.5,2.5,3.5,4.5,5.5,6.5,7.5)))
	ax1.grid(which='minor',axis='y',linestyle=':',linewidth=.2,color='grey')
	ax1.set_yticklabels(['', 'OC', 'GPS', 'HTR', 'HF', 'Cases', 'SC', 'FG', 'Modem'],fontsize=9)

		### Sets up CPU load plot to plot integers
	ax2.yaxis.set_major_locator(tckr.MultipleLocator(base=2.0))
	ax2.yaxis.set_minor_locator(tckr.MultipleLocator(base=1.0))
	ax2.grid(which='minor',axis='y',linestyle=':',linewidth=.2,color='grey')

		### Sets up y axis labels for plots
	ylabel_size=9
	ylabel_weight='bold'
	ax1.set_ylabel('Equipment\nOn/Off',fontsize=ylabel_size,fontweight=ylabel_weight)					# Sets Y axis labels
	ax2.set_ylabel('CPU Load\n1=At Capacity',fontsize=ylabel_size,fontweight=ylabel_weight)			# Sets Y axis labels
	ax3.set_ylabel('Battery\nVoltage (V)',fontsize=ylabel_size,fontweight=ylabel_weight)				# Sets Y axis labels
	ax4.set_ylabel('Input Current (A)\nInput Power (W)',fontsize=ylabel_size,fontweight=ylabel_weight)	# Sets Y axis labels
	ax5.set_ylabel('Battery Temp\nDegrees (C)',fontsize=ylabel_size,fontweight=ylabel_weight)				# Sets Y axis labels
	ax6.set_ylabel('Sensor Temp\nDegrees (C)',fontsize=ylabel_size,fontweight=ylabel_weight)				# Sets Y axis labels

		### Sets up the x_axis label for the whole figure on the bottom plot
	ax6.set_xlabel('Date/Time (UTC)',fontsize=ylabel_size,fontweight=ylabel_weight,labelpad=1)			# sets label of x axis

	if tickdelta:
		print 'Start:',start_end[0].strftime('%Y-%m-%d_%H_%M_%S'),'\nEnd:',start_end[1].strftime('%Y-%m-%d_%H_%M_%S'),'\n'
		startdelta = int(raw_input('Start ticker delta (minutes)? '))
		enddelta = int(raw_input('End ticker delta (minutes)? '))
		print '\nNew Start:',(start_end[0]+timedelta(minutes=startdelta)).strftime('%Y-%m-%d_%H_%M_%S'),'\n New End:',(start_end[1]+timedelta(minutes=enddelta)).strftime('%Y-%m-%d_%H_%M_%S')
		locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(minutes=enddelta))]
		# locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(seconds=15))]
		locator= tckr.FixedLocator(locs)
		ax.xaxis.set_major_locator(locator)	
	else:
		pass
	
		### Automatically resizes the subplots to eliminate whitespace before we resize in next step
	plt.autoscale(enable=True,axis='x',tight=True)
	plt.tight_layout(pad=3.5) # defines the amount of space between the outer text and the outside of the figure, based on text size (according to source documentation)

		### Places the legends
	leg1,leg2,leg3,leg4,leg5,leg6=0,0,0,0,0,0
	for subplot,leg in zip([ax1,ax2,ax3,ax4,ax5,ax6],[leg1,leg2,leg3,leg4,leg5,leg6]):
		leg = subplot.legend(bbox_to_anchor=(1,.5), loc='center left', ncol=1)		# sets the position of our legends
		subplot.get_yaxis().set_label_coords(-0.04,.5)		# sets position of y axis labels

		### rotates the x-tick labels
	plt.setp(ax6.xaxis.get_majorticklabels(),rotation=90,horizontalalignment='center',size=ticker_settings['major_size'])		# rotates x-ticks on the last subplot (for space and legibility purposes), and centers them
	plt.setp(ax6.xaxis.get_minorticklabels(), rotation=90,size=ticker_settings['minor_size'])

		### adjusts spacing to get everything into the figure
	f.subplots_adjust(left=0.06,right=0.87,hspace=0.05) # moves the sides of the plots and pushes them together

		### saves the figure with the name given by plotfile_namer
	plt.savefig(plotfile_namer(sysnum,pgnum,out_fname,date_0,date_n,length),dpi=500)




def CASES_plotter(sys3,sys4,sys5,sys6,length,out_fname,title_days,tickdelta,equipment):
	ticker_settings = range_to_tickers(length) # pulls ticker settings based on number of days in plot
	start_end = start_end_locator(sys3[0],sys4[0],sys5[0],sys6[0])

	fig, ax = plt.subplots(figsize=(12,2))
	

	try:
		plt.plot(sys3[0],sys3[1],color='red',linewidth=3,label='SYS_3')#,marker=False)#,markersize=0)
	except IndexError:
		pass
	try:
		plt.plot(sys4[0],sys4[1],color='blue',linewidth=3,label='SYS_4')#,marker=False)#,markersize=0)
	except IndexError:
		pass
	try:
		plt.plot(sys5[0],sys5[1],color='orange',linewidth=3,label='SYS_5')#,marker=False)#,markersize=0)
	except IndexError:
		pass
	try:
		plt.plot(sys6[0],sys6[1],color='black',linewidth=3,label='SYS_6')#,marker=False)#,markersize=0)
	except IndexError:
		pass
	tline_one = equipment+' On/Off Plot'
	tline_two = start_end[0].strftime('%Y-%m-%d')+' to '+start_end[1].strftime('%Y-%m-%d')

	plt.title(str(tline_one+'\n'+tline_two))
	plt.ylabel('System '+equipment+' Operation')
	plt.yticks((1,2,3,4),('Sys_6','Sys_5','Sys_4','Sys_3'))

	# years = mdates.YearLocator()
	# months = mdates.MonthLocator()
	# weeks = mdates.WeekLocator()


	ax.xaxis.set_major_locator(ticker_settings['mj_loc'])
	ax.xaxis.set_major_formatter(ticker_settings['mj_fmt'])
	ax.xaxis.set_minor_locator(ticker_settings['mn_loc'])
	ax.xaxis.set_minor_formatter(ticker_settings['mn_fmt'])

	plt.setp(ax.xaxis.get_minorticklabels(), rotation=90,size=ticker_settings['minor_size'])
	plt.xticks(rotation=90,size=ticker_settings['major_size'])

	#### USED TO ADD START AND END TICKS IF NEEDED ###
	if tickdelta:
		print 'Start:',start_end[0].strftime('%Y-%m-%d_%H_%M_%S'),'\nEnd:',start_end[1].strftime('%Y-%m-%d_%H_%M_%S'),'\n'
		startdelta = int(raw_input('Start ticker delta (minutes)? '))
		enddelta = int(raw_input('End ticker delta (minutes)? '))
		print '\nNew Start:',(start_end[0]+timedelta(minutes=startdelta)).strftime('%Y-%m-%d_%H_%M_%S'),'\n New End:',(start_end[1]+timedelta(minutes=enddelta)).strftime('%Y-%m-%d_%H_%M_%S')
		locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(minutes=enddelta))]
		# locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(seconds=15))]
		locator= tckr.FixedLocator(locs)
		ax.xaxis.set_major_locator(locator)	
	else:
		pass
	######### REMOVE AFTER USE #######################

	plt.autoscale(enable=True,axis='x',tight=True)
	plt.tight_layout(pad=.5)

	plt.grid(which='major',axis='x',linewidth=.2,color='black')
	plt.grid(which='minor',axis='x',linewidth=.1,color='grey')

	
	# plt.show()
	if out_fname:
		plt.savefig(out_fname,dpi=500)
	else:
		out_fname = str(equipment+'_plot_'+start_end[0].strftime('%Y_%m_%d')+'_to_'+start_end[1].strftime('%Y_%m_%d')+'.png')
		# out_fname = str(equipment+'_plot_'+datetime.now().strftime('%Y-%m-%d_%H_%M_%S')+'.png') 	# use this line for plots named by when they were saved (for debugging)
		plt.savefig(out_fname,dpi=500)

def equip_plotter(sys2,sys3,sys4,sys5,sys6,sys8,length,out_fname,title_days,tickdelta,equipment):
	ticker_settings = range_to_tickers(length) # pulls ticker settings based on number of days in plot
	start_end = start_end_locator(sys3[0],sys4[0],sys5[0],sys6[0])

	fig, ax = plt.subplots(figsize=(12,2))

	for sys,color,label in zip([sys2,sys3,sys4,sys5,sys6,sys8],['red','blue','orange','black','green','purple'],['SYS_2','SYS_3','SYS_4','SYS_5','SYS_6','SYS_8']):
		print sys[0:10],color,label
		try:
			plt.plot(sys[0],sys[1],color=color,linewidth=3,label=label)#,marker=False)#,markersize=0)
		except IndexError:
			pass

	tline_one = equipment+' On/Off Plot'
	tline_two = start_end[0].strftime('%Y-%m-%d')+' to '+start_end[1].strftime('%Y-%m-%d')

	plt.title(str(tline_one+'\n'+tline_two))

	plt.ylabel('System '+equipment+' Operation')


	plt.yticks((1,2,3,4,5,6),('Sys_8','Sys_6','Sys_5','Sys_4','Sys_3','Sys_2'))

	# years = mdates.YearLocator()
	# months = mdates.MonthLocator()
	# weeks = mdates.WeekLocator()


	ax.xaxis.set_major_locator(ticker_settings['mj_loc'])
	ax.xaxis.set_major_formatter(ticker_settings['mj_fmt'])
	ax.xaxis.set_minor_locator(ticker_settings['mn_loc'])
	ax.xaxis.set_minor_formatter(ticker_settings['mn_fmt'])

	plt.setp(ax.xaxis.get_minorticklabels(), rotation=90,size=ticker_settings['minor_size'])
	plt.xticks(rotation=90,size=ticker_settings['major_size'])

	#### USED TO ADD START AND END TICKS IF NEEDED ###
	if tickdelta:
		print 'Start:',start_end[0].strftime('%Y-%m-%d_%H_%M_%S'),'\nEnd:',start_end[1].strftime('%Y-%m-%d_%H_%M_%S'),'\n'
		startdelta = int(raw_input('Start ticker delta (minutes)? '))
		enddelta = int(raw_input('End ticker delta (minutes)? '))
		print '\nNew Start:',(start_end[0]+timedelta(minutes=startdelta)).strftime('%Y-%m-%d_%H_%M_%S'),'\n New End:',(start_end[1]+timedelta(minutes=enddelta)).strftime('%Y-%m-%d_%H_%M_%S')
		locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(minutes=enddelta))]
		# locs = [mdates.date2num(start_end[0]+timedelta(minutes=startdelta))]+list(ax.get_xticks())+[mdates.date2num(start_end[1]+timedelta(seconds=15))]
		locator= tckr.FixedLocator(locs)
		ax.xaxis.set_major_locator(locator)	
	else:
		pass
	######### REMOVE AFTER USE #######################

	plt.autoscale(enable=True,axis='x',tight=True)
	plt.tight_layout(pad=.5)

	plt.grid(which='major',axis='x',linewidth=.2,color='black')
	plt.grid(which='minor',axis='x',linewidth=.1,color='grey')

	
	# plt.show()
	if out_fname:
		plt.savefig(out_fname,dpi=500)
	else:
		out_fname = str(equipment+'_plot_'+start_end[0].strftime('%Y_%m_%d')+'_to_'+start_end[1].strftime('%Y_%m_%d')+'.png')
		# out_fname = str(equipment+'_plot_'+datetime.now().strftime('%Y-%m-%d_%H_%M_%S')+'.png') 	# use this line for plots named by when they were saved (for debugging)
		plt.savefig(out_fname,dpi=500)

def equip_separator(equip,dtg,value):
	i=0
	try:
		while i < len(equip):
			if equip[i] == 1:
				equip[i] = 1+value
				# print equip[i]
			else:
				equip[i] = np.nan
				# print equip[i]
			i+=1
	except IndexError:
		pass
	return np.array([dtg,equip])
def plot_titler(sysnum,length,first,last):
	## set up the title of the plot
	first_titleday = first.strftime('%Y_%m_%d')		# setting the format for title dates
	last_titleday = last.strftime('%Y_%m_%d')

	if length == 1:
		return str('System '+sysnum+' HSKP Plotter: \n' + first_titleday + '\n')	# label for plot based on day
	else:
		return str('System '+sysnum+' HSKP Plotter: \n' + first_titleday + ' through ' + last_titleday + '\n')		# label for plot based on start and end dates
def plotfile_namer(sysnum,pgnum,out_fname,date_0,date_n,length):
	 # creates names based on given output filename
	if out_fname:
		return str('Sys_'+sysnum+'_'+out_fname)


		## includes pg number in title, don't use until there is a way to properly determine pg location from data
	# 	return str('Sys_'+sysnum+'_PG_'+pgnum+'_'+out_fname)

	# else:
	# 	if date_0.strftime('%Y_%m_%d') == date_n.strftime('%Y_%m_%d'):
	# 		return str('Sys_'+sysnum+'_PG_'+pgnum+'_HSKP_'+date_0.strftime('%Y_%m_%d')+'.png')
	# 	else:	
	# 		return str('Sys_'+sysnum+'_PG_'+pgnum+'_HSKP_'+date_0.strftime('%Y_%m_%d')+'_to_'+date_n.strftime('%Y_%m_%d')+'.png')


	## uses standard name from start and end dates
	else:
		if date_0.strftime('%Y_%m_%d') == date_n.strftime('%Y_%m_%d'):
			return str('Sys_'+sysnum+'_HSKP_'+date_0.strftime('%Y_%m_%d')+'.png')
		else:	
			return str('Sys_'+sysnum+'_HSKP_'+date_0.strftime('%Y_%m_%d')+'_to_'+date_n.strftime('%Y_%m_%d')+'.png')

		### for easy file generation while writing code, name is just timestamp of when file was written
		# return str('Sys_'+sysnum+'_PG_'+pgnum+'_'+'HSKP_'+datetime.now().strftime('%Y-%m-%d_%H_%M_%S')+'.png')
def sysnum_to_pgnum(sysnum):
	return {'1':'1','2':'0','3':'5','4':'2','5':'3','6':'4','8':'4'}.get(str(sysnum))
def pgnum_to_sysnum(pgnum):
	return {'1':'1','0':'2','5':'3','2':'4','3':'5','4':'6','4':'8'}.get(str(pgnum))
def equip_to_row(hw):
	if hw == 'CASES' or hw == 'cases' or hw == 'Cases':
		row = 9
	elif hw == 'Modem' or hw == 'modem' or hw == 'MODEM':
		row = 6
	elif hw == 'FLUXGATE' or hw == 'Fluxgate' or hw == 'fluxgate' or hw == 'fg' or hw == 'FG':
		row = 7
	elif hw == 'SEARCHCOIL' or hw == 'Searchcoil' or hw == 'searchcoil' or hw == 'SC' or hw == 'sc':
		row = 8
	elif hw == 'HF' or hw == 'Hf' or hw == 'hf':
		row = 10
	elif hw == 'HEATER' or hw == 'Heater' or hw == 'heater' or hw == 'htr' or hw == 'HTR':
		row = 11
	elif hw == 'GPS' or hw == 'Gps' or hw == 'gps':
		row = 12
	elif hw == 'OVERCURRENT' or hw == 'Overcurrent' or hw == 'overcurrent' or hw == 'OC' or hw == 'oc':
		row = 13
	else:
		row = hardware_to_row(raw_input('Invalid equipment name supplied. \nPlease enter equipment name (e.g. CASES, fluxgate, or SC): '))
	return row
def start_end_locator(pg2,pg3,pg4,pg5):
	starts = []
	ends = []
	try:
		starts.append(pg2[0])
		ends.append(pg2[-1])
	except IndexError:
		pass
	except AttributeError:
		pass
	try:
		starts.append(pg3[0])
		ends.append(pg3[-1])
	except IndexError:
		pass
	except AttributeError:
		pass
	try:
		starts.append(pg4[0])
		ends.append(pg4[-1])
	except IndexError:
		pass
	except AttributeError:
		pass
	try:
		starts.append(pg5[0])
		ends.append(pg5[-1])
	except IndexError:
		pass
	except AttributeError:
		pass	
	return (min(starts),max(ends))


if __name__ == '__main__':
	main(sys.argv[1:])

print("-- %s seconds--" % (time.time() - start_time))