import numpy as np
import iApi

M=1 #without conversion all values given in SI units
L=1
T=1
V=1

def setUnits(unitScheme):
    global M, L, T, V
    if unitScheme=='SI':
        M=1 #kg
        L=1 #m
        T=1 #s
        V=1 #ms-1
    elif unitScheme=='cgs':
        M=1000 #g
        L=100 #cm
        T=1 #s
        V=100 #cms-1
    elif unitScheme=='Cosmology':
        M=5.03e-31 #solar mass
        L=3.24e-20 #kpc
        T=3.17e-17 #Gyr
        V=0.001 #kms-1
    elif unitScheme=='Zephyr': #same as Cosmology but using kpc/Gyr for velocity (almost the same, much more intuitive and self consistant)
        M=5.03e-31 #solar mass
        L=3.24e-20 #kpc
        T=3.17e-17 #Gyr
        V=0.00102 #kpc/Gyr
    else:
        print('not a valid unit scheme')
        print('choices are:')
        print('"SI" - m, kg, s')
        print('"cgs" - cm, g, s')
        print('"Cosmology" - kpc, M_sun, Gyr (, kms-1)')
        print('"Zephyr" - kpc, M_sun, Gyr')

def makeParticleDict(snapshot=135,simulation='Illustris-1'):
    simData=iApi.getSimData(simulation)
    h=simData['h']
    #gets scale factor. This does not exist for corrupted snapshots so will skip forward until finds a non corrupted one
    a=-1
    skip=0
    while a==-1:
        a=simData['Redshifts'][snapshot+skip,2]
        skip=skip+1
    
    pDict={'Coordinates':a*3.086e+19*L/h}
    pDict['Density']=h**2*10e10*1.989e30*M/(a*3.086e+19*L)**3
    pDict['ElectronAbundance']=1
    pDict['GFM_AGNRadiation']=1000*M/T**3
    pDict['GFM_CoolingRate']=1000*M*(100*L)**5/T**3
    pDict['GFM_Metallicity']=1
    pDict['GFM_WindDMVelDisp']=1000*V
    pDict['InternalEnergy']=(1000*V)**2
    pDict['Masses']=10e10*1.989e30*M/h
    pDict['NeutralHydrogenAbundance']=1
    pDict['NumTracers']=1
    pDict['ParticleIDs']=1
    pDict['Potential']=(1000*V)**2/a 
    pDict['SmoothingLength']=a*3.086e+19*L/h
    pDict['StarFormationRate']=1.989e30*M/(31556926*L)
    pDict['SubfindDensity']=h**2*10e10*1.989e30*M/(a*3.086e+19*L)**3
    pDict['SubfindHsml']=a*3.086e+19*L/h
    pDict['SubfindVelDisp']=1000*V
    pDict['Velocities']=1000*V*np.sqrt(a)
    pDict['Volume']=1/(a*3.086e+19*L/h)**3
    #next 3 are tracer properties which I'm not touching...
    pDict['FluidQuantities']=1
    pDict['ParentID']=1
    pDict['TracerID']=1
    
    pDict['GFM_InitialMass']=10e10*1.989e30*M/h
    #WHY THE HELL IS THIS IN SCALEFACTOR UNITS???? Again, not touching it
    pDict['GFM_StellarFormationTime']=1
    #could convert to luminosity if really wanted...
    pDict['GFM_StellarPhotometrics']=1
    
    pDict['BH_CumEgyInjection_QM']=(10e10*1.989e30*M/h)*(a*3.086e+19*L/h)**2/(0.978*1e9*31556926*T/h)**2
    pDict['BH_CumMassGrowth_QM']=10e10*1.989e30*M/h
    pDict['BH_Density']=h**2*10e10*1.989e30*M/(a*3.086e+19*L)**3
    pDict['BH_Hsml']=a*3.086e+19*L/h
    pDict['BH_Mass']=10e10*1.989e30*M/h
    pDict['BH_Mass_bubbles']=10e10*1.989e30*M/h
    pDict['BH_Mass_ini']=10e10*1.989e30*M/h
    pDict['BH_MDot']=(10e10*1.989e30*M/h)/(0.978*1e9*31556926*T/h)
    pDict['BH_Pressure']=(10e10*1.989e30*M/h)/((a*3.086e+19*L)*(0.978*1e9*31556926*T/h))
    pDict['BH_Progs']=1
    pDict['BH_U']=(1000*V)**2
    pDict['HostHaloMass']=10e10*1.989e30*M/h
    
    return pDict
    
