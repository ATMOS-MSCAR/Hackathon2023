# MSCAR Hackathon 2023
Welcome to the inaugural hackathon at the 7th Midwest Student Conference on Atmospheric Research! This year's hackathon challenge will be centered around cloud detection and cloud masking of satellite remote sensing imagery. The problem of cloud detection is a current area of research and has implications in the remote sensing of several atmospheric properties including aerosol and cloud property retrievals.

The hackathon challenge requires little-to-no background in remote sensing, radiation, or coding. Follow along with the tips in the "Getting Started" and "Tutorial" sections and start brainstorming how you will create the best cloud detection algorithm!

## Getting Started
The Advanced Spaceborne Thermal Emission and Reflection Radiometer (ASTER) is a high spatial resolution (15 - 90 m) instrument aboard NASA's Terra platform, which has been flying for over 20 years and collecting spectral data at 14 wavelengths in the very near infrared (0.52 - 0.86 micrometers), short-wave infrared (1.600 - 2.43 micrometers), and thermal infrared (8.125 - 11.65 micrometers).

Zhao and Di Girolamo (2007) selected a set of 151 ASTER scenes over ocean in which they carefully defined cloud mask thresholds for each scene (pixels with values greater than the threshold are considered cloudy, while pixels with values less than the threshold are considered clear). The instructions below will guide you through obtaining this set of ASTER data along with the corresponding cloud mask. The manual definition of a cloud mask threshold is highly accurate as we are able to adjust the threshold based off of what the human eye deems as cloud, however, this is not a practical method to obtain cloud masks on a global scale. Instead of manually creating a threshold for each ASTER image, as was done in Zhao and Di Girolamo (2007), your job is to come up with an algorithm which can determine a cloudy pixel from clear for any given ASTER scene over ocean. Naturally, this problem lends itself well to a machine learning approach, and you are welcome to use the training data provided to do so. Other methods, such as a simple single number threshold as demonstrated in the tutorial, are also sufficient so long as it can be applied to an arbitrary ASTER scene that is not already in the provided data set.

To set up your coding environment and download the data files, follow the instructions below.

