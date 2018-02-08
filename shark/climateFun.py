# -*- coding: utf-8 -*-
"""
Created on Fri Nov 17 13:21:59 2017

@author: Astrid
"""
from shark import supp
import pandas as pd
import os
import numpy as np
import math as m

def extractClimateYears(path_climate, year_start, years, number, path_save=None, exclude=list()):
    climateparam_list = supp.getFileList(path_climate, '.ccd')[0]
    # remove climate parameters from exclude
    for e in exclude:
        climateparam_list.remove(e+'.ccd')
    # extract years of eacht climate parameter
    row_start = int(365*24*(year_start-1))
    row_end = int(365*24*years + row_start)
    if path_save == None:
        clim=pd.DataFrame()
    for c in climateparam_list:
        # read ccd file
        value = supp.readccd(os.path.join(path_climate,c))
        value = value[row_start:row_end]
        if path_save != None:
            # save ccd file
            if number != None:
                supp.saveccd(os.path.join(path_save,'%03i_%s' %(number,c)), value)
            else:
                supp.saveccd(os.path.join(path_save,'%s' % c), value)
        else:
            clim[c.replace('.ccd','')] = value
    if path_save == None:
        return clim

def calcIntClimateEN13788(path_climate, load, number, path_save=None):
    # Load exterior climate temperature and relative humidity
    Te = supp.readccd(path_climate+'Temperature.ccd')
    RHe = supp.readccd(path_climate+'RelativeHumidity.ccd')
    # Convert relative humidity to unit
    if all(rh > 1 for rh in RHe): RHe = [rh/100 for rh in RHe]
    # Calculate daily mean exterior temperature
    Te_dmean = list()
    for i in range(int(len(Te)/24)):
        Te_day = Te[i*24:(i+1)*24]
        Te_dmean.extend([np.mean(Te_day)]*24)
    # Calculate monthly mean exterior temperature and relative humidity
    Te_mmean = list()
    RHe_mmean = list()
    years = int(len(Te)/24/365)
    months = int(years*12)
    hours = int(len(Te)/months)
    for i in range(int(months)):
        s1,s2 = i*hours, (i+1)*hours
        Te_month = Te[s1:s2]
        Te_mmean.extend([np.mean(Te_month)]*hours)
        RHe_month = RHe[s1:s2]
        RHe_mmean.extend([np.mean(RHe_month)]*hours)
    # Exterior saturated vapour pressure (based on monthly mean exterior temperature)
    pve_sat = list()
    for i in range(len(Te_mmean)):
        if Te_mmean[i] > 0:
            p = 611*m.exp((17.08*Te_mmean[i])/(234.18+Te_mmean[i])) # Pa
            pve_sat.append(p) # Pa
        else:
            p = 611*m.exp((22.44*Te_mmean[i])/(272.44+Te_mmean[i])) # Pa
            pve_sat.append(p) # Pa
    # Exterior vapour pressure (monthly mean)
    pve = [RHe[i]*pve_sat[i] for i in range(len(RHe))] # Pa
    # Calculate interior climate
    # Interior temperature
    Ti = list()
    for i in range(len(Te_mmean)):
        if Te_mmean[i] < 10:
            Ti.append(20)
        elif Te_mmean[i] > 20:
            Ti.append(25)
        else:
            Ti.append(0.5*Te_mmean[i]+15)
    # Interior relative humidity
    if load == 1:
        a,b = 270,27/2
    elif load == 2:
        a,b = 540,27
    elif load == 3:
        a,b = 810,81/2
    elif load == 4:
        a,b = 1080,54
    else:
        print('Error: wrong interior humidity class')
    pvi_d = list()
    for i in range(len(Te_mmean)):
        if Te_mmean[i] < 0:
            pvi_d.append(a)
        elif Te_mmean[i] > 20:
            pvi_d.append(0)
        else:
            pvi_d.append(-b*Te_mmean[i]+a)
    # Interior vapour pressure (monthly mean)
    pvi = [pve[i] + pvi_d[i] for i in range(len(pve))]
    # Interior saturated vapour pressure
    pvi_sat = [611*m.exp((17.08*t)/(234.18+t)) for t in Ti] # Pa
    # Interior relative humidity
    RHi = [100*p/ps for p,ps in zip(pvi,pvi_sat)]
    # Save interior climate to ccd or return interior climate
    if path_save == None:
        return Ti, RHi
    else:
        if number != None:
            supp.saveccd(os.path.join(path_save,'%03i_Temperature.ccd' % number), Ti)
            supp.saveccd(os.path.join(path_save,'%03i_RelativeHumidity.ccd' % number), RHi)
        else:
            supp.saveccd(os.path.join(path_save,'Temperature.ccd'), Ti)
            supp.saveccd(os.path.join(path_save,'RelativeHumidity.ccd'), RHi)

