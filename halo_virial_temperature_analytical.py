import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
from colossus.cosmology import cosmology
from colossus.lss import mass_function

root_dir = os.getcwd()
subDirectories = [x[0] for x in os.walk(root_dir)]
sys.path.extend(subDirectories)
sa_dir = os.path.dirname(os.getcwd()) + '/simulation_analysis'  
subDirectories = [x[0] for x in os.walk(sa_dir)]
sys.path.extend(subDirectories)
from tools import *
from load_halo_catalogs import load_listFiles
from internal_energy import get_temp
from cosmo_constants import *
from mass_function import compute_mass_function
from virial_temperature import get_virial_radius, get_virial_temp


data_dir = '/home/bruno/Desktop/ssd_0/data/'
simulation_dir = data_dir + 'cosmo_sims/256_dm_50Mpc/'
halos_dir = simulation_dir + 'halo_files/'
snapshots_dir = simulation_dir + 'snapshots_Tvir/'
output_dir   = simulation_dir + 'figures/virial_temperature/'
create_directory( output_dir )




cosmology.setCosmology('planck18')
cosmo = cosmology.getCurrent()
cosmo_h = cosmo.h



Lbox = 50   #Mpc/h
rho_mean = cosmo.rho_m(0)  #Mean density h^2 Msun kpc^-3
rho_crit = cosmo.rho_c(0)  #Mean density h^2 Msun kpc^-3
M_total = rho_mean * (Lbox*1e3)**3   #h^-1 Msun 
T_start = 231 #k
z_start = 100

a_start = 1. / ( z_start + 1 )



# m_cut = None
m_cut = True



M_start = 1e1
M_end = 1e18
n_bins = 1000

if m_cut:
  M_start = 1.286e+09 * 100
  M_end = 1e18


# mass_bins_edges = np.array([ 1.9e11, 1e12 ])
mass_bins_edges = np.logspace( np.log10(M_start), np.log10(M_end), n_bins+1 )
mass_bins_edges_log = np.log( mass_bins_edges )
delta_M = mass_bins_edges[1:] - mass_bins_edges[:-1]
delta_logM = mass_bins_edges_log[1:] - mass_bins_edges_log[:-1]
mass_bins = np.sqrt( mass_bins_edges[:-1] * mass_bins_edges[1:] )
radius_bins = get_virial_radius( mass_bins, cosmo_h, rho_crit )

T_vals = [] 

z_vals = np.linspace( 0, 100, 1000 )

model = 'sheth99'


for z in z_vals:

  current_a = 1./ ( z+1 )
  dn_dlogM = mass_function.massFunction( mass_bins, z,  model=model, q_out='dndlnM' )  #Press& Schechter 1974
  n_halos = dn_dlogM * delta_logM 
  N_halos = n_halos * Lbox**3
  M_halos = N_halos * mass_bins
  T_halos = get_virial_temp( mass_bins, radius_bins, cosmo_h, z )
  T_vir_halos = ( T_halos * M_halos ).sum() / M_total
  M_igm = M_total - M_halos.sum()
  T_igm = T_start * ( a_start / current_a )**2 * M_igm / M_total
  T_mean = T_vir_halos + T_igm
  print( f'z: {z:0.1f}   Mfrac_halos: {M_halos.sum()/M_total:.2e}   T_mean: {T_mean:.2e}' )
  T_vals.append( T_mean ) 
  
  
T_vals = np.array( T_vals ) 
data = np.array( [ z_vals, T_vals ])

file_name = output_dir + f'data_Tvir_analytical_{model}.txt'
if m_cut: file_name = output_dir + f'data_Tvir_analytical_{model}_mcut.txt'
np.savetxt( file_name, data )
print( f'Saved File: {file_name}')


