import os,sys
import argparse as ap
import yaml as ym
from cascripts.imgfns import *

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
    parser.add_argument("--imgname", help = "Name of the image (only for imaging)", type = str, default = None)
    parser.add_argument("--pipedir", help = "Directory to the pipeline", type = str, default = None)
    parser.add_argument("--savemodel", help = "Save model column?", action='store_true')
    parser.add_argument("--intmask", help = "Interactive masking?", action='store_true')
    parser.add_argument("--calmode", help = "Self-calibration mode (p/ap)", type = str, default = None)
    parser.add_argument("--overwrite", help = "Clear existing files?", action='store_true')

    args = parser.parse_args()

    return args


def print_modes():
    print("\n You need to specify a mode with --mode !!!!!\n")
    print(" Supported modes are      avgtarget   - Channel average target visibilities")
    print("                          imgtarget   - Image the calibrated target")
    print("                          selfcal     - Self calibrate")
    print("                          flagcal     - Flag calibrated visibilities")
    print("                          contimg     - Attempt to produce the *final* continuum image")
    print("                          getuvsub    - Subtract the final continuum model")
    print("                          flaguvsub   - Flag continuum subtracted visibilities")
    
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

#   ------------------  Make data directories   ---------------

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


#   -------------------------   Missing mode    ---------
if (argus.mode == None):
    print_modes()
    sys.exit()

#   --------------------------- Tasks   ------------



#   Channel average target visibilities
if (argus.mode == "avgtarget"):      

    for ivis in pars['VisList']:
        avgtarget (ivis, pars)




#   Convert fits to MS
elif (argus.mode == "imgtarget"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg.ms" for vis in pars['VisList'] ]

    imgtarget(listofvis, argus.imgname, argus.savemodel, argus.intmask, pars)




#   Self-calibrate
elif (argus.mode == "selfcal"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg" for vis in pars['VisList'] ]

    for ivis in listofvis:
        selfcal (ivis, ivis+".scal", argus.calmode, pars)




#   Flag calibrated visibilities
elif (argus.mode == "flagcal"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg" for vis in pars['VisList'] ]

    for ivis in listofvis:
        flagcaltarget (ivis, pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)




#   Attempt to produce the *final* continuum image
elif (argus.mode == "contimg"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg.ms" for vis in pars['VisList'] ]

    finalimg(listofvis, argus.savemodel, pars)




#   Channel average target visibilities
elif (argus.mode == "getuvsub"):      

    for ivis in pars['VisUvSub']:
        getuvsub (ivis, ivis+"_f_avg.scal", pars)




#   Flag continuum subtracted visibilities
elif (argus.mode == "flaguvsub"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_uvsub" for vis in pars['VisUvSub'] ]

    for ivis in listofvis:
        flagavguvsub (ivis, pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)



else:
    print_modes()

