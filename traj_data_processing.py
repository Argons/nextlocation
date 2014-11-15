# -*- coding: utf-8 -*-
import datetime as dt
import pandas as pd 
import re 
import json
import os
import webbrowser

def clean_traj_data(data_file_name,
                    options = {'date_start': '2014-10-01',
                               'date_end': '2014-10-07',
                               'time_start': '00:00:00',
                               'time_end': '23:59:59',
                               'min_record_num': 200,
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


def plot_traj_on_baidu(data_file_name,
                       options = {'date_start': '2014-10-01',
                                  'date_end': '2014-10-07',
                                  'time_start': '00:00:00',
                                  'time_end': '23:59:59',
                                  'min_record_num': 200,
                                  'weekday': True,
                                  'weekend': True,
                                  'polyline': True},
                       dev_ak='ZsqMjA0ruVar6oDqPnOSLpRH'):
    """
    Plot users' trajectory data on Baidu map.
    """
    
    users_traj = clean_traj_data(data_file_name, options)
    latlngs = [map(lambda x,y: [x,y], list(users_traj[u]['lng']), \
                                      list(users_traj[u]['lat'])) \
               for u in users_traj]
    
    # mark users with different colors
    js_latlngs = 'var data = {"data":' + json.dumps(latlngs) + '}'
    js_file = open('users_traj.js', 'w')
    js_file.write(js_latlngs)
    js_file.close()

    # plot Baidu map on browser
    polyline = "" 
    if options['polyline'] == True: # plot polylines on Baidu map
        polyline = """
            var polyline = new BMap.Polyline(points,{strokeColor:point_color,
                                                     strokeWeight:2,
                                                     strokeOpacity:0.8}); 
            // polyline.setPath(points,{strokeColor:getRandomColor(),strokeWeight:3,strokeOpacity:0.5});
            map.addOverlay(polyline);
        """
    html_script = """
        <!DOCTYPE HTML>
        <html>
        <head>
          <title>User Trajectory Visualization</title>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <meta name="viewport" content="width=device-width, initial-scale=1.0,
                                    maximum-scale=1.0, minimum-scale=1.0, user-scalabe=no">
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
        """ + """
          <script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=%s"></script>
          <script type="text/javascript" src="users_traj.js"></script>
        </head>""" % dev_ak + """
        <body>
            <div id="map"></div>
            <script type="text/javascript">
            var map = new BMap.Map("map", {});                      
            map.centerAndZoom(new BMap.Point(105.000, 38.000), 5);   
            map.enableScrollWheelZoom();
            map.setMapStyle({style:'midnight'});
            if (document.createElement('canvas').getContext) {  
                function getRandomColor() {
                    var letters = '0123456789ABCDEF'.split('');
                    var color = '#';
                    for (var i = 0; i < 6; i++ ) {
                        color += letters[Math.floor(Math.random() * 16)];
                    }
                    return color;
                }
                for (var i = 0; i < data.data.length; i++) {
                    var points = [];
                    for (var j = 0; j < data.data[i].length; j++) {
                      points.push(new BMap.Point(data.data[i][j][0], data.data[i][j][1]));
                    }
                    var point_color = getRandomColor();
                    var options = {
                        size: BMAP_POINT_SIZE_SMALL,
                        shape: BMAP_POINT_SHAPE_CIRCLE,
                        color: point_color
                    }
                    var pointCollection = new BMap.PointCollection(points, options); 
                    pointCollection.addEventListener('click', function (e) {
                      alert(e.point.lng + ',' + e.point.lat);
                    });
                    map.addOverlay(pointCollection);
            """ + polyline + """
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
    options = { 'date_start': '2014-10-01',
                'date_end': '2014-10-07',
                'time_start': '00:00:00',
                'time_end': '23:59:59',
                'min_record_num': 100,
                'weekday': True,
                'weekend': True,
                'polyline': False }
    #plot_traj_on_baidu(data_file_name='043139_1_hdfs_part.txt', options=options)
    pass
