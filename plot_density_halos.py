import sys, os, time
from subprocess import call
import matplotlib
import matplotlib.pyplot as plt
root_dir = os.getcwd()
sys.path.append(root_dir + '/tools')
from tools import *
from load_data import load_snapshot_data_distributed
from load_halo_catalogs import load_list_file
import palettable.scientific.sequential as scientific
import palettable.cmocean.sequential as cmocean


n_cells = 1024
L_Mpc = 25

sim_name = f'{n_cells}_{L_Mpc}Mpc_cdm'
density_type = 'cic'

data_dir = '/data/groups/comp-astro/bruno/'
base_dir = data_dir + f'cosmo_sims/wdm_sims/tsc/'
sim_dir  = base_dir + f'{sim_name}/{density_type}/'
input_dir = sim_dir + 'snapshot_files/'
halos_dir = sim_dir + 'halo_files/'
output_dir = root_dir + '/'
create_directory( output_dir )

Lbox = L_Mpc * 1e3    #kpc/h
box_size = [ Lbox, Lbox, Lbox ]
grid_size = [ n_cells, n_cells, n_cells ] #Size of the simulation grid
precision = np.float64
fields = [ 'density' ]

snap_id = 8

# Load the halo catalog
halo_data = load_list_file( snap_id, halos_dir )
halo_mass = halo_data['Mvir']
mass_min = 1e10
indices = halo_mass > mass_min
halo_mass = halo_mass[indices]
halo_pos_x = halo_data['X'][indices]
halo_pos_y = halo_data['Y'][indices]
halo_pos_z = halo_data['Z'][indices]
halo_radius = halo_data['Rvir'][indices] * 1e-3 #convert to Mpc/h
halo_radius = halo_radius**2 * 70  #Increase the size for image, the units in the image are pixel^2

data_type = 'hydro'
# data_type = 'particles'
snap_data = load_snapshot_data_distributed( data_type, fields,  snap_id, input_dir,  box_size, grid_size, precision  )
z = snap_data['Current_z']
density = snap_data['density']
max_dens = 0.0002 * density.max()
density[density > max_dens] = max_dens
 
# proj = ( density**2 ).sum(axis=0) / density.sum(axis=0)  
proj = density.sum(axis=0)
log_proj = np.log10( proj )

label_size = 12

import matplotlib
matplotlib.font_manager.findSystemFonts(fontpaths=['fonts/Helvetica'], fontext='ttf')
matplotlib.rcParams['font.sans-serif'] = "Helvetica"
matplotlib.rcParams['font.family'] = "sans-serif"
matplotlib.rcParams['mathtext.fontset'] = 'cm'
matplotlib.rcParams['mathtext.rm'] = 'serif'

nrows, ncols = 1, 1
fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6*ncols,6*nrows))

# cmap = scientific.Davos_20.mpl_colormap
cmap = cmocean.Deep_20_r.mpl_colormap
im = ax.imshow( log_proj, cmap=cmap, extent=(0, L_Mpc, 0, L_Mpc), origin='lower' )
# cbar = plt.colorbar( im, ax=ax )
# cbar.set_label( r'$  \log_{10} \, \Delta_\mathrm{DM} $', fontsize=label_size )


# cmap = matplotlib.cm.get_cmap('YlOrRd_r')
cmap = matplotlib.cm.get_cmap('hot')
im= ax.scatter( halo_pos_x, halo_pos_y, s=halo_radius, c=halo_radius, facecolors='none', cmap=cmap, alpha=0.5 )
cbar = plt.colorbar( im, ax=ax, shrink=0.75, pad=0.02 )
cbar.set_label( r'$  R_\mathrm{vir} $', fontsize=label_size )
cbar.ax.tick_params(axis='both', which='major', direction='in'  )

ax.set_xticks([])
ax.set_yticks([])

plt.text( L_Mpc*0.05, L_Mpc*0.92, r'$z$={0:.1f}'.format(z), fontsize=10, color='white'  )

line_y = L_Mpc* 0.05
line_x = L_Mpc* 0.07
line_length = 5 * 0.6766
ax.text( line_x+0.1 , line_y+0.4, '5 cMpc', fontsize=10, color='white'  )
ax.plot( [line_x, line_x+line_length], [line_y, line_y], lw=1.5, c='white')


figure_name = output_dir + f'density_halos_{data_type}_{snap_id}.png'
fig.savefig( figure_name, bbox_inches='tight', dpi=300, facecolor=fig.get_facecolor() )
print( f'Saved Figure: {figure_name}' )
