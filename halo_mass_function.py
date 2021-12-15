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
T_start = 270
z_start = 100

a_start = 1. / ( z_start + 1 )

M_start = 1e1
M_end = 1e16
n_bins = 1000


# mass_bins_edges = np.array([ 1.9e11, 1e12 ])
mass_bins_edges = np.logspace( np.log10(M_start), np.log10(M_end), n_bins+1 )
mass_bins_edges_log = np.log( mass_bins_edges )
delta_M = mass_bins_edges[1:] - mass_bins_edges[:-1]
delta_logM = mass_bins_edges_log[1:] - mass_bins_edges_log[:-1]
mass_bins = np.sqrt( mass_bins_edges[:-1] * mass_bins_edges[1:] )

z_vals = np.linspace( 0, 20, 11 )

data_mf = {}
# model = 'tinker08'
model = 'sheth99'
for z in z_vals:
  current_a = 1./ ( z+1 )
  if model == 'tinker08': dn_dlogM = mass_function.massFunction( mass_bins, z,  model=model, mdef='200m', q_out='dndlnM' )  
  else: dn_dlogM = mass_function.massFunction( mass_bins, z,  model=model, q_out='dndlnM' )  #Press& Schechter 1974
  n_halos = dn_dlogM * delta_logM 
  N_halos = n_halos * Lbox**3
  cum_N =  N_halos.sum() - N_halos.cumsum()
  data_mf[z] = {}
  data_mf[z]['n'] = n_halos
  data_mf[z]['N'] = N_halos
  


import matplotlib
import matplotlib.font_manager
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'

prop = matplotlib.font_manager.FontProperties( fname=os.path.join('/home/bruno/fonts', "Helvetica.ttf"), size=12)


nrows = 1
ncols = 1

font_size = 18
label_size = 16
alpha = 0.8




fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10*ncols,8*nrows))

for z in z_vals:
  n = data_mf[z]['n']
  N = data_mf[z]['N']
  label = f'$z={z:.1f}$'
  ax.plot( mass_bins, N, label=label )



ax.tick_params(axis='both', which='major', direction='in', labelsize=label_size )
ax.tick_params(axis='both', which='minor', direction='in' )
ax.set_ylabel( r'$N$  in $50 \,h^{-1}\mathrm{Mpc}$ box', fontsize=font_size  )
ax.set_xlabel( r'$M_{vir}\,\,\,[\,h^{-1}\,\mathrm{M_\odot}]$', fontsize=font_size )
leg = ax.legend(loc=1, frameon=False, fontsize=font_size, prop=prop)
ax.set_xscale('log')
ax.set_yscale('log')

ax.set_ylim(1e-4, 1e13 )

figure_name = output_dir + f'N_in_box_{model}.png'
fig.savefig( figure_name, bbox_inches='tight', dpi=300 )
print( f'Saved Figure: {figure_name}' )




# h = 0.6766
# Lbox = 50000.0 #kpc
# 
# 

# 
# 
# snapshots = range(290,300)
# catalogs = load_listFiles( snapshots, halos_dir )
# 
# n_snap = 298
# snap_catalog = catalogs[n_snap]
# M_vir = snap_catalog['Mvir']
# mass_func, bin_centers = compute_mass_function( M_vir, n_bins=30 )
# 


