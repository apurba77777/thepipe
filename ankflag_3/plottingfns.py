import sys
import numpy as np
import matplotlib.pyplot as plt





#	-----------------------------------------------------------------------------------------------------
#	Function to plot visibility amplitudes and phases vs row before and after flagging
#	-----------------------------------------------------------------------------------------------------

def amphasevsrow (data, data2, flagparams, fig_size=10.0, figname=None):
	

	fig 	= plt.figure(figsize=(1.2 * fig_size, fig_size))
    
	axtl 	= fig.add_axes([0.1,0.5,0.35,0.35])
	axtr 	= fig.add_axes([0.5,0.5,0.35,0.35])
	axbl 	= fig.add_axes([0.1,0.1,0.35,0.35])
	axbr 	= fig.add_axes([0.5,0.1,0.35,0.35])
	axlist	= [[axtl,axtr],[axbl,axbr]]

	axtl.set_title("Before flagging")
	axtr.set_title("After flagging")

	bldata	= [data.data, data2.data]	

	gcols	= ['b', 'k']
	bcols	= ['r', 'c']

	for bls in range (0, len(bldata)):

		for p in range (0, flagparams['Npols']):			

			tfdata	=	bldata[bls][:,0,0,0,:,p,:]		#	Time frequency data
			tfre	=	tfdata[:,:,0]					#	Real part
			tfim	=	tfdata[:,:,1]					#	Imaginary Part
			tfw		=	tfdata[:,:,2]					#	Weight
			tfamp	=	np.sqrt(tfre*tfre + tfim*tfim)	#	Amplitude
			tfph	=	np.arctan2(tfim, tfre)			#	Phase

			rownum	=	np.arange(0, tfamp.shape[0]-0.5, 1.0)

			#axlist[0][bls].plot(rownum[tfw[:,0] <= 0.0], tfamp[tfw <= 0.0], bcols[p]+'.', alpha=0.3)	
			#axlist[1][bls].plot(rownum[tfw[:,0] <= 0.0], tfph[tfw <= 0.0], bcols[p]+'.',  alpha=0.3)	

			axlist[0][bls].plot(rownum[tfw[:,0] > 0.0], tfamp[tfw > 0.0], gcols[p]+'o', markersize=1)	
			axlist[1][bls].plot(rownum[tfw[:,0] > 0.0], 180*tfph[tfw > 0.0]/np.pi, gcols[p]+'o', markersize=1)				

	axbl.set_xlabel("Row")
	axbr.set_xlabel("Row")	
	axtl.set_ylabel("Amplitude")
	axbl.set_ylabel("Phase (deg)")	

	if (figname==None):
		plt.show()
	else:
		plt.savefig(figname, dpi=300)
		plt.close()
	
	return (0)

#	----------------------------------------------------------------------------------------------------





#	-----------------------------------------------------------------------------------------------------
#
#	Function to show time-frequency plot for one single baseline
#
#	-----------------------------------------------------------------------------------------------------

def showbasecomparison(bl,data,data2,dopl):
	
	flfrac	=	[]
	
	bdata	=	data[data.par('BASELINE')==bl[2]]
	
	if(len(bdata)==0):
		print('Baseline	%d-%d		No data'%(bl[0],bl[1]))
		return (np.ones(2*npols))
	
	if(dopl):
		fig=plt.figure(figsize=(12,8))
		
	bldata	=	bdata.data
	
	for p in range (0,npols):
			
		tfdata	=	bldata[:,0,0,0,:,p,:]			#	Time frequency data
		tfre	=	tfdata[:,:,0]					#	Real part
		tfim	=	tfdata[:,:,1]					#	Imaginary Part
		tfw		=	tfdata[:,:,2]					#	Weight
		tfamp	=	np.sqrt(tfre*tfre+tfim*tfim)	#	Amplitude
		
		tfamp[tfw<=0.0]	=	0.0
		
		flfrac.append(1.0-float(np.count_nonzero(tfw>0.0))/np.size(tfw))
		
		if(dopl):
			ax=fig.add_subplot(npols,2,npols*p+1)
			plt.imshow(tfamp,interpolation='none',aspect='auto')
			plt.colorbar()
	
	bdata	=	data2[data.par('BASELINE')==bl[2]]
		
	bldata	=	bdata.data
	
	for p in range (0,npols):
			
		tfdata	=	bldata[:,0,0,0,:,p,:]			#	Time frequency data
		tfre	=	tfdata[:,:,0]					#	Real part
		tfim	=	tfdata[:,:,1]					#	Imaginary Part
		tfw		=	tfdata[:,:,2]					#	Weight
		tfamp	=	np.sqrt(tfre*tfre+tfim*tfim)	#	Amplitude
		
		tfamp[tfw<=0.0]	=	0.0
		
		flfrac.append(1.0-float(np.count_nonzero(tfw>0.0))/np.size(tfw))
		
		if(dopl):
			ax=fig.add_subplot(npols,2,npols*p+2)
			plt.imshow(tfamp,interpolation='none',aspect='auto')
			plt.colorbar()
			
	print('Baseline	%d-%d	flagged fractions	'%(bl[0],bl[1])),
	for p in range (0,npols):
		print('%.2f %.2f	'%(flfrac[p],flfrac[p+npols])),
	print('\n')
	
	if(dopl):
		plt.show()
	
	return (np.array(flfrac))

#	----------------------------------------------------------------------------------------------------


	

































