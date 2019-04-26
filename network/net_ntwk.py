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
# Date: 02/3/2019
# Author: Zhangyu Guan
# network class 
#######################################################

# from current folder
import net_name, net_func, net_node, netcfg, net_channel, net_gui

import flytera_cfg

import math, numpy as np

def new_ntwk(ntwk_type = None):
    '''
    create a network of the specified network type
    '''
    elmt_name = net_name.ntwk
    elmt_type = ntwk_type
    elmt_num  = 1    
    
    # network topology info, 1 network created
    addi_info = {'ntwk':None, 'parent':None}
    info = net_func.mkinfo(elmt_name, elmt_type, elmt_num, addi_info)    

    # create network
    return net_ntwk_dhs(info)                                                

class net_ntwk(net_func.netelmt_group):
    def __init__(self, net_info):      
        # from base network element
        net_func.netelmt_group.__init__(self, net_info) 

        # default network width and length in meter
        self.net_width  = 3000
        self.net_length = 3000
        
        # Maintain the list of all nodes in the network, initialized to empty list
        # Updated when nodes are created
        self.name_list_all_nodes = []
        
        # The list of the names of all node_to_node channel modules
        # Initialized to empty, updated when channel modules are created 
        # Also updated at each coherent time interval: reset all the channels and generate new channel states
        self.name_list_all_n2n_chnl = []
        
        # Total number of nodes in the network, incremented by 1 when a new node is created
        # The network-wide index of the node is also calculated based on this parameter
        # Initialize to 0
        self.tot_node_num = 0
               
        # x-, y- and z-axis coordinates of the nodes in name_list_all_nodes, updated when nodes created, move
        self.axis_x = []
        self.axis_y = []
        self.axis_z = []
        
        # distance from between nodes: row index for transmitter, column index for receiver
        # will be updated when coordinates of the nodes changes
        self.dist_matrix = None 
        
        # positive path loss factor 
        self.positive_pathloss_fact = 4
        
        
        # The list of active wifi stations including the wifi ap
        # Initialized to be empty
        # Will be updated dynamically as wifi stations turn on and off
        self.list_active_wifi_sta = []
        
        # The list of all LTE base stations
        # For each LTE base station, the channel covariance matrix will be estimated
        # Initialized to empty, updated as LTE BSs are created
        self.list_lte_bs = []
        
        # GUI, created when the network elements have been created
        self.gui = None
               
        print('Blank network created.')
        
    def reset_chnl(self):
        '''
        Reset all the node-to-node channels, called at the beginning of each coherent time interval
        '''
        
        # loop over all channel modules
        for chnl_name in self.name_list_all_n2n_chnl:
            # get the object of the channel modules
            chnl_obj = self.get_netelmt(chnl_name)
            
            # reset the channel
            chnl_obj.reset()
            
    def refresh_chnl(self):
        '''
        Refresh all the node-to-node channels, called at the beginning of each coherent time interval
        '''
        
        # loop over all channel modules
        for chnl_name in self.name_list_all_n2n_chnl:
            # get the object of the channel modules
            chnl_obj = self.get_netelmt(chnl_name)
            
            # reset the channel
            chnl_obj.refresh()            

    def operation(self, env):
        '''
        Periodic network operations
        '''
        while True:
            print(self.name + ': Refreshing channel at {}'.format(env.now))
            self.reset_chnl()                               # set channel to be ineffective
            self.refresh_chnl()                             # regenerate channel state information
            yield env.timeout(netcfg.chn_cohr_time_tic)     # wait for next channel coherent time interval
        
    def pre_processing(self):
        '''
        Func: After all the nodes have been created, initialize some parameters, e.g., the distance matrix        
        '''
        # Initialize distance between nodes
        self.ini_dist()
        
        # # Initialize the channels for the network 
        # self.ini_channel()
        
        # # Initialize the channel variance matrix for each of the registered LTE BSs
        # for name_lte_bs in self.list_lte_bs:
            # # first get the object of the LTE BS with given name
            # obj_lte_bs = self.get_netelmt(name_lte_bs)
            
            # # update channel covariance matrix
            # obj_lte_bs.est_chn_cov_from_wifi()
            
        # Initialize GUI
        if netcfg.plot_net == True:
            self.gui = net_gui.new_gui(self)
        
    def ini_channel(self):
        '''
        Func: Generate the channel modules for each pair of the nodes in the network
        '''
        
        # Initialize channel for each node
        for node_name in self.name_list_all_nodes:
            node_obj = self.get_netelmt(node_name)          # Get the object of the node 
            node_obj.ini_channel()                          # Initialize channel
        
                
    def ini_dist(self):
        '''
        Calculate the distance between nodes: row index - first node; column index - second node
        '''
        
        # check if there are nodes in the network
        if self.name_list_all_nodes == []:
            print('Error: There are no nodes in the network.')
            exit(0)        
        
        # Loop over all node names in self.name_list_all_nodes. For each name, calculate the distance to all other nodes
        # including itself. Then, append the obtained array to the distance matrix.
        for node_name in self.name_list_all_nodes:           
            # Obtain the object of the node, and then get the network-wide node index of the node
            node_obj = self.get_netelmt(node_name)
            node_index = node_obj.ntwk_wide_index
            
            # x-, y- and z-axis of current node
            curr_x = self.axis_x[node_index]
            curr_y = self.axis_y[node_index]
            curr_z = self.axis_z[node_index]
            
            # convert x-, y- and z-axis from list to array
            array_axis_x = np.asarray(self.axis_x)
            array_axis_y = np.asarray(self.axis_y)
            array_axis_z = np.asarray(self.axis_z)
            
            # calculate distance 
            curr_dst_array = np.sqrt(np.power(curr_x - array_axis_x, 2) + np.power(curr_y - array_axis_y, 2) + np.power(curr_z - array_axis_z, 2))

            # Update the overall distance matrix
            if self.dist_matrix is None:
                # This is the first row
                self.dist_matrix = curr_dst_array
            else:
                # append the current row to the overall distance matrix
                self.dist_matrix = np.vstack([self.dist_matrix, curr_dst_array])    

        # print(self.dist_matrix)
        # exit(0)
        
    def updt_dist(self):
        '''
        Recalculate distance among nodes
        '''
        self.dist_matrix = None    # First initialize the matrix to None. Otherwise, the new matrix will be appended to the existing one
        self.ini_dist()            # The recalculate the matrix
                                           
    def ping(self):
        '''
        disp network information, only test purpose for now
        '''        
        net_func.netelmt_group.ping(self) 
        
    def set_net_area(self, net_width, net_length, net_height):
        '''
        set the width and length of the network area
        '''
        self.net_width  = net_width
        self.net_length = net_length
        self.net_height = net_height
        print('Network dimension is set to {}x{}x{} in meter.'.format(self.net_width, self.net_length, self.net_height))
        
    def add_node(self, node_type, node_number):
        '''
        add nodes with given type and number of the nodes
        '''  
        # Check if the node type supported
        if node_type not in net_name.node_type_list:
            print('Error: Node type not supported.')
            exit(0)
        
        # Find out the group name corresponding to the node type
        group_name = net_name.node2group.get(node_type)
                        
        # If the network doesn't support this group, add the group to the network
        # and initialize the group to None 
        if hasattr(self, group_name) == False:
            setattr(self, group_name, None)
                
        # If the group hasn't bee created, create it
        if getattr(self, group_name) == None:            
            # Call the function to create the group object, defined in net_node.py
            new_group_obj = net_node.new_group(self, group_name)    
           
            # Update the group object for the network
            setattr(self, group_name, new_group_obj)
           
        # Add new nodes to the group
        new_group_obj.add_node(node_type, node_number)  
            
    def get_node_list(self, node_type):
        '''
        Func: get the list of nodes with type node_type in the network
        node_type: node type
        '''
        # node list initialized to empty
        node_list = []
        
        # Check if the node type supported
        if node_type not in net_name.node_type_list:
            print('Error: Node type not supported.')
            exit(0)                
        
        # Find out the group name corresponding to the node type
        group_name = net_name.node2group.get(node_type)
                        
        # Get the node list
        if hasattr(self, group_name) == False:
            # If there is no such a group, do nothing
            print('Warning: No such node type {}'.format(group_name))                
        else:
            # Otherwise, get the group object
            group_obj = getattr(self, group_name)
            node_list = node_list + group_obj.member
               
        return node_list        

