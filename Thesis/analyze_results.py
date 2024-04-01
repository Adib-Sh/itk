import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = os.getcwd()
with open(path + "\\results\\20240314\\ABCStar_R5H0_ppa_20240314_502_3_RESPONSE_CURVE_PPA.json", "r") as file:
    data = json.load(file)



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
results = data["results"]
gain_under =  results["gain_under"]
gain_away =  results["gain_away"]

vt50_under = results["vt50_under"]
vt50_away = results["vt50_away"]

innse_under = results["innse_under"]
innse_away = results["innse_away"]


channels_len = sum(len(results) for results in results["gain_under"])
#channels_len = len(gain_under)
channel = np.linspace(0, 100, channels_len)

#Plots
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']
'''
for sublist, color in zip(gain_under, colors):
    plt.scatter(range(len(sublist)), sublist, color=color, label=f'List {colors.index(color)+1}')
# Add labels and legend
plt.title('Scatter plot of values in sublists')
plt.xlabel('Index')
plt.ylabel('Value')
plt.legend()

# Show the plot
plt.show()
'''

combined_list1 = [item for sublist in gain_under for item in sublist]
combined_list2 = [item for sublist in vt50_under for item in sublist]

coeffs = np.polyfit(combined_list1, combined_list2, 1)
fitted_line_x = np.linspace(min(combined_list1), max(combined_list1), 100)
fitted_line_y = np.polyval(coeffs, fitted_line_x)

#plt.scatter(vt50_under, gain_under, marker='o', linestyle='-')
plt.plot(fitted_line_x, fitted_line_y, color='r', linestyle='-', linewidth=3)

plt.grid(True)



# Plot each sublist from list1 against corresponding sublist from list2
for sublist1, sublist2 in zip(gain_under, vt50_under):
    plt.scatter(sublist1, sublist2, marker="o", facecolor="none", edgecolors=colors)
    # Calculate linear fit for the current pair of sublists
    coeffs = np.polyfit(sublist1, sublist2, 1)
    fitted_line = np.polyval(coeffs, sublist1)

    # Plot the linear fit line
    plt.plot(sublist1, fitted_line, linestyle='--')

# Add labels
plt.title('Gain vs. vt50_under')
plt.xlabel('Gain')
plt.ylabel('vt50_under')

# Show the plot
plt.show()