def makeHaloDict(snapshot=135,simulation='Illustris-1'):
    simData=iApi.getSimData(simulation)
    h=simData['h']
    #gets scale factor. This does not exist for corrupted snapshots so will skip forward until finds a non corrupted one
    a=-1
    skip=0
    while a==-1:
        a=simData['Redshifts'][snapshot+skip,2]
        skip=skip+1
    
    hDict={'GroupBHMass':10e10*1.989e30*M/h}
    hDict['GroupBHMdot']=(10e10*1.989e30*M/h)/(0.978*1e9*31556926*T/h)
    hDict['GroupCM']=a*3.086e+19*L/h
    hDict['GroupFirstSub']=1
    hDict['GroupGasMetallicity']=1
    hDict['GroupLen']=1
    hDict['GroupLenType']=1
    hDict['GroupMass']=10e10*1.989e30*M/h
    hDict['GroupMassType']=10e10*1.989e30*M/h
    hDict['GroupNsubs']=1
    hDict['GroupPos']=a*3.086e+19*L/h
    hDict['GroupSFR']=1.989e30*M/(31556926*L)
    hDict['GroupStarMetallicity']=1
    hDict['GroupVel']=(1000*V)/a
    hDict['GroupWindMass']=10e10*1.989e30*M/h
    hDict['Group_M_Crit200']=10e10*1.989e30*M/h
    hDict['Group_M_Crit500']=10e10*1.989e30*M/h
    hDict['Group_M_Mean200']=10e10*1.989e30*M/h
    hDict['Group_M_TopHat200']=10e10*1.989e30*M/h
    hDict['Group_R_Crit200']=a*3.086e+19*L/h
    hDict['Group_R_Crit500']=a*3.086e+19*L/h
    hDict['Group_R_Mean200']=a*3.086e+19*L/h
    hDict['Group_R_TopHat200']=a*3.086e+19*L/h
    
    return hDict
    
def makeSubhaloDict(snapshot=135,simulation='Illustris-1'):
    simData=iApi.getSimData(simulation)
    h=simData['h']
    #gets scale factor. This does not exist for corrupted snapshots so will skip forward until finds a non corrupted one
    a=-1
    skip=0
    while a==-1:
        a=simData['Redshifts'][snapshot+skip,2]
        skip=skip+1
    
    sDict={'SubhaloBHMass':10e10*1.989e30*M/h}
    sDict['SubhaloBHMdot']=(10e10*1.989e30*M/h)/(0.978*1e9*31556926*T/h)
    sDict['SubhaloCM']=a*3.086e+19*L/h
    sDict['SubhaloGasMetallicity']=1
    sDict['SubhaloGasMetallicityHalfRad']=1
    sDict['SubhaloGasMetallicityMaxRad']=1
    sDict['SubhaloGasMetallicitySfr']=1
    sDict['SubhaloGasMetallicitySfrWeighted']=1
    sDict['SubhaloGrNr']=1
    sDict['SubhaloHalfmassRad']=a*3.086e+19*L/h
    sDict['SubhaloHalfmassRadType']=a*3.086e+19*L/h
    sDict['SubhaloIDMostbound']=1
    sDict['SubhaloLen']=1
    sDict['SubhaloLenType']=1
    sDict['SubhaloMass']=10e10*1.989e30*M/h
    sDict['SubhaloMassInHalfRad']=10e10*1.989e30*M/h
    sDict['SubhaloMassInHalfRadType']=10e10*1.989e30*M/h
    sDict['SubhaloMassInMaxRad']=10e10*1.989e30*M/h
    sDict['SubhaloMassInMaxRadType']=10e10*1.989e30*M/h
    sDict['SubhaloMassInRad']=10e10*1.989e30*M/h
    sDict['SubhaloMassInRadType']=10e10*1.989e30*M/h
    sDict['SubhaloMassType']=10e10*1.989e30*M/h
    sDict['SubhaloParent']=1
    sDict['SubhaloPos']=a*3.086e+19*L/h
    sDict['SubhaloSFR']=1.989e30*M/(31556926*L)
    sDict['SubhaloSFRinHalfRad']=1.989e30*M/(31556926*L)
    sDict['SubhaloSFRinMaxRad']=1.989e30*M/(31556926*L)
    sDict['SubhaloSFRinRad']=1.989e30*M/(31556926*L)
    sDict['SubhaloSpin']=(3.086e+19*L/h)*(1000*V)
    sDict['SubhaloStarMetallicity']=1
    sDict['SubhaloStarMetallicityHalfRad']=1
    sDict['SubhaloStarMetallicityMaxRad']=1
    #could convert to luminosity if really wanted...
    sDict['SubhaloStellarPhotometrics']=1
    sDict['SubhaloStellarPhotometricsMassInRad']=10e10*1.989e30*M/h
    sDict['SubhaloStellarPhotometricsRad']=a*3.086e+19*L/h
    sDict['SubhaloVel']=(1000*V)
    sDict['SubhaloVelDisp']=(1000*V)
    sDict['SubhaloVmax']=(1000*V)
    sDict['SubhaloVmaxRad']=3.086e+19*L/h
    sDict['SubhaloVelDisp']=(1000*V)
    sDict['SubhaloWindMass']=10e10*1.989e30*M/h
    
    return sDict

def makeSimDict(): #CURRENTLY UNUSED!!
    h=0.704 #would get it from sim data but would end up calling it recursively
    
    simDict={'BoxSize':3.086e+19*L/h}
    simDict['MassDM']=1.989e30*M
    simDict['MassGas']=1.989e30*M
    simDict['Time']=3.16e16*T
    
    return simDict