class net_ntwk_dhs(net_ntwk):
    '''
    Class of drone network
    '''
    def __init__(self, net_info):      
        # from base network element
        net_ntwk.__init__(self, net_info)   

        # Transmitter (the first dhs) and receiver (the second dhs)
        # Updated when the dhs are created
        self.tsmt = None
        self.rcvr = None
        
        # Roll, yaw, pitch of receiver with respect to the transmitter
        # Updated in each tick
        self.roll_rel   = 0
        self.pitch_rel  = 0
        self.yaw_rel    = 0
        
        # Initial relative roll, pitch, yaw, initialized before the network runs, updated periodically
        self.roll_rel_ini   = 0
        self.pitch_rel_ini  = 0
        self.yaw_rel_ini    = 0
               
        # Relative coordinates in x-, y-, and z-axis, updated in pre_processing and every tick operation
        self.x_rel = 0
        self.y_rel = 0
        self.z_rel = 0
        
        # Initial relative coordinates, initialized before the network runs, updated periodically
        self.x_rel_ini  = 0
        self.y_rel_ini  = 0
        self.z_rel_ini  = 0    

        # Adjusted relative coordinates since last time beam alignment
        self.x_rel_adj  = 0
        self.y_rel_adj  = 0
        self.z_rel_adj  = 0
        
        # Adjusted gyro (roll, pitch, yaw) coordinates since last time beam alignment
        self.roll_rel_adj   = 0
        self.pitch_rel_adj  = 0
        self.yaw_rel_adj    = 0        
        
        # Distance between transmitter, updated in pre_processing and tick operation
        self.comm_dist = 0
        
        
    def pre_processing(self):
        # pre_processing from parent class
        net_ntwk.pre_processing(self)
        
        # Update initial relative coordinates and roll, pitch, yaw
        self.updt_rel_xyz_ini()
        self.updt_rel_rpy_ini()
                       
        # Update the communication distance between transmitter and receiver
        self.comm_dist =  self.get_comm_dist()
               
        
    def updt_rel_xyz(self):
        '''
        Update relative coordinates of the receiver with respect to the transmitter
        '''
        self.x_rel = self.rcvr.coord_x - self.tsmt.coord_x 
        self.y_rel = self.rcvr.coord_y - self.tsmt.coord_y 
        self.z_rel = self.rcvr.coord_z - self.tsmt.coord_z 
        # print(self.x_rel, self.y_rel, self.z_rel)
        
    def updt_rel_rpy(self):
        '''
        Update relative roll, pitch, yaw
        '''
        self.roll_rel   = self.rcvr.roll  - self.tsmt.roll
        self.pitch_rel  = self.rcvr.pitch - self.tsmt.pitch
        self.yaw_rel    = self.rcvr.yaw   - self.tsmt.yaw   

    def updt_rel_xyz_ini(self):
        '''
        Update initial relative xyz
        '''
        # First update relative coordinates
        self.updt_rel_xyz()     
        
        # Then update the initial
        self.x_rel_ini  = self.x_rel
        self.y_rel_ini  = self.y_rel
        self.z_rel_ini  = self.z_rel       
        
    def updt_rel_rpy_ini(self):
        '''
        Update initial relative rpy
        '''
        # First update relative roll, pitch, yaw
        self.updt_rel_rpy()  
        
        # Then update the initial
        self.roll_rel_ini   = self.roll_rel
        self.pitch_rel_ini  = self.pitch_rel
        self.yaw_rel_ini    = self.yaw_rel
        
    def updt_rel_xyz_adj(self):
        '''
        Update adjusted relative xyz
        '''      
        # Update relative coordinates
        self.updt_rel_xyz()      
        
        # Updated adjusted relative xyz
        self.x_rel_adj  = self.x_rel - self.x_rel_ini
        self.y_rel_adj  = self.y_rel - self.y_rel_ini
        self.z_rel_adj  = self.z_rel - self.z_rel_ini
        
        # print(self.x_rel_adj, self.y_rel_adj, self.z_rel_adj)
        
    def updt_rel_rpy_adj(self):
        '''
        Update adjusted relative rpy
        '''
        # Update relative roll, pitch, yaw
        self.updt_rel_rpy()  
        
        # Updated adjusted relative rpy
        self.roll_rel_adj   = self.roll_rel - self.roll_rel_ini
        self.pitch_rel_adj  = self.pitch_rel - self.pitch_rel_ini
        self.yaw_rel_adj    = self.yaw_rel - self.yaw_rel_ini        
        
    def get_comm_dist(self):
        '''
        Get the communication distance between the transmitter and the receiver
        '''
        # Get the index of the transmitter and receiver
        idx1 = self.tsmt.ntwk_wide_index
        idx2 = self.rcvr.ntwk_wide_index
        
        # print('***', self.comm_dist)
        
        return self.dist_matrix[idx1, idx2]
        
    def updt_tsmt_wavefront(self):
        '''
        Update the wavefront of the transmitter
        '''
        self.tsmt.updt_tsmt_wavefront()
    
    def updt_rcv_area(self):
        '''
        Update the receive area of the receiver
        '''
        self.rcvr.updt_rcv_area()
        
    def get_normalized(self):
        '''
        Get the normalized achievable capacity
        '''
        
        # First, get the overlapping area of the transmit wavefront and the receive antenna surface
        tsmt_polygon = self.tsmt.ant_mdl.polygon
        rcvr_polygon = self.rcvr.ant_mdl.polygon
        ovlp_area = tsmt_polygon.intersection(rcvr_polygon).area
        
        # The total area of the receive antenna
        tot_area = math.pi * math.pow(flytera_cfg.radius, 2)
        
        nmlzd_cap = ovlp_area/tot_area
        
        # print(nmlzd_cap)
        
        return nmlzd_cap
        
    def beam_alignment(self, env, almt_itvl):
        '''
        Periodic beam alignment        
        env: the discrete simulation environment        
        almt_itvl: alignment interval, in ticks
        '''      
        while True:
            
            # Reset relative angle of roll, pitch, and yaw
            self.updt_rel_rpy_ini()
            
            # Reset displacement in x-, y- and z-axis
            self.updt_rel_xyz_ini()
            
            
            yield env.timeout(almt_itvl)           # wait for next interval
            
    def operation(self, env):
        '''
        Periodic network operations
        '''
        while True:
            # print('Network operating...')
            
            # Update adjust relative xyz and rpy
            self.updt_rel_xyz_adj()
            self.updt_rel_rpy_adj()
                                          
            # Update communication distance             
            self.updt_dist()  # First, update distance matrix
            self.comm_dist = self.get_comm_dist()
            # print(self.comm_dist)            
            
            # Update the wavefront of the transmitter
            self.updt_tsmt_wavefront()
            
            # Update the receive area of the receiver
            self.updt_rcv_area()  

            # Calculate the normalized capacity
            nmlzd_cap = self.get_normalized()
            
            if flytera_cfg.sim_index == 0:
                flytera_cfg.sim_time.append(self.tsmt.smpl_itvl * env.now)
                flytera_cfg.data1.append(nmlzd_cap)
                
            if flytera_cfg.sim_index == 1:
                flytera_cfg.data2.append(nmlzd_cap)
                
            if flytera_cfg.sim_index == 2:
                flytera_cfg.data3.append(nmlzd_cap)                
              
            
            # print(self.roll_rel)
            yield env.timeout(1)           # wait for next tick