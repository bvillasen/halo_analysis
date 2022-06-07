import sys, os
import numpy as np
import matplotlib.pyplot as plt
import h5py as h5
#Extend path to inclide local modules
root_dir = os.getcwd() + '/'
sub_directories = [x[0] for x in os.walk(root_dir)]
sys.path.extend(sub_directories)
from tools import *
from load_halo_catalogs import load_list_file, load_list_file_crocs, find_parents
from colossus.cosmology import cosmology
from colossus.lss import mass_function


def Get_Mass_Function( h_mass, n_bins=10, bins=None, log_mass=True ):
  if log_mass: mass_log = np.log10( h_mass )
  if bins is None: bins = n_bins
  hist, bin_edges = np.histogram( mass_log, bins=bins )
  bin_centers = (bin_edges[:-1] + bin_edges[1:])/2
  n_total = hist.sum()
  hist_cumul = ( n_total - hist.cumsum() )
  if log_mass: bin_centers = 10**bin_centers
  return bin_centers, hist, hist_cumul

extra_name = '_over10'
rockstar_dir = home_dir + 'halo_analysis/halo_finding/rockstar/'
simulation_dir = data_dir + 'cosmo_sims/crocs_comparison/rei40A_mr2/'
input_dir_cholla = simulation_dir + f'cholla_halo_files{extra_name}/'
input_dir_crocs  = simulation_dir + 'crocs_halo_files/'
output_dir = simulation_dir + 'figures/'
create_directory( output_dir )

Lbox = 40 #Mpc/h


crocs_files = [ f for f in os.listdir(input_dir_crocs) ]
crocs_files.sort()
n_files = len( crocs_files )
crocs_a_vals = np.array([ float(f[f.find('_')+1:f.find('.l')]) for f in crocs_files ])
z_vals = 1/crocs_a_vals - 1


cholla_indices = np.arange( 1, 11, 1 )
# cholla_indices = np.arange( 1, 2, 1 )

# Get halo/sub_halo category
get_subhalos = False
if get_subhalos:
  print( 'Getting parent IDs')
  for file_indx in cholla_indices:
    in_file_name = input_dir_cholla + f'out_{file_indx}.list'
    out_file_name = input_dir_cholla + f'catalog_{file_indx:02}.dat'
    find_parents(in_file_name, Lbox, out_file_name, rockstar_dir )



 
# cosmology.setCosmology('planck18')
# cosmo = cosmology.getCurrent()

params = {'flat': True, 'H0': 68.14, 'Om0': 0.3036, 'Ob0': 0.0479, 'sigma8': 0.81, 'ns': 0.95}
cosmology.addCosmology('myCosmo', params)
cosmo = cosmology.setCosmology('myCosmo')
cosmo_h = cosmo.h

crocs_raw = False
exclude_subhalos = False
print( f'Crocs Raw: {crocs_raw}' )
print( f'Exclude Subhalos: {exclude_subhalos}')

snap_id_to_load = 9

