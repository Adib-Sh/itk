import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt



class get_data():
    def __init__(self):
        self.path = os.getcwd()
        self.rc_file = self.path + "\\results\\20240314\\ABCStar_R5H1_ppa_20240314_502_3_RESPONSE_CURVE_PPA.json"
        self.no_file = self.path + "\\results\\20240314\\ABCStar_R5H1_ppa_20240314_502_16_NO_PPA.json"

    
    def rc_data(self):
        with open(self.rc_file, "r") as file:
            data = json.load(file)
            
        return data
    
    def no_data(self):
        with open(self.no_file, "r") as file:
            data = json.load(file)
            
        return data
    
#Read Data
reader = get_data()
rc_data = reader.rc_data()["results"]
'''
KEYS:
    ['gain_away', 'gain_mean_away', 'gain_mean_under', 'gain_rms_away',
     'gain_rms_under', 'gain_under', 'innse_away', 'innse_mean_away',
     'innse_mean_under', 'innse_rms_away', 'innse_rms_under', 'innse_under',
     'offset_mean_away', 'offset_mean_under', 'offset_rms_away',
     'offset_rms_under', 'outnse_away', 'outnse_under', 'rc_fit_away',
     'rc_fit_under', 'vt50_away', 'vt50_mean_away', 'vt50_mean_under',
     'vt50_rms_away', 'vt50_rms_under', 'vt50_under']
'''
no_data = reader.no_data()["results"]
'''
KEYS:
    ['enc_est_away', 'enc_est_under', 'occupancy_mean_away', 'occupancy_mean_under',
     'occupancy_rms_away', 'occupancy_rms_under', 'offset_away', 'offset_under']
'''

#Data for plots

#RC data
gain_under =  rc_data["gain_under"]
gain_away =  rc_data["gain_away"]
gain_mean_under =  rc_data["gain_mean_under"]
gain_mean_away =  rc_data["gain_mean_away"]
gain_mean_under =  [np.mean(sublist) for sublist in rc_data["gain_under"]]
gain_mean_away =  [np.mean(sublist) for sublist in rc_data["gain_away"]]

vt50_under = rc_data["vt50_under"]
vt50_away = rc_data["vt50_away"]
vt50_mean_under = rc_data["vt50_mean_under"]
vt50_mean_away = rc_data["vt50_mean_away"]
vt50_mean_under = [np.mean(sublist) for sublist in rc_data["vt50_under"]]
vt50_mean_away = [np.mean(sublist) for sublist in rc_data["vt50_away"]]

innse_under = rc_data["innse_under"]
innse_away = rc_data["innse_away"]
innse_mean_under = rc_data["innse_mean_under"]
innse_mean_away = rc_data["innse_mean_away"]
innse_mean_under = [np.mean(sublist) for sublist in rc_data["innse_under"]]
innse_mean_away = [np.mean(sublist) for sublist in rc_data["innse_away"]]

outnse_under = rc_data["outnse_under"]
outnse_away = rc_data["outnse_away"]



#NO data
enc_est_under =  no_data["enc_est_under"]
enc_est_away =  no_data["enc_est_away"]

occupancy_mean_under = no_data["occupancy_mean_under"]
occupancy_mean_away = no_data["occupancy_mean_away"]

offset_under = no_data["offset_under"]
offset_away = no_data["offset_away"]

#Plots

xval= vt50_mean_under
yval= gain_mean_under
#channels_len = sum(len(results) for results in yval)
channels_len = len(yval)
channels = np.linspace(0, channels_len, channels_len)
plt.scatter(channels, yval, marker='o', linestyle='-')
plt.title('vt50_under vs. gain_under')
plt.xlabel('vt50_under')
plt.ylabel('gain_under')
plt.legend()