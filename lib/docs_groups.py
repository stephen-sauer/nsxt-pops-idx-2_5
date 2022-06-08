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
from lib.excel import FillSheet, Workbook, FillSheetCSV, FillSheetJSON, FillSheetYAML
from lib.system import style, GetAPI, ConnectNSX, os, GetOutputFormat



def SheetSecGrp(auth_list,WORKBOOK,TN_WS, NSX_Config = {}):
    NSX_Config['Groups'] = []
    Dict_Groups = {}

    domain_id = 'default'
    # Connection for get Groups criteria - REST/API
    Groups_list_url = '/policy/api/v1/infra/domains/' + domain_id + '/groups'
    
    SessionNSX = ConnectNSX(auth_list)
    Groups_list_json = GetAPI(SessionNSX[0],Groups_list_url, auth_list)

    XLS_Lines = []
    TN_HEADER_ROW = ('Group Name', "UUID", 'Tags', 'Scope', 'Criteria Type', 'Criteria', 'IP addresses', 'Virtual Machines', 'Segments', 'Segments Ports', 'Path', 'Relative Path')
    
    if isinstance(Groups_list_json, dict) and 'results' in Groups_list_json and Groups_list_json['result_count'] > 0: 
        count = 1
        for group in Groups_list_json['results']:
            print(str(count) + " - Treating NS group: " + style.ORANGE + group['display_name'] + style.NORMAL)
            count += 1 
            # Get Tag and scope
            List_Tag = []
            List_Scope = []
            # Check if tag is in a group
            if "tags" in group:
                for tag in group['tags']:
                    List_Tag.append(tag['tag'])
                    List_Scope.append(tag['scope'])
                Tags = ','.join(List_Tag)
                Scope = ','.join(List_Scope)
            else:
                Tags = ""
                Scope = ""

             #Criteria Treatment
            if group['expression'] == []:
                print('skipping group without expression')
                continue
            for nbcriteria in group['expression']:
                criteria = GetCriteria(SessionNSX[0], auth_list, nbcriteria)

            # Create IP Address List for each group
            IPs_url = '/policy/api/v1/infra/domains/' + domain_id + '/groups/' + group['id'] + '/members/ip-addresses'
            IPs_json = GetAPI(SessionNSX[0],IPs_url, auth_list)
            IP = ""
            if isinstance(IPs_json, dict) and 'results' in IPs_json and 'result_count' in IPs_json and IPs_json['result_count'] > 0:
                IP = ', '.join(IPs_json['results'])

            # Create Virtual Machine List for each group
            VMs_url = '/policy/api/v1/infra/domains/' + domain_id + '/groups/' + group['id'] + '/members/virtual-machines'
            VMs_json = GetAPI(SessionNSX[0],VMs_url, auth_list)
            VM = ""
            VMList =[]
            if isinstance(VMs_json, dict) and 'results' in VMs_json and 'result_count' in VMs_json  and VMs_json['result_count'] > 0:
                for vm in VMs_json['results']:
                    VMList.append(vm['display_name'])
                VM = ', '.join(VMList)

            # Create Segment List for each group
            Segs_url = '/policy/api/v1/infra/domains/' + domain_id + '/groups/' + group['id'] + '/members/segments'
            Segs_json = GetAPI(SessionNSX[0],Segs_url, auth_list)
            Segment = ""
            SegList = []
            if isinstance(Segs_json, dict) and 'results' in Segs_json and 'result_count' in Segs_json and Segs_json['result_count'] > 0:
                for seg in Segs_json['results']:
                    SegList.append(seg['display_name'])
                Segment = ', '.join(SegList)

            # Create Segment Port/vNIC List for each group
            Seg_Ports_url = '/policy/api/v1/infra/domains/' + domain_id + '/groups/' + group['id'] + '/members/segment-ports'
            Seg_Ports_json = GetAPI(SessionNSX[0],Seg_Ports_url, auth_list)
            SegPort = ""
            SegPortList = []
            if isinstance(Seg_Ports_json, dict) and 'results' in Seg_Ports_json and 'result_count' in Seg_Ports_json and Seg_Ports_json['result_count'] > 0:
                for segport in Seg_Ports_json['results']:
                    SegPortList.append(segport['display_name'])
                SegPort = ', '.join(SegPortList)

            Dict_Groups['name'] = group['display_name']
            Dict_Groups['UUID'] = group['unique_id']
            Dict_Groups['tags'] = List_Tag
            Dict_Groups['scope'] = List_Scope
            Dict_Groups['type_crtieria'] = criteria[1]
            Dict_Groups['criteria'] = criteria[0]
            Dict_Groups['ip'] = IP
            Dict_Groups['vm'] = VMList
            Dict_Groups['segment'] = SegList
            Dict_Groups['segment_port'] = SegPortList
            Dict_Groups['path'] = group['path']
            Dict_Groups['rel_path'] = group['relative_path']
            NSX_Config['Groups'].append(Dict_Groups)
            XLS_Lines.append([group['display_name'],group['unique_id'],Tags,Scope,'\n'.join(criteria[1]),criteria[0],IP,VM,Segment,SegPort,group['path'],group['relative_path']])
    else:
        XLS_Lines.append(['No results', "", "", "", "", "", "", "", "", "", "", ""])

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


