# -*- coding: utf-8 -*-
"""
Created on Nov 16, 2014
@author: Haishan Wu
"""

import numpy as np

def wgs2gcj(wgsLat, wgsLon):
    a = 6378245.0
    f = 0.00335233
    b = a * (1 - f)
    ee = (a*a - b*b)/(a*a)
    
    if outofChina(wgsLat,wgsLon):
        return wgsLat, wgsLon
    dLat = transformLat(wgsLon - 105.0, wgsLat - 35.0)
    dLon = transformLon(wgsLon - 105.0, wgsLat - 35.0)
    radLat = wgsLat/180.0 * np.pi
    magic =  np.sin(radLat)
    magic  = 1 - ee*magic*magic
    sqrtMagic = np.sqrt(magic)
    dLat = (dLat * 180.0)/((a * (1-ee)) / (magic*sqrtMagic) * np.pi)
    dLon = (dLon * 180.0)/(a/sqrtMagic * np.cos(radLat) * np.pi)
    gcjLat = wgsLat + dLat
    gcjLon = wgsLon + dLon
    return gcjLat, gcjLon
    
def outofChina(lat, lon):
    if lon < 72.004 or lon > 137.8347: return True
    if lat < 0.8293 or lat > 55.8271:  return True
    return False
        
def transformLat(x, y):
    ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.abs(x))
    ret = ret + (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
    ret = ret + (20.0 * np.sin(y * np.pi) + 40.0 * np.sin(y / 3.0 * np.pi)) * 2.0 / 3.0
    ret = ret + (160.0 * np.sin(y / 12.0 * np.pi) + 320.0 * np.sin(y * np.pi / 30.0)) * 2.0 / 3.0
    return ret

def transformLon(x, y):
    ret = 300.0 + x + 2.0 * y + 0.1 * x * x +  0.1 * x * y + 0.1 * np.sqrt(abs(x))
    ret = ret + (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
    ret = ret + (20.0 * np.sin(x * np.pi) + 40.0 * np.sin(x / 3.0 * np.pi)) * 2.0 / 3.0
    ret = ret + (150.0 * np.sin(x / 12.0 * np.pi) + 300.0 * np.sin(x * np.pi / 30.0)) * 2.0 / 3.0
    return ret
    
def gcj2wgs(gcjLat, gcjLon):
    g0 = np.hstack([gcjLat, gcjLon])
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

def gcj2bd(gcjLat, gcjLon):
    z = np.sqrt(np.power(gcjLat,2) + np.power(gcjLon,2)) + 0.00002 * np.sin(gcjLat * np.pi * 3000.0/180.0)
    theta = np.arctan2(gcjLat,gcjLon) + 0.000003 * np.cos(gcjLon * np.pi * 3000.0/180.0)
    bdLon = z * np.cos(theta) + 0.0065
    bdLat = z * np.sin(theta) + 0.006
    return bdLat, bdLon

def bd2gcj(bdLat, bdLon):
    x = bdLon - 0.0065
    y = bdLat - 0.006
    z = np.sqrt(np.power(x,2) + np.power(y,2)) - 0.00002 * np.sin(y * np.pi * 3000.0/180.0)
    theta = np.arctan2(y,x) - 0.000003 * np.cos(x * np.pi *3000.0/180.0)
    gcjLon = z * np.cos(theta)
    gcjLat = z * np.sin(theta)
    return gcjLat, gcjLon
    
def wgs2bd(wgsLat, wgsLon):
    gcjLat, gcjLon = wgs2gcj(wgsLat, wgsLon)
    return gcj2bd(gcjLat, gcjLon)
    
def bd2wgs(bdLat, bdLon):
    gcjLat,gcjLon = bd2gcj(bdLat, bdLon)
    return gcj2wgs(gcjLat, gcjLon)