data = {}
for snap_id in range( 0, 10 ):

  if snap_id != snap_id_to_load: continue

  print( f'\nLoading snap: {snap_id}' )
  crocs_file = input_dir_crocs + crocs_files[snap_id]
  halo_catalog_crocs = load_list_file_crocs( crocs_file )
  h_mass_crocs = halo_catalog_crocs['Mvir(10)']
  p_ids = halo_catalog_crocs['pid(5)']
  cr_x = halo_catalog_crocs['x(17)']
  cr_y = halo_catalog_crocs['y(18)']
  cr_z = halo_catalog_crocs['z(19)']
  halos = np.where( p_ids < 0  )[0]
  subhalos = np.where( p_ids >= 0  )[0]
  print( f'Subhalos/Halos: {len(subhalos)/len(halos)}')  
  if exclude_subhalos: 
    h_mass_crocs = h_mass_crocs[halos]
  
  
  if not crocs_raw: h_mass_crocs /= cosmo_h
  min_mass = h_mass_crocs.min()

  cholla_indx = cholla_indices[snap_id]
  file_name = f'catalog_{cholla_indx:02}.dat' 
  halo_catalog_cholla = load_list_file( cholla_indx, input_dir_cholla, file_name=file_name )
  h_mass_cholla = halo_catalog_cholla['Mvir']
  p_ids = halo_catalog_cholla['PID']
  ch_x = halo_catalog_cholla['X']
  ch_y = halo_catalog_cholla['Y']
  ch_z = halo_catalog_cholla['Z']
  halos = np.where( p_ids < 0  )[0]
  subhalos = np.where( p_ids >= 0  )[0]
  print( f'Subhalos/Halos: {len(subhalos)/len(halos)}')  
  if exclude_subhalos: 
    h_mass_cholla = h_mass_cholla[halos]
  # h_mass_cholla = h_mass_cholla[h_mass_cholla >= min_mass ]
    
  n_halos_ch = len(h_mass_cholla)
  n_halos_cr = len(h_mass_crocs)
  print( f'N halos cholla: {n_halos_ch}' )
  print( f'N halos crocs:  {n_halos_cr}' )

  max_id_cr = np.where( h_mass_crocs == h_mass_crocs.max() )[0]
  max_id_ch = np.where( h_mass_cholla == h_mass_cholla.max() )[0]
  
  data[snap_id] = { 'crocs' :{'x':cr_x, 'y':cr_y, 'z':cr_z, 'm':h_mass_crocs },
                    'cholla':{'x':ch_x, 'y':ch_y, 'z':ch_z, 'm':h_mass_cholla } }



figure_width = 6
fig_width =    figure_width
fig_height =  0.5*figure_width
nrows = 1
ncols = 2
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



snap_id = snap_id_to_load

delta_logM = 1

m_cr = data[snap_id]['crocs']['m']
m_ch = data[snap_id]['cholla']['m']
mass_h = max( m_cr.max(), m_ch.max() )
mass_l = 10**( np.log10(mass_h) - delta_logM )

fig, ax_l = plt.subplots(nrows=nrows, ncols=ncols, figsize=(figure_width*ncols,6*nrows))
plt.subplots_adjust( hspace = 0.15, wspace=0.18)

ax = ax_l[0]
data_sim = data[snap_id]['crocs']
m = data_sim['m']
indices = (m >= mass_l) * (m<=mass_h)
x = data_sim['x'][indices]
y = data_sim['y'][indices]
z = data_sim['z'][indices]
m = data_sim['m'][indices]
s = np.log10(m)
ax.scatter( x, y, s=s  )

ax = ax_l[1]
data_sim = data[snap_id]['cholla']
m = data_sim['m']
indices = (m >= mass_l) * (m<=mass_h)
x = data_sim['x'][indices]
y = data_sim['y'][indices]
z = data_sim['z'][indices]
m = data_sim['m'][indices]
s = np.log10(m) 
ax.scatter( z, y, s=s  )



z = z_vals[snap_id]
ax.text(0.9, 0.93, r'$z=${0:.1f}'.format(z), horizontalalignment='center',  verticalalignment='center', transform=ax.transAxes, fontsize=figure_text_size, color=text_color) 

leg = ax.legend(  loc=3, frameon=False, fontsize=legend_font_size    )




# ax.set_ylabel( r' $N (M = M_{\mathrm{vir}})$', fontsize=label_size, color= text_color )
# ax.set_xlabel( r'$ M_{\mathrm{vir}}  [h^{-1}M_\odot]$', fontsize=label_size, color= text_color )
# 

ax.tick_params(axis='both', which='major', color=text_color, labelcolor=text_color, labelsize=tick_label_size_major, size=tick_size_major, width=tick_width_major, direction='in' )
ax.tick_params(axis='both', which='minor', color=text_color, labelcolor=text_color, labelsize=tick_label_size_minor, size=tick_size_minor, width=tick_width_minor, direction='in')


figure_name = output_dir + f'halo_positions'
if crocs_raw: figure_name += '_crocs_raw'
if exclude_subhalos: figure_name += '_nosubhalos'
figure_name += '.png'
fig.savefig( figure_name, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor() )
print( f'Saved Figure: {figure_name}' )

