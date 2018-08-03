import requests
import numpy as np
import h5py
import changeUnits

users_api_key = "83e79a727bdc1a445cea4b9bb9335faa"

baseUrl = 'http://www.illustris-project.org/api/'
headers = {"api-key" : users_api_key}


def update_api_key(api_key):
    """
    Add or change the API key used by this module
    
    Parameters
    ----------
    api_key : str
        Your API key for the illustris databank
    
    """
    
    global headers
    users_api_key = api_key
    headers = {"api-key" : users_api_key}


def setUnits(unitScheme):
    """
    Tells the unit conversion routine which units we want
    """
    changeUnits.setUnits(unitScheme)
    
    
def get(path, params=None, fName='temp'): # gets data from url, saves to file
    """
    Routine to pull data from online
    """
    
    # make HTTP GET request to path
    if (len(headers['api-key'])!=32):
        print("Have you put in your API key? This one isn't working")
        print('Currently it is: ',headers['api-key'])
        print('You can find your API key on the Illustris website:')
        print('http://www.illustris-project.org/data/')
        print('and update it in this program using')
        print("iApi.headers['api-key']='*MYAPIKEY*'")
        print("Or permanently change it in iApi.py")
    r = requests.get(path, params=params, headers=headers)
    
    # raise exception if response code is not HTTP SUCCESS (200)
    r.raise_for_status()

    if r.headers['content-type'] == 'application/json':
        return r.json() # parse json responses automatically

    dataFile=fName+'.hdf5'
    # Saves to file, currently disabled
    if 'content-disposition' in r.headers:
        filename = r.headers['content-disposition'].split("filename=")[1]
        with open(dataFile, 'wb') as f:
            f.write(r.content)
        return dataFile # return the filename string

    return r


