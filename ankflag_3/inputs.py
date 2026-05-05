import numpy as np
import yaml as ym
import argparse as ap




#	***************************************************************
#	About this script
#
#	***************************************************************





#	Control parameters for debugging only

ConvertFITS	= True		#	Convert FITS to binary ?	
DoFlag		= True		#	Do flagging ?
ReadBack	= True		#	Read back baselines ?
WriteOut	= True		#	Write output ?



#	List of optiopns used for internal processes

exmode		=	['baseline', 'uvbin']
flagwhat	=	['vis_ind', 'chan_ind', 'rec_ind', 'vis_block', 'chan_block', 'rec_block']
flagon		=	['mean', 'rms', 'mean_rms']
statused	=	['median', 'mean']
datype		=	['re', 'im', 'am', 'ph']
blkorder	=	['ascending', '', 'descending']
tartypes	=	['calch0', 'calbp', 'normal', 'uvsub']
partypes	=	['FlgCalCh0', 'FlgCalBp', 'FlgNorm', 'FlgUvsub']




#	-------------------------------------------------------------
#	Parse input control parameters 
#	-------------------------------------------------------------



def get_args():
    
	#   Read command-line arguments

	parser = ap.ArgumentParser(
		description = "Run aNKflag"
	)

	parser.add_argument("--ankdir", help = "Where to find the ankflag binary", type = str, default = './')

	parser.add_argument("--flagmode", help = "Mode of flagging (baseline / uvbin)", type = str, default = None)
	parser.add_argument("--parfile", help = "YAML file with input params (without .yml)", type = str, default = None)
	parser.add_argument("--scratchdir", help = "Scratch directory", type = str, default = None)
	parser.add_argument("--targetype", help = "Target source type", type = str, default = None)
     
	parser.add_argument("--infilename", help = "Input FITS file (without .fits)", type = str, default = None)
	parser.add_argument("--outfilename", help = "output FITS file (without .fits)", type = str, default = None)
	parser.add_argument("--logfile", help = "Name of the logfile", type = str, default = "logfile")
	parser.add_argument("--rfifreqfile", help = "File with RFI frequencies", type = str, default = None)
     
	parser.add_argument("--nthreads", help = "Number of threads [1]", type = int, default = 1)

	parser.add_argument("--clearscratch", help = "Clear scratch directory?", action='store_true')
	parser.add_argument("--flagautocorr", help = "Flag autocorrelations?", action='store_true')

	args = parser.parse_args()

	return args
#   ---------------------------------------------------------------------------------------------------------





def getparsyaml (infile, showparams = False):
	
	#	Read parameters from the input YAML file

	with open(infile+'.yml', 'r') as infl:
		flagparams = ym.load(infl, Loader=ym.SafeLoader)
		
		if(showparams):
			print(" Inputs provided -- \n")
			print(ym.dump(flagparams, sort_keys=False))

	return (flagparams)

#	-------------------------------------------------------------




'''






#	For bandpass calibrated data

FLAGPARS1		=	[	[ 'chan_ind',	'rms',		'median',	'am',	2.0,	0.1,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'mean',		'median',	'am',	2.0,	0.1,	0,	'',				0,	0,	0.0,	0.0],
						[ 'vis_ind',	'mean',		'mean',		'am',	3.0,	0.1,	0,	'',				0,	0,	0.0,	0.0]	]

FLAGPARS2		=	[	[ 'rec_ind',	'rms',		'median',	'am',	5.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'rms',		'median',	'am',	5.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'rec_ind',	'mean',		'median',	'am',	2.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'mean',		'median',	'am',	2.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'rec_ind',	'mean',		'mean',		'am',	3.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'mean',		'mean',		'am',	3.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'rec_ind',	'rms',		'mean',		'am',	2.0,	0.01,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'rms',		'mean',		'am',	2.0,	0.01,	0,	'',				0,	0,	0.0,	0.0]	]
						
FLAGPARS3		=	[	[ 'chan_ind',	'mean',		'mean',		'am',	1.5,	0.1,	0,	'',				0,	0,	0.0,	0.0],
						[ 'chan_ind',	'rms',		'median',	'am',	1.2,	0.1,	0,	'',				0,	0,	0.0,	0.0]	]

FLAGPARS4		=	[	[ 'chan_ind',	'rms',		'mean',		'am',	1.5,	0.1,	0,	'',				0,	0,	0.0,	0.0]	]
'''
#
#	FLAGON			=	'mean'		/	'rms'		/	'mean_rms'
#	STATYPE			=	'mean'		/	'median'
#	DATATYPE		=	're'		/	'im'		/	'am'		(/	'ph'	---- NOT YET SUPPORTED)
#	ORDER			=	'ascending'			(/	'descending' --- NOT YET SUPPORTED)

