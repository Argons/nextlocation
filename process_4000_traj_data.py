# -*- coding: utf-8 -*-
import webbrowser
import re 
import json
import os
import sys
import datetime as dt

def clean_traj_data(data_file_name='traj_100000.txt',
                    time_start="2014-07-01 00:00:01", 
                    time_end="2014-10-16 23:59:59",
                    records_num_limit=500,
                    daily_records_num_limit=10):
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()

    for i in xrange(len(data)): data[i] = data[i].split('\t')
    traj = [[re.findall(r'\d+.\d+', j) for j in i[2].split(',')] for i in data]
    for i in xrange(len(traj)): traj[i].sort()
    for i in xrange(len(traj)):
        for j in xrange(len(traj[i])):
            traj[i][j][0] = dt.datetime.fromtimestamp(float(traj[i][j][0])).strftime('%Y-%m-%d %H:%M:%S')
    
    #uids = [i[0] for i in data]
    #latlons = [[j[1:] for j in i] for i in traj]
    #time = [[j[0] for j in i] for i in traj]
    #time = [[datetime.datetime.fromtimestamp(float(j)).strftime('%Y-%m-%d %H:%M:%S') for j in i] for i in time]

    # choose users with high data density: records number within time length > records_num_limit
    traj = [[j for j in i if j[0] >= time_start and j[0] <= time_end] \
            for i in traj if len(i)>records_num_limit]
    traj = [i for i in traj if len(i)>=records_num_limit]
    latlons = [[j[1:] for j in i] for i in traj]
    time = [[j[0] for j in i] for i in traj]
    return latlons


def plot_traj_on_baidu(data_file_name='traj_100000.txt', 
                       time_start="2014-07-01 00:00:01", 
                       time_end="2014-10-16 23:59:59", 
                       records_num_limit=500,
                       dev_ak='ZsqMjA0ruVar6oDqPnOSLpRH'):
    """
    generate Baidu map using user trajectory data.
    """
    latlons = clean_traj_data(data_file_name, time_start, time_end, records_num_limit)
    
    # mark users with different colors
    js_latlons = 'var data = {"data":' + json.dumps(latlons) + '}'
    js_file = open('users_traj.js', 'w')
    js_file.write(js_latlons)
    js_file.close()

    # plot Baidu map on browser
    html_file_path = 'file://' + os.getcwd() + '/' + 'BaiduMap.html'
    webbrowser.open(html_file_path)

if __name__ == '__main__':
    #plot_traj_on_baidu(time_start='2014-10-01',time_end='2014-10-08',records_num_limit=100)