### 0. Windows Users
The easiest way to obtain the data is via [The Windows Subsystem for Linux](https://learn.microsoft.com/en-us/windows/wsl/install) (WSL). In a powershell, install WSL by running
```
wsl --install
```
Upon completion, restart your computer and launch wsl from the start menu. This will launch a linux terminal from which you are able to perform the following steps.

Note: Your `C:\\` drive is located at `/mnt/c/` on the WSL.

### 1. Create Earthdata Search Account
In order to obtain the data set, you must [create an Earthdata Login](https://urs.earthdata.nasa.gov/users/new). 
### 2. Obtain repository
Obtain a copy of the repository by [cloning](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) or by downloading the repository as a zip file.

### 3. Set-up Conda environment
If you do not have conda installed on your machine, follow these [instructions](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) to install Miniconda or Anaconda.

In WSL, you may download an Anaconda installer with
```
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh
```
Once the file is installed, run the shell script and proceed through the requested prompts.
```
bash Anaconda3-2020.07-Linux-x86_64.sh
```

With Miniconda or Anaconda installed, in the root directory of the Hackathon23 repository, create an environment for the hackathon.
```
conda env create -f hackathon.yml
conda activate hackathon
```
If the above fails, execute the following sequence of commands.
```
conda  create  -n  hackathon  python=3.11.4
conda activate hackathon
conda install -c conda-forge tqdm numpy pandas xarray netcdf4 pyhdf matplotlib seaborn
conda install pytorch torchvision -c pytorch
pip install tensorflow
conda install -c anaconda jupyter
```
**Important: your submitted code must run in the provided conda environment. If you require additional dependencies, you must get them approved by emailing atmos-mscar@illinois.edu requesting a dependency. You must also submit a `hackathon.yml` file containing the additional approved dependencies.** If approval is granted, the `hackathon.yml` file can be created by running `conda env export --no-builds > hackathon.yml` in the active conda environment, which contains the additional, approved dependencies.

### 4. Download ASTER data

**Note: The complete ASTER data set (151 files) requires about 20 GB of memory. If your machine does not have that much memory available, you may download a subset of the total dataset.** 

Navigate to the `scripts` directory and run the python script `create_cmasks.py` to obtain the preprocessed  ASTER files. This will take a while to run (30 minutes - 6 hours... sorry). You will be prompted to enter your Earthdata Search credentials from step 1.
```
cd scripts
python create_cmasks.py
```
This script performs the following steps for each ASTER data file used in Zhao and Di Girolamo (2007):
- Downloads the ASTER data file.
- Extracts bands 3, 6, and 14.
- Extrapolates lower resolution images (bands 6 and 14) to high resolution 15 m^2^ pixels.
- Crops each image to a standard 2000 pixel x 2000 (30 km x 30 km) pixel image.
- Creates a cloud mask derived from the analysis in Zhao and Di Girolamo (2007).
- Saves bands 3, 6, 14, and the cloud mask in netCDF file format located in the `training_data` and `testing_data` directories.

Note: The script is divided into two stages. The first stage will download 51 ASTER files into `testing_data`. The second stage will download the remaining 100 ASTER files into `training_data`. There is nothing unique about how these files are split up. If you are unable to download all 151 files due to memory requirements, you may download a subset and manually split-up the testing and training data as you see fit.

After downloading the full or partial ASTER data set, the setup is complete.

## Tutorial

For more instructions on how to set up your workspace, take a look at our notebook tutorial covering the following steps:
1. Import your packages
2. Quick python basics
3. Read in your data
4. Visualize your data
5. Creating your first cloud mask 'model'
6. Generate accuracy measurements
7. Explore and develop

## Rules and Guidelines

Hackathon participants may work individually or together in self-organized teams. Participants must be registered in the 2023 Midwest Student Conference on Atmospheric Research either virtually or in-person. The winning individual or team will receive a $100 Amazon gift card.

Submitted code must run successfully in the conda environment provided for the competition (see instructions above to set up the environment). If a participant requires python dependencies not included in the provided environment, they must get them approved by the hackathon committee by emailing atmos-mscar@illinois.edu requesting approval for an additional dependency. You must also submit a `hackathon.yml` file containing the additional approved dependency (see "Set-up Conda environment" section above for instructions to create `hackathon.yml`).

### Code Submission

Code must be emailed to atmos-mscar@illinois.edu by 11:59 pm Central Time on September 29, 2023. Email submissions must include the following:

 - An attachment to the `run.py` script containing your cloud masking model. **Only the `model_1` function should be modified in the `run.py` script** (see "How to use `run.py`" below).
 - A list of  names of everyone who contributed.
 - (Optional) An attachment containing a `hackathon.yml` file if the conda environment used is different than the environment provided. (You must seek approval from the hackathon organizing committee)
 - (Optional) A brief written statement describing methodology or anything you would like the judges to know.

Participants will be scored based primarily on the accuracy of their cloud mask. The hackathon committee will evaluate submissions by evaluating the accuracy of submitted cloud mask models against a set of judging data, which is separate from the training and testing data provided. The judging data set contains ASTER scenes over ocean with human-derived thresholds similar to the data provided in the testing and training datasets. In the event of a tie in the accuracy of submitted algorithms, run time will be used to determine the winner.

### How to use `run.py`
Located within the `scripts` directory, the `run.py` script will be used for cede submission. Hackathon participants will place their cloud masking model into the `model_1` function provided. The `model_1` function should take as input a numpy array of shape (3, m, n) where the first dimension corresponds to bands 3, 6, and 14, and each band has an image dimension of m by n pixels. Images can be assumed to be of clouds over ocean. The `model_1` function should then return your best cloud mask in the form of a numpy array of shape (m, n).

You may choose to develop your algorithm directly within the `run.py` script, or you may choose to develop in your own script. **If you choose to create your own script, you must port your algorithm into the `run.py` script upon submission.**

A few more notes on the `run.py` script:

 - Executing the script requires one command line argument pointing to the directory containing ASTER testing or training data files (i.e. `/training_data` or `/testing_data`). The script will save netCDF files containing cloud masks of every ASTER scene contained in the directory passed into python generated by `model_1` saved to the directory `/new_masks`.
 - You may wish to modify more than just the `model_1` function in the `run.py` script for development. That is fine, however, when submitting, **please submit the original `run.py` script with only the `model_1` function modified.**

## References

Zhao, G., and L. Di Girolamo (2007), Statistics on the macrophysical properties of trade wind cumuli over the tropical western Atlantic, *J. Geophys. Res., 112,* D10204, doi:10.1029/2006JD007371.

