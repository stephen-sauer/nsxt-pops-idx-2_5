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
from lib.excel import FillSheet, FillSheetCSV, Workbook, FillSheetCSV, FillSheetJSON, FillSheetYAML
from lib.system import style, GetAPI, ConnectNSX, os, GetOutputFormat


def SheetSecRulesSec(auth_list, WORKBOOK,TN_WS, NSX_Config = {}):
    NSX_Config['Policies'] = []
    NSX_Config['Sections'] = []
    NSX_Config['Apply'] = []
    Dict_Policies = {}
    Dict_Sections = {}
    Dict_Apply = {}
    Dict_Tags = {}
    # connection to NSX
    SessionNSX = ConnectNSX(auth_list)
    sections_json = GetAPI(SessionNSX[0],'/api/v1/firewall/sections', auth_list)
    policies_json = GetAPI(SessionNSX[0],'/policy/api/v1/infra/domains/default/security-policies', auth_list)
    # Header of Excel and initialization of lines
    XLS_Lines = []
    XLS_Lines2 = []  
    """  
    TN_HEADER_ROW = ('Section ID', 'Section Name', 'Resource Type','Section Type', 'Enforced On', 'is Stateful', 'Rules per Section' , 'Apply To' , 'Tags')
    if isinstance(sections_json, dict) and 'results' in sections_json and sections_json['result_count'] > 0: 
        for section in sections_json["results"]:
            print ("----------------------------------------------------------")
            print ("Section: ", section['display_name'])
            Dict_Sections['id'] = section['id']
            Dict_Sections['name'] =  section['display_name']
            Dict_Sections['resource'] = section['resource_type']
            Dict_Sections['section'] = section['section_type']
            Dict_Sections['enforced_on'] = section['enforced_on']
            Dict_Sections['stateful'] = section['stateful']
            Dict_Sections['numrules'] = section['rule_count']
            Dict_Sections['Apply_To'] = "Apply Target(s):"
            Dict_Sections['taglist'] = "Tag(s):"
            if 'applied_tos' in section:
                print ("-- Applied_To Exists")
                for applied in section["applied_tos"]:
                    Dict_Apply['target_id'] = applied['target_id']
                    Dict_Apply['target_display_name'] = applied['target_display_name']
                    Dict_Apply['target_type'] = applied['target_type']
                    applyto = (applied['target_type']+" : Name "+applied['target_display_name']+" -- ")
                    Dict_Sections['Apply_To'] = Dict_Sections['Apply_To']+" To "+applyto
                ##    NSX_Config['Apply'].append(Dict_Apply)
                ##    print ("---- Apply Target " , applied['target_id'])
                ##    print ("---- Apply Target " , applied['target_display_name'])  
                    print (Dict_Sections['Apply_To'])
            else:
                print ("-- Applied_To DFW")
                Dict_Apply['target_id'] = "----"
                Dict_Apply['target_display_name'] = "Applied to DFW"
                Dict_Apply['target_type'] = "Global"
                ## NSX_Config['Apply'].append(Dict_Apply)
                Dict_Sections['Apply_To'] = Dict_Sections['Apply_To']+" DFW "
            if 'tags' in section:
                print ("-- Tag Exists")
                for tags in section["tags"]:
                    Dict_Tags['tag'] = tags['tag']
                    Dict_Tags['scope'] = tags['scope']
                    print ("---- Tag: " , tags['tag'] , " Scope: " , tags['scope'])
                    taglist = (tags['tag']+" Scope: "+tags['scope']+" -- ")
                    Dict_Sections['taglist'] = Dict_Sections['taglist']+" Tag: "+taglist
                ##    NSX_Config['Apply'].append(Dict_Apply)
                ##    print ("---- Apply Target " , applied['target_id'])
                ##    print ("---- Apply Target " , applied['target_display_name'])  
                    print (Dict_Sections['taglist'])
            else:
                print ("No Tag to this section")

            NSX_Config['Sections'].append(Dict_Sections)
            XLS_Lines.append([section['id'], section['display_name'], section['resource_type'],section['section_type'],section['enforced_on'],section['stateful'],section['rule_count'],Dict_Sections['Apply_To'],Dict_Sections['taglist']])
    else:
        XLS_Lines.append(['No results', "", "", "", "", ""])    
    
    if isinstance(policies_json, dict) and 'results' in policies_json and policies_json['result_count'] > 0: 
        for policy in policies_json["results"]:
            Dict_Policies['id'] = policy['id']
            Dict_Policies['name'] =  policy['display_name']
            Dict_Policies['path'] = policy['path']
            Dict_Policies['sequence_number'] = policy['sequence_number']
            Dict_Policies['category'] = policy['category']
            Dict_Policies['stateful'] = policy['stateful']
            NSX_Config['Policies'].append(Dict_Policies)
            XLS_Lines.append([policy['id'], policy['display_name'], policy['path'], policy['sequence_number'], policy['category'], policy['stateful']])
    else:
        XLS_Lines.append(['No results', "", "", "", "", "" , "" , ""])
    
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
    """
