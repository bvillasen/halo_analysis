import sys, os, time
from subprocess import call


from mpi4py import MPI
MPIcomm = MPI.COMM_WORLD
pId = MPIcomm.Get_rank()
nProc = MPIcomm.Get_size()

currentDirectory = os.getcwd()
#Add Modules from other directories
devDirectory = '/home/bruno/Desktop/Dropbox/Developer/'
cosmoToolsDirectory = devDirectory + 'cosmo_tools/'
loadDataDirectory = cosmoToolsDirectory + 'load_data/'
sys.path.extend([ loadDataDirectory ])
from load_halo_catalogs import *

# dataDir = "/home/bruno/Desktop/data/galaxies/cosmo_512/data/"
# dataDir = "/media/bruno/hard_drive_1/data/cosmo/256/"
# dataDir = '/raid/bruno/data/cosmo_sims/cholla_pm/cosmo_256_dm/'
dataDir = '/raid/bruno/data/'
# dataDir = '/home/bruno/Desktop/hard_drive_1/data/'
inDir = dataDir + 'cosmo_sims/cholla_pm/256_hydro_50Mpc/'

rockstarDir = devDirectory + 'cosmo_tools/halo_finding/rockstar/'
rockstarComand = rockstarDir + 'rockstar'

h = 0.6766
rockstarConf = {
'FILE_FORMAT': '"CHOLLA"',
'TOTAL_PARTICLES': 256**3,
'BOX_SIZE': 50,        #Mpc/h
'FORCE_RES': 50./256/2 ,                 #Mpc/h
'OUTBASE': inDir + 'halos_100/',
# 'FULL_PARTICLE_CHUNKS': 1
}
parallelConf = {
'PARALLEL_IO': 1,
'PERIODIC': 1,                                #non-periodic boundary conditions
'INBASE':  inDir ,               #"/directory/where/files/are/located"
'NUM_BLOCKS': 8,                              # <number of files per snapshot>
'NUM_SNAPS': 100,                               # <total number of snapshots>
'STARTING_SNAP': 0,
'FILENAME': '"<snap>_particles.h5.<block>"',              #"my_sim.<snap>.<block>"
# 'SNAPSHOT_NAMES': dataDir + 'halos/snaps_names.txt',
# 'BGC2_SNAPNAMES': dataDir + 'halos/snaps_names.txt',
'NUM_WRITERS': 8,                             #<number of CPUs>
'FORK_READERS_FROM_WRITERS': 1,
'FORK_PROCESSORS_PER_MACHINE': 64,             #<number of processors per node>
}

if pId == 0:
  if not os.path.exists( rockstarConf['OUTBASE']): os.makedirs(rockstarConf['OUTBASE'])
  rockstarconfigFile = rockstarConf['OUTBASE'] + '/rockstar_param.cfg'
  rckFile = open( rockstarconfigFile, "w" )
  for key in list(rockstarConf.keys()):
    rckFile.write( key + " = " + str(rockstarConf[key]) + "\n" )
  for key in list(parallelConf.keys()):
    rckFile.write( key + " = " + str(parallelConf[key]) + "\n" )
  rckFile.close()
  #Run ROCKSTAR finder
  print("\nFinding halos...")
  print(" Parallel configuration")
  print("Output: ", rockstarConf['OUTBASE'] + '\n')

MPIcomm.Barrier()
start = time.time()
if pId == 0: call([rockstarComand, "-c", rockstarconfigFile ])
if pId == 1:
  time.sleep(5)
  call([rockstarComand, "-c", rockstarConf['OUTBASE'] + '/auto-rockstar.cfg' ])  
print("Time: ", time.time() - start)

if pId == 0:
  print("Finding Parents")
  for snap in range(parallelConf['NUM_SNAPS'] ):
    print(" Finding Parents  Snap: {0}".format(snap))
    outputFile = 'catalog_{0}.dat'.format(snap)
    find_parents(snap, rockstarConf['BOX_SIZE'], rockstarConf['OUTBASE'], rockstarDir, outputFile)
