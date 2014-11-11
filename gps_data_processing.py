# -*- coding: utf-8 -*-
"""
Created on Sun Nov  2 21:39:50 2014

@author: haishanwu
"""

import numpy as np
import math
import webbrowser
import re #in case of multiple tabs
import json
import os
import sys
import datetime
import random

a = 6378245.0
f = 0.00335233
b = a * (1 - f)
ee = (a*a - b*b)/(a*a)

def wgs2gcj(wgsLat,wgsLon):
    if outofChina(wgsLat,wgsLon):
        return wgsLat,wgsLon
    dLat = transformLat(wgsLon - 105.0, wgsLat - 35.0)
    dLon = transformLon(wgsLon - 105.0, wgsLat - 35.0)
    radLat = wgsLat/180.0 * math.pi
    magic =  np.sin(radLat)
    magic  = 1 - ee*magic*magic
    sqrtMagic = np.sqrt(magic)
    dLat = (dLat * 180.0)/((a * (1-ee)) / (magic*sqrtMagic) * math.pi)
    dLon = (dLon * 180.0)/(a/sqrtMagic * np.cos(radLat) * math.pi)
    gcjLat = wgsLat + dLat
    gcjLon = wgsLon + dLon
    return gcjLat,gcjLon
    
def outofChina(lat,lon):
    if lon < 72.004 or lon >137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False
        
