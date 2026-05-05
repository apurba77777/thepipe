import os,sys
import numpy as np
import time as tm
import argparse as ap
from convertfits import *
from inputs import *
from plottingfns import *



#	***************************************************************
#	About this script
#
#	***************************************************************




argus   = get_args()

print("\n\n ************ This is aNKflag ************ \n\n")




#	--------------------------------------
#   Read and verify input parameters
#	--------------------------------------

if (argus.parfile == None):
    print(" Missing input YAML file! Please provide one...")
    sys.exit()
else:
    flagparams	= getparsyaml (argus.parfile, showparams=False)



if (argus.scratchdir == None):
    print(" A scratch directory in critically required! Please provide through --scratchdir")
    sys.exit()
else:
	if (os.path.exists(argus.scratchdir)):
		if (argus.clearscratch):
			print('\nClearing scratch directory....\n')
			os.system('rm -rf '+argus.scratchdir+'/*')
	else:
		os.system('mkdir '+argus.scratchdir)



if (argus.infilename == None):
	print("\n Well... what do you want me to do without an input file?")
	print("\n Provide a filename without .fits\n")
	sys.exit()
elif (os.path.exists(argus.infilename+".fits")):
	infilefits	= argus.infilename+".fits"
else:
	print("\n Well... that doesn't exist, does it?")
	print("\n Provide a real file without .fits\n")
	sys.exit()




if (argus.outfilename == None):
	print("\n Well... don't you want to save the output?")
	print("\n Provide a filename without .fits\n")
	sys.exit()
else:
	outfilefits	= argus.outfilename+".fits"



if ( not (argus.flagmode=="uvbin" or argus.flagmode=="baseline")):
	print("Didn't get that flagging mode... Won't be flagging anything.\n\n")
else:
	print("Flagging in "+argus.flagmode+" mode \n")



if (argus.targetype in tartypes):
	print("Target type -- ",argus.targetype)
	partype	= partypes[tartypes.index(argus.targetype)]
	if (partype in flagparams):
		print("Using parameters -- ",partype)
		print("Flagging commands --")
		print(*flagparams[partype], sep='\n')
	else:
		print(partype, "is not provided...")
		sys.exit()
else:
	print("Hmm... What type of target is that? I know only -- ", *tartypes, sep=" ")
	sys.exit()
	


if ((argus.targetype == "calch0") or (argus.targetype == "calbp")):
	uugrids	= flagparams['UgridCal']
	vvgrids	= flagparams['VgridCal']
else:
	uugrids	= flagparams['UgridTar']
	vvgrids	= flagparams['VgridTar']




#	Convert parameters to aNKflag secret codes
covertparams(flagparams, partype, argus.scratchdir+'/flagpars.pars', argus, uugrids=uugrids, vvgrids=vvgrids)





#	**********************************************************************************
#	----------------------------	Convert FITS to aNKflag compatible binary files
#	..................................................................................



start0	=	tm.time()	

#	Preflag autocorrelations
if (argus.flagautocorr):
	infile		=	fits.open(infilefits)
	data		=	infile[0].data	
	nauto 		= 	flagautocorr(flagparams['N_ants'],data)
	infile.writeto(argus.scratchdir+'/scratchfits.fits',output_verify='warn',overwrite=True)
	infile.close()




if (ConvertFITS):

	if (argus.flagautocorr):
		infile		=	fits.open(argus.scratchdir+'/scratchfits.fits')
	else:
		infile		=	fits.open(infilefits)


	data		=	infile[0].data


		
	#	-----------	Flagging hopeless channels	---------------------------

	if ( (argus.rfifreqfile != None) and os.path.exists(argus.rfifreqfile) ):

		print("Identifying bad channels from ",argus.rfifreqfile)

		'''hopelesschans	=	[]
		allbadchans		=	np.loadtxt(allbadchanfile).astype('int')
		
		if(len(allbadchans.shape)==2):
			if(allbadchans.shape[1]==2):
				print("Bad channel list")
				for lk in range(0,allbadchans.shape[0]):
					print("%d	%d"%(allbadchans[lk,0],allbadchans[lk,1]+1))
					for bc in range(allbadchans[lk,0],allbadchans[lk,1]+1):
						hopelesschans.append(bc)
				hopelesschans	=	np.array(hopelesschans)	
				nhopelesschans	=	flagchanlist(ANTS,data,hopelesschans)
				print("Flagged %d bad channels everywhere..."%nhopelesschans)
			else:
				print("Useless bad channel list... ignoring")
		else:
			print("Useless bad channel list... ignoring")'''
	else:
		print("No bad channel list found... continuing...\n")

	#	-------------------------------------------------------------------

	if ( argus.flagmode == "uvbin" ):		
		uvfitstobinary(data, argus.scratchdir, uugrids, vvgrids, flagparams, figname=argus.logfile+'_uvbin.png')

	elif ( argus.flagmode == "baseline" ):		
		baselinestobinary(flagparams['N_ants'], data, argus.scratchdir, flagparams['ScanBrkSec'], flagparams)
			
	else:
		print("Unknown flagging mode !!!!			Please tell me how to execute it ........")
	
	infile.close()	
	print("\nConvertion done in 		%d seconds\n"%(tm.time()-start0))





#	****************************************************
#
# 				Actual flagging is done here 
#
#	****************************************************


start1	=	tm.time()

if (DoFlag):
	status	=	os.system(argus.ankdir+'/ankflag '+argus.scratchdir+' > '+argus.logfile+'_log.txt')	
	print("\nFlagging done in 		%d seconds\n"%(tm.time()-start1))
	


	


#	**********************************************************************************
#	----------------------------	Convert back binary files to FITS
#	..................................................................................




if (ReadBack):

	if (argus.flagautocorr):
		infile2		=	fits.open(argus.scratchdir+'/scratchfits.fits')
	else:
		infile2		=	fits.open(infilefits)		
	data2		=	infile2[0].data	



	if ( argus.flagmode == "uvbin" ):	
		bintofits	=	uvfitsfrombinary(data2, argus.scratchdir, uugrids, vvgrids, flagparams)

	elif ( argus.flagmode == "baseline" ):
		baselinesfrombinary(flagparams['N_ants'], data2, argus.scratchdir, flagparams)





	#	-------------------------------		Plot diagnostics	---------------

	#if (argus.targetype == 'calch0'):
	#	amphasevsrow (data, data2, flagparams, fig_size=12.0, figname=argus.logfile+'_amphasevsrow.png')



	#	-------------------------------		Write the output FITS --------------


	if (WriteOut):
		print("Writing output FITS...")
		infile2.writeto(outfilefits,output_verify='warn',overwrite=True)

	infile2.close()
	print("\nEverything done in 		%d seconds\n"%(tm.time()-start0))

	#	----------------------------------------------------------------------------





if (argus.clearscratch):
	print('\nClearing scratch directory....\n')
	os.system('rm -rf '+argus.scratchdir)



