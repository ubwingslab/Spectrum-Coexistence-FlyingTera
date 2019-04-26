# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#######################################################
## Date: 02/01/2019
## Author: Zhangyu Guan
## Configurations related FlyingTera
#######################################################
import numpy as np
import scipy.io as sio

# Number of drone hotspots
num_dhs = 2                         

# Initial coordinates of the two drones, with distance around 10 meters
ini_axis_x = np.matrix('100   107')
ini_axis_y = np.matrix('100   107')
ini_axis_z = np.matrix('10     10')

#######################################################
## Load traces of the drones

## Variables contained in the traces:
## gyr_micro_1000_inst1
## gyr_micro_1000_inst2
## gyr_micro_1000_inst3
## gyr_micro_1000_inst4

## gyr_small_1000_inst1
## gyr_small_1000_inst2
## gyr_small_1000_inst3
## gyr_small_1000_inst4

## gyr_large_75_inst1
## gyr_large_75_inst2

## lac_micro_1000_inst1
## lac_micro_1000_inst2

## lac_small_1000_inst1
## lac_small_1000_inst2

## 1000 means there are 1000 samples, and 75 means 65 samples

## For all micro and small traces, the sampling rate is 200
## For large traces, the sampling rate is 15
#######################################################

mat_fname = 'dhs_trace.mat'
dhs_trace = sio.loadmat(mat_fname)
# print(dhs_trace['lac_micro_1000_inst1'])
# exit(0)

# Trace selection
gry_trace_id    = [0, 1]            # [for dhs1, for dhs2]
gry_trace_name  = ['gyr_micro_1000_inst1', 'gyr_micro_1000_inst2', 'gyr_micro_1000_inst3', 'gyr_micro_1000_inst4',\
                   'gyr_small_1000_inst1', 'gyr_small_1000_inst2', 'gyr_small_1000_inst3', 'gyr_small_1000_inst4',\
                   'gyr_large_75_inst1',   'gyr_large_75_inst2']
                   
# print(dhs_trace['gyr_micro_1000_inst4'])
# exit(0)

# Sampling rat for each trace
gry_trace_smpl_rate = [200, 200, 200, 200, 200, 200, 200, 200, 200, 200]                  
# print(gry_trace_smpl_rate)

# Large scale linear acceleration is not collected, will be generated randomly
lac_trace_id   = [0, 1]              # [for dhs1, for dhs2]
lac_trace_name = ['lac_micro_1000_inst1', 'lac_micro_1000_inst2', 'lac_small_1000_inst1', 'lac_small_1000_inst2',\
                  'lac_large_inst1', 'lac_large_inst2']
lac_trace_smpl_rate = [200, 200, 200, 200]  

#######################################################
##    Configurations related to discrete simulation 
#######################################################
time_wait  = 0.1        # time to wait, used for animation only
sim_tick   = 1000       # the number ticks to simulate


#######################################################
##    Antenna model 
#######################################################
angle   = 5               # Beamwidth in degree 
radius  = 0.04            # Radius of receive surface in meter 


# Beam searching time
beam_sch_time = 0.01      # in second, takes values from [0.01, 0.05, 0.1, 0.5] 

# Beam alignment interval
beam_alignment_itvl = [1, 50, 5000]

# Plot, updated as the network runs
sim_index   = 0           # 0, 1, 2, updating data1, data2, data3, respectively. sim_time updated if 0

sim_time    = [0]
data1       = [1]
data2       = [1]
data3       = [1]

#######################################################
##    Configurations for different figures
#######################################################
fig1 = {'gry_trace_id':(0, 1), 'lac_trace_id':(0, 1), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 10}
fig2 = {'gry_trace_id':(4, 5), 'lac_trace_id':(2, 3), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 10}
fig3 = {'gry_trace_id':(8, 9), 'lac_trace_id':(4, 5), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 10}
fig4 = {'gry_trace_id':(0, 4), 'lac_trace_id':(0, 2), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 5}
fig5 = {'gry_trace_id':(6, 7), 'lac_trace_id':(2, 3), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 5}
fig6 = {'gry_trace_id':(8, 9), 'lac_trace_id':(4, 5), 'beam_alignment_itvl':(1, 100, 5000), 'beam_width': 5}


figs = {'1':fig1, '2':fig2, '3':fig3, '4':fig4, '5':fig5, '6':fig6}

