#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 14:17:42 2023
Script that creates netCDF4 files from ASTER granules, containing all ASTER bands
interpolated to a 15m domain, and the corresponding cloud mask from Zhao et al. (2007)
@author: jdnied1@illinois.edu
"""

from pyhdf.SD import SD, SDC
from pyhdf.HDF import HDF
from pyhdf.VS import VS
import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import subprocess
import tqdm
import xarray as xr

def check_for_zeros(img):
	# Throw an error if there are zeros in the cropping
	# this shouldn't happen...
	if not np.all(img):
		print(d, ' ')
		print('ERROR')
		plt.figure()
		plt.imshow(img)
		plt.show()
		quit()

def rescale_image(img, high_res_dim):
	
	# get the rescaling factor to extrapolate a low dimension band to the highest dimension
	factor_correction = int(np.ceil((high_res_dim) / img.shape[0]))
	
	#perform extrapolation
	img = np.kron(img, np.ones((factor_correction,factor_correction)))
	
	# trim off the excess pixels
	diff = high_res_dim-img.shape[0]
	img = img[:diff,:diff]
	
	# check to see if the reshape is correct.. if not there is a flaw with the algorithm
	if high_res_dim != img.shape[0]:
		print('Data cube dimensions error')
		print(high_res_dim, ' ' ,img.shape[0], ' ', diff)
		quit()
	else:
		return img

def get_high_res_dim(sd):
	b1 = sd.select('ImageData1')[:]
	return np.shape(b1)[0]

def process_file(file_path, attr_names=None):
	"""
	Command processes and creates netCDF4 files containing ASTER band data (in the form of digital numbers)
	and a cloud mask from Zhao et al. (2007)

	attr_names - the attribute tags for each band in the ASTER .hdf file
	"""
	training_dates = get_text_data('training_files.txt')
	all_dates = get_text_data('retrieve_dates.txt')
	thresholds = open(os.path.join('..', 'retrieval_files', 'thresh.txt')).read()[1:-2].replace("'","").split(', ')

	sd = SD(str(file_path))

	
	# grab the dimensions of the image at 15m resolution
	high_res_dim = get_high_res_dim(sd)	

	X_DIM = 2000
	Y_DIM=2000

	# create the datacube we will use to write the data
	data_cube = np.zeros((len(attr_names) + 1, X_DIM, Y_DIM))
	band_index = 0

	for b, band_index in zip(attr_names, range(len(attr_names))):

		# read in the hdf file and select data attribute b
		img = sd.select(b)[:]
			
		if high_res_dim != img.shape[0]:
			img = rescale_image(img, high_res_dim)
			
		# set up cropping dimensions and coordinates
		centerx, centery = [int(img.shape[0] / 2) - int(X_DIM/2), int(img.shape[1] / 2) - int(Y_DIM/2)]
		# crop the img to remove nan data values and check none remain
		img = img[centerx:centerx + X_DIM, centery:centery + Y_DIM]
		
		check_for_zeros(img)

		# add the band image to the datacube
		data_cube[band_index, :, :] = img
		band_index += 1

		img = None


	# append the cloud mask
	img = sd.select('ImageData3N')[:]
	centerx, centery = [int(img.shape[0] / 2) - int(X_DIM/2), int(img.shape[1] / 2) - int(Y_DIM/2)]
	img = img[centerx:centerx + X_DIM, centery:centery + Y_DIM]
	data_cube[-1] = create_cmask(str(file_path).split('_')[2][3:], all_dates, thresholds, img)
	img = None
	
	sd.end()

	# check if training or testing data
	if str(file_path).split('_')[2][3:] in training_dates:
		out_root = 'training_data'
	else:
		out_root = 'testing_data'
		
	# write out the new ASTER file
	write_file(out_root, format_out_filename(str(file_path)), data_cube, attr_names, X_DIM, Y_DIM) 

def create_cmask(date, all_dates, thresholds, img):
	"""
	Command that takes a given date, retrieves the corresponding threshold and
	applies the threshold on a ASTER img

	date - a str sequence for the corresponding datetime
	all_dates - a list of the dates within our dataset
	thresholds - list of thresholds corresponding to each entry in all_dates
	img - a specific band img from ASTER

	return - the cloud mask for this ASTER granule
	"""
	index = np.where(date==np.array(all_dates))[0][0]	
	thresh = int(thresholds[index])
	return (img > thresh).astype(int)

def get_text_data(filename):
	"""
	Command opens and formats data from a .txt file

	filename - the file name in the retrieval files directory

	returns - a list containing the .txt data
	"""
	path = os.path.join('..', 'retrieval_files', filename)
	txt_file = open(path)
	return txt_file.read().split('\n')[0:-1]

def format_out_filename(filename):
	"""
	Command creates the new netCDF4 output file name
	
	filename - original hdf filename

	returns - formatted netCDF4 file name with the same datetime from the input
	"""
	return f'AST_{filename.split("_")[2][3:]}.nc'	

def write_file(root, filename, data_cube, attr_names, X_DIM, Y_DIM):
	"""
	Write out the ASTER data to a netCDF4 file

	root - the root directory of where to put the .nc files
	filename - the output .nc filename
	data_cube - a numpy data array containing all the band and cloud mask data
	attr_names - the names of each output attribute (i.e bands, cloud mask, etc)	
	X_DIM, Y_DIM - the image size of the band data
	"""
	band_labels = [f'Band_{n.split("ImageData")[1]}' for n in attr_names]
	band_labels.append('Cloud_Mask')
	band_labels = np.array(band_labels)
	ds = xr.Dataset(data_vars=dict(data=(["Bands","x","y"], data_cube)), coords=dict(Bands=band_labels))

	ds.to_netcdf(os.path.join('..', root, filename))



def get_username_password():
	user = input("Please enter your Username for earthdata.nasa.gov: ")
	password = input("Please enter your Password for earthdata.nasa.gov: ")
	return user, password

def get_bands_to_process():
	valid_input = False
	while(not valid_input):
		bands_to_use = input("""Please enter the bands you want to use from the ASTER data in the format of a list. For example, if you want to example, if you want bands 3, 4, and 14 (our recommendation), you would enter: [3,4,14]. Enter here: """)
		non_int_flag = False
		for i in bands_to_use[1:-1].split(','):
			if not i.isdigit() or int(i) < 1 or int(i) > 14:
				non_int_flag = True
		if bands_to_use[0] != '[' or bands_to_use[-1] != ']' or non_int_flag:
			print()
			print('Invalid input, please ensure that you enter a properly formatted list and that bands numbers are numbers 1 through 14')
			print()
			print('___________________________________________')
		else:
			valid_input = True
			return bands_to_use[1:-1].split(',')
		

def process_dates(dates, band_attr_names):
	for date in tqdm.tqdm(dates):
		yr = date[4:8]
		mon = date[0:2]
		day = date[2:4]

		URL = f'https://e4ftl01.cr.usgs.gov/ASTT/AST_L1T.003/{yr}.{mon}.{day}/'
		
		subprocess.run(['wget', '-np', '-nd', '-r', '-N', f'--user={username}', f'--password={password}', '-P', f'{str(hdf_output_path)}', '-A', f'AST_L1T_003{date}*.hdf', URL], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

		file_path = glob.glob(os.path.join('..', 'data', '*.hdf'))
		if len(file_path) > 0:
			process_file(file_path[0], band_attr_names)
			os.remove(file_path[0])	
		else:
			print(f'ERROR: File not found for date: {date}')
			print("Moving on to the next file")



if __name__ == "__main__":
	#band_numbers = get_bands_to_process()
	band_numbers = [3, 6, 14]
	band_attr_names = [f'ImageData{n}' if int(n)!=3 else f'ImageData{n}N' for n in band_numbers] 
	
	username, password = get_username_password()

	training_dates = get_text_data('training_files.txt')
	testing_dates = get_text_data('testing_files.txt')
	path_to_wget_script = os.path.join('.', 'get_ASTER_datafiles.sh')
	hdf_output_path = os.path.join('..', 'data', '.')
	train_output_path = os.path.join('..', 'training_data', '.')
	test_output_path = os.path.join('..', 'testing_data', '.')

	if not os.path.exists(hdf_output_path):
    		os.makedirs(hdf_output_path)

	if not os.path.exists(train_output_path):
    		os.makedirs(train_output_path)

	if not os.path.exists(test_output_path):
    		os.makedirs(test_output_path)


	process_dates(testing_dates, band_attr_names)
	process_dates(training_dates, band_attr_names)


