import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py as h5

root_dir = os.getcwd()
subDirectories = [x[0] for x in os.walk(root_dir)]
sys.path.extend(subDirectories)
sa_dir = os.path.dirname(os.getcwd()) + '/simulation_analysis'  
subDirectories = [x[0] for x in os.walk(sa_dir)]
sys.path.extend(subDirectories)
from tools import *
from load_halo_catalogs import load_listFiles
from load_data import load_cholla_snapshot_file
from internal_energy import get_temp
from cosmo_constants import *

h = 0.6766

Lbox = 50000.0 #kpc
n_points = 256
dx = Lbox / n_points
dv = dx**3




data_dir = '/home/bruno/Desktop/ssd_0/data/'
simulation_dir = data_dir + 'cosmo_sims/256_dm_50Mpc/'
halos_dir = simulation_dir + 'halo_files/'
snapshots_dir = simulation_dir + 'snapshots_Tvir/'

outDir = simulation_dir + 'figures/virial_temperature/'
create_directory( outDir )



T0 = 231. #K
z_0 = 100.
scale_0 = 1. / (z_0+1) 


snapshots = range(1,300)
catalogs = load_listFiles( snapshots, halos_dir )



z_list = []
t_cosmo_list = []
t_vir_list = []
halo_fracc_list = []
 
M_total = 1.0793416975505616e+16
 
nSnap = 0
for nSnap in snapshots:
  data_cholla = load_cholla_snapshot_file( nSnap, snapshots_dir , hydro=False, dm=True)
  current_z = data_cholla['current_z']
  current_a = 1./( current_z + 1 )
  t_cosmo = T0 *  ( scale_0 / current_a )**2
  z_list.append( current_z )
  t_cosmo_list.append( t_cosmo )
  # dens_dm = data_cholla['dm']['density'][...]
  # M_total = dens_dm.sum() * dv 

  halosData = catalogs[nSnap]
  nHalos = halosData['nHalos']
  if nHalos == 0:
    M_halos = 0
    T_halos = 0

  else:
    h_mass = halosData['Mvir']
    h_radius = halosData['Rvir']
    M_halos = h_mass.sum()
    m_vir = h_mass * Msun / h
    r_vir = h_radius * kpc / h * current_a
    mu = 1.
    psi = 1.
    temp_vir = psi/3. * mu * M_p / K_b * G * m_vir / r_vir 
    T_halos = (h_mass * temp_vir).sum()


  M_igm = M_total - M_halos
  T_igm = M_igm * t_cosmo
  # 
  T_avrg = ( T_igm + T_halos ) / M_total 
  t_vir_list.append( T_avrg )
  halo_fracc_list.append( nHalos)
  print ( f"n:{nSnap}  z:{current_z}  T:{T_avrg}")


data_out = np.array([ z_list, t_vir_list])  
out_file_name = outDir + 'data_Tvir_HighRes.txt'
np.savetxt( out_file_name, data_out )














