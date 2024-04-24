import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path = os.getcwd()
with open(path + "\\results\\20240314\\ABCStar_R5H0_ppa_20240314_502_16_NO_PPA.json", "r") as file:
    data = json.load(file)



'''
KEYS:
    ['enc_est_away', 'enc_est_under', 'occupancy_mean_away', 'occupancy_mean_under',
     'occupancy_rms_away', 'occupancy_rms_under', 'offset_away', 'offset_under']
'''
results = data["results"]
enc_est_under =  results["enc_est_under"]
enc_est_away =  results["enc_est_away"]

occupancy_mean_under = results["occupancy_mean_under"]
occupancy_mean_away = results["occupancy_mean_away"]

offset_under = results["offset_under"]
offset_away = results["offset_away"]




#Plots


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