def calcIntClimateEN15026(path_climate, load, number, path_save=None):
    # Load exterior climate temperature
    Te = supp.readccd(path_climate+'Temperature.ccd')
    # Calculate daily mean exterior temperature
    Te_mean = list()
    for i in range(int(len(Te)/24)):
        Te_day = Te[i*24:(i+1)*24]
        Te_mean.extend([np.mean(Te_day)]*24)
    # Calculate interior climate
    # Interior temperature
    Ti = list()
    for i in range(len(Te_mean)):
        if Te_mean[i] < 10:
            Ti.append(20)
        elif Te_mean[i] > 20:
            Ti.append(25)
        else:
            Ti.append(0.5*Te_mean[i]+15)
    # Interior relative humidity
    if load.lower() == 'a' or load == 1:
        a,b,c = 30,60,40
    elif load.lower() == 'b' or load == 2:
        a,b,c = 40,70,50
    else:
        print('Error: wrong interior humidity load')
    RHi = list()
    for i in range(len(Te_mean)):
        if Te_mean[i] < -10:
            RHi.append(a)
        elif Te_mean[i] > 20:
            RHi.append(b)
        else:
            RHi.append(Te_mean[i]+c)
    # Save interior climate to ccd or return interior climate
    if path_save == None:
        return Ti, RHi
    else:
        if number != None:
            supp.saveccd(os.path.join(path_save,'%03i_Temperature.ccd' % number), Ti)
            supp.saveccd(os.path.join(path_save,'%03i_RelativeHumidity.ccd' % number), RHi)
        else:
            supp.saveccd(os.path.join(path_save,'Temperature.ccd'), Ti)
            supp.saveccd(os.path.join(path_save,'RelativeHumidity.ccd'), RHi)

