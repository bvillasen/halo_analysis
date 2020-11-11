import sys, os, time
from subprocess import call

currentDirectory = os.getcwd()
#Add Modules from other directories
devDirectory = '/home/bruno/Desktop/Dropbox/Developer/'
toolsDirectory = devDirectory + "tools/"
sys.path.append( toolsDirectory )
from tools import *
#import haloAnalysis as haloA

# dataDir = "/home/bruno/Desktop/data/galaxies/cosmo_512/data/"
dataDir = "/media/bruno/hard_drive_1/data/cosmo/256/"
rockstarDir = devDirectory + 'cosmo_sims/halo_finding/rockstar/'
rockstarComand = rockstarDir + 'rockstar'
rockstarConfig = dataDir + 'halos/rockstar.cfg'
consitentDir = devDirectory + 'cosmo_sims/halo_finding/consistent-trees/'
consitentComand = consitentDir + 'gen_sussing_forests'

call(["perl", consitentComand, rockstarConfig ])