def getGalaxy(whichGalaxy, fields, simulation='Illustris-1', snapshot=135,
              fileName='tempGal', rewriteFile=1, getHalo=0):
        
    """
    Pulls particle data for a particular galaxy for a list of specified fields
    
    This pulls particle data for a particular galaxy for a list of specified 
    fields and particle types. To be more exact it downloads, opens and returns 
    data from a hdf5 file.

    Parameters
    ----------
    whichGalaxy : int
        The subhalo number (SubfindId to be exact) of the galaxy

    fields : list
        List of fields to be returned. Can have as many entries as wanted but 
        must be in the specified format. For each desired field (e.g. positions 
        of stars) you must specify a particle type and desired field. The 
        particle types are labelled by the numbers 0 through 5

        0. Gas
        1. Dark matter
        2. Empty (don't ask)
        3. Tracers (if you don't know what this means you probably can ignore it)
        4. Stars
        5. Black holes (bear in mind a galaxy may have none)
        The fields can be found in section 1. of this page. 
        http://www.illustris-project.org/data/docs/specifications/
        See below for an example

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from

    getHalo : int
        [0 or 1] Instead of pulling all the data in a subhalo you can set this 
        to 1 to get all particle data in a halo. Roughly speaking a galaxy is 
        synonymous with a subhalo and a cluster with a halo (don't ask me) so 
        the data may be large!

    fileName : str
        Default is 'tempGal.hdf5'. Filename for where to store or load the data 

    rewriteFile : int
        [0 or 1] If this is equal to 0 then the program will try and pull data 
        from the file specified by fileName rather than re-downloading. This can 
        save time, especially for galaxies which are large or you will work on 
        frequently, but you will only be able to access fields you originally 
        requested

    
    Returns
    -------
    data : list
        A list of numpy arrays, each one containing the data for a specific 
        field for all particles of a given type, in the order of fields

    
    Examples
    --------
    Let's pull out the stellar masses, positions, velocities and gas coordinates 
    and temperatures for particles in a galaxy at redshift z=1 (snapshot 85) 
    in illustris 3

    Define the fields we want
    
        >>> fields=[
        [4,'Masses'], # star mass (N_star values)
        [4,'Coordinates'], # star position (N_star x 3 values)
        [4,'Velocities'], # star velocity (N_star x 3 values)
        [0,'Coordinates'], # gas position (N_gas x 3 values)
        [0,'InternalEnergy'] # gas temperature, after a simple conversion (N_gas x 3 values)
        ]
        
    
    Get the data
    
        >>> galaxyData=iApi.getGalaxy(100, fields, simulation='Illustris-3', snapshot=85)

    Split the data into seperate numpy arrays

        >>> mStar=galaxyData[0][:]
        >>> rStar=galaxyData[1][:,:] #don't forget this is a 2d array
        >>> vStar=galaxyData[2][:,:]
        >>> rGas=galaxyData[3][:,:]
        >>> uGas=galaxyData[4][:]
    
    """
        
    fields=np.array(fields) # converts to array
    order=np.argsort(fields[:,0])
    disorder=np.argsort(order) # needed to unsort the fields later...
    fields=fields[order,:] # orders by particle type
    nFields=order.size
    
    if rewriteFile==1: # redownloads file from the internet
        url='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/subhalos/'+str(whichGalaxy)+'/cutout.hdf5?'
        if getHalo==1:
            url='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/halos/'+str(whichGalaxy)+'/cutout.hdf5?'
        
        thisParticle=0
        thisEntry=0
        firstParticle=1
        while thisParticle<6: # cycles through all particle type

            if (int(fields[thisEntry,0])!=thisParticle): # checks there is at least one field for this particle
                thisParticle+=1
                continue
            if firstParticle==1: # first particle requires no ampersand
                firstParticle=0
            else: # all later particles do
                url+='&' 
            particleTypeNames=['gas','dm','error','tracers','stars','bhs']                 
            url+=particleTypeNames[thisParticle]+'=' # adds the name of the particle type
        
            firstEntry=1
            while int(fields[thisEntry,0])==thisParticle:
                if firstEntry==1: #first entry requires no comma
                    firstEntry=0
                else: # all later entries do
                    url+=','
                url+=fields[thisEntry,1] # adds every associated field
                thisEntry+=1
                if thisEntry==nFields:
                    break
            if thisEntry==nFields:
                break
            thisParticle+=1
        dataFile=get(url,fName=fileName)
    # end of "if rewriteFile==1:"
    if rewriteFile == 0: # if we're not redownloading need to set path to the file
        dataFile=fileName+'.hdf5'
    
    # gets a dictionary for unit conversions
    units=changeUnits.makeParticleDict(simulation=simulation,snapshot=snapshot)
    
    # actually get the data (saved to .hdf5 file)
    data=[] # initially empty list that we will fill up with the data
    with h5py.File(dataFile,'r') as f:
        for i in range(disorder.size):
            thisField=fields[disorder[i],:] # ensures data returned in original order of fields
            data.append(units[thisField[1]]*np.array(f['PartType'+thisField[0]][thisField[1]]))
            # returns all particle data of each field as a numpy array
    return data # returns all the particle fields as a list of numpy arrays in the same order as initial fields


