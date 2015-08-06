



for k in range(nlay):
	# if convertible
	if not laytyp[k] == 0:

		SGWF2LPF7HCOND
		SGWF2LPF7VCOND

# if transient
if transient:
	for k in range(nlay):
		# if non-convertible
		if laytyp[k] == 0:
			for i in range(nrow):
				for j in range(ncol):
					if IBOUND[i,j,k] >= 0:
						 RHO=SC1(J,I,K)*TLED
            HCOF(J,I,K)=HCOF(J,I,K)-RHO
            RHS(J,I,K)=RHS(J,I,K)-RHO*HOLD(J,I,K)