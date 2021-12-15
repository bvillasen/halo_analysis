import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
#Extend path to inclide local modules
root_dir = os.getcwd() + '/'
sub_directories = [x[0] for x in os.walk(root_dir)]
sys.path.extend(sub_directories)
from tools import *
from load_halo_catalogs import load_list_file, load_list_file_crocs
from colossus.cosmology import cosmology
from colossus.lss import mass_function


def Get_Mass_Function( h_mass, n_bins=10, bins=None, log_mass=True ):
  if log_mass: mass_log = np.log10( h_mass )
  if bins is None: bins = n_bins
  hist, bin_edges = np.histogram( mass_log, bins=bins )
  bin_centers = (bin_edges[:-1] + bin_edges[1:])/2
  n_total = hist.sum()
  hist_cumul = ( n_total - hist.cumsum() )
  return bin_centers, hist, hist_cumul

simulation_dir = data_dir + '/cosmo_sims/crocs_comparison/rei20A_mr2/'
input_dir_cholla = simulation_dir + 'halo_files_half_cell_force/'
input_dir_crocs = simulation_dir + 'crocs_halo_files/'
output_dir = simulation_dir + 'figures/'
create_directory( output_dir )

a_vals = np.array([ 0.09, 0.1, 0.1111, 0.12, 0.128, 0.135, 0.14, 0.145, 0.15, 0.155, 0.16 ]) 
z_vals = 1/a_vals - 1

Lbox = 20 #Mpc/h

cosmology.setCosmology('planck18')
cosmo = cosmology.getCurrent()
cosmo_h = cosmo.h


data = {}
for n_snap in range( 2, 12 ):
  
  print( f'Loading snap: {n_snap}' )
  halo_catalog_cholla = load_list_file( n_snap, input_dir_cholla )
  h_mass_cholla = halo_catalog_cholla['Mvir']

  halo_catalog_crocs = load_list_file_crocs( n_snap, input_dir_crocs )
  h_mass_crocs = halo_catalog_crocs['Mvir(10)']
  # h_mass_crocs = h_mass_cholla

  m_max = max( h_mass_crocs.max(), h_mass_cholla.max() )
  m_min = min( h_mass_crocs.min(), h_mass_cholla.min() )

  n_bins = 20
  bins = np.linspace( np.log10(m_min), np.log10(m_max), n_bins ) 
  bin_centers, mf_ch, cmf_ch = Get_Mass_Function( h_mass_cholla, bins=bins )
  bin_centers, mf_cr, cmf_cr = Get_Mass_Function( h_mass_crocs,  bins=bins )
  data[n_snap] = { 'bin_centers':bin_centers, 'mf_ch':mf_ch, 'mf_cr':mf_cr }
  
  bin_centers = 10**bin_centers
  mass_bins = bin_centers
  mass_bins_edges_log = bins
  delta_logM = mass_bins_edges_log[1:] - mass_bins_edges_log[:-1]
  
  model = 'tinker08'
  z = z_vals[n_snap-1]
  dn_dlogM = mass_function.massFunction( mass_bins, z,  model=model, mdef='200m', q_out='dndlnM' )
  n_halos = dn_dlogM * delta_logM 
  N_halos = n_halos * Lbox**3 / cosmo_h
  data[n_snap]['mf_an'] = N_halos

figure_width = 6
fig_width =    figure_width
fig_height =  3*figure_width
nrows = 4
ncols = 3
h_length = 4
main_length = 3


label_size = 14
figure_text_size = 14
tick_label_size_major = 15
tick_label_size_minor = 13
tick_size_major = 5
tick_size_minor = 3
tick_width_major = 1.5
tick_width_minor = 1
text_color = 'black'
legend_font_size = 14

import matplotlib
matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'


fig, ax_l = plt.subplots(nrows=nrows, ncols=ncols, figsize=(figure_width*ncols,6*nrows))
plt.subplots_adjust( hspace = 0.15, wspace=0.18)

for i in range(nrows):
  for j in range(ncols):
    fig_id = i*ncols + j 
    if fig_id >= 10: continue
    ax = ax_l[i][j]
    
    n_snap = fig_id + 2
    data_snap = data[n_snap]
    bin_centers = data_snap['bin_centers']
    mf_ch = data_snap['mf_ch']
    mf_cr = data_snap['mf_cr']
    mf_an = data_snap['mf_an']
    ax.plot( bin_centers, mf_cr, label='Crocs' )
    ax.plot( bin_centers, mf_ch, label='Cholla' )
    ax.plot( bin_centers, mf_an, '--', c='k', label='Tinker (2008)' )
  
    z = z_vals[fig_id+1]
    ax.text(0.9, 0.93, r'$z=${0:.1f}'.format(z), horizontalalignment='center',  verticalalignment='center', transform=ax.transAxes, fontsize=figure_text_size, color=text_color) 

    leg = ax.legend(  loc=3, frameon=False, fontsize=legend_font_size    )
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    
    ax.set_ylabel( r' $N (m = M_{\mathrm{vir}})$', fontsize=label_size, color= text_color )
    ax.set_xlabel( r'$ M_{\mathrm{vir}}  [h^{-1}M_\odot]$', fontsize=label_size, color= text_color )
    
   
    ax.tick_params(axis='both', which='major', color=text_color, labelcolor=text_color, labelsize=tick_label_size_major, size=tick_size_major, width=tick_width_major, direction='in' )
    ax.tick_params(axis='both', which='minor', color=text_color, labelcolor=text_color, labelsize=tick_label_size_minor, size=tick_size_minor, width=tick_width_minor, direction='in')


figure_name = output_dir + 'mass_function_comparison.png'
fig.savefig( figure_name, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor() )
print( f'Saved Figure: {figure_name}' )

