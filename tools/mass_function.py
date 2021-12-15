import numpy as np



def compute_mass_function( mass, n_bins=30 ):
  m_min, m_max = mass.min()*0.99, mass.max()*1.01
  bin_edges = np.logspace( np.log10(m_min), np.log10(m_max), n_bins+1 )
  hist, bin_edges = np.histogram( mass, bins=bin_edges )
  bin_centers = np.sqrt( bin_edges[1:] * bin_edges[:-1])
  return hist, bin_centers