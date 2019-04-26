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
## Date: 02/02/2019
## Run Network
## Author: Zhangyu Guan
#######################################################
# network configuration
import netcfg, flytera_cfg

import FlyTera

import matplotlib

print('Please select the figure to be ploted from [1, 2, 3, 4, 5, 6]')
print('(for Linux OS, please quote the input with \'\')')
fig_id = input('[Input Please:]')

# print(flytera_cfg.figs[fig_id])
# exit(0)

# Update the simulation parameters
flytera_cfg.gry_trace_id        = flytera_cfg.figs[fig_id]['gry_trace_id']
flytera_cfg.lac_trace_id        = flytera_cfg.figs[fig_id]['lac_trace_id']
flytera_cfg.beam_alignment_itvl = flytera_cfg.figs[fig_id]['beam_alignment_itvl']
flytera_cfg.angle               = flytera_cfg.figs[fig_id]['beam_width']

# loop over all beam alignment intervals
for almt_itvl in flytera_cfg.beam_alignment_itvl:
    FlyTera.run_net(almt_itvl)
    flytera_cfg.sim_index += 1   
    # input('...')    
    
# print(flytera_cfg.sim_time)    

# Plot figures
font = {'family' : 'sans',
        'size'   : 14}	
matplotlib.rc('font', **font)

matplotlib.pyplot.plot(flytera_cfg.sim_time, flytera_cfg.data1, 'k--', flytera_cfg.sim_time, flytera_cfg.data2, 'r-',\
                       flytera_cfg.sim_time, flytera_cfg.data3, 'b.-', )
if fig_id in ['1']:                       
    matplotlib.pyplot.ylim(0.9983935, 0.9983945)
    matplotlib.pyplot.legend(('Ideal Beam Alignment', 'Adaptive Beam Alignment', 'No Beam Alignment'),
               loc='lower left')   
elif fig_id in ['4']:                       
    matplotlib.pyplot.ylim(0.97, 0.999)
    matplotlib.pyplot.legend(('Ideal Beam Alignment', 'Adaptive Beam Alignment', 'No Beam Alignment'),
               loc='lower left')                  
elif fig_id in ['2', '5']:
    matplotlib.pyplot.legend(('Ideal Beam Alignment', 'Adaptive Beam Alignment', 'No Beam Alignment'),
               loc='lower left')                
else:
    matplotlib.pyplot.legend(('Ideal Beam Alignment', 'Adaptive Beam Alignment', 'No Beam Alignment'),
               loc='center right')                   
    
matplotlib.pyplot.xlabel('Time (s)') 
matplotlib.pyplot.ylabel('Normalized Capacity') 

matplotlib.pyplot.grid(True)
  
matplotlib.pyplot.show()
