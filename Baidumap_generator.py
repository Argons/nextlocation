# -*- coding: utf-8 -*-
import datetime
import json
import random

def clean_traj_data(data_file_name='traj_100_new.txt'):
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
    for i in xrange(len(time)):
        time[i][0] = time[i][0][1:]
    time = [[datetime.datetime.fromtimestamp(int(j)).strftime('%Y-%m-%d %H:%M:%S') for j in i] for i in time]
    return latlons

def plot_traj_on_baidu(data_file_name, dev_ak='ZsqMjA0ruVar6oDqPnOSLpRH'):
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
    js_pointcollections = """
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
    """
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
        """ + """
          <script type="text/javascript" src="http://api.map.baidu.com/api?v=2.0&ak=%s"></script>
          <script type="text/javascript" src="%s"></script>
        </head>""" % (dev_ak, js_file.name) + """
        <body>
            <div id="map"></div>
            <script type="text/javascript">
            var map = new BMap.Map("map", {});                        // 创建Map实例
            map.centerAndZoom(new BMap.Point(105.000, 38.000), 5);     // 初始化地图,设置中心点坐标和地图级别
            map.enableScrollWheelZoom();                        //启用滚轮放大缩小
            if (document.createElement('canvas').getContext) {  // 判断当前浏览器是否支持绘制海量点
        """ + js_pointcollections + """
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


time_label = """
    var point = new BMap.Point(116.417854,39.921988);
    map.centerAndZoom(point, 15);
    var opts = {
      position : point,    // 指定文本标注所在的地理位置
      offset   : new BMap.Size(30, -30)    //设置文本偏移量
    }
    var label = new BMap.Label("欢迎使用百度地图，这是一个简单的文本标注哦~", opts);  // 创建文本标注对象
            label.setStyle({
                     color : "red",
                     fontSize : "12px",
                     height : "20px",
                     lineHeight : "20px",
                     fontFamily:"微软雅黑"
             });
    map.addOverlay(label);     
    """

if __name__ == "__main__":
    pass

