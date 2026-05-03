#!/bin/bash

#   ***********************************************************#
#   A common script to run imaging and transient search
#
#   Inputs are	          <mode> <o (optional)>
#   ***********************************************************

#   Python exetuable to use 
pyex="/home/bera/basilisk/bin/python"


#	Set the desired directories (Use abosulte paths to avoid confusion)

Pipe_Dir="../../thepipe/"
Input_Dir="../inputfiles/"


#	CELEBI options

parfile="march15"
flgpar="ankpar"
rfifile="rfifreqb3.txt"


#   Read command line inputs

if [[ "$1" == "h" ]]; then
	mode="--help"
else
    mode="--mode $1"
fi

if [ "$2" == "o" ]; then
	ovr="--overwrite"
else
    ovr=""
fi


#   Run commands

echo "${pyex} ${Pipe_Dir}/pipescripts/pipeline.py --pipedir ${Pipe_Dir} --infile ${Input_Dir}/${parfile} --flgin ${Input_Dir}/${flgpar} --rfifile ${Input_Dir}/${rfifile} ${mode} ${ovr}"

export PYTHONPATH=${PYTHONPATH}:${Pipe_Dir} && ${pyex} ${Pipe_Dir}/pipescripts/ankimager.py --pipedir ${Pipe_Dir} --infile ${Input_Dir}/${parfile} --flgin ${Input_Dir}/${flgpar} --rfifile ${Input_Dir}/${rfifile} ${mode} ${ovr}