def GetCriteria(SESSION, auth_list, DictExpression):
    ListReturn = []
    TypeCriteriaList = []
    criteria = ""
    # Dictionary mapping API/REST ressource Type to Type of criteria
    Dict_MAP_Criteria ={
        'IPAddressExpression': 'IP Address',
        'Condition' : 'Membership Criteria',
        'MACAddressExpression': 'MAC Address',
        'ConjunctionOperator': 'conjunction_operator',
        'NestedExpression': 'Nested',
        'PathExpression': 'Members',
        'ExternalIDExpression': 'ExternalIDExpression',
        'IdentityGroupExpression': 'AD Group'
    }
    # Group with operator
    if DictExpression['resource_type'] == 'ConjunctionOperator': 
        criteria = criteria + DictExpression['conjunction_operator']+ "\n"
        TypeCriteriaList.append(DictExpression['conjunction_operator'])
    else:
        TypeCriteriaList.append(Dict_MAP_Criteria[DictExpression['resource_type']])
    # Missing Group with AD -  expression ExternalIDExpression and IdentityGroupExpression
    # Path Expression Group
    if DictExpression['resource_type'] == 'PathExpression':
        for path in DictExpression['paths']:
            Group = GetAPI(SESSION,"/policy/api/v1" + path, auth_list)
            criteria = criteria + Group['resource_type'] + ': ' + Group['display_name'] + '\n'
    # Nested Group - recursive function
    if DictExpression['resource_type'] == 'NestedExpression':
        for expression in DictExpression['expressions']:
            criteria = criteria + GetCriteria(SESSION, auth_list, expression)[0]
    # Mac address Group
    if DictExpression['resource_type'] == 'MACAddressExpression': criteria = criteria + 'MAC: ' + ','.join(DictExpression['mac_addresses'])
    # IP address Group
    if DictExpression['resource_type'] == 'IPAddressExpression': criteria = criteria + 'IP: ' + ','.join(DictExpression['ip_addresses'])
    # Conditionnal Group - Membership
    if DictExpression['resource_type'] == 'Condition':
        criteria = DictExpression['member_type'] + ' with ' + DictExpression['key'].lower() + ' ' + DictExpression['operator'].lower()
        ListTAG = DictExpression['value'].split('|')
        if len(ListTAG) > 1:
            if ListTAG[1] == '': criteria = criteria + ' NoTag scope: ' + ListTAG[0] + '\n'
            elif ListTAG[0] == '': criteria = criteria + ' ' + ListTAG[1] + '\n'
            else: criteria = criteria + ' ' + ListTAG[1] + ' scope ' + ListTAG[0]
        else:
            criteria = criteria + ' ' + ListTAG[0]

    ListReturn = [criteria, TypeCriteriaList]
    return ListReturn

