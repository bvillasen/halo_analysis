import os, sys
from os import listdir
from os.path import isfile, join
import numpy as np
import h5py as h5
import time

system = None
system = os.getenv('SYSTEM_NAME')
if not system:
  print( 'Can not find the system name')
  exit(-1)
# print( f'System: {system}')

if system == 'Eagle':    data_dir = '/media/bruno/ssd_bruno/data/'
# if system == 'Eagle':    data_dir = '/home/bruno/Desktop/data/'
if system == 'Tornado':  data_dir = '/home/bruno/Desktop/ssd_0/data/'
if system == 'Shamrock': data_dir = '/raid/bruno/data/'
if system == 'Lux':      data_dir = '/data/groups/comp-astro/bruno/'
if system == 'Summit':   data_dir = '/gpfs/alpine/ast169/scratch/bvilasen/'
if system == 'xps':      data_dir = '/home/bruno/Desktop/data/'
if system == 'Mac_mini': data_dir = '/Users/bruno/Desktop/data/'

if system == 'Tornado':  home_dir = '/home/bruno/'
if system == 'Shamrock': home_dir = '/home/bruno/'
if system == 'xps':      home_dir = '/home/bruno/'
if system == 'Mac_mini': home_dir = '/Users/bruno/'


def split_indices( indices, rank, n_procs ):
  n_index_total = len(indices)
  n_proc_indices = (n_index_total-1) // n_procs + 1
  indices_to_generate = np.array([ rank + i*n_procs for i in range(n_proc_indices) ])
  indices_to_generate = indices_to_generate[ indices_to_generate < n_index_total ]
  return indices_to_generate

def extend_path( dir=None ):
  if not dir: dir = os.getcwd()
  subDirectories = [x[0] for x in os.walk(dir) if x[0].find('.git')<0 ]
  sys.path.extend(subDirectories)


def print_mpi( text, rank, size,  mpi_comm):
  for i in range(size):
    if rank == i: print( text )
    time.sleep( 0.01 )
    mpi_comm.Barrier()

def print_line_flush( terminalString ):
  terminalString = '\r' + terminalString
  sys.stdout. write(terminalString)
  sys.stdout.flush()


def create_directory( dir ):
  print(("Creating Directory: {0}".format(dir) ))
  indx = dir[:-1].rfind('/' )
  inDir = dir[:indx]
  dirName = dir[indx:].replace('/','')
  dir_list = next(os.walk(inDir))[1]
  if dirName in dir_list: print( " Directory exists")
  else:
    os.mkdir( dir )
    print( " Directory created")


def get_files_names( fileKey, inDir, type='cholla' ):
  if type=='nyx': dataFiles = [f for f in listdir(inDir) if (f.find(fileKey) >= 0 )  ]
  if type == 'cholla': dataFiles = [f for f in listdir(inDir) if (isfile(join(inDir, f)) and (f.find(fileKey) >= 0 ) ) ]
  dataFiles = np.sort( dataFiles )
  nFiles = len( dataFiles )
  # index_stride = int(dataFiles[1][len(fileKey):]) - int(dataFiles[0][len(fileKey):])
  if type == 'nyx': return dataFiles, nFiles
  if type == 'cholla': return dataFiles, nFiles
