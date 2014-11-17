# -*- coding: utf-8 -*-
"""
Created on Nov 16, 2014
@author: Haishan Wu, Sol
"""

import numpy as np
import pandas as pd
import datetime as dt
import re
import json
import os
import sys
import webbrowser

import convert_coords # convert coordinate system

def clean_gps_data(data_file_name,
                   options = {'date_start': '2014-07-15',
                              'date_end': '2014-11-10',
                              'time_start': '00:00:00',
                              'time_end': '23:59:59',
                              'min_record_num': 300,
                              'weekday': True,
                              'weekend': True}):
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()

    if len(data[0].split('\t')) >= 16:
        return clean_loc_data(data_file_name, options)
    else:
        return clean_traj_data(data_file_name, options)

def plot_gps_data(data_file_name,
                  options = {'date_start': '2014-07-15',
                             'date_end': '2014-11-10',
                             'time_start': '00:00:00',
                             'time_end': '23:59:59',
                             'min_record_num': 300,
                             'weekday': True,
                             'weekend': True,
                             'plot_type': 'traj_lines'}):
    if options['plot_type'] == 'points':
        return plot_points_on_baidu(data_file_name, options)
    if options['plot_type'] == 'heatmap':
        return plot_heatmap_on_google(data_file_name, options)
    if options['plot_type'] == 'traj_points':
        return plot_traj_points_on_baidu(data_file_name, options)
    if options['plot_type'] == 'traj_lines':
        return plot_traj_lines_on_baidu(data_file_name, options)

    
def clean_loc_data(data_file_name,
                   options = {'date_start': '2014-11-02',
                              'date_end': '2014-11-03',
                              'time_start': '00:00:00',
                              'time_end': '23:59:59',
                              'min_record_num': 1,
                              'weekday': True,
                              'weekend': True}):
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()

    traj, users_traj = {}, {}
    for i in xrange(len(data)):
        data[i] = data[i].split('\t')
        if traj.has_key(data[i][0]):
            traj[data[i][0]].append([data[i][1], float(data[i][3]), float(data[i][4])])
        else:
            traj[data[i][0]] = [[pd.to_datetime(data[i][1]), float(data[i][3]), float(data[i][4])]]
            
    col_names = ['time', 'lng', 'lat']
    for u in traj:
        traj[u] = pd.DataFrame(data=traj[u], columns=col_names, dtype=float)
        traj[u] = traj[u].set_index(['time'])
    
    # select set of users that fit options
    if options['weekday'] and not options['weekend']: # only extract traj on weekdays
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time()) &\
                           (traj[u].index.weekday < 5)][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    if not options['weekday'] and options['weekend']: # only extract traj on weekends
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time()) &\
                           (traj[u].index.weekday >= 5)][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    if options['weekday'] and options['weekend']:
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time())][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    return users_traj

    
def plot_points_on_baidu(data_file_name,
                         options = {'date_start': '2014-11-02',
                                    'date_end': '2014-11-03',
                                    'time_start': '00:00:00',
                                    'time_end': '23:59:59',
                                    'min_record_num': 1,
                                    'weekday': True,
                                    'weekend': True,
                                    'plot_type': 'points'}):
    users_traj = clean_gps_data(data_file_name, options)
    latlngs = []   
    for u in users_traj:
        latlngs += map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                          list(users_traj[u]['lat']))
    
    js_latlons = 'var data = {"data":' + json.dumps(latlngs) + ',"total":' + str(len(latlngs)) + '}'
    js_file = open('point_gps.js', 'w')
    js_file.write(js_latlons)
    js_file.close()
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_points_on_baidu.html'
    webbrowser.open(html_file_path)
    return True

    
def plot_heatmap_on_baidu(data_file_name,
                          options = {'date_start': '2014-11-02',
                                     'date_end': '2014-11-03',
                                     'time_start': '00:00:00',
                                     'time_end': '23:59:59',
                                     'min_record_num': 1,
                                     'weekday': True,
                                     'weekend': True,
                                     'plot_type': 'heatmap'}):
    users_traj = clean_gps_data(data_file_name, options)
    latlngs = []   
    for u in users_traj:
        latlngs += map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                          list(users_traj[u]['lat']))
     
    js_file = open('point_heatmap_baidu.js','w')
    js_file.write('var points = [\n')
    for i in range(len(latlngs)-1):
        data_point = '{"lng":' + str(latlngs[i][0]) + ',"lat":' + str(latlngs[i][1]) +',"count":1},\n' 
        js_file.write(data_point)
        
    last_data_point = '{"lng":' + str(latlngs[-1][0]) + ',"lat":' + str(latlngs[-1][1]) +',"count":1}\n' 
    js_file.write(last_data_point)
    js_file.write('];')
    js_file.close();
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_heatmap_on_baidu.html'
    webbrowser.open(html_file_path)
    return True

    
