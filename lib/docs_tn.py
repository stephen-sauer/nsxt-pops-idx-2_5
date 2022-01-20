#!/usr/local/bin/python3
# coding: utf-8
#############################################################################################################################################################################################
#                                                                                                                                                                                           #
# NSX-T Power Operations                                                                                                                                                                    #
#                                                                                                                                                                                           #
# Copyright 2020 VMware, Inc.  All rights reserved				                                                                                                                            #
#                                                                                                                                                                                           #
# The MIT license (the “License”) set forth below applies to all parts of the NSX Power Operations project.  You may not use this file except in compliance with the License.               #
#                                                                                                                                                                                           #
# MIT License                                                                                                                                                                               #
#                                                                                                                                                                                           #
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),                                        #
# to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,                                        #
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:                                                #
#                                                                                                                                                                                           #
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.                                                            #
#                                                                                                                                                                                           #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,                                       #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,                             #
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                #
#                                                                                                                                                                                           #
# *--------------------------------------------------------------------------------------* #                                                                                                #
# **************************************************************************************** #                                                                                                #
#   VMware NSX-T PowerOps by @dominicfoley & @stephensauer                                 #                                                                                                #
#   A day 2 operations tool for helping to document and healthcheck an NSX-T environment   #                                                                                                #
# **************************************************************************************** #                                                                                                #
# *--------------------------------------------------------------------------------------* #                                                                                                #
#                                                                                                                                                                                           #
#############################################################################################################################################################################################
import pathlib, lib.menu
from lib.excel import FillSheet, Workbook, ConditionnalFormat, FillSheetCSV, FillSheetJSON, FillSheetYAML
from lib.system import style, GetAPI, ConnectNSX, os, datetime, GetOutputFormat


def SheetFabTransportNodes(auth_list,WORKBOOK,TN_WS, NSX_Config = {}):

    Dict_TransportNodes = {}     # Dict Transport nodes initialization
    NSX_Config['TransportNodes'] = []
    # Connect to NSX
    SessionNSX = ConnectNSX(auth_list)
    transport_nodes_url = '/api/v1/transport-nodes'
    transport_nodes_json = GetAPI(SessionNSX[0],transport_nodes_url, auth_list)
    transport_nodes = (transport_nodes_json['results'])
    tnode_dict = {}
    
    # Construct Line
    TN_HEADER_ROW = ('Transport Node Type','Display name', 'OS Type', 'OS Version', 'FQDN', 'UUID', 'In Maintenance Mode')
    XLS_Lines = []
    
    
    n = transport_nodes_json['result_count']
    
    pyth = n
    if pyth == 0:
        XLS_Lines.append(["no Transport Nodes", "", "", "", "", "", "", "", ""])
    else:
        for n in range(len(transport_nodes)):       
            tnode_dict = {}
    
            tnode_dict['node_id'] = transport_nodes_json["results"][n]["node_id"]
    
            tnode_dict['maintenance_mode'] = transport_nodes_json["results"][n]["maintenance_mode"]
            # print(transport_nodes_json["results"][n]["node_id"])
            # print(transport_nodes_json["results"][n]["maintenance_mode"])
        
            
            if transport_nodes_json["results"][n]["node_deployment_info"]["resource_type"] == 'HostNode':
            
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["resource_type"])
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["os_type"])
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["os_version"])
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["display_name"])
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["fqdn"])
                tnode_dict['Resource_Type'] = transport_nodes_json["results"][n]["node_deployment_info"]["resource_type"]
                tnode_dict['os_type'] = transport_nodes_json["results"][n]["node_deployment_info"]["os_type"]
                tnode_dict['os_version'] = transport_nodes_json["results"][n]["node_deployment_info"]["os_version"]
                tnode_dict['display_name'] = transport_nodes_json["results"][n]["node_deployment_info"]["display_name"]
                tnode_dict['fqdn'] = transport_nodes_json["results"][n]["node_deployment_info"]["fqdn"]

            else:
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["resource_type"])
            #    print(transport_nodes_json["results"][n]["node_deployment_info"]["display_name"])
                tnode_dict['Resource_Type'] = transport_nodes_json["results"][n]["node_deployment_info"]["resource_type"]
                tnode_dict['os_type'] = 'NA'
                tnode_dict['os_version'] = 'NA'
                tnode_dict['display_name'] = transport_nodes_json["results"][n]["node_deployment_info"]["display_name"]
                tnode_dict['fqdn'] = 'Not Found'

            # Create line
            XLS_Lines.append([tnode_dict['Resource_Type'], tnode_dict['display_name'], tnode_dict['os_type'],tnode_dict['os_version'],tnode_dict['fqdn'], tnode_dict['node_id'],tnode_dict['maintenance_mode']])
            NSX_Config['TransportNodes'].append(tnode_dict)
        

    if GetOutputFormat() == 'CSV':
        CSV = WORKBOOK
        FillSheetCSV(CSV,TN_HEADER_ROW,XLS_Lines)
    elif GetOutputFormat() == 'JSON':
        JSON = WORKBOOK
        FillSheetJSON(JSON, NSX_Config)
    elif GetOutputFormat() == 'YAML':
        YAML = WORKBOOK
        FillSheetYAML(YAML, NSX_Config)
    else:
        FillSheet(WORKBOOK,TN_WS.title,TN_HEADER_ROW,XLS_Lines,"0072BA")
        #ConditionnalFormat(TN_WS, 'K2:K' + str(len(XLS_Lines) + 1), 'poweredOn')
        #ConditionnalFormat(TN_WS, 'L2:L' + str(len(XLS_Lines) + 1), 'false')
        #ConditionnalFormat(TN_WS, 'Q2:Q' + str(len(XLS_Lines) + 1), 'connected')
