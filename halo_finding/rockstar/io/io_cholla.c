#ifdef ENABLE_HDF5
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <inttypes.h>
#include <math.h>
#include <rpc/types.h>
#include <rpc/xdr.h>
#include "../check_syscalls.h"
#include "../universal_constants.h"
#include "../config_vars.h"
#include "../config.h"
#include <hdf5.h> /* HDF5 required */
#include <inttypes.h>
// #include "io_cholla.h"
#include "../particle.h"


void load_particles_cholla(char *filename, struct particle **p, int64_t *num_p){

  // fprintf(stderr, "Loading CHOLLA file.\n");

  hid_t  file_id;
  herr_t  status;

  // open the file
  file_id = H5Fopen(filename, H5F_ACC_RDONLY, H5P_DEFAULT);
  if (file_id < 0) {
    printf("Unable to open input file.\n");
    exit(0);
  }

  int64_t nParts_local;
  double current_a;
  double particle_mass;
  double hubble_0, Omega_M, Omega_L; 

  hid_t     attribute_id;
  // attribute_id = H5Aopen(file_id, "nParts_local", H5P_DEFAULT);
  attribute_id = H5Aopen(file_id, "n_particles_local", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_ULONG, &nParts_local);
  status = H5Aclose(attribute_id);
  
  // attribute_id = H5Aopen(file_id, "n_particles_total", H5P_DEFAULT);
  // status = H5Aread(attribute_id, H5T_NATIVE_ULONG, &nParts_total);
  // status = H5Aclose(attribute_id);

  attribute_id = H5Aopen(file_id, "current_a", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_DOUBLE, &current_a);
  status = H5Aclose(attribute_id);

  attribute_id = H5Aopen(file_id, "particle_mass", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_DOUBLE, &particle_mass);
  status = H5Aclose(attribute_id);
  
  attribute_id = H5Aopen(file_id, "h0", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_DOUBLE, &hubble_0);
  status = H5Aclose(attribute_id);

  attribute_id = H5Aopen(file_id, "Omega_M", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_DOUBLE, &Omega_M);
  status = H5Aclose(attribute_id);

  attribute_id = H5Aopen(file_id, "Omega_L", H5P_DEFAULT);
  status = H5Aread(attribute_id, H5T_NATIVE_DOUBLE, &Omega_L);
  status = H5Aclose(attribute_id);


  SCALE_NOW = current_a;
  // BOX_SIZE = 50.0;
  Om = Omega_M;
  Ol = Omega_L;
  h0 = hubble_0;                //[km/s / Mpc]
  
  
  // printf(" TOTAL_PARTICLES: %ld  \n", TOTAL_PARTICLES );
  // printf(" Box size %f\n", BOX_SIZE );
  // printf(" current_a: %f\n", SCALE_NOW);
  // printf(" h0: %f\n", h0);
  // printf(" Omega_M: %f\n", Om );
  // printf(" Omega_L: %f\n", Ol );


  // PARTICLE_MASS = particle_mass;
  PARTICLE_MASS = Om*CRITICAL_DENSITY * pow(BOX_SIZE, 3) / TOTAL_PARTICLES;

  AVG_PARTICLE_SPACING = cbrt(PARTICLE_MASS / (Om*CRITICAL_DENSITY));
  // printf("Particle mass: %f    %f\n", particle_mass, PARTICLE_MASS );
  // printf(" Loading %ld particles\n", nParts_local );


  check_realloc_s((*p), ((*num_p) + nParts_local), sizeof(struct particle));
  // printf("  Particles allocated: %ld \n", *num_p + nParts_local);



  char gid[10] = "/";
  hid_t HDF_GroupID = H5Gopen(file_id, gid);
  if (HDF_GroupID < 0) {
    fprintf(stderr, "[Error] Failed to open group %s in HDF5 file %s!\n", gid, filename);
    exit(1);
  }

  hid_t HDF_DatasetID;
  double      *dataset_buffer_px;
  double      *dataset_buffer_py;
  double      *dataset_buffer_pz;
  double      *dataset_buffer_vx;
  double      *dataset_buffer_vy;
  double      *dataset_buffer_vz;
  // double      *dataset_buffer_m;

  char dataid_px[10] = "pos_x";
  dataset_buffer_px = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_px);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_px, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_px);
  status = H5Dclose(HDF_DatasetID);

  char dataid_py[10] = "pos_y";
  dataset_buffer_py = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_py);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_py, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_py);
  status = H5Dclose(HDF_DatasetID);

  char dataid_pz[10] = "pos_z";
  dataset_buffer_pz = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_pz);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_pz, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_pz);
  status = H5Dclose(HDF_DatasetID);

  char dataid_vx[10] = "vel_x";
  dataset_buffer_vx = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_vx);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_vx, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_vx);
  status = H5Dclose(HDF_DatasetID);

  char dataid_vy[10] = "vel_y";
  dataset_buffer_vy = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_vy);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_vy, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_vy);
  status = H5Dclose(HDF_DatasetID);


  char dataid_vz[10] = "vel_z";
  dataset_buffer_vz = (double *) malloc(nParts_local*sizeof(double));
  HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_vz);
  if (HDF_DatasetID < 0) {
    fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_vz, filename);
    exit(1);
  }
  status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_vz);
  status = H5Dclose(HDF_DatasetID);

  //
  // char dataid_m[10] = "mass";
  // dataset_buffer_m = (double *) malloc(nParts_local*sizeof(double));
  // HDF_DatasetID = H5Dopen(HDF_GroupID, dataid_m);
  // if (HDF_DatasetID < 0) {
  //   fprintf(stderr, "[Error] Failed to open dataset %s/%s in HDF5 file %s!\n", gid, dataid_m, filename);
  //   exit(1);
  // }
  // status = H5Dread(HDF_DatasetID, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_m);
  // status = H5Dclose(HDF_DatasetID);


  double colla_legnth_conv = 1e-3;
  double colla_vel_conv = sqrt(SCALE_NOW) ;
  for(int i = 0; i < nParts_local; i++) {
    (*p)[i+(*num_p)].id = i+(*num_p);
    (*p)[i+(*num_p)].pos[0] = dataset_buffer_pz[i] * colla_legnth_conv;
    (*p)[i+(*num_p)].pos[1] = dataset_buffer_py[i] * colla_legnth_conv;
    (*p)[i+(*num_p)].pos[2] = dataset_buffer_px[i] * colla_legnth_conv;
    (*p)[i+(*num_p)].pos[3] = dataset_buffer_vz[i] * colla_vel_conv;
    (*p)[i+(*num_p)].pos[4] = dataset_buffer_vy[i] * colla_vel_conv;
    (*p)[i+(*num_p)].pos[5] = dataset_buffer_vx[i] * colla_vel_conv;
  }



  *num_p += nParts_local;

  // // close the file
  // hid_t     attribute_id, dataset_id;
  // // Real      *dataset_buffer_px;
  // double      *dataset_buffer_py;
  // // Real      *dataset_buffer_pz;
  // // Real      *dataset_buffer_vx;
  // // Real      *dataset_buffer_vy;
  // // Real      *dataset_buffer_vz;
  // // Real      *dataset_buffer_m;
  // dataset_buffer_py = (double *) malloc(256*256*256/8*sizeof(double));
  // dataset_id = H5Dopen(file_id, "pos_y" );
  // status = H5Dread(dataset_id, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dataset_buffer_py);
  // status = H5Dclose(dataset_id);

  status = H5Fclose(file_id);
  free(dataset_buffer_px);
  free(dataset_buffer_py);
  free(dataset_buffer_pz);
  free(dataset_buffer_vx);
  free(dataset_buffer_vy);
  free(dataset_buffer_vz);
  // free(dataset_buffer_m);
}

#endif /* ENABLE_HDF5 */
