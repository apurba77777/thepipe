import os,sys
import argparse as ap
import yaml as ym
from cascripts.calfns import *

#	---------------------------------------------------------------------------------------------------------
#
#	This is aNKcalibrator
#                                                   AB  [last updated: 10 May 2026]
#
#   This programme can be used to calibrate (GMRT) visibility data
#
#   To run this programme, use the following command with a python executor
#
#   ankcalibrator.py    --[mode(s)]                 //  processing step(s) -- see description below
#                       --infile [param_YAML]       //  YAML file containing input parameters
#                       --flgin [ankflag_YAML]      //  YAML file containing aNKflag parameters
#                       --rfifile [RFI_text]        //  TEXT file with RFI frequency ranges
#                       --pipedir [pipe_direcory]   //  Path to the pipeline itself
#
#
#   Supported modes are                 fitstoms    //  Convert FITS to MS
#                                       initrawms   //  Initialize raw MS
#                                       makech0     //  Create single channel file
#                                       fluxch0     //  Set flux density of single channel file
#                                       calch0      //  Calibrate single channel file
#                                       flagch0     //  Flag single channel file
#                                       exbpcal     //  Extract bandpass calibrator file
#                                       calbpcal    //  Calibrate bandpass
#                                       flagbpcal   //  Flag bandpass calibrator file
#                                       extarget    //  Extract calibrated target file
#                                       flagtarget  //  Flag calibrated target file
#
#       Combined modes                  calgt       //  Calibrate time dependent gain in single channel 
#                                       calbp       //  Calibrate bandpass
#                                       caltar      //  Calibrate both gain and bandpass
#
#       Charms & spells  ( Extreme caution recommended !!)
#                        
#                                     --obliviate   //  Clear existing files? 
#                                     --lumos       //  List usable modes on screen
#                                     --aparecium   //  Reveal input parameters 
#                                     --reducto     //  Reduce entire dataset to calibrated target outputs
#
#
#	--------------------------------------------------------------------------------------------------------



#   --------------------------------------------------------------------------------------------------------
def get_args():
    
    #   Read command-line arguments

    parser = ap.ArgumentParser(
        description = "Run aNKcalibrator"
    )

    parser.add_argument("--infile", help = "YAML file with input params", type = str, default = None)
    parser.add_argument("--flgin", help = "YAML file with flagging params", type = str, default = None)
    parser.add_argument("--rfifile", help = "File with list of RFI frequencies", type = str, default = None)
    parser.add_argument("--pipedir", help = "Directory to the pipeline", type = str, default = None)

    #   Modes
    parser.add_argument("--fitstoms", help = "Convert FITS to MS", action='store_true')
    parser.add_argument("--initrawms", help = "Initialize raw MS", action='store_true')
    parser.add_argument("--makech0", help = "Create single channel file", action='store_true')
    parser.add_argument("--fluxch0", help = "Set flux density of single channel file", action='store_true')
    parser.add_argument("--calch0", help = "Calibrate single channel file", action='store_true')
    parser.add_argument("--flagch0", help = "Flag single channel file", action='store_true')
    parser.add_argument("--exbpcal", help = "Extract bandpass calibrator file", action='store_true')
    parser.add_argument("--calbpcal", help = "Calibrate bandpass", action='store_true')
    parser.add_argument("--flagbpcal", help = "Flag bandpass calibrator file", action='store_true')
    parser.add_argument("--extarget", help = "Extract calibrated target file", action='store_true')
    parser.add_argument("--flagtarget", help = "Flag calibrated target file", action='store_true')

    #   Combined modes
    parser.add_argument("--calgt", help = "Calibrate time dependent gain in single channel", action='store_true')
    parser.add_argument("--calbp", help = "Calibrate bandpass", action='store_true')
    parser.add_argument("--caltar", help = "Calibrate both gain and bandpass", action='store_true')

    #   Charms & spells -- Extreme caution recommended 
    parser.add_argument("--obliviate", help = "Clear existing files ?", action='store_true')
    parser.add_argument("--lumos", help = "List usable modes on screen", action='store_true')
    parser.add_argument("--aparecium", help = "Reveal input parameters", action='store_true')
    parser.add_argument("--reducto", help = "Reduce entire dataset to calibrated target outputs", action='store_true')

    args = parser.parse_args()

    return args