def calcRainLoad(path_climate, ori, number, loc=[5,5], path_save=None):
    #If the inclination of the wall is not specified, set default incination 90 deg
    if not isinstance(ori, list):
        ori = [ori]
        ori.append(90)
    # Load exterior climate (rain, wind direction, wind speed)
    if number != None and path_climate[-4:] == '%03i_' % number:
        rain_h = supp.readccd(path_climate+'VerticalRain.ccd')
        winddir = supp.readccd(path_climate+'WindDirection.ccd')
        windvel = supp.readccd(path_climate+'WindVelocity.ccd')
    else:
        rain_h = supp.readccd(path_climate+'VerticalRain.ccd')
        winddir = supp.readccd(path_climate+'WindDirection.ccd')
        windvel = supp.readccd(path_climate+'WindVelocity.ccd')
    # Load catch ratio and catch ratio parameters
    catch_ratio = np.load(os.path.join(os.path.dirname(__file__), 'data', 'catch_ratio.npy'))
    catch_param = {'height': [0.0, 5.0, 8.0, 8.5, 9.0, 9.25, 9.5, 9.75, 10.0],
                   'horizontal rain intensity': [0.0, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0],
                   'width': [0.0, 2.5, 5.0, 7.5, 10.0],
                   'wind speed': [0, 1, 2, 3, 4, 5, 6, 8, 10]}
    
    # Convert deg to rad
    ori = [m.radians(x) for x in ori]
    winddir = [m.radians(x) for x in winddir]
    # Calculate rain load on facade, for each time step
    rain = list()
    rain_v = list()
    for t in range(len(rain_h)):
        # Wind speed at facade
        Vloc = windvel[t]*m.cos(winddir[t]-ori[1])
        # Check if wind driven rain falls on facade
        if rain_h[t]*Vloc > 0:
            # STEP 1: interpolation based on vertical and horizontal location
            # 1.1a Interpolation boundary for vertical location
            k = len(catch_param['height'])-2
            for knm in range(len(catch_param['height'])-1):
                if loc[0] >= catch_param['height'][knm] and loc[0] < catch_param['height'][knm+1]:
                    k = knm
                    break
            # 1.1b Interpolation boundary for horizontal location
            l = len(catch_param['width'])-2
            for lnm in range(len(catch_param['width'])-1):
                if loc[1] >= catch_param['width'][lnm] and loc[1] < catch_param['width'][lnm+1]:
                    l = lnm
                    break
            # 1.2 Interpolating horizontal and vertical location
            # interpolating horizontal location for vertical location 1
            x = loc[1]
            x1, x2 = catch_param['width'][l], catch_param['width'][l+1]
            y1, y2 = catch_ratio[:,:,k,l], catch_ratio[:,:,k,l+1]
            catc5 = y1 + (y2-y1)*((x-x1)/(x2-x1))
            # interpolating horizontal location for vertical location 2
            y1,y2 = catch_ratio[:,:,k+1,l], catch_ratio[:,:,k+1,l+1]
            catc6 = y1 + (y2-y1)*((x-x1)/(x2-x1))
            # interpolating vertical location for interpolated horizontal location
            x = loc[0]
            x1, x2 = catch_param['height'][k], catch_param['height'][k+1]
            catc = catc5 + (catc6 - catc5)*((x-x1)/(x2-x1))
            
            # STEP 2: interpolation based on wind speed and rain intensity
            # 2.1a Interpolation boundary for wind speed
            i = catc.shape[0]-2
            for inm in range(catc.shape[0]-1):
                if Vloc >= catch_param['wind speed'][inm] and Vloc < catch_param['wind speed'][inm+1]:
                    i = inm
                    break
            # 2.1a Interpolation boundary for rain intensity
            j = catc.shape[1]-2
            for jnm in range(catc.shape[1]-1):
                if rain_h[t] >= catch_param['horizontal rain intensity'][jnm] and rain_h[t] < catch_param['horizontal rain intensity'][jnm+1]:
                    j = jnm
                    break
            # 2.2 Interpolation wind speed and rain intensity
            # interpolating rain intensity for wind speed 1
            x = rain_h[t]
            x1, x2 = catch_param['horizontal rain intensity'][j], catch_param['horizontal rain intensity'][j+1]
            y1, y2 = catc[i,j], catc[i,j+1]
            cat5 = y1 + (y2-y1)*((x-x1)/(x2-x1))
            # interpolating rain intensity for wind speed 2
            y1, y2 = catc[i+1,j], catc[i+1,j+1]
            cat6 = y1 + (y2-y1)*((x-x1)/(x2-x1))
            # interpolation wind speed for interpolated rain intensity
            x = Vloc
            x1, x2 = catch_param['wind speed'][i], catch_param['wind speed'][i+1]
            cat = (cat5 + (cat6 - cat5)*(x - x1)/(x2 - x1))
            
            # STEP 3: Calculate wind driven rain
            rain_v.append(rain_h[t]*cat)
            
        # No wind driven rain on facade
        else:
            rain_v.append(0)
        
        # Calculate total rain load (horizontal + wind driven) on facade
        rain.append(round(rain_h[t]*m.cos(ori[1]) + rain_v[t]*m.sin(ori[1]),8))
    
    # Check if rain contains negative values or NaN values
    for r in rain:
        if r < 0:
            print('Error: Negative value for rain intensity')
        if m.isnan(r):
            print('Error: NAN value for rain intensity\n')
    
    # Save rain load to ccd or return rain load
    if path_save == None:
        return rain
    else:
        if number != None:
            supp.saveccd(os.path.join(path_save,'%03i_VerticalRain.ccd' % number), rain)
        else:
            supp.saveccd(os.path.join(path_save,'VerticalRain.ccd'), rain)

