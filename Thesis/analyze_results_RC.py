import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = os.getcwd()
with open(path + "/results/20240314/ABCStar_R5H0_ppa_20240314_502_3_RESPONSE_CURVE_PPA.json", "r") as file:
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




#Plots
colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple']

combined_list1 = [item for sublist in gain_away for item in sublist]
combined_list2 = [item for sublist in innse_away for item in sublist]

coeffs = np.polyfit(combined_list1, combined_list2, 1)
fitted_line_x = np.linspace(min(combined_list1), max(combined_list1), 100)
fitted_line_y = np.polyval(coeffs, fitted_line_x)

plt.scatter(combined_list1, combined_list2, marker='o', linestyle='-')
plt.plot(fitted_line_x, fitted_line_y, color = 'r', linestyle='-', linewidth=3, label=f'Fit to the full data')

plt.grid(True)



# Plot each sublist from list1 against corresponding sublist from list2
for sublist1, sublist2, color in zip(vt50_away, innse_away, colors):
    #plt.scatter(sublist1, sublist2, marker="o")
    # Calculate linear fit for the current pair of sublists
    coeffs = np.polyfit(sublist1, sublist2, 1)
    fitted_line = np.polyval(coeffs, sublist1)

    # Plot the linear fit line
    #plt.plot(sublist1, fitted_line, color=color, linestyle='--')

# Add labels
plt.title('vt50_away vs. innse_away')
plt.xlabel('vt50_away')
plt.ylabel('insse_away')
plt.legend(f'Fit')
plt.legend()


# Show the plot
plt.show()

#Per read-out----------------------------------------------------

channels_len = sum(len(results) for results in results["gain_under"])
#channels_len = len(gain_under)
channel = np.linspace(0, len(combined_list1), len(combined_list1))

plt.scatter(channel, combined_list1, marker='o', linestyle='-')
ylim = [0,200]

plt.show()