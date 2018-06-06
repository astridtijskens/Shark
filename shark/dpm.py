# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 13:22:26 2017

@author: Astrid
"""
import math as m

def freezeThawCyclesDTU(T, RH, w=None, wcrit=1):
    """
    arguments:
    T = temperature time series [°C]
    RH = relative humidity time series [- or %]
    w = moisture saturation degree [-]
        defaults to None, moist freeze-thaw will not be calculated
    wcrit = critical moisture satiration degree for which damage occurs [-]
            defaults to 1
            
    return:
    frost_cyc_tot = total number of freeze-thaw cycles [-]
    frost_cyc_moist_tot = total number of moist freeze-thaw cycles [-]
    """
    
    # Define parameters
    rhol = 1000 # kg/m3 density of water
    hi = -333500 # J/kg phase change enthalpy of ice
    T0 = 273.15 # K temperature at 0°C
    cl = 4187 # J/kgK specific heat capacity of water
    ci = 2100 # J/kgK specific heat capacity of ice
    Rv = 461.89 # J/kgK
    
    # Convert temperature from degC to Kelvin
    T = [t+273.15 for t in T] # K
    # Convert relative humidity to percentage
    if all(rh > 1 for rh in RH): RH = [rh/100 for rh in RH]
    # Length of time-series
    ts = len(T)
    
    # Calculate (moist) freeze-thaw cycles
    pc_freeze = [rhol*(-hi/T0*(t-T0)+(cl-ci)*(t*m.log(t/T0)-(t-T0))) for t in T]
    RH_freeze = [m.exp(p/(rhol*Rv*t)) for t,p in zip(T,pc_freeze)]
    frost_cyc, frost_cyc_moist = [0]*ts, [0]*ts
    for t in range(ts):
        if T[t] < T0 and RH[t] >= RH_freeze[t]: 
            frost_cyc[t] = 1 # freeze-thaw cycles
            if w and w[t] > wcrit: frost_cyc_moist[t] = 1 # moist freeze-thaw cycles
    # Total number of moist freeze-thaw cycles
    frost_cyc_tot, frost_cyc_moist_tot = 0, 0
    frost_cyc_ser, frost_cyc_moist_ser = [0]*ts, [0]*ts
    if frost_cyc[0] == 1: 
        frost_cyc_tot = frost_cyc_tot+1
        frost_cyc_ser[0] = 1
    if frost_cyc_moist[0] == 1: 
        frost_cyc_moist_tot = frost_cyc_moist_tot+1
        frost_cyc_moist_ser[0] = 1
    for t in range(1,ts):
        frost_cyc_ser[t] = frost_cyc_ser[t-1]
        frost_cyc_moist_ser[t] = frost_cyc_moist_ser[t-1]
        if frost_cyc[t] == 1 and frost_cyc[t-1] == 0: 
            frost_cyc_tot = frost_cyc_tot+1
            frost_cyc_ser[t] = frost_cyc_ser[t]+1
        if frost_cyc_moist[t] == 1 and frost_cyc_moist[t-1] == 0: 
            frost_cyc_moist_tot = frost_cyc_moist_tot+1
            frost_cyc_moist_ser[t] = frost_cyc_moist_ser[t]+1
    
    if not w: frost_cyc_moist_tot = None
    
    return frost_cyc_tot, frost_cyc_moist_tot, frost_cyc_ser, frost_cyc_moist_ser

def mouldVTTupdate(T, RH, sens_class='vs', C_eff=1):
    """
    H. Viitanen, T. Ojanen, and R. Peuhkuri, “Mould growth modelling to evaluate 
    durability of materials,” in Proceedings of the 12DBMC - International Conference 
    on Durability of Building Materials and Components, 2011, pp. 1–8.
    
    arguments:
    T = temperature time series [°C]
    RH = relative humidity time series [- or %]
    sens_class = sensitivity class 
                 possible values: 'vs' (very sensitive), 
                                  's' (sensitive), 
                                  'mr' (medium resistant), 
                                  'r' (resistant)
                 defaults to 'vs'
    C_eff = relative coefficient for mould index decline
            defaults to 1
            
    return:
    M = mould index time series [-]
    """
    
    # Convert relative humidity to unit
    if all(rh <= 1 for rh in RH): RH = [rh*100 for rh in RH]
    
    # Define parameters
    if sens_class =='vs': # very sensitive
        k1_1, k1_2 = 1, 2 # M<1, M>1
        A, B, C = 1, 7, 2
        RH_min = 80
    elif sens_class =='s': # sensitive
        k1_1, k1_2 = 0.578, 0.386 #• M<1, M>1
        A, B, C = 0.3, 6, 1
        RH_min = 80
    elif sens_class == 'mr': # medium resistant
        k1_1, k1_2 = 0.072, 0.097 # M<1, M>1
        A, B, C = 0, 5, 1.5
        RH_min = 85;
    elif sens_class =='r': # resistant
        k1_1, k1_2 = 0.33, 0.014 # M<1, M>1
        A, B, C = 0, 3, 1
        RH_min = 85
    else:
        print('''Error: senitivity class not valid, use 'vs', 's', 'mr' or 'r' ''')
    
    # Calculate mould index
    M = [0] # start at mould index 0
    dt_unfav = 0 # no previous infavourable conditions
    for t in range(1,len(RH)): # start at t=1 because at t=0 always M=0
        # Critical RH = lowest humidity for mould growth
        if T[t] <= 20:
            RH_crit = -0.00267*T[t]**3+0.16*T[t]**2-3.13*T[t]+100
        elif T[t] > 20:
            RH_crit = RH_min
        # Maximum mould growth index
        RH_diff = (RH_crit-RH[t])/(RH_crit-100)
        M_max = max(0, A+B*RH_diff-C*RH_diff**2) # [-]
        # k1
        if M[t-1] < 1:
            k1 = k1_1 # [-]
        elif M[t-1] >= 1:
            k1 = k1_2 # [-]
        # k2
        k2 = max(0, (1-m.exp(2.3*(M[t-1]-M_max)))) # [-]
        # dMdt
        if T[t] > 0: # only mould growth when T > 0°C
            W, SQ = 0, 0
            ret = 7*m.exp(-0.68*m.log(T[t])-13.90*m.log(RH[t])+0.14*W-0.33*SQ+66.02)
            dMdt = k1*k2/(7*ret)/24 # [-/hours] devided by 24!
        else: # no mould growth when T <= 0°C
            dMdt = 0 # [-/hours]
        dt = 1
        # dMdt_decline_pine
        if RH[t] < RH_crit:
            dt_unfav = dt_unfav + 1
            if dt_unfav <= 6:
                dMdt_decline = -0.00133
            elif 6 < dt_unfav and dt_unfav <= 24:
                dMdt_decline = 0
            elif dt_unfav > 24:
                dMdt_decline = -0.000667
        else:
            dt_unfav = 0
            dMdt_decline = 0
        # Mould index
        M.append(max(0, m.ceil((M[t-1] + dMdt*dt + C_eff*dMdt_decline*dt)*2/2))) # [-]
    
    return M

def woodDecayVTT(T, RH):
    """
    H. Viitanen, T. Toratti, L. Makkonen, R. Peuhkuri, T. Ojanen, L. Ruokolainen, 
    and J. Räisänen, “Towards modelling of decay risk of wooden materials,” 
    European Journal of Wood and Wood Products, vol. 68, no. 3, pp. 303–313, 2010.
    
    arguments:
    T = temperature time series [°C]
    RH = relative humidity time series [- or %]
    
    return:
    ML = wood mass loss time series = [%]
    """
    
    # Convert relative humidity to unit
    if all(rh <= 1 for rh in RH): RH = [rh*100 for rh in RH]
    
    # Calculate wood decay mass loss
    alpha = [0] # start at beginning of activation proces
    ML = [0] # start at 0% mass loss
    dt = 1 # time steps of 1h
    t_dec_lin = 17520
    for t in range(1,len(RH)):
        if ML[t-1] == 100:
            ML.append(100)
        else:
            # Critical time for decay to start
            t_crit = (2.3*T[t]+0.035*RH[t]-0.024*T[t]*RH[t])/(-42.9+0.14*T[t]+0.45*RH[t])*30*24 # [h]
            # Activation process
            if T[t] > 0 and RH[t] > 95:
                delt_alpha = dt/t_crit # [-]
                alpha.append(min(1,alpha[t-1] + delt_alpha)) # alpha can only increase to 1
            else:
                delt_alpha = -dt/t_dec_lin # [-]
                alpha.append(max(0,alpha[t-1] + delt_alpha)) # alpha can only decrease to 0
            # Mass loss process
            if alpha[t] == 1:
                MLdt = max(0, -5.96*10**(-2)+1.96*10**(-4)*T[t]+6.25*10**(-4)*RH[t]) # [%/h] MLdt can not be negative
            else:
                MLdt = 0
            ML.append(min(100, int(ML[t-1] + MLdt*dt))) # [%] ML can only increase to 100
    
    return ML