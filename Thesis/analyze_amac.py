import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

path = os.getcwd()
class get_data():
    def __init__(self):
        self.path = os.getcwd()
        self.rc_file = self.path + "/results/20240404/amac_data.json"

    
    def test_amac_data(self):
        with open(self.rc_file, "r") as file:
            data = json.load(file)
            
        return data
    
    
#Read Data
reader = get_data()
test_amac_data = reader.test_amac_data()


#Data for plots
time = test_amac_data["timestamps"]
time_labels = [datetime.fromisoformat(t).strftime('%H:%M:%S') for t in time]


Iin = test_amac_data["Iin"][:len(time)]
Iin_Low = test_amac_data["Iin_Hi"][:len(time)]
Iin_Hi = test_amac_data["Iin_Hi"][:len(time)]

Iout = test_amac_data["Iout"][:len(time)]
Iout_Low = test_amac_data["Iout_Hi"][:len(time)]
Iout_Hi = test_amac_data["Iout_Hi"][:len(time)]

Vin = test_amac_data["Vin"][:len(time)]
Vout = test_amac_data["Vout"][:len(time)]


#Plots


# Creating subplots
# Plotting the first set of data
plt.figure(figsize=(12, 9))
plt.suptitle('Plot of test interval amac data ', fontsize=20)


plt.subplot(4, 2, 1)
plt.plot(time_labels, Iin, 'r-')
plt.ylabel('Iin')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
plt.subplot(4, 2, 2)
plt.plot(time_labels, Iout, 'r-')
plt.ylabel('Iout')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(4, 2, 3)
plt.plot(time_labels, Iin_Low, 'b-')
plt.ylabel('Iin_low')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
    
plt.subplot(4, 2, 4)
plt.plot(time_labels, Iout_Low, 'b-')
plt.ylabel('Iout_Low')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(4, 2, 5)
plt.plot(time_labels, Iout_Low, 'g-')
plt.ylabel('Iout_Low')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(4, 2, 6)
plt.plot(time_labels, Iout_Hi, 'g-')
plt.ylabel('Iout_Hi')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(4, 2, 7)
plt.plot(time_labels, Vin, 'y-')
plt.ylabel('Vin')
plt.xlabel('timestamp')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 

plt.subplot(4, 2, 8)
plt.plot(time_labels, Vout, 'y-')
plt.ylabel('Vout')
plt.xlabel('timestamp')
plt.xticks(ticks=range(0, len(time_labels), len(time_labels) // 9 + 1)) 
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig(path+"/results/20240404/Plots/amac_plot.png", dpi=500)
plt.show()


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