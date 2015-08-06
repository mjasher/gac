import numpy as np
import scipy.linalg
import scipy.stats

"""
TODO:
* stability condition of dt vs delr,delc,dv (http://www.timteatro.net/2010/10/29/performance-python-solving-the-2d-diffusion-equation-with-numpy/)
* wet/dry
* Vertical Flow Correction Under Dewatered Conditions
* SPECIFIC YIELD (transient and convertible) vs SPECIFIC STORAGE OR STORAGE COEFFICIENT (transient) 
* harmonic mean, +1/2, -1/2 indexing
* laytyp confined/unconfined
* flopy (nlay,nrow,ncol) or documentation (nrow,ncol,nlay) or MODFLOW (NCOL,NROW,NLAY)???
* sparse
* ctypes 
* RIV
* GHB
* WEL
* RCH


scipy.sparse.linalg.cgs allows callbac, SC1 and SC2 are changes each iteration (multiple times per timestep)
"""



# Model domain and grid definition
Lx = 1000.
Ly = 1000.
ztop = 0.
zbot = -50.
nrow, ncol, nlay = 10, 10, 1
delr = Lx/ncol
delc = Ly/nrow
delv = (ztop - zbot) / nlay
botm = np.linspace(ztop, zbot, nlay + 1)
# dis = flopy.modflow.ModflowDis(mf, nlay, nrow, ncol, delr=delr, delc=delc, top=ztop, botm=botm[1:])

# Variables for the BAS package
# NOTE: change from flopy's (nlay,nrow,ncol) to (nrow,ncol,nlay)
ibound = np.ones((nrow,ncol,nlay), dtype=np.int32)
ibound[:, 0, :] = -1
ibound[:, -1, :] = -1
strt = np.ones((nrow,ncol,nlay), dtype=np.float32)
strt[:, 0, :] = 10.
strt[:, -1, :] = 0.
# bas = flopy.modflow.ModflowBas(mf, ibound=ibound, strt=strt)

hk=10. 
vka=10.
laytyp = [0] # confined


# h[i,j,k] is the head at node i,j,k
# KR[i,j-1/2,k] is hydraulic conductivity along the row between nodes i,j,k and i,j-1,k (LT^{-1})
# q[i,j-1/2,k] is the volumetric flow rate through the face between cells i,j,k and i,j-1,k (L^3T^{-1})

# indexing as numpy.flatten default
# [i,j,k] -> i*J*K+ j*K + k
# [i,j,k,m] -> i*J*K*M + j*K*M + k*M + m

PERLEN = [1, 5]
NSTP = [1, 5]
NPER = len(PERLEN)
ISSFLG = [True, False]

h_0 = strt
IBOUND = ibound
BOT = np.ones((ncol,nrow,nlay+1))
for i in range(len(botm)):
    BOT[:,:,i] *= botm[i]

delr = delr * np.ones((ncol))
delc = delc * np.ones((nrow))

HK = hk * np.ones((ncol,nrow,nlay))

"""
intransient inputs
"""
SS = np.ones((nrow,ncol,nlay)) # SPECIFIC STORAGE
SY = np.ones((nrow,ncol,nlay)) # SPECIFIC YIELD
HANI = np.ones((nrow,ncol,nlay)) # SPECIFIC YIELD
VK = np.ones((nrow,ncol,nlay)) # SPECIFIC YIELD

TSMULT = 1.


"""
state
"""
A = np.zeros((nrow*ncol*nlay, nrow*ncol*nlay))

RHS = np.empty((nrow, ncol, nlay))
HCOF = np.empty((nrow, ncol, nlay))
CC = np.empty((nrow+1, ncol+1, nlay+1))
CR = np.empty((nrow+1, ncol+1, nlay+1))
CV = np.empty((nrow+1,ncol+1,nlay+1))

dv = np.zeros((nrow,ncol,nlay))
q_c = np.zeros((nrow,ncol,nlay))

h_old = np.empty((nrow*ncol*nlay))
h_new = np.empty((nrow*ncol*nlay))

h_old = h_0.flatten()

h_all = np.empty((nrow, ncol, nlay, np.sum(NSTP)))

Q = np.zeros((nrow,ncol,nlay))
P = np.zeros((nrow,ncol,nlay))

# DELT
# bug potentiall line 574 of gwf2lpf7.f

