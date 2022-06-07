import sys, os, time
from subprocess import call
root_dir = os.getcwd()
sys.path.append(root_dir + '/tools')
from tools import *
extend_path()

from mpi4py import MPI
MPIcomm = MPI.COMM_WORLD
pId = MPIcomm.Get_rank()
nProc = MPIcomm.Get_size()

simulation_dir = data_dir + 'cosmo_sims/wdm_sims/tsc/1024_25Mpc_cdm/cic/'
input_dir = simulation_dir + 'snapshot_files/'
output_dir = simulation_dir + 'halo_files/'
if pId == 0: create_directory(output_dir)

cwd = os.getcwd()
rockstarDir = cwd + '/halo_finding/rockstar/'
rockstarComand = rockstarDir + 'rockstar'

n_points = 1024
Lbox = 25.0 #Mpc/h

rockstarConf = {
'FILE_FORMAT': '"CHOLLA"',
'TOTAL_PARTICLES': n_points**3,
'BOX_SIZE': Lbox,                                   #Mpc/h
'FORCE_RES': Lbox/n_points/10 ,                    #Mpc/h
'OUTBASE': output_dir,                       #output directory
# 'FULL_PARTICLE_CHUNKS': 1
}
parallelConf = {
'PARALLEL_IO': 1,
'PERIODIC': 1,                                  #periodic boundary conditions
'INBASE':  input_dir ,                              #input directory
'NUM_BLOCKS': 128,                                # <number of files per snapshot>
'NUM_SNAPS': 9,                               # <total number of snapshots>
'STARTING_SNAP': 0,
'FILENAME': '"<snap>_particles.h5.<block>"',              #"my_sim.<snap>.<block>"
# 'SNAPSHOT_NAMES': dataDir + 'halos/snaps_names.txt',
# 'BGC2_SNAPNAMES': dataDir + 'halos/snaps_names.txt',
'NUM_WRITERS': 8,                             #<number of CPUs>
'FORK_READERS_FROM_WRITERS': 1,
'FORK_PROCESSORS_PER_MACHINE': 32,             #<number of processors per node>
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
