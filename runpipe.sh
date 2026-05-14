#!/bin/bash

#   ***********************************************************#
#   A common script to run imaging and transient search
#
#   Inputs are	          <operation> <task> <o or p or imgname (optional)> <savemodel and/or intmask>
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

parfile="calibration_b4_exam"
flgpar="ankpar_b4"
rfifile="rfifreqb4.txt"

imgparfile="img_b4_lugia"
imgext="03"
imgext0="02"

searchpars="search_b4"

savemodel=""
intmask=""
scalmode=""
ovr=""

#   Read command line inputs

mode="$2"

if [[ "$3" == "o" ]]; then
	ovr="--obliviate"
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
    --oldimg ${imgext0} \
    ${savemodel} ${intmask} ${scalmode} \
    ${mode} ${ovr}"

snapcmd="${pyex} ${Pipe_Dir}/pipescripts/snapshoter.py \
    --infile ${Input_Dir}/${imgparfile} \
    ${mode} ${ovr}"

searchcmd="${pyex} ${Pipe_Dir}/pipescripts/temprocess.py \
    --infile ${Input_Dir}/${searchpars} \
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
elif [[ "$1" == "snapshot" ]]; then
    excmd="$snapcmd"
    echo "Running snapshot imaging... "    
    echo $excmd
elif [[ "$1" == "search" ]]; then
    excmd="$searchcmd"
    echo "Looking for trnsients... "    
    echo $excmd
else
    echo "Unknown operation mode..."
fi


export PYTHONPATH=${PYTHONPATH}:${Pipe_Dir} 

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

${excmd} 