for IPER in range(NPER):
	for ISTP in range(NSTP[IPER]):

		"""
		transient inputs
		"""
		Q *= 0.
		P *= 0.

		dt = 1.
		# dt = PERLEN * (TSMULT - 1) / (TSMULT**NSTP[IPER] - 1)

		for k in range(0, nlay):
			for i in range(0, nrow):
				for j in range(0, ncol):
					# note i is i+1/2, i-1 is i-1/2, same for j and k
					# this means 
					node = i*ncol*nlay + j*nlay + k

					# saturated thickness dv, h_old = HNEW
					if h_old[node] >= BOT[i,j,k-1]:
						dv[i,j,k] = BOT[i,j,k-1] - BOT[i,j,k]
					elif BOT[i,j,k-1] > h_old[node] and h_old[node] > BOT[i,j,k]:
						dv[i,j,k] = h_old[node] - BOT[i,j,k]
					else:  # h_old[node] <= BOT[i,j,k]
						dv[i,j,k] = 0
					# dv[i,j,k] = max(BOT[i,j,k], min(BOT[i,j,k-1], HNEW[i,j,k])) - BOT[i,j,k]


					if IBOUND[i,j,k] < 0:
						CV[i,j,k] = 0
						CC[i,j,k] = 0
						CR[i,j,k] = 0
						CV[i,j,k+1] = 0
						CC[i+1,j,k] = 0
						CR[i,j+1,k] = 0

						q_c[i,j,k] = 0
					else:	
						# (5-17A)
						TR_ijk = dv[i,j,k] * HK[i,j,k]
						TR_ij1k = dv[i,j+1,k] * HK[i,j+1,k]
						# (5-17B)
						TC_ijk = dv[i,j,k] * HK[i,j,k] * HANI[i,j,k]
						TC_i1jk = dv[i+1,j,k] * HK[i+1,j,k] * HANI[i+1,j,k]
						# CR[i,j+1,k] is CR[i,j+1/2,k] in documentation
						# harmonic mean used here, there are alternatives, see (5-6)
						# (5-14)
						CR[i,j+1,k] = 2.0 * delc[i] * TR_ijk * TR_ij1k / ( TR_ijk*delr[j+1] + TR_ij1k*delr[j] )
						# (5-15)
						CC[i+1,j,k] = 2.0 * delr[j] * TC_ijk * TC_i1jk / ( TC_ijk*delc[i+1] + TC_i1jk*delc[i] )
						

						# TODO
						semiconfining = False
						if semiconfining:
							# semi confining unit
							# (5-26)
							# 	dv_CB is the thickness of the semiconfining unit
							# 	VKCB[i,j,k] is the hydraulic conductivity of the semiconfining unit between cells i,j,k and i,j,k+1
							CV[i,j,k+1] = delr[j] * delc[i] / ( 0.5*dv[i,j,k]/VK[i,j,k] + dv_CB/VKCB[i,j,k] + 0.5*dv[i,j,k+1]/VK[i,j,k+1] )
						else:	
							# (5-24)
							CV[i,j,k+1] = 2.0 * delr[j] * delc[i] / ( dv[i,j,k]/VK[i,j,k] + dv[i,j,k+1]/VK[i,j,k+1] )


						# TODO
						flow_correction = False
						if flow_correction:
							# flow correction
							if h_old[node] <= BOT[i,j,k]:
								# (5-30), when underlying cell i,j,k+1 is dewatered
								q_c[i,j,k] = CV[i,j,k+1] * (h_old[i,j,k+1] - TOP[i,j,k+1])
								# (5-31), for dewaterd cell itself
								q_c[i,j,k] = CV[i,j,k] * (TOP[i,j,k] - h_old[node])
							else:
								q_c[i,j,k] = 0



					# SC1[i,j,k] = SS[i,j,k] * delr[j] * delc[i] * dv[i,j,k]
					# SC2[i,j,k] = SY[i,j,k] * delr[j] * delc[i]
					
					# (5-38)
					# TODO based on iterations !!!
					# if TOP[i,j,k] < h_old[node]:
					# 	SCA = SC1[i,j,k]
					# 	SCB = SC2[i,j,k]
					# else:
					# 	SCB = SC1[i,j,k]

					SCA = SS[i,j,k] * delr[j] * delc[i] * dv[i,j,k]
					SCB = SY[i,j,k] * delr[j] * delc[i]


					# (2-26)
					HCOF[i,j,k] = P[i,j,k] - SCB / dt
					# HCOF[i,j,k] = P[i,j,k] - ( SS[i,j,k] * delr[j] * delc[i] * dv[k] ) / dt

					# RHS[i,j,k] = A[i*ncol*nlay + j*nlay + k, :] DOT h
					node = i*ncol*nlay + j*nlay + k
					A[node, node] = ( -CV[i,j,k] - CC[i,j,k] - CR[i,j,k] 
									-CV[i,j,k+1] - CC[i+1,j,k] - CR[i,j+1,k] +  HCOF[i,j,k] )

					if k > 0:
						A[node, node-1] = CV[i,j,k]
					if j > 0:
						A[node, node-nlay] = CR[i,j,k]
					if i > 0:
						A[node, node-ncol*nlay] = CC[i,j,k]

					if k < nlay-1:
						A[node, node+1] = CV[i,j,k+1] 
					if j < ncol-1:
						A[node, node+nlay] = CR[i,j+1,k]
					if i < nrow-1:
						A[node, node+ncol*nlay] = CC[i+1,j,k]


					# (2-26)
					RHS[i,j,k] =  -Q[i,j,k] - (SCA * ( BOT[i,j,k-1] - h_old[node] ) - SCB * BOT[i,j,k-1]) / dt
					# RHS[i,j,k] =  -Q[i,j,k] - ( SS[i,j,k] * delr[j] * delc[i] * dv[k] ) * h_old[node] / dt

		q = RHS.flatten()

		# MODFLOW 2005 doc (2-26) and (5-2) is main equation
		# A h = q
		h_new = scipy.linalg.solve(A, q)
		h_old = h_new

		h_all[:,:,:, ISTP + np.sum(NSTP[:IPER])] = h_new.reshape((nrow, ncol, nlay))


print h_all[:]


import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

matplotlib.rcParams['xtick.direction'] = 'out'
matplotlib.rcParams['ytick.direction'] = 'out'

delta = 0.025
x = np.arange(delr/2, Lx+delr/2, delr)
y = np.arange(delc/2, Ly+delc/2, delc)
X, Y = np.meshgrid(x, y)

Z = h_all[:,:,0,-1]

print X
print Y
print Z

plt.figure()
CS = plt.contour(X, Y, Z)
plt.clabel(CS, inline=1, fontsize=10)
plt.title('head')
plt.show()



