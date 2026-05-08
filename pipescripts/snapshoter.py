import os,sys
import argparse as ap
import yaml as ym
from cascripts.timaging import *

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
    parser.add_argument("--overwrite", help = "Clear existing files?", action='store_true')

    args = parser.parse_args()

    return args


def print_modes():
    print("\n You need to specify a mode with --mode !!!!!\n")
    print(" Supported modes are      maketime    - Make list of timestamps in MJD")
    print("                          snapshot    - Make snapshot images")
    
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


#   ------------------  Make data directories   ---------------


if (os.path.exists(pars['OutDir']+pars['CubeDir'])):
    print("Found ",pars['OutDir']+pars['CubeDir'])
else:
    print("Creating ",pars['OutDir']+pars['CubeDir'])
    os.system("mkdir "+pars['OutDir']+pars['CubeDir'])


#   -------------------------   Missing mode    ---------
if (argus.mode == None):
    print_modes()
    sys.exit()

#   --------------------------- Tasks   ------------


#   Make list of timestamps in MJD

elif (argus.mode == "maketime"):  
    
    listofvis   = [ pars['WorkDir']+pars['ImgUvDir']+vis+"_uvsub_f_avg" for vis in pars['VisUvSub'] ]

    for ivis in listofvis:
        maketime (ivis)




#   Make snapshot images

elif (argus.mode == "snapshot"):

    listofvis   = [ vis+"_uvsub_f_avg" for vis in pars['VisUvSub'] ]

    for ivis in listofvis:
        times = np.loadtxt(pars['WorkDir']+pars['ImgUvDir']+ivis+"_mjds.txt")
        timager (pars['WorkDir']+pars['ImgUvDir']+ivis, pars['WorkDir']+pars['ImgDir']+ivis, times, pars, ntime=-1)

        cubename    = pars['OutDir']+pars['CubeDir']+"/"+ivis+"_tcube"
        makefits (times, cubename, ntime=-1)


else:
    print_modes()