#	Vis individual	=	[ 'vis_ind',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	0, 				fit order,  '', 	0, 			0, 			0, 				0			 	]

#	Chan individual	=	[ 'chan_ind',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	min fraction,	fit order,	'',		0,			0,			0,				0			 	]

#	Rec individual	=	[ 'rec_ind',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	min fraction,			0,	'',		0,			0,			0,				0			 	]

#	Vis block		=	[ 'vis_block',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	min fraction,	fit order,	ORDER,	chan_block,	rec_block,	chan_max_frac,	rec_max_frac 	]

#	Chan block		=	[ 'chan_block',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	min fraction,	fit order,	ORDER,	chan_block,	0,			chan_max_frac,	0 				]

#	Rec block		=	[ 'rec_block',	FLAGON,	STATYPE,	DATATYPE,	tolerance,	min fraction,	fit order,	ORDER,	0,			rec_block,	0,				rec_max_frac 	]





#	*******************************************************************************
#	--------------		Convert parameters to aNKflag secret codes 
#	-------------------------------------------------------------------------------

def covertparams(flagparams, partype, flagparfile, argus, uugrids, vvgrids):

	#	Write encoded parameters in flagparfile

	print('\nTotal flagging rounds	=	%d\n'%len(flagparams[partype]))

	flagparfile	=	open(flagparfile,'w')
	flagparfile.write('%d	%d	%d	%d	%d	'\
					%(flagparams['N_ants'], exmode.index(argus.flagmode), uugrids, \
						flagon.index(flagparams['ScanFlMean'][0])+1, vvgrids))
	flagparfile.write('%f	%f	%d	%d	%d	%f	%f\n'\
					%(float(flagparams['ScanFlMean'][1]), float(flagparams['ScanFlMean'][2]), len(flagparams[partype]), \
						argus.nthreads, WriteOut, float(flagparams['BlockPow']), float(flagparams['ScanFlMean'][3])))

	for flpar in flagparams[partype]:
		flagparfile.write('%d	%d	%d	%d	%d	'\
							%(flagwhat.index(flpar['what']), flagon.index(flpar['flagon'])+1, statused.index(flpar['stat']), \
								datype.index(flpar['data']), -(blkorder.index('ascending')-1)))
		

		fitorder		= int(flpar["fitorder"]) if ("fitorder" in flpar) else 0	
		minfrac			= float(flpar["minfrac"]) if ("minfrac" in flpar) else 0.1	
		chan_block		= int(flpar["chan_block"]) if ("chan_block" in flpar) else 1	
		rec_block		= int(flpar["rec_block"]) if ("rec_block" in flpar) else 1	
		chan_max_frac	= float(flpar["chan_max_frac"]) if ("chan_max_frac" in flpar) else 0.1
		rec_max_frac	= float(flpar["rec_max_frac"]) if ("rec_max_frac" in flpar) else 0.1

		flagparfile.write('%f	%f	%d	%d	%d	%f	%f\n'\
							%(float(flpar['tol']), minfrac, fitorder+1, chan_block, rec_block, chan_max_frac, rec_max_frac))

	flagparfile.close()

	return(0)

#	-------------------------------------------------------------






































































