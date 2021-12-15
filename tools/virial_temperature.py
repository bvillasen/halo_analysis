import numpy as np


#Boltazman constant
K_b = 1.38064852e-23 #m2 kg s-2 K-1
#Mass of proton
M_p = 1.6726219e-27 #kg
#Gravitational constant
G = 6.67408e-11 # m3 kg-1 s-2
#Parsec
pc = 3.0857e16  #m
kpc = 1e3 * pc
Mpc = 1e6 * pc
#Solare Mass
Msun = 1.98847e30  #kg


def get_virial_radius( M_vir, h, rho_c, delta=None ):
  #M_vir: Virial Mass  h^-1 Msun
  #halo_radius: comoving radius #h^-1 kpc
  #rho_c: critical density h^2 Msun kpc^-3 
  if not delta: delta = 18*np.pi**2
  r_vir = ( 3 * M_vir / ( 4 * np.pi * delta * rho_c ) )**(1./3)
  return r_vir

def get_virial_temp( M_vir, halo_radius, h, current_z, mu=1, psi=1 ):
  #M_vir: Virial Mass  h^-1 Msun
  #halo_radius: comoving radius #h^-1 kpc
  #Hubble parameter
  #rho_c: critical density h^2 Msun kpc^-3 
  current_a = 1 / ( current_z + 1 )
  m_vir = M_vir * Msun / h
  r_vir = halo_radius * kpc / h * current_a
  temp_vir = psi/3. * mu * M_p / K_b * G * m_vir / r_vir 
  return temp_vir
