# halo_analysis


## Find Halos 

To find halos in a Cholla particles files using ROCKSTAR first you need to compile ROCKSTAR by running:

```
cd halo_finding/rockstar
make with_hdf5
```

Then change the parameters in the file **find_halos_cholla.py** and then run:

```
mpirun -n 2 python find_halos_cholla.py
```