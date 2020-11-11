import numpy as np
import os, sys

def load_asciiFiles(  snapshots, nFilesPerSnapshot, inputDir,  ):
  halosData = {}
  for snapshot in snapshots:
    halosData[snapshot] = {}
    asciiData_all = []
    for box in range(nFilesPerSnapshot):
      asciiFile = inputDir + 'halos_{0}.{1}.ascii'.format(snapshot, box )
      asciiString = open( asciiFile ).read()
      headers = asciiString.splitlines()[0][1:].split()
      nColums = len( headers )
      with np.warnings.catch_warnings():
        np.warnings.simplefilter("ignore")
        asciiData = np.loadtxt( asciiFile )
      if asciiData.shape[0] == 0: continue
      if len(asciiData.shape) == 1 :
        asciiData = asciiData.reshape(1,nColums)
      asciiData_all.append( asciiData )
    if len(asciiData_all) == 0:
      asciiData_out = -1*np.ones([1,nColums])
      halosData[snapshot]['nHalos'] = 0
    else:
      asciiData_out = np.concatenate( asciiData_all )
      halosData[snapshot]['nHalos'] = len(asciiData_out)
    # print snapshot, asciiData_out.shape[0]
    # if asciiData.shape[0] == 0: halosData[snapshot] = False
    # else:
    for i in range( nColums ):
      halosData[snapshot][headers[i]] = asciiData_out[:,i]
  return halosData

def load_listFiles( snapshots, outputDir  ):
  # ms_nHalos = []
  ms_halosData = {}
  for snapshot in snapshots:
    listFile = outputDir + 'out_{0}.list'.format(snapshot)
    listString = open( listFile ).read()
    headers = listString.splitlines()[0][1:].split()
    nColums = len( headers )
    listData = np.loadtxt( listFile )
    if len(listData) == 0:
      ms_halosData[snapshot] = {}
      ms_halosData[snapshot]['nHalos'] = listData.shape[0]
    else:
      ms_halosData[snapshot] = { headers[i]: listData[:,i] for i in range( nColums ) }
      ms_halosData[snapshot]['nHalos'] = listData.shape[0]
  return ms_halosData



def find_parents(snap, box_size, inputDir, rks_dir, outputFile):
  parents_cmnd = rks_dir + 'util/find_parents'
  list_file = inputDir + 'out_{0}.list'.format(snap)
  print(' Loading file: ', list_file)
  # print parents_cmnd, list_file, str(box_size), '>', outputFile
  cmd = '{0} {1} {2:.1f} > {3}'.format( parents_cmnd, list_file, box_size, inputDir + outputFile )
  # print cmd
  os.system( cmd )
  print(' Saved file: ', outputFile)
  # call([parents_cmnd, list_file, str(box_size), '>', outputFile ])
  # p = Popen([parents_cmnd, list_file, str(box_size)  ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  # output, err = p.communicate()
  
def load_parents_list_file( snapshot, outputDir ):
  listFile = outputDir + 'catalog_{0}.dat'.format(snapshot)
  listString = open( listFile ).read()
  headers = listString.splitlines()[0][1:].split()
  nColums = len( headers )
  listData = np.loadtxt( listFile )
  # print nColums
  if len(listData) == 0:
    ms_halosData = {}
    ms_halosData['nHalos'] = listData.shape[0]
  else:
    if len(listData.shape) == 1:
      ms_halosData = { headers[i]: np.array([listData[i]]) for i in range( nColums ) }
      ms_halosData['nHalos'] = 1
    else:
      ms_halosData = { headers[i]: listData[:,i] for i in range( nColums ) }
      ms_halosData['nHalos'] = listData.shape[0]
  return ms_halosData

