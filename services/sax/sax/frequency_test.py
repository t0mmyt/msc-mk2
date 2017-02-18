#!/usr/bin/env python3
import requests
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from frequency import Frequency
from paa import Paa

r = requests.get(
    "http://localhost:8004/v1/sax/Z?network=YW&station=NAB1&start=1315406870000&end=1315406872000&normalise=true&absolute=false&distribution=gaussian&bandpassLow=1&bandpassHigh=20"
)
results = r.json()['results']

t_orig, z_orig = zip(*results)
t_dt = [datetime.utcfromtimestamp(i/1000) for i in t_orig]
t_orig = np.array(t_orig)
z_orig = np.array(z_orig)

f = Frequency(*zip(*results))
tf = f.frequency_basic()
t, f = (zip(*tf))
t = np.array(t)
f = np.array(f)
t = [datetime.utcfromtimestamp(i/1000) for i in t]

p = Paa(t_orig, z_orig)

t_paa, z_paa = zip(*p.paa(20))
t_paa_plot = np.zeros(len(t_paa) * 2 - 2)
z_paa_plot = np.zeros(len(z_paa) * 2 - 2)
for i in range(len(t_paa) - 1):
    t_paa_plot[2 * i] = t_paa[i]
    t_paa_plot[2 * i + 1] = t_paa[i + 1]
    z_paa_plot[2 * i] = z_paa[i]
    z_paa_plot[2 * i + 1] = z_paa[i]
t_paa_plot = [datetime.utcfromtimestamp(i/1000) for i in t_paa_plot]

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

print(t_paa_plot, z_paa_plot)

ax1.plot(t_dt, z_orig, 'b-')
ax1.plot(t_paa_plot, z_paa_plot, 'g-')
ax2.plot(t, f, 'r')
ax1.set_ylabel('Original Data', color='b')
ax2.set_ylabel('Frequency (Hz)', color='r')

#
# # t = np.arange(0.01, 10.0, 0.01)
# # s1 = np.exp(t)
# # ax1.plot(t, s1, 'b-')
# # ax1.set_xlabel('time (s)')
# # # Make the y-axis label, ticks and tick labels match the line color.
# # ax1.set_ylabel('exp', color='b')
# # ax1.tick_params('y', colors='b')
# #
# # s2 = np.sin(2 * np.pi * t)
# # ax2.plot(t, s2, 'r.')
# # ax2.set_ylabel('sin', color='r')
# # ax2.tick_params('y', colors='r')
# #
fig.tight_layout()
plt.show()
