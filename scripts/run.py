import numpy as np 
import matplotlib.pyplot as plt
import os
import pandas as pd 
import seaborn as sn
import xarray as xr
import sys


def model_1(img):
	"""
	This is where you create your cloud mask.
        
	Parameters
        __________

        img: (3, M, N) numpy array
            A numpy array containing 3 (M, N) images at bands 3, 6, and 14

        Returns
        _______

        cloud_mask: (M, N) numpy array
            A numpy array containing an (M, N) binary cloud mask of img
        """
	cloud_mask = img[0] > 100
	return cloud_mask
	
def read_in_files(testing_directory):
	testing_data_bands = np.zeros((len(os.listdir(testing_directory)),3,2000,2000))
	file_num = 0
	fnames = []
	for filename in os.listdir(testing_directory):
		f = os.path.join(testing_directory, filename)
		# checking if it is a file
		if f[-2:] == 'nc':
			fnames.append(filename)
			ds_test = xr.open_dataset(f)
			img_bands = ds_test.data.to_numpy()[:-1]
			testing_data_bands[file_num, :, :, :] = img_bands
	return testing_data_bands, fnames

def run_model(model, data):
	masks = np.zeros((data.shape[0],data.shape[-2],data.shape[-1]))
	i = 0
	for d in data:
		masks[i] = model(d)
		i += 1	
	return masks

def save_data(filenames, new_masks):
	if not os.path.exists(os.path.join('..', 'new_masks')):
    		os.makedirs(os.path.join('..', 'new_masks'))
	for f,m in zip(filenames, new_masks):
		ds = xr.Dataset(data_vars=dict(data=(["x","y"], m)))
		ds.to_netcdf(os.path.join('..', 'new_masks', f))


if __name__ == "__main__":
	testing_dir = sys.argv[1]
	bands, filenames = read_in_files(testing_dir)
	m = model_1
	new_masks = run_model(m, bands)
	save_data(filenames, new_masks)	
