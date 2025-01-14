from __future__ import division


import numpy as np
from tigre.algorithms.iterative_recon_alg import IterativeReconAlg
from tigre.algorithms.iterative_recon_alg import decorator
from tigre.utilities.Atb import Atb
from tigre.utilities.Ax import Ax



class MLEM(IterativeReconAlg):  # noqa: D101
    __doc__ = (
        " MLEM_CBCT solves the CBCT problem using the maximum likelihood expectation maximization\n"
        " algorithm\n"
        " \n"
        "  MLEM_CBCT(PROJ,GEO,ANGLES,NITER) solves the reconstruction problem\n"
        "  using the projection data PROJ taken over ALPHA angles, corresponding\n"
        "  to the geometry descrived in GEO, using NITER iterations."
    ) + IterativeReconAlg.__doc__

    def __init__(self, proj, geo, angles, niter, **kwargs):
        # Don't precompute V and W.
        kwargs.update(dict(W=None, V=None))
        kwargs.update(dict(blocksize=angles.shape[0]))
        IterativeReconAlg.__init__(self, proj, geo, angles, niter, **kwargs)

        if self.init is None:
            self.res += 1.0

        self.W = Atb(np.ones(proj.shape, dtype=np.float32), geo, angles, gpuids=self.gpuids)
        self.W[self.W <= 0.0] = np.inf

    # Overide
    def run_main_iter(self):
        self.res[self.res < 0.0] = 0.0
        for i in range(self.niter):
            self._estimate_time_until_completion(i)

            den = Ax(self.res, self.geo, self.angles, "interpolated", gpuids=self.gpuids)
            den[den == 0.0] = np.inf
            auxmlem = self.proj / den

            # update
            img = Atb(auxmlem, self.geo, self.angles, backprojection_type="matched", gpuids=self.gpuids) / self.W

            self.res = self.res * img
            self.res[self.res < 0.0] = 0.0


mlem = decorator(MLEM, name="mlem")
