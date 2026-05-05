#!/bin/bash

#   ***********************************************************#
#   A common script to run imaging and transient search
#
#   Inputs are	          <operation> <task> <o or p or imgname (optional)> <savemodel and or intmask>
#
#   Operation modes       calibrate, imgcal
#
#   ***********************************************************

#   Python exetuable to use 
pyex="/home/bera/basilisk/bin/python"


#	Set the desired directories (Use abosulte paths to avoid confusion)

Pipe_Dir="../../thepipe/"
Input_Dir="../inputfiles/"


#	Input files

parfile="march15"
flgpar="ankpar"
rfifile="rfifreqb3.txt"

imgparfile="img_b3_lugia"
imgext="00"

savemodel=""
intmask=""
scalmode=""
ovr=""

#   Read command line inputs

if [[ "$2" == "h" ]]; then
	mode="--help"
else
    mode="--mode $2"
fi

if [[ "$3" == "o" ]]; then
	ovr="--overwrite"
elif [[ "$3" == "p" ]]; then
	scalmode="--calmode p"
else
    imgext="$3"
fi

if [[ "$4" == "savemodel" || "$5" == "savemodel" ]]; then
	savemodel="--savemodel"
fi

if [[ "$4" == "intmask" || "$5" == "intmask" ]]; then
	intmask="--intmask"
fi

#   Construct commands

ankcalcmd="${pyex} ${Pipe_Dir}/pipescripts/ankcalibrator.py \
    --pipedir ${Pipe_Dir} \
    --infile ${Input_Dir}/${parfile} \
    --flgin ${Input_Dir}/${flgpar} \
    --rfifile ${Input_Dir}/${rfifile} \
    ${mode} ${ovr}"

ankimgcmd="${pyex} ${Pipe_Dir}/pipescripts/ankimager.py \
    --pipedir ${Pipe_Dir} \
    --infile ${Input_Dir}/${imgparfile} \
    --flgin ${Input_Dir}/${flgpar} \
    --rfifile ${Input_Dir}/${rfifile} \
    --imgname ${imgext} \
    ${savemodel} ${intmask} ${scalmode} \
    ${mode} ${ovr}"

#   Run commands

excmd=""

if [[ "$1" == "calibrate" ]]; then
    excmd="$ankcalcmd"
    echo "Running calibration processes... "    
    echo $excmd
elif [[ "$1" == "imgcal" ]]; then
    excmd="$ankimgcmd"
    echo "Running imaging and selfcal processes... "    
    echo $excmd
else
    echo "Unknown operation mode..."
fi


export PYTHONPATH=${PYTHONPATH}:${Pipe_Dir} 

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

${excmd} 