def getSubhaloField(field, simulation='Illustris-1', snapshot=135,
                    fileName='tempCat', rewriteFile=1):
    """
    Data from one field for all subhalos in a given snapshot      
    
    These two commands are near identical, so I'm going to detail them both here. 
    They have the same input and output, except one deals with halos (roughly 
    speaking 'groups/ clusters') and the other with the subhalos in those halos 
    (the 'galaxies' in those 'groups'). See Intro to the Data (or Naming 
    Conventions) for more on the data structure/ naming conventions used.
    
    
    Parameters
    ----------
    field : str
        Name of the one field to be returned. The fields can be found in 
        section 2. of this page
        http://www.illustris-project.org/data/docs/specifications/

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from

    The following two parameters are discussed in more detail here!

    fileName : str
        Default is 'tempGal.hdf5'. Filename for where to store or load the data 

    rewriteFile : int
        [0 or 1] If this is equal to 0 then the program will try and pull data 
        from the file specified by fileName rather than re-downloading. This can 
        save time, especially for galaxies which are large or you will work on 
        frequently, but you will only be able to access fields you originally 
        requested
        
        
    Returns
    -------
    data : array
        A numpy array containing the data for a specific field for all halos/subhalos

        
    Examples
    --------
    Let's pull out the velocity dispersion of stars in every subhalo and their 
    DM mass, and then restrict ourselves to only looking at the primary subhalo 
    in each halo (i.e. the most massive galaxy in each group).

    The velocity dispersion (N_sub values)
    
        >>> galaxyVelDisp=iApi.getSubhaloField('SubhaloVelDisp')

    The mass of each different particle type in a galaxy (N_sub x 6 values, 
    see getGalaxyData for more info on particle types)
    
        >>> galaxyMassType=iApi.getSubhaloField('SubhaloMassType') 

    The subhalo number of the primary subhalo in each halo (N_halo values)
        
        >>> primarySubhalos=iApi.getHaloField('GroupFirstSub') 

    Velocity dispersion of primary subhalos
    
        >>> velDisp=galaxyVelDisp[primarySubhalos]

    Total dark matter mass of primary subhalos 
    
        >>> mDM=galaxyMassType[primarySubhalos,1] 
    
    """
    
    if rewriteFile==1: # redownloads file from the internet
        url='http://www.illustris-project.org/api/'+simulation+'/files/groupcat-'+str(snapshot)+'/?Subhalo='+field
        dataFile=get(url,fName=fileName)
    if rewriteFile == 0: # if we're not redownloading need to set path to the file
        dataFile=fileName+'.hdf5'
        
    with h5py.File(dataFile,'r') as f:
        data=np.array(f['Subhalo'][field])
    units=changeUnits.makeSubhaloDict(simulation=simulation,snapshot=snapshot)
    return data*units[field]
    
  
def getHaloField(field, simulation='Illustris-1', snapshot=135,
                 fileName='tempCat', rewriteFile=1):
    """
    Data from one field for all halos/subhalos in a given snapshot      
    
    These two commands are near identical, so I'm going to detail them both here. 
    They have the same input and output, except one deals with halos (roughly 
    speaking 'groups/ clusters') and the other with the subhalos in those halos 
    (the 'galaxies' in those 'groups'). See Intro to the Data (or Naming 
    Conventions) for more on the data structure/ naming conventions used.
    
    
    Parameters
    ----------
    field : str
        Name of the one field to be returned. The fields can be found in 
        section 2. of this page
        http://www.illustris-project.org/data/docs/specifications/

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from

    The following two parameters are discussed in more detail here!

    fileName : str
        Default is 'tempGal.hdf5'. Filename for where to store or load the data 

    rewriteFile : int
        [0 or 1] If this is equal to 0 then the program will try and pull data 
        from the file specified by fileName rather than re-downloading. This can 
        save time, especially for galaxies which are large or you will work on 
        frequently, but you will only be able to access fields you originally 
        requested
        
        
    Returns
    -------
    data : array
        A numpy array containing the data for a specific field for all halos/subhalos

        
    Examples
    --------
    Let's pull out the velocity dispersion of stars in every subhalo and their 
    DM mass, and then restrict ourselves to only looking at the primary subhalo 
    in each halo (i.e. the most massive galaxy in each group).

    The velocity dispersion (N_sub values)
    
        >>> galaxyVelDisp=iApi.getSubhaloField('SubhaloVelDisp')

    The mass of each different particle type in a galaxy (N_sub x 6 values, 
    see getGalaxyData for more info on particle types)
    
        >>> galaxyMassType=iApi.getSubhaloField('SubhaloMassType') 

    The subhalo number of the primary subhalo in each halo (N_halo values)
        
        >>> primarySubhalos=iApi.getHaloField('GroupFirstSub') 

    Velocity dispersion of primary subhalos
    
        >>> velDisp=galaxyVelDisp[primarySubhalos]

    Total dark matter mass of primary subhalos 
    
        >>> mDM=galaxyMassType[primarySubhalos,1] 
    
    """
    
    if rewriteFile==1: # redownloads file from the internet
        url='http://www.illustris-project.org/api/'+simulation+'/files/groupcat-'+str(snapshot)+'/?Group='+field
        dataFile=get(url,fName=fileName)
    if rewriteFile == 0: # if we're not redownloading need to set path to the file
        dataFile=fileName+'.hdf5'
        
    with h5py.File(dataFile,'r') as f:
        data=np.array(f['Group'][field])
    units=changeUnits.makeHaloDict(simulation=simulation,snapshot=snapshot)
    return data*units[field]
    

def getHaloData(whichHalo, simulation='Illustris-1', snapshot=135):
    """
    Returns a dictionary with all catalog data corresponding to a halo or subhalo
    
    Docstring is identical for `getHaloData`and `getSubhaloData`
    
    These two commands are effectively identical. They have the same input and 
    output, except one deals with halos (roughly speaking 'groups/ clusters') 
    and the other with the subhalos in those halos (the 'galaxies' in those 
    'groups'). See Intro to the Data (or Naming Conventions) for more on the 
    data structure/ naming conventions used.

    Parameters
    ----------
    whichHalo : int
        halo/subhalo number of the galaxy you wish to get data for

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from

        
    Returns
    -------
    data : dict
        A dictionary of data, with an entry for each field (with field names 
        from section 2. of this page
        http://www.illustris-project.org/data/docs/specifications/
        
    
    """

    units=changeUnits.makeHaloDict(simulation=simulation,snapshot=snapshot)
    url='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/halos/'+str(whichHalo)+'/info.json'
    data=get(url)
    haloData=data['Group']
    haloKeys=list(haloData.keys())
    for i in range(len(haloKeys)):
        oldValue=np.array(haloData[haloKeys[i]])
        convFactor=units[haloKeys[i]]
        haloData[haloKeys[i]]=convFactor*oldValue
    return haloData
    
    

def getSubhaloData(whichSubhalo, simulation='Illustris-1', snapshot=135):
    """
    Returns subhalo data for a particular subhalo, plus progenitors!
    
    Docstring is identical for `getHaloData`and `getSubhaloData`
    
    These two commands are effectively identical. They have the same input and 
    output, except one deals with halos (roughly speaking 'groups/ clusters') 
    and the other with the subhalos in those halos (the 'galaxies' in those 
    'groups'). See Intro to the Data (or Naming Conventions) for more on the 
    data structure/ naming conventions used.

    Parameters
    ----------
    whichSubhalo : int
        halo/subhalo number of the galaxy you wish to get data for

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from

        
    Returns
    -------
    data : dict
        A dictionary of data, with an entry for each field (with field names 
        from section 2. of this page
        http://www.illustris-project.org/data/docs/specifications/

    """

    units=changeUnits.makeSubhaloDict(simulation=simulation,snapshot=snapshot)
    infoUrl='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/subhalos/'+str(whichSubhalo)+'/info.json'
    infoData=get(infoUrl)
    subhaloData=infoData['Subhalo']
    subhaloKeys=list(subhaloData.keys())
    for i in range(len(subhaloKeys)):
        oldValue=np.array(subhaloData[subhaloKeys[i]])
        convFactor=units[subhaloKeys[i]]
        subhaloData[subhaloKeys[i]]=convFactor*oldValue
    return subhaloData
    

def getTree(whichSubhalo, simulation='Illustris-1', snapshot=135):
    """
    Returns the merger tree of a specified subhalo at some snapshot    
    
    
    Parameters
    ----------
    whichSubhalo : int
        halo/subhalo number of the galaxy you wish to get data for

    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from
    
    
    Returns
    -------
    treeData : dict
        Returns a dict with the Subhalo index numbers for the main subhalo for
        each snapshot and also the indexes of halos which mergers with the main
        subhalo during the time since the last snapshot
    
    """

    treeUrl='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/subhalos/'+str(whichSubhalo)+'/sublink/simple.json'
    treeData=get(treeUrl)
    treeData['Main']=np.array(treeData['Main']) #don't know why these are lists but numpy arrays seem more useful
    treeData['Mergers']=np.array(treeData['Mergers'])
    return treeData
    

def getSnapData(snapshot=135, simulation='Illustris-1'):
    """
    Returns relevant details for a particular snapshot
    
    Returns a dictionary of data for a particular snap. Useful for finding the 
    number of particles of various types, and number of halos/subhalos. 
    Also includes the redshift.
    
    
    Parameters
    ----------
    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from
        
        
    Returns
    -------
    data : dict
        
    """
    
    snapUrl='http://www.illustris-project.org/api/'+simulation+'/snapshots/'+str(snapshot)+'/'
    snapData=get(snapUrl)
    data={'Simulation':simulation}
    data['SnapshotNumber']=snapshot
    #could add time
    data['Redshift']=snapData['redshift']
    data['NumPartGas']=snapData['num_gas']
    data['NumPartDM']=snapData['num_dm']
    data['NumPartTracer']=snapData['num_trmc']
    data['NumPartStar']=snapData['num_stars']
    data['NumPartBH']=snapData['num_bhs']
    data['NumHalos']=snapData['num_groups_fof']
    data['NumSubhalos']=snapData['num_groups_subfind']
    return data
 
#returns relevant details for a particular simulation
def getSimData(simulation='Illustris-1', getRedshifts=1):
    """
    Returns relevant details for a particular simulation
    
    Returns a dictionary of data about a particular simulation. This includes 
    cosmological parameters and the box size. If getRedshifts==1 then it will 
    also find and return a list of snapshot numbers and their associated 
    redshift, scale factor and time. THIS REQUIRES SCIPY for the numerical 
    integration.

    NOTE: These units are not converted! They are given in 10^10 M_sun/h, Gyr 
    and comoving kpc/h (which can be converted by dividing by 'h' and box length 
    converted to physical coordinates by multiplying by the scalefactor at a 
    given snapshot)
    
    
    Parameters
    ----------
    simulation : str
        Which simulation to pull data from

    snapshot : int
        Which snapshot (moment in time) to pull data from
        
        
    Returns
    -------
    data : dict
        
    """

    simUrl='http://www.illustris-project.org/api/'+simulation+'/'
    simData=get(simUrl)
    #could add table of snapshots, redshifts and times
    data={'Simulation':simulation}
    data['BoxSize']=simData['boxsize']
    h=simData['hubble']
    data['h']=simData['hubble']
    data['Omega_0']=simData['omega_0']
    data['Omega_L']=simData['omega_L']
    data['Omega_B']=simData['omega_B']
    data['MassDM']=simData['mass_dm']
    data['MassGas']=simData['mass_gas']
    
    if getRedshifts==1: # get a list of the redshifts, cosmic time and scale factor of each snapshots
        from scipy import integrate #needed for numerical inetgration to get t(z)
        H0=100*data['h']
        omM=data['Omega_0']+data['Omega_B']
        omL=data['Omega_L']
        
        def tInt(a):
            return 1/(H0*a*np.sqrt(omL + omM*a**-3))
        
        nSnapshots=simData['num_snapshots']
        snapshotsUrl=simUrl+'snapshots/'
        snapshotsData=get(snapshotsUrl)
        finalSnapshot=snapshotsData[-1]['number'] # may be larger than nSnapshots if there are corrupted files
        snapshots=-np.ones((finalSnapshot+1,4)) #corrupted snapshots will have -1's in redshift, scale factor and time
        snapshots[:,0]=np.arange(0,finalSnapshot+1)
        for i in range(nSnapshots):
            thisSnap=snapshotsData[i]['number'] #note, sometimes a sim may skip a snapshot
            z=snapshotsData[i]['redshift']
            snapshots[thisSnap,1]=z
            a=1/(1+z)
            snapshots[thisSnap,2]=a
            snapshots[thisSnap,3]=integrate.quad(tInt,0,a)[0] #NOT THE SAME AS ON THE ILLUSTRIS WEBSITE (no idea why not tho...)
        data['Redshifts']=snapshots
    return data
