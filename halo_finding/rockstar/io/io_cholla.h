#ifndef _IO_CHOLLA_
#define _IO_CHOLLA_
#ifdef ENABLE_HDF5
#include <hdf5.h> /* HDF5 required */
#include <inttypes.h>
#include "../particle.h"

void load_particles_cholla(char *filename, struct particle **p, int64_t *num_p);


#endif /* ENABLE_HDF5 */
#endif /* _IO_CHOLLA_ */
