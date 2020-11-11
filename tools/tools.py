import os, sys
from os import listdir
from os.path import isfile, join
import numpy as np
import h5py as h5
import time


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