def plot_heatmap_on_google(data_file_name,
                           options = {'date_start': '2014-11-02',
                                      'date_end': '2014-11-03',
                                      'time_start': '00:00:00',
                                      'time_end': '23:59:59',
                                      'min_record_num': 1,
                                      'weekday': True,
                                      'weekend': True,
                                      'plot_type': 'heatmap'}):
    users_traj = clean_gps_data(data_file_name, options)
    latlngs = []   
    for u in users_traj:
        latlngs += map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                          list(users_traj[u]['lat']))
    latlngs = np.array(latlngs)  
    lat_gcj, lng_gcj = convert_coords.bd2gcj(latlngs[:,1],latlngs[:,0])
    
    js_file = open('point_heatmap_google.js','w')
    js_file.write('var taxiData = [\n')
    for i in range(len(lat_gcj)-1):
        data_point = 'new google.maps.LatLng(' + str(lat_gcj[i]) + ',' + str(lng_gcj[i]) +'),\n' 
        js_file.write(data_point)
    last_data_point = 'new google.maps.LatLng(' + str(lat_gcj[-1]) + ',' + str(lng_gcj[-1]) +')\n'
    
    js_file.write(last_data_point)
    js_file.write('];')
    js_file.close();
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_heatmap_on_google.html'
    webbrowser.open(html_file_path)
    return True


def clean_traj_data(data_file_name,
                    options = {'date_start': '2014-10-01',
                               'date_end': '2014-10-07',
                               'time_start': '00:00:00',
                               'time_end': '23:59:59',
                               'min_record_num': 100,
                               'weekday': True,
                               'weekend': True}):
    """
    Clean raw user trajectory data, and return a dictionary of
    individuals' trajectory data of pandas.DataFrame format.
    """
    
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()

    for i in xrange(len(data)):
        data[i] = re.split(r'\t|\x01', data[i])
        if len(data[i]) == 6 and len(data[i][1]) == 0: # 'traj_100_new.txt' format
            a = data[i][2].split('{')
            data[i][2] = a[0] + ']'
            data[i].insert(3, '{'+a[1])
            
    # extract each individual's trajectory data which consists of time_lng_lat
    traj = [[re.findall(r'\d+\.?\d+', j) for j in re.split(r',|\x02', i[2])] for i in data]
    
    col_names = ['time', 'lng', 'lat']
    for i in xrange(len(traj)): 
        traj[i].sort()
        for j in xrange(len(traj[i])):
            traj[i][j][0] = dt.datetime.fromtimestamp(float(traj[i][j][0]))
            traj[i][j] = traj[i][j][0:3] # only keep time_lng_lat part
        traj[i] = pd.DataFrame(data=traj[i], columns=col_names, dtype=float)
        traj[i] = traj[i].set_index(['time'])

    traj = {data[i][0]: traj[i] for i in xrange(len(data))} # user_id as dict keys
    users_traj = {}
    
    # select set of users that fit options
    if options['weekday'] and not options['weekend']: # only extract traj on weekdays
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time()) &\
                           (traj[u].index.weekday < 5)][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    if not options['weekday'] and options['weekend']: # only extract traj on weekends
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time()) &\
                           (traj[u].index.weekday >= 5)][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    if options['weekday'] and options['weekend']:
        for u in traj:
            index_array = [(traj[u].index >= options['date_start']) &\
                           (traj[u].index <= options['date_end']) &\
                           (traj[u].index.time >= pd.to_datetime(options['time_start']).time()) &\
                           (traj[u].index.time <= pd.to_datetime(options['time_end']).time())][0]
            if sum(index_array) >= options['min_record_num']:
                users_traj[u] = traj[u][index_array]
                
    return users_traj


def plot_traj_points_on_baidu(data_file_name,
                              options = {'date_start': '2014-10-01',
                                         'date_end': '2014-10-07',
                                         'time_start': '00:00:00',
                                         'time_end': '23:59:59',
                                         'min_record_num': 100,
                                         'weekday': True,
                                         'weekend': True,
                                         'plot_type': 'traj_points'}):
    users_traj = clean_gps_data(data_file_name, options)
    latlngs = [map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                      list(users_traj[u]['lat'])) \
               for u in users_traj]
    
    # mark users with different colors
    js_latlngs = 'var data = {"data":' + json.dumps(latlngs) + '}'
    js_file = open('users_traj.js', 'w')
    js_file.write(js_latlngs)
    js_file.close()

    # plot Baidu map on browser
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_traj_points_on_baidu.html'
    webbrowser.open(html_file_path)
    return True

def plot_traj_lines_on_baidu(data_file_name,
                             options = {'date_start': '2014-10-01',
                                        'date_end': '2014-10-07',
                                        'time_start': '00:00:00',
                                        'time_end': '23:59:59',
                                        'min_record_num': 100,
                                        'weekday': True,
                                        'weekend': True,
                                        'plot_type': 'traj_lines'}):
    """
    Plot users' trajectory data on Baidu map.
    """
    
    users_traj = clean_gps_data(data_file_name, options)
    latlngs = [map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                      list(users_traj[u]['lat'])) \
               for u in users_traj]
    
    # mark users with different colors
    js_latlngs = 'var data = {"data":' + json.dumps(latlngs) + '}'
    js_file = open('users_traj.js', 'w')
    js_file.write(js_latlngs)
    js_file.close()

    # plot Baidu map on browser
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_traj_lines_on_baidu.html'
    webbrowser.open(html_file_path)
    return True
    

if __name__ == '__main__':
    if len(sys.argv) == 1:
        data_file_name = './1103_1900_android_beijing.txt'
    else:
        data_file_name = sys.argv[1]

    options = {'date_start': '2014-10-01',
               'date_end': '2014-10-07',
               'time_start': '00:00:00',
               'time_end': '23:59:59',
               'min_record_num': 100,
               'weekday': True,
               'weekend': True,
               'plot_type': 'traj_lines'}
    #users_traj = clean_gps_data(data_file_name, options)
    #plot_gps_data(data_file_name, options)
