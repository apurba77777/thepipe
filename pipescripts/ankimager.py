import os,sys
import argparse as ap
import yaml as ym
from cascripts.calfns import *

#	---------------------------------------------------------------------------------------------------------
#
#	-------
#
#	--------------------------------------------------------------------------------------------------------



#   --------------------------------------------------------------------------------------------------------
def get_args():
    
    #   Read command-line arguments

    parser = ap.ArgumentParser(
        description = "Run the *unnamed* pipeline"
    )

    parser.add_argument("--mode", help = "What to do", type = str, default = None)
    parser.add_argument("--infile", help = "YAML file with input params", type = str, default = None)
    parser.add_argument("--flgin", help = "YAML file with flagging params", type = str, default = None)
    parser.add_argument("--rfifile", help = "File with list of RFI frequencies", type = str, default = None)
    parser.add_argument("--pipedir", help = "Directory to the pipeline", type = str, default = None)
    parser.add_argument("--overwrite", help = "Clear existing files?", action='store_true')

    args = parser.parse_args()

    return args


def print_modes():
    print("\n You need to specify a mode with --mode !!!!!\n")
    print(" Supported modes are      fitstoms    - Convert FITS to MS")
    print("                          initrawms   - Initialize raw MS")
    print("                          makech0     - Create single channel file")
    print("                          fluxch0     - Set flux density of single channel file")
    print("                          calch0      - Calibrate single channel file")
    print("                          flagch0     - Flag single channel file")
    print("                          exbpcal     - Extract bandpass calibrator file")
    print("                          calbpcal    - Calibrate bandpass")
    print("                          flagbpcal   - Flag bandpass calibrator file")
    print("                          extarget    - Extract calibrated target file")
    print("\n Let's try again...\n")
    return (0)

#   ---------------------------------------------------------------------------------------------------------

#   ------------------------------------    Main script starts here ----------------------

argus   = get_args()

print("\n\n ******** This is *unnamed* pipeline ******** \n\n")

#   Read input parameters
if (argus.infile == None):
    print(" Missing input YAML file! Please provide one...")
    sys.exit()
else:
    with open(argus.infile+'.yml', 'r') as infl:
        pars = ym.load(infl, Loader=ym.SafeLoader)
        print(" Inputs provided -- \n")
        print(ym.dump(pars, sort_keys=False))

if (argus.flgin == None):
    print(" Missing YAML file for flagging! aNKflag won't run...\n")

#   ------------------  Make data directories
if (os.path.exists(pars['WorkDir']+pars['CalibDir'])):
    print("Found ",pars['WorkDir']+pars['CalibDir'])
else:
    print("Creating ",pars['WorkDir']+pars['CalibDir'])
    os.system("mkdir "+pars['WorkDir']+pars['CalibDir'])

if (os.path.exists(pars['WorkDir']+pars['UvMsDir'])):
    print("Found ",pars['WorkDir']+pars['UvMsDir'])
else:
    print("Creating ",pars['WorkDir']+pars['UvMsDir'])
    os.system("mkdir "+pars['WorkDir']+pars['UvMsDir'])

if (os.path.exists(pars['WorkDir']+pars['ImgDir'])):
    print("Found ",pars['WorkDir']+pars['ImgDir'])
else:
    print("Creating ",pars['WorkDir']+pars['ImgDir'])
    os.system("mkdir "+pars['WorkDir']+pars['ImgDir'])

if (os.path.exists(pars['WorkDir']+pars['LogDir'])):
    print("Found ",pars['WorkDir']+pars['LogDir'])
else:
    print("Creating ",pars['WorkDir']+pars['LogDir'])
    os.system("mkdir "+pars['WorkDir']+pars['LogDir'])


#   -------------------------   Missing mode
if (argus.mode == None):
    print_modes()
    sys.exit()

#   --------------------------- Tasks   ------------
#   Convert fits to MS
if (argus.mode == "fitstoms"):  
    importrawuvfile(pars['RawDir'] + pars['RawUvFile'], pars['RawFlagFiles'], ovrt=argus.overwrite)

#   Initialize raw MS file
elif (argus.mode == "initrawms"):   
    initrawuvfile(pars['RawDir'] + pars['RawUvFile'], pars, rfifreq=argus.rfifile, ovrt=argus.overwrite)

#   Create single channel file
elif (argus.mode == "makech0"):  
    makesinglechan(pars['RawDir'] + pars['RawUvFile'], pars['SingleChan'], pars, ovrt=argus.overwrite)

#   Set flux scale of single channel file
elif (argus.mode == "fluxch0"):  
    setfluxsinglechan(pars)

#   Calibrate single channel file
elif (argus.mode == "calch0"):  
    calsinglechan(pars)

#   Flag single channel file
elif (argus.mode == "flagch0"):  
    flagsinglechan(pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)

#   Extract bpcal file
elif (argus.mode == "exbpcal"):  
    exbpcal(pars['RawDir'] + pars['RawUvFile'], pars['FluxCal'], pars)

#   Calibrate bandpass
elif (argus.mode == "calbpcal"):  
    calbpcal( pars['FluxCal'], pars)

#   Flag bandpass calibrator file
elif (argus.mode == "flagbpcal"):  
    flagbpcal(pars['FluxCal'], pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)

#   Extract calibrated target file
elif (argus.mode == "extarget"):  
    extarget(pars['RawDir'] + pars['RawUvFile'], pars['FluxCal'], pars)

else:
    print_modes()

