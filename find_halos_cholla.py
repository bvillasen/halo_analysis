import sys, os, time
from subprocess import call
sys.path.append('tools')
from tools import *
extend_path()

from mpi4py import MPI
MPIcomm = MPI.COMM_WORLD
pId = MPIcomm.Get_rank()
nProc = MPIcomm.Get_size()


dataDir = '/data/groups/comp-astro/bruno/'
simulationDir = dataDir + 'cosmo_sims/256_dm_50Mpc/'
inDir = simulationDir + 'output_files/'
outDir = simulationDir + 'halo_files/'
if pId == 0: create_directory(outDir)


cwd = os.getcwd() 
rockstarDir = cwd + '/halo_finding/rockstar/'
rockstarComand = rockstarDir + 'rockstar'

rockstarConf = {
'FILE_FORMAT': '"CHOLLA"',
'TOTAL_PARTICLES': 256**3,
'BOX_SIZE': 50.0,                          #Mpc/h
'FORCE_RES': 50./256 / 10 ,                    #Mpc/h
'OUTBASE': outDir,                       #output directory
# 'FULL_PARTICLE_CHUNKS': 1
}
parallelConf = {
'PARALLEL_IO': 1,
'PERIODIC': 1,                                  #periodic boundary conditions
'INBASE':  inDir ,                              #input directory
'NUM_BLOCKS': 8,                                # <number of files per snapshot>
'NUM_SNAPS': 300,                               # <total number of snapshots> 
'STARTING_SNAP': 0,
'FILENAME': '"<snap>_particles.h5.<block>"',              #"my_sim.<snap>.<block>"
# 'SNAPSHOT_NAMES': dataDir + 'halos/snaps_names.txt',
# 'BGC2_SNAPNAMES': dataDir + 'halos/snaps_names.txt',
'NUM_WRITERS': 8,                             #<number of CPUs>
'FORK_READERS_FROM_WRITERS': 1,
'FORK_PROCESSORS_PER_MACHINE': 40,             #<number of processors per node>
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
  print("Output: " + rockstarConf['OUTBASE'] + '\n')

MPIcomm.Barrier()
start = time.time()
if pId == 0: call([rockstarComand, "-c", rockstarconfigFile ])
if pId == 1:
  time.sleep(5)
  call([rockstarComand, "-c", rockstarConf['OUTBASE'] + '/auto-rockstar.cfg' ])  
print("Time: {0}".format( time.time() - start) )

# if pId == 0:
#   print("Finding Parents")
#   for snap in range(parallelConf['NUM_SNAPS'] ):
#     print(" Finding Parents  Snap: {0}".format(snap))
#     outputFile = 'catalog_{0}.dat'.format(snap)
#     find_parents(snap, rockstarConf['BOX_SIZE'], rockstarConf['OUTBASE'], rockstarDir, outputFile)