def calcSWRad(path_climate, ori, sun_abs, number, loc_geo=50.8, gr_relf=0.2, path_save=None):
    # Inner functions
    def signum(val):
        if val < 0.0: return -1.0
        else: return 1.0
    
    def f_deltG(t):
        return Fakt1 * m.sin(Pi2_365 *(t + Kt1))
    
    def f_delta(t):
        return f_deltG(t) * Pi_180
    
    def f_sin_h(phi, t):
        delt = Fakt2 * m.sin(Pi2_365 *(t + Kt1))
        ret = m.sin(phi) * m.sin(delt)
        return ret - m.cos(phi) * m.cos(delt) * m.cos(Pi2 * t)
    
    def f_cos_h(phi, t):
        sinh = f_sin_h(phi, t)
        return m.sqrt(1 - sinh * sinh)
    
    def f_h_t(phi, t):
    	return m.asin(f_sin_h(phi, t))
    
    def f_D_t(sinh):
        if m.asin(sinh) >= 0.0: return  1.0
        else: return  0.0
    
    def f_sin_a(phi, t):
        ret = m.cos(f_delta(t)) * m.sin(Pi2 * t)
        return ret / f_cos_h( phi, t)
    
    def f_sinK1(t):
        return Fakt2 * m.sin(Pi2_365 * (t + Kt1))
    
    def f_cosK1(t):
        return Fakt3 * m.cos(Pi2_365 * (t + Kt1))
    
    def f_csKt(t):
        return m.cos(f_sinK1(t))
    
    def f_ssKt(t):
        return m.sin(f_sinK1(t))
    
    def f_dsin_a(phi, t):
        sPhi = m.sin(phi)
        cPhi = m.cos(phi)
        spi2t = m.sin(Pi2 * t)
        cpi2t = m.cos(Pi2 * t)
        CssKt = f_ssKt(t)
        CcsKt = f_csKt(t)
        fakt = sPhi * CssKt - cPhi * CcsKt * cpi2t
        Nenner = m.sqrt(1.0 - fakt * fakt)
        CcosK1 = f_cosK1(t)
    
        f1 = -CssKt * CcosK1 * spi2t / Nenner
        f1 = f1 + CcsKt * cpi2t * Pi2 / Nenner
        f2 = sPhi * CssKt - cPhi * CcsKt * cpi2t
        f2 = f2 * CcosK1 * (sPhi * CcsKt *  + cPhi * CssKt * cpi2t) + cPhi * CcsKt * spi2t * Pi2
        f2 = f2 * CcsKt * spi2t / Nenner / Nenner
        return f1 + f2
    
    def f_a1(phi, t):
        ret = f_sin_a(phi, t) * -1.0
        return ret * signum(f_dsin_a(phi, t))
    
    def f_B2(sinh, beta, phi, t):
        sina = f_sin_a(phi, t)
        ret = m.sqrt(1.0 - sina * sina) * m.cos(beta) * signum(f_dsin_a(phi, t))
        ret = ret + sina * m.sin(beta)
        ret = ret / sinh
        return ret * m.sqrt(1.0 - sinh * sinh)
    
    def f_S(Dt, b2, alpha):
        calpha = m.cos(alpha)
        if Dt == 0.0 or calpha == 1.0:
            if calpha > 0.0: return 1.0
            else: return 0.0
        else:
            s1 = calpha + m.sin(alpha) * b2 * Dt
            if s1 > 0.0: return 1.0
            else: return 0.0
    
    #If the inclination of the wall is not specified, set default incination 90 deg
    if not isinstance(ori, list):
        ori = [ori]
        ori.append(90)
    # Load exterior climate (rain, wind direction, wind speed)
    if number != None and path_climate[-4:] == '%03i_' % number:
        dirrad = supp.readccd(path_climate+'DirectRadiation.ccd')
        diffrad = supp.readccd(path_climate+'DiffuseRadiation.ccd')
    else:
        dirrad = supp.readccd(path_climate+'DirectRadiation.ccd')
        diffrad = supp.readccd(path_climate+'DiffuseRadiation.ccd')
    # Parameters
    alpha = m.radians(ori[1]) # inlination, radians
    beta = m.radians(ori[0]) # orientation, radians
    phi = m.radians(loc_geo) # geographical location, radians
    
    # Calculate H_soldir
    # f_DirRad
    f_DirRad = list()
    Pi2_365 = m.pi*2/365
    Pi_180 = m.pi/180
    Pi2 = m.pi*2
    Kt1 = 10 + 365/4
    Fakt1 = -23.5
    Fakt2 = Fakt1*Pi_180
    Fakt3 = Fakt1*Pi_180*Pi2_365
    for s in range(1,len(dirrad)+1): # Loop over time [h]
        t = s/24 #Loop over time [d]
        sinh = f_sin_h(phi, t) # sun height h
        Dt = f_D_t(sinh)
        if Dt == 0.0: # if sun is to low, no radiation on surface
            f_DirRadfact = 0.0
        else:
            cB2 = f_B2(sinh, beta, phi, t)
            cS = f_S(Dt, cB2, alpha)
            if cS == 0.0:
                f_DirRadfact = 0.0
            else:
                ret = m.cos(alpha)
                ret = ret + m.sin(alpha) * cB2
                ret = ret * cS * Dt
                if ret < 0.0:
                    f_DirRadfact = 0.0
                else:
                    if ret > 5.0:
                        f_DirRadfact = 5.0
                    else:
                        f_DirRadfact = ret
        f_DirRad.append(f_DirRadfact)
    # H_soldir
    H_dir_n = [f*dirr for f,dirr in zip(f_DirRad,dirrad)] # W/m2
    
    # Calculate H_soldiff
    H_diff_n = [m.cos(alpha/2)*m.cos(alpha/2)*diffr + gr_relf*m.sin(alpha/2)*m.sin(alpha/2)*(dirr+diffr) for diffr,dirr in zip(dirrad,diffrad)] # W/m2
    
    # Calculate H_sol
    H_sol = [sun_abs*(Hdir + Hdiff) for Hdir,Hdiff in zip(H_dir_n,H_diff_n)] # W/m2
    
    # Save short wave radiation to ccd or return rain load
    if path_save == None:
        return H_sol
    else:
        if number != None:
            supp.saveccd(os.path.join(path_save,'%03i_ShortWaveRadiation.ccd' % number), H_sol)
        else:
            supp.saveccd(os.path.join(path_save,'ShortWaveRadiation.ccd'), H_sol)