# illustrisAPI
tools to make accessing (all) Illustris data simple, using just a laptop and an internet connection

[SEE ALSO](https://github.com/zpenoyre/illustrisAPI/wiki) the wiki for more about the specific functions!

The basic philosophy of these tools is this:
  anyone with a computer, an internet connection, can access (basically) all of the Illustris data quickly and easily.
Obviously the Illustris data is huge, but most users will only want a fraction of it at a time, be it the properties of stars in one galaxy or a few select bulk properties of every galaxy in the simulation.
This means you can download the data in manageable chunks with a reasonably fast internet connection, and start playing with them straight away.
It builds on the excellent API tools created by the Illustris team (http://www.illustris-project.org/data/) but attempts to translate most tasks you might want to complete into simple commands.

The data structure is as similar in organization and naming convention to the raw illustris data as I could manage. I'll try and point out where names differ. Here's a brief overview of that structure:

  there are numerous simulations
  
    each has ~136 snapshots (some, e.g. a couple at ~z=1 in Illustris-1, are corrupted and thus left out)
    
      the data in the snapshots are sorted into individual dark matter halos and subhalos (the latter is roughly synonomous with an individual galaxy)
      
        each halo/subhalo has some bulk properties, like total stellar mass or mean gas metalicity
        
          each halo/subhalo contains a whole bunch of particles (gas,DM,stars and BHs + more obscure things) and each particles has simple properties (like position, mass and velocity)

Sometimes you may want to compare just bulk properties of galaxies (e.g. in the example notebook we recreate the M_BH, sigma relation)
Sometimes you may want to look at specific galaxies (e.g. in the example notebook we plot the projected stellar denisty of a galaxy from a few angles)

The code is relatively simple, and I plan to expand further, get in touch if there's something you'd like to see/do!

The repository contains a few files, all the routines live in iApi.py, an example of their use can be found in the apiTestNotebook (though you must add your own API key, more on that later) and temporary data will start appearing in temp*.hdf5 files as you use it.

______Requirements:

Python packages - numpy, h5py and requests (all easy to get via anaconda) + matplotlib for the example notebook
    (I wrote everything in python 3, hopefully it should all work in python 2 but let me know!)

An API key - Anyone can sign up for an account to use the Illustris data here: http://www.illustris-project.org/data/ .
    You'll be given an API key, which lets the system know that it's you trying to access the data
    You need to replace the placeholder value with your own! (see example notebook for, surprisingly, an example)

Some disk space - Most of the files you'll be using will be nice and small, but it's probably possible to pull something of order ~1 GB (e.g. particle data from the largest galaxies in Illustris 1). 
    You can always check the size of the temp*.hdf5 files, and if they're larger than you can handle think of ways you can pull less data.
    E.g. Pull less fields, look at a smaller galaxy with less particles or use one of the smaller box/ lower resolution simulation runs.

An internet connection - I made and tested this package using the free municipal wifi (albeit in Germany), so it doesn't require blisteringly fast internet
    The biggest problem is a patchy connection, it's not uncommon to see an error involving a 'truncated end of file' on worse connections.
    To the best of my understanding this is caused by the connection faltering part way through a big download.
    We're thinking of a better solution, but for now the fixes are to: download smaller data (not ideal), improve your connection (not ideal) or try again (suprisingly effective!)


______Basic commands:
I'll outline the basic functionality of the commands below. Note they all default to pulling from the main simulation at z=0 but will work for any simulation and snapshot.
  
  Object Data - the following commands gets a *dictionary* of data about a particular object: Simulations, Snapshots and Halos/Subhalos
  
    getSimData(simulation='Illustris-1') 
    getSnapData(snapshot=135, simulation='Illustris-1')
    getHaloData(whichHalo, simulation='Illustris-1', snapshot=135)
    getSubhaloData(whichSubhalo, simulation='Illustris-1', snapshot=135, ...)
    
  Halo and Subhalo Catalogs - these commands pull data on every galaxy in a given simulation and snapshot from ONE FIELD from the halo/subhalo catalog
  
    getHaloField(field, simulation='Illustris-1', snapshot=135, ...)
    getSubhaloField(field, simulation='Illustris-1', snapshot=135, ...)
    
  Galaxy Particles - this command pulls data for the particles in a given subhalo (or halo if you really want) for a list of particle types and fields
  
    getGalaxy(whichGalaxy, fields, simulation='Illustris-1', snapshot=135)
    
  And finally there's the get(path, ...) command. This is doing the actual pulling from online, you hopefully won't need to touch it.
    
______Installation:
      
The install should be like any other python package, but just in case you're not sure how to do it (I always forget...) dowload it from here, store it wherever you want and add it to your PYTHONPATH (I always fall back on the 2nd comment on this thread - http://www.bdnyc.org/2012/09/editing-pythonpath-to-import-modules/)
