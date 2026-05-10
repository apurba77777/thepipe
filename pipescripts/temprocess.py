import os,sys
import argparse as ap
import yaml as ym
from dynspecripts.transearch import *

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
    print(" Supported modes are      searchpos   - Search at a specific sky position")
    print("                          qqqqqqqq    - ")
    
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


if (os.path.exists(pars['OutDir']+pars['PlotDir'])):
    print("Found ",pars['OutDir']+pars['PlotDir'])
else:
    print("Creating ",pars['OutDir']+pars['PlotDir'])
    os.system("mkdir "+pars['OutDir']+pars['PlotDir'])


#   -------------------------   Missing mode    ---------
if (argus.mode == None):
    print_modes()
    sys.exit()

#   --------------------------- Tasks   ------------


#   Search at a specific sky position

if (argus.mode == "searchpos"):  
    
    fitslist   = [ pars['OutDir']+pars['CubeDir']+fname for fname in pars['FitsNames'] ]

    for fitsname in fitslist:
        getdynspec (fitsname, pars)







else:
    print_modes()

