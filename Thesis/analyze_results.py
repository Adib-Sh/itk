import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

path = os.getcwd()
class get_data():
    def __init__(self):
        self.path = os.getcwd()
        self.rc_file = self.path + "/results/20240404/ABCStar_R5H0_ppa_20240404_520_40_RESPONSE_CURVE_PPA.json"
        self.no_file = self.path + "/results/20240404/ABCStar_R5H0_ppa_20240404_520_50_NO_PPA.json"

    
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

xval= vt50_under
yval= gain_under
channels_len = sum(len(results) for results in yval)
#channels_len = len(yval)
channels = np.linspace(0, channels_len, channels_len)


'''
plt.scatter(channels, yval, marker='o', linestyle='-')
plt.title('vt50_under vs. gain_under')
plt.xlabel('vt50_under')
plt.ylabel('gain_under')
plt.legend()
plt.show()
'''

# Creating subplots of RC

gain_under = [item for sublist in gain_under for item in sublist]
innse_under = [item for sublist in innse_under for item in sublist]
vt50_under = [item for sublist in vt50_under for item in sublist]

gain_away = [item for sublist in gain_away for item in sublist]
innse_away = [item for sublist in innse_away for item in sublist]
vt50_away = [item for sublist in vt50_away for item in sublist]

# Plotting the first set of RC data
plt.figure(figsize=(14, 10))
plt.suptitle('Response vs. channel at 1 fC', fontsize=20)
x_divisions = np.linspace(min(channels), max(channels), num=10)

plt.subplot(3, 2, 1)
plt.plot(channels, gain_under, 'r-')
plt.ylabel('gain(mV/fC)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)
plt.text(10, 80.5, 'ATLAS ITk', weight='bold', fontsize = 13)
plt.text(230, 80.5, 'work in progress', fontsize = 10)

plt.text(800, 80.5, 'preliminary test conducted', weight='bold', fontsize =  7)
plt.text(800, 80, 'in coldbox @ Lund University', weight='bold', fontsize = 7)

plt.text(800, 79, 'ITk Strip R5 PPA1', weight='bold', fontsize = 8)

plt.subplot(3, 2, 2)
plt.plot(channels, gain_away, 'r-')
plt.ylabel('gain(mV/fC)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)

plt.subplot(3, 2, 3)
plt.plot(channels, innse_under, 'g-')
plt.ylabel('input noise (ENC)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)
    
plt.subplot(3, 2, 4)
plt.plot(channels, innse_away, 'g-')
plt.ylabel('input noise (ENC)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)

plt.subplot(3, 2, 5)
plt.plot(channels, vt50_under, 'b-')
plt.ylabel('vt_50 (mV)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)
plt.xlabel('channels of under section')

plt.subplot(3, 2, 6)
plt.plot(channels, vt50_away, 'b-')
plt.ylabel('vt_50 (mV)')
for i in range(0, 9, 2):
    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)
plt.xlabel('channels of away section')




plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig(path+"/results/20240404/Plots/LTRT_2_plot.png", dpi=300)
plt.show()



# Creating subplots of NO
'''
plt.figure(figsize=(30, 10))
plt.suptitle('Plot of vt50/input noise/gain at each channel', fontsize=20)


plt.subplot(2, 3, 1)
xval = vt50_mean_under
yval = occupancy_mean_under
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('VT50(under)')
plt.ylabel('Occupancy (under)')
plt.yscale('log')
plt.ylim(0.0000001, 10)
x_divisions = np.linspace(min(xval), max(xval), num=10)
#for i in range(0, 9, 2):
#    plt.axvspan(x_divisions[i], x_divisions[i+1], color='grey', alpha=0.3)

plt.subplot(2, 3, 4)
xval = vt50_mean_away
yval = occupancy_mean_away
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('VT50(away)')
plt.ylabel('Occupancy (away)')
plt.yscale('log')
plt.ylim(0.0000001, 10)


plt.subplot(2, 3, 2)
xval = enc_est_under
yval = occupancy_mean_under
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('ENC (under)')
plt.ylabel('Occupancy (under)')
plt.yscale('log')
plt.ylim(0.0000001, 10)


plt.subplot(2, 3, 5)
xval = enc_est_away
yval = occupancy_mean_away
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('ENC(away)')
plt.ylabel('Occupancy (away)')
plt.yscale('log')
plt.ylim(0.0000001, 10)


plt.subplot(2, 3, 3)
xval = gain_mean_under
yval = occupancy_mean_under
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('Gai (under)')
plt.ylabel('Occupancy (under)')
plt.yscale('log')
plt.ylim(0.0000001, 10)


plt.subplot(2, 3, 6)
xval = gain_mean_away
yval = occupancy_mean_away
plt.scatter(xval, yval, c='r', s=10)
plt.xlabel('Gain(away)')
plt.ylabel('Occupancy (away)')
plt.yscale('log')
plt.ylim(0.0000001, 10)
'''
'''
# Plot each read-out with individual fit
###!!!Works only with detailed data NOT MEAN!!!###
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']
for sublist1, sublist2, color in zip(xval, yval, colors):
    plt.scatter(sublist1, sublist2, marker="o")
    # Calculate linear fit for the current pair of sublists
    coeffs = np.polyfit(sublist1, sublist2, 1)
    fitted_line = np.polyval(coeffs, sublist1)
    
    # Plot the linear fit line
    #plt.plot(sublist1, fitted_line, color=color, linestyle='--')
plt.title('vt50_under vs. gain_under')
plt.xlabel('vt50_under')
plt.ylabel('gain_under')
plt.legend()
plt.show()
'''