def load_catalog( start_snap, snap, boxSize, inputDir, rks_dir  ):
  snap_name = 'snapshot_{0:03}'.format( snap )
  catalog_name = 'snap_{0:03}.catalog'.format( snap )
  files_inDir = os.listdir( inputDir )
  if catalog_name not in files_inDir:
    print(' Finding parents for snap: {0}'.format(snap - start_snap))
    find_parents( snap - start_snap , boxSize, inputDir, rks_dir, catalog_name  )
  listFile = inputDir + catalog_name
  print(' Loading Catatalog: ', listFile)
  listString = open( listFile ).read()
  headers = listString.splitlines()[0][1:].split()
  nColums = len( headers )
  listData = np.loadtxt( listFile )
  halosData = { headers[i]: listData[:,i] for i in range( nColums ) }
  halosData['nHalos'] = listData.shape[0]
  return halosData


def get_parents_ids( snap, box_size, inputDir, rks_dir ):
  from subprocess import Popen, PIPE
  parents_cmnd = rks_dir + 'util/find_parents'
  list_file = inputDir + 'out_{0}.list'.format(snap)
  # print parents_cmnd, list_file, box_size
  # return_call = call([parents_cmnd, list_file, str(box_size) ])
  p = Popen([parents_cmnd, list_file, str(box_size) ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
  output, err = p.communicate()
  rc = p.returncode
  output = output.split('\n')
  start = 0
  while output[start][0] == '#':
    start += 1
  data = output[start:]
  parents = { }
  data_list = []
  for line in data:
    if line == '': continue
    halo_id, desc_id, mass, parent_id = line.split()
    data_list.append([ int(halo_id), float(mass), int(parent_id)  ])
    parents[int(halo_id)] = ( float(mass), int(parent_id) )
  parents_data = np.array( data_list )
  sortedIndxs = np.argsort(parents_data[:,0])
  parents_data = parents_data[sortedIndxs]
  return parents, parents_data

def find_bgc2_snap_files( snap, inputDir ):
  snap_str = '{0:03}'.format(snap)
  bgc2_files = [ f for f in os.listdir( inputDir ) if f.find('.bgc2')>-1]
  snap_files = [ inputDir + f for f in bgc2_files if f.find( snap_str )>-1 ]
  snap_files.sort()
  return snap_files


def finish_bgc2( start_snap, snap, inputDir, rks_dir  ):
  snap_number = snap-start_snap
  finish_bgc2_cmd = rks_dir + 'util/finish_bgc2'
  cnfig = inputDir + 'rockstar.cfg'
  cmd = '{0} -c {1} -s {2}'.format( finish_bgc2_cmd, cnfig, snap_number )
  print(' Finishing bgc2 catalog for snap: ', snap)
  os.system( cmd )
  print('  Completed bgc2 ')

def get_catalog_from_bgc2( start_snap, snap, inputDir, rks_dir  ):
  snap_number = snap-start_snap
  print(' Geting Catatalog from bgc2 for snap: ', snap)
  ascii_bgc2_cmd = rks_dir + 'util/bgc2_to_ascii'
  cnfig = inputDir + 'rockstar.cfg'
  bgc2_output_halos = inputDir + 'snap_{0:03}_bgc2.catalog'.format(snap)
  cmd = '{0} -c {1} -s {2} > {3}'.format( ascii_bgc2_cmd, cnfig, snap_number, bgc2_output_halos )
  os.system( cmd )
  print('  Catatalog from bgc2 saved: ', bgc2_output_halos)


def load_catalog_bgc2( start_snap, snap, inputDir, rks_dir  ):
  snap_number = snap-start_snap
  bgc2_output_halos = 'snap_{0:03}_bgc2.catalog'.format(snap)
  files_inDir = os.listdir( inputDir )
  if bgc2_output_halos not in files_inDir: get_catalog_from_bgc2( start_snap, snap, inputDir, rks_dir  )
  print(' Loading bgc2 Catatalog: ', bgc2_output_halos)
  listFile = inputDir + bgc2_output_halos
  listString = open( listFile ).read()
  headers = listString.splitlines()[0][1:].split()
  nColums = len( headers )
  listData = np.loadtxt( listFile )
  halosData = { headers[i]: listData[:,i] for i in range( nColums ) }
  halosData['nHalos'] = listData.shape[0]
  return halosData
