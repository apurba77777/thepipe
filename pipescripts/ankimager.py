import os,sys
import argparse as ap
import yaml as ym
from cascripts.imgfns import *

#	---------------------------------------------------------------------------------------------------------
#
#	This is aNKimager
#                                                   AB  [last updated: 13 May 2026]
#
#   This programme can be used to calibrate (GMRT) visibility data
#
#   To run this programme, use the following command with a python executor
#
#   ankimager.py        --[mode(s)]                 //  processing step(s) -- see description below
#                       --infile [param_YAML]       //  YAML file containing input parameters
#                       --flgin [ankflag_YAML]      //  YAML file containing aNKflag parameters
#                       --rfifile [RFI_text]        //  TEXT file with RFI frequency ranges
#                       --pipedir [pipe_direcory]   //  Path to the pipeline itself
#                       --overwrite                 //  If certain outputs are to be overwritten
#
#
#   Supported modes are                 avgtarget   //  Channel average target visibilities
#                                       imgtarget   //  Image the calibrated target
#                                       findsrcs    //  (For internal use only)
#                                       selfcal     //  Self calibrate
#                                       chkselfcal  //  (For internal use only)
#                                       flagcal     //  Flag calibrated visibilities
#                                       contimg     //  Attempt to produce the *final* continuum image
#                                       getuvsub    //  Subtract the final continuum model
#                                       flaguvsub   //  Flag continuum subtracted visibilities
#
#
#       Combined modes                  fullselfcal //  Self calibrate until 'convergence' 
#
#	--------------------------------------------------------------------------------------------------------



#   --------------------------------------------------------------------------------------------------------
def get_args():
    
    #   Read command-line arguments

    parser = ap.ArgumentParser(
        description = "Run the *unnamed* pipeline"
    )

    parser.add_argument("--infile", help = "YAML file with input params", type = str, default = None)
    parser.add_argument("--flgin", help = "YAML file with flagging params", type = str, default = None)
    parser.add_argument("--rfifile", help = "File with list of RFI frequencies", type = str, default = None)
    parser.add_argument("--imgname", help = "Name of the image (only for imaging)", type = str, default = "random")
    parser.add_argument("--oldimg", help = "Old image for checking selfcal", type = str, default = "random")
    parser.add_argument("--pipedir", help = "Directory to the pipeline", type = str, default = None)
    parser.add_argument("--savemodel", help = "Save model column?", action='store_true')
    parser.add_argument("--intmask", help = "Interactive masking?", action='store_true')
    parser.add_argument("--calmode", help = "Self-calibration mode (p/ap)", type = str, default = "p")
    parser.add_argument("--overwrite", help = "Clear existing files?", action='store_true')
    parser.add_argument("--listmodes", help = "List supported modes", action='store_true')
    parser.add_argument("--listpars", help = "List input parameters", action='store_true')


    #   Modes
    parser.add_argument("--avgtarget", help = "Channel average target visibilities", action='store_true')
    parser.add_argument("--imgtarget", help = "Image the calibrated target", action='store_true')
    parser.add_argument("--selfcal", help = "Self calibrate", action='store_true')
    parser.add_argument("--findsrcs", help = "(For internal use only)", action='store_true')
    parser.add_argument("--chkselfcal", help = "(For internal use only)", action='store_true')
    parser.add_argument("--flagcal", help = "Flag calibrated visibilities", action='store_true')
    parser.add_argument("--contimg", help = "Attempt to produce the *final* continuum image", action='store_true')
    parser.add_argument("--getuvsub", help = "Subtract the final continuum model", action='store_true')
    parser.add_argument("--flaguvsub", help = "Flag continuum subtracted visibilities", action='store_true')

    #   Combined modes
    parser.add_argument("--fullselfcal", help = "Self calibrate until convergence reached", action='store_true')

    args = parser.parse_args()

    return args


def print_modes():
    print("\n You need to specify a mode with --mode !!!!!\n")
    print(" Supported modes are      avgtarget   - Channel average target visibilities")
    print("                          imgtarget   - Image the calibrated target")
    print("                          selfcal     - Self calibrate")
    print("                          findsrcs    - (For internal use only)")
    print("                          chkselfcal  - (For internal use only)")
    print("                          flagcal     - Flag calibrated visibilities")
    print("                          contimg     - Attempt to produce the *final* continuum image")
    print("                          getuvsub    - Subtract the final continuum model")
    print("                          flaguvsub   - Flag continuum subtracted visibilities\n")

    print(" Combined modes           fullselfcal - Self calibrate until convergence reached")
    
    print("\n Let's try again...\n")
    return (0)

#   ---------------------------------------------------------------------------------------------------------

#   ------------------------------------    Main script starts here ----------------------

argus   = get_args()

print("\n\n ******** This is aNKimager ******** \n\n")

#   Read input parameters
if (argus.infile == None):
    print(" Missing input YAML file! Please provide one...")
    sys.exit()
else:
    with open(argus.infile+'.yml', 'r') as infl:
        pars = ym.load(infl, Loader=ym.SafeLoader)
        if (argus.listpars):
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
#   List supported modes
if (argus.listmodes):  
    print_modes()

#   --------------------------- Tasks   ------------



#   Channel average target visibilities
if (argus.avgtarget):      
    for ivis in pars['VisList']:
        avgtarget (ivis, pars)


#   Image the target field
if (argus.imgtarget):      
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg.ms" for vis in pars['VisList'] ]

    imgtarget(listofvis, argus.imgname, argus.savemodel, argus.intmask, pars)


#   Find sources and make a catalogue
if (argus.findsrcs):  
    imgfile  = pars['WorkDir']+pars['ImgDir']+'/'+pars['TargetName']+'_'+argus.imgname   

    findsrcs (imgfile, pars)


#   Check if self calibration converged
if (argus.chkselfcal):  
    img1  = pars['WorkDir']+pars['ImgDir']+'/'+pars['TargetName']+'_'+argus.imgname
    img2  = pars['WorkDir']+pars['ImgDir']+'/'+pars['TargetName']+'_'+argus.oldimg    

    checkselfcal (img1, img2, pars)


#   Self-calibrate
if (argus.selfcal):      
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg" for vis in pars['VisList'] ]

    for ivis in listofvis:
        selfcal (ivis, ivis+".scal", argus.calmode, pars)


#   Flag calibrated visibilities
if (argus.flagcal):      
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg" for vis in pars['VisList'] ]

    for ivis in listofvis:
        flagcaltarget (ivis, pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)


#   Attempt to produce the *final* continuum image
if (argus.contimg):      
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_avg.ms" for vis in pars['VisList'] ]

    finalimg(listofvis, argus.savemodel, pars)


#   Channel average target visibilities
if (argus.getuvsub):      
    for ivis in pars['VisUvSub']:
        getuvsub (ivis, ivis+"_f_avg.scal", pars)


#   Flag continuum subtracted visibilities
if (argus.flaguvsub):      
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_uvsub" for vis in pars['VisUvSub'] ]

    for ivis in listofvis:
        flagavguvsub (ivis, pars, ankdir=argus.pipedir+"ankflag_3/", ankin=argus.flgin, ovrt=argus.overwrite)