def print_modes():
    print("\n You need to specify one or more mode(s) with --[mode(s)] !!!!!\n")
    print(" Supported modes are      --fitstoms    - Convert FITS to MS")
    print("                          --initrawms   - Initialize raw MS")
    print("                          --makech0     - Create single channel file")
    print("                          --fluxch0     - Set flux density of single channel file")
    print("                          --calch0      - Calibrate single channel file")
    print("                          --flagch0     - Flag single channel file")
    print("                          --exbpcal     - Extract bandpass calibrator file")
    print("                          --calbpcal    - Calibrate bandpass")
    print("                          --flagbpcal   - Flag bandpass calibrator file")
    print("                          --extarget    - Extract calibrated target file")
    print("                          --flagtarget  - Flag calibrated target file\n")

    print(" Combined modes           --calgt       - Calibrate time dependent gain in single channel")
    print("                          --calbp       - Calibrate bandpass")
    print("                          --caltar      - Calibrate both gain and bandpass \n")

    print(" Charms & spells  ( Extreme caution recommended !!) \n")
    print("                          --obliviate   - Clear existing files")
    print("                          --lumos       - List usable modes on screen")
    print("                          --aparecium   - Reveal configuration parameters")
    print("                          --reducto     - Reduce entire dataset to calibrated target outputs")
    
    print("\n Let's try again...\n")
    return (0)

#   ---------------------------------------------------------------------------------------------------------

#   ------------------------------------    Main script starts here ----------------------

argus   = get_args()

print("\n\n ******** This is aNKcalibrator ******** \n\n")

#   Read input parameters
if (argus.infile == None):
    print(" Missing input YAML file! Please provide one...")
    sys.exit()
else:
    with open(argus.infile+'.yml', 'r') as infl:
        pars = ym.load(infl, Loader=ym.SafeLoader)
        if (argus.aparecium):
            print(" Inputs provided -- \n")
            print(ym.dump(pars, sort_keys=False))

if (argus.flgin == None):
    print(" Missing YAML file for flagging! aNKflag won't run...\n")


#   ------------------  Make data directories


if (os.path.exists(pars['WorkDir'])):
    print("Found ",pars['WorkDir'])
else:
    print("Creating ",pars['WorkDir'])
    os.system("mkdir "+pars['WorkDir'])

if (os.path.exists(pars['WorkDir']+pars['UvMsDir'])):
    print("Found ",pars['WorkDir']+pars['UvMsDir'])
else:
    print("Creating ",pars['WorkDir']+pars['UvMsDir'])
    os.system("mkdir "+pars['WorkDir']+pars['UvMsDir'])

if (os.path.exists(pars['WorkDir']+pars['LogDir'])):
    print("Found ",pars['WorkDir']+pars['LogDir'])
else:
    print("Creating ",pars['WorkDir']+pars['LogDir'])
    os.system("mkdir "+pars['WorkDir']+pars['LogDir'])



#   List supported modes
if (argus.lumos):  
    print_modes()


#   --------------------------- Tasks   ------------
#   Convert fits to MS
if (argus.fitstoms):  
    importrawuvfile(pars['RawUvFile'], pars['RawFlagFiles'], pars, ovrt=argus.obliviate)

#   Initialize raw MS file
if (argus.initrawms or argus.reducto):   
    initrawuvfile(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars, rfifreq=argus.rfifile, ovrt=argus.obliviate)

#   Create single channel file
if (argus.makech0):  
    makesinglechan(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars, ovrt=argus.obliviate)

#   Set flux scale of single channel file
if (argus.fluxch0):  
    setfluxsinglechan(pars)

#   Calibrate single channel file
if (argus.calch0):  
    calsinglechan(pars)

#   Flag single channel file
if (argus.flagch0):  
    flagsinglechan(pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.obliviate)

#   Calibrate time dependent gain in single channel
if (argus.calgt or argus.caltar or argus.reducto):
    makesinglechan(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars, ovrt=argus.obliviate)
    setfluxsinglechan(pars)
    
    for i in range(0, pars['CalIter']):
        print(f'\n Gain calibration iteration {i}...\n')
        flagsinglechan(pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=True)
        calsinglechan(pars)


#   Extract bpcal file
if (argus.exbpcal):  
    exbpcal(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars['FluxCal'], pars)

#   Calibrate bandpass
if (argus.calbpcal):  
    calbpcal( pars['FluxCal'], pars)

#   Flag bandpass calibrator file
if (argus.flagbpcal):  
    flagbpcal(pars['FluxCal'], pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.obliviate)


#   Calibrate time dependent gain in single channel
if (argus.calbp or argus.caltar or argus.reducto):
    exbpcal(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars['FluxCal'], pars)

    for i in range(0, pars['BpIter']):
        print(f'\n Bandpass calibration iteration {i}...\n')
        flagbpcal(pars['FluxCal'], pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=True)
        calbpcal( pars['FluxCal'], pars)


#   Extract calibrated target file
if (argus.extarget or argus.caltar or argus.reducto):  
    extarget(pars['WorkDir']+pars['UvMsDir']+pars['ReducedName'], pars['FluxCal'], pars)


#   Flag calibrated target file
if (argus.flagtarget or argus.reducto):  
    flagtarget(pars['TargetName'], pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.obliviate)