def transformLat(x,y):
      ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.abs(x))
      ret = ret + (20.0 * np.sin(6.0 * x * math.pi) + 20.0 * np.sin(2.0 * x * math.pi)) * 2.0 / 3.0
      ret = ret + (20.0 * np.sin(y * math.pi) + 40.0 * np.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
      ret = ret + (160.0 * np.sin(y / 12.0 * math.pi) + 320.0 * np.sin(y * math.pi / 30.0)) * 2.0 / 3.0
      return ret

def transformLon(x,y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x +  0.1 * x * y + 0.1 * np.sqrt(abs(x))
    ret = ret + (20.0 * np.sin(6.0 * x * math.pi) + 20.0 * np.sin(2.0 * x * math.pi)) * 2.0 / 3.0
    ret = ret + (20.0 * np.sin(x * math.pi) + 40.0 * np.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
    ret = ret + (150.0 * np.sin(x / 12.0 * math.pi) + 300.0 * np.sin(x * math.pi / 30.0)) * 2.0 / 3.0
    return ret
    
def gcj2wgs(gcjLat,gcjLon):
    g0 = np.hstack([gcjLat,gcjLon])
    w0 = g0
    if len(w0.shape)==1:
        g1Lat,g1Lon = wgs2gcj(w0[0],w0[1])
    else:
        g1Lat,g1Lon = wgs2gcj(w0[:,0],w0[:,1])
    g1 = np.hstack([g1Lat, g1Lon])
    w1 = w0 - (g1 - g0)
    while np.abs(w1 - w0).max() >= 1e-6:
        w0 = w1
        if len(w0.shape)==1:
            g1Lat, g1Lon = wgs2gcj(w0[0],w0[1])
        else:
            g1Lat, g1Lon = wgs2gcj(w0[:,0],w0[:,1])
        g1 = np.hstack([g1Lat,g1Lon])
        w1 = w0 - (g1 - g0)
    if len(w1.shape)==1:
        return w1[0], w1[1]
    else:    
        return w1[:,0], w1[:,1]

def gcj2bd(gcjLat,gcjLon):
    z = np.sqrt(np.power(gcjLat,2) + np.power(gcjLon,2)) + 0.00002 * np.sin(gcjLat * math.pi * 3000.0/180.0)
    theta = np.arctan2(gcjLat,gcjLon) + 0.000003 * np.cos(gcjLon * math.pi * 3000.0/180.0)
    bdLon = z * np.cos(theta) + 0.0065
    bdLat = z * np.sin(theta) + 0.006
    return bdLat,bdLon

def bd2gcj(bdLat,bdLon):
    x = bdLon - 0.0065
    y = bdLat - 0.006
    z = np.sqrt(np.power(x,2) + np.power(y,2)) - 0.00002 * np.sin(y * math.pi * 3000.0/180.0)
    theta = np.arctan2(y,x) - 0.000003 * np.cos(x * math.pi *3000.0/180.0)
    gcjLon = z * np.cos(theta)
    gcjLat = z * np.sin(theta)
    return gcjLat,gcjLon
    
def wgs2bd(wgsLat,wgsLon):
    gcjLat, gcjLon = wgs2gcj(wgsLat,wgsLon)
    return gcj2bd(gcjLat,gcjLon)
    
def bd2wgs(bdLat,bdLon):
    gcjLat,gcjLon = bd2gcj(bdLat,bdLon)
    return gcj2wgs(gcjLat,gcjLon)

def read_gps_data(data_file_name):
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()
    latlon = [[float(re.split(r'\t+',i)[3]),float(re.split(r'\t+',i)[4])] for i in data[0:50000]]
    return latlon
    
def plot_point_on_baidu(latlon): 
    js_latlons = 'var data = {"data":' + json.dumps(latlon) + ',"total":' + str(len(latlon)) + '}'
    js_file = open('point_gps.js', 'w')
    js_file.write(js_latlons)
    js_file.close()
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_point_on_baidu.html'
    webbrowser.open(html_file_path)
    return True
    
def plot_heatmap_on_baidu(latlon):
    js_file = open('point_heatmap_baidu.js','w')
    js_file.write('var points = [\n')
    for i in range(len(latlon)-1):
        data_point = '{"lng":' + str(latlon[i][0]) + ',"lat":' + str(latlon[i][1]) +',"count":1},\n' 
        js_file.write(data_point)
        
    last_data_point = '{"lng":' + str(latlon[-1][0]) + ',"lat":' + str(latlon[-1][1]) +',"count":1}\n' 
    js_file.write(last_data_point)
    js_file.write('];')
    js_file.close();
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_heatmap_on_baidu.html'
    webbrowser.open(html_file_path)
    return True
    
    
def plot_heatmap_on_google(latlon):
    latlon = np.array(latlon)
    lat_gcj, lon_gcj = bd2gcj(latlon[:,1],latlon[:,0])#convert BD-09 to GCJ-02
    
    js_file = open('point_heatmap_google.js','w')
    js_file.write('var taxiData = [\n')
    for i in range(len(lat_gcj)-1):
        data_point = 'new google.maps.LatLng(' + str(lat_gcj[i]) + ',' + str(lon_gcj[i]) +'),\n' 
        js_file.write(data_point)
    last_data_point = 'new google.maps.LatLng(' + str(lat_gcj[-1]) + ',' + str(lon_gcj[-1]) +')\n'  
    js_file.write(last_data_point)
    js_file.write('];')
    js_file.close();
    html_file_path = 'file://' + os.getcwd() + '/' + 'plot_heatmap_on_google.html'
    webbrowser.open(html_file_path)


def clean_traj_data(data_file_name):
    # raw data
    f = open(data_file_name, 'r')
    data = f.readlines()
    f.close()

    # data cleaning
    for i in xrange(len(data)):
        data[i] = data[i].split()
        if len(data[i]) == 8:
            data[i][2] += data[i][3] + data[i][4]
            data[i].pop(3)
            data[i].pop(3)
        if len(data[i]) == 7:
            data[i][2] += data[i][3]
            data[i].pop(3)
        if len(data[i]) == 5:
            a = data[i][1].split('{')
            data[i][1] = a[0] + ']'
            data[i].insert(2, '{'+a[1])

    traj = [i[1].split(',') for i in data]
    uids = [i[0] for i in data]
    latlons = [[[float(j.split('_')[1]), float(j.split('_')[2])] for j in i] for i in traj]
    time = [[j.split('_')[0][1:] for j in i] for i in traj]
    for i in xrange(len(time)): time[i][0] = time[i][0][1:]
    time = [[datetime.datetime.fromtimestamp(int(j)).strftime('%Y-%m-%d %H:%M:%S') for j in i] for i in time]
    return latlons

def plot_traj_on_baidu(data_file_name):
    """
    generate Baidu map using user trajectory data.
    """
    latlons = clean_traj_data(data_file_name)
    
    # mark users with different colors
    js_latlons = 'var data = {"data":' + json.dumps(latlons) + '}'
    js_file = open('users_traj.js', 'w')
    js_file.write(js_latlons)
    js_file.close()

    # generate Baidu map html code 
    html_script = """
        <!DOCTYPE HTML>
        <html>
        <head>
          <title>加载海量点</title>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalabe=no">
          <style type="text/css">
            html,body{
                margin:0;
                width:100%;
                height:100%;
                background:#ffffff;
            }
            #map{
                width:100%;
                height:100%;
            }
            #panel {
                position: absolute;
                top:30px;
                left:10px;
                z-index: 999;
                color: #fff;
            }
            #login{
                position:absolute;
                width:300px;
                height:40px;
                left:50%;
                top:50%;
                margin:-40px 0 0 -150px;
            }
            #login input[type=password]{
                width:200px;
                height:30px;
                padding:3px;
                line-height:30px;
                border:1px solid #000;
            }
            #login input[type=submit]{
                width:80px;
                height:38px;
                display:inline-block;
                line-height:38px;
            }
          </style>
          <script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=ZsqMjA0ruVar6oDqPnOSLpRH"></script>
          <script type="text/javascript" src="users_traj.js"></script>
        </head>
        <body>
            <div id="map"></div>
            <script type="text/javascript">
            var map = new BMap.Map("map", {});                        // 创建Map实例
            map.centerAndZoom(new BMap.Point(105.000, 38.000), 5);     // 初始化地图,设置中心点坐标和地图级别
            map.enableScrollWheelZoom();
            function getRandomColor() {
                var letters = '0123456789ABCDEF'.split('');
                var color = '#';
                for (var i = 0; i < 6; i++ ) {
                    color += letters[Math.floor(Math.random() * 16)];
                }
                return color;
            }
            if (document.createElement('canvas').getContext) {  // 判断当前浏览器是否支持绘制海量点
                for (var i = 0; i < data.data.length; i++) {
                    var points = [];
                    for (var j = 0; j < data.data[i].length; j++) {
                      points.push(new BMap.Point(data.data[i][j][0], data.data[i][j][1]));
                    }
                    var options = {
                        size: BMAP_POINT_SIZE_SMALL,
                        shape: BMAP_POINT_SHAPE_CIRCLE,
                        color: getRandomColor()
                    }
                    var pointCollection = new BMap.PointCollection(points, options);  // 初始化PointCollection
                    pointCollection.addEventListener('click', function (e) {
                      alert(e.point.lng + ',' + e.point.lat);
                    });
                    map.addOverlay(pointCollection);
                }
            } else {
                alert('请在chrome、safari、IE8+以上浏览器查看本示例');
            }
          </script>
        </body>
        </html>
    """
    html_file = open('BaiduMap.html', 'w')
    html_file.write(html_script)
    html_file.close()
    html_file_path = 'file://' + os.getcwd() + '/' + 'BaiduMap.html'
    webbrowser.open(html_file_path)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        data_file_name = './1102_1900_android_beijing.txt'
    else:
        data_file_name = sys.argv[1]
    #latlon = read_gps_data(data_file_name)
    #plot_point_on_baidu(latlon)
    #plot_heatmap_on_google(latlon)
    