## FW Rules per Section 
    TN_HEADER_ROW2 = ('Section ID', 'Section Name', 'Resource Type','Section Type', 'Enforced On', 'is Stateful', 'Rules per Section' , 'Apply To' , 'Tags', 'Rule name' , 'json rule')
    if isinstance(sections_json, dict) and 'results' in sections_json and sections_json['result_count'] > 0: 
        for section in sections_json["results"]:
            print ("----------------------------------------------------------")
            print ("Section: ", section['display_name'])
            print ("Enforced: ", section['enforced_on'])
            Dict_Sections['id'] = section['id']
            Dict_Sections['name'] =  section['display_name']
            Dict_Sections['resource'] = section['resource_type']
            Dict_Sections['section'] = section['section_type']
            Dict_Sections['enforced_on'] = section['enforced_on']
            Dict_Sections['stateful'] = section['stateful']
            enforced = section['enforced_on']            
            Dict_Sections['numrules'] = section['rule_count']
            Dict_Sections['Apply_To'] = "Apply Target(s):"
            Dict_Sections['taglist'] = "Tag(s):"

            if 'applied_tos' in section:
                print ("-- Applied_To Exists")
                for applied in section["applied_tos"]:
                    Dict_Apply['target_id'] = applied['target_id']
                    Dict_Apply['target_display_name'] = applied['target_display_name']
                    Dict_Apply['target_type'] = applied['target_type']
                    applyto = (applied['target_type']+" : Name "+applied['target_display_name']+" -- ")
                    Dict_Sections['Apply_To'] = Dict_Sections['Apply_To']+" To "+applyto
                ##    NSX_Config['Apply'].append(Dict_Apply)
                ##    print ("---- Apply Target " , applied['target_id'])
                ##    print ("---- Apply Target " , applied['target_display_name'])  
                    print (Dict_Sections['Apply_To'])
            else:
                print ("-- Applied_To DFW")
                Dict_Apply['target_id'] = "----"
                Dict_Apply['target_display_name'] = "Applied to DFW"
                Dict_Apply['target_type'] = "Global"
                ## NSX_Config['Apply'].append(Dict_Apply)
                Dict_Sections['Apply_To'] = Dict_Sections['Apply_To']+" DFW "
            if 'tags' in section:
                print ("-- Tag Exists")
                for tags in section["tags"]:
                    Dict_Tags['tag'] = tags['tag']
                    Dict_Tags['scope'] = tags['scope']
                    print ("---- Tag: " , tags['tag'] , " Scope: " , tags['scope'])
                    taglist = (tags['tag']+" Scope: "+tags['scope']+" -- ")
                    Dict_Sections['taglist'] = Dict_Sections['taglist']+" Tag: "+taglist
                ##    NSX_Config['Apply'].append(Dict_Apply)
                ##    print ("---- Apply Target " , applied['target_id'])
                ##    print ("---- Apply Target " , applied['target_display_name'])  
                    print (Dict_Sections['taglist'])
            else:
                print ("No Tag to this section")

            NSX_Config['Sections'].append(Dict_Sections)             
            if enforced == "VIF" :
                print ("-- FW Rules in VIF section")
                print (section["id"])
                
                ## SessionNSX = ConnectNSX(auth_list)
                dfwpersection_json = GetAPI(SessionNSX[0],'/api/v1/firewall/sections/'+section['id']+'/rules', auth_list)
                print (dfwpersection_json)
                if isinstance(dfwpersection_json, dict) and 'results' in dfwpersection_json and dfwpersection_json['result_count'] > 0:
                    for dfwpersec in dfwpersection_json["results"]:
                        Dict_Apply['dfw_name'] = dfwpersec['display_name']
                        print (Dict_Apply['dfw_name']," ---------")
                        print (dfwpersec)
                        XLS_Lines2.append([section['id'], section['display_name'], section['resource_type'],section['section_type'],section['enforced_on'],section['stateful'],section['rule_count'],Dict_Sections['Apply_To'],Dict_Sections['taglist'],dfwpersec['display_name'],dfwpersec])
            else:
                print ("-- Not associated to VIF or no rule")
    if GetOutputFormat() == 'CSV':
        CSV2 = WORKBOOK
        FillSheetCSV(CSV2,TN_HEADER_ROW2,XLS_Lines2)
