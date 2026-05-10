import os,sys
import numpy as np
import casatasks as ct
import casatools
from casaplotms import plotms




#   -----------------------------------------------------------------------------------------------------
def importrawuvfile (fitsname, rawflglist, ovrt = False):
    
    #   Import the raw UV data and apply the raw flagfile

    if (os.path.exists(fitsname+".ms")):
        if (ovrt):
            print("Clearing existing "+fitsname+".ms")
            os.system("rm -rf "+fitsname+".ms")
        else:
            print("MS file exists. use --overwrite to clear it.")
            return (1)

    print("Creating MS file...")              
    ct.importgmrt(fitsfile=fitsname+".fits", flagfile=rawflglist, vis=fitsname+".ms")
    print("\n Done!\n")
    
    return (0)
#   -----------------------------------------------------------------------------------------------------





def initrawuvfile (fitsname, pars, rfifreq=None, ovrt = False):
    
    #   Prepare listobs and flag auto correlations

    print("Preparing listobs...\n")              
    ct.listobs(vis=fitsname+".ms", listfile=pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+".listobs", overwrite=ovrt)

    print("Flagging autocorrelations...\n") 
    ct.flagdata(vis=fitsname+".ms", mode="manual", autocorr=True)

    print("\nFlagging beginning and end of scans...\n")
    ct.flagdata(vis=fitsname+".ms", mode="quack", quackmode='beg', quackinterval=float(pars['CalScanEnd']))
    ct.flagdata(vis=fitsname+".ms", mode="quack", quackmode='endb', quackinterval=float(pars['CalScanEnd']))

    wmsmd   = casatools.msmetadata()
    wmsmd.open(fitsname+".ms")
    chan_freqs  = wmsmd.chanfreqs(0)/1.0e6
    chan_wmhz   = np.mean(wmsmd.chanwidths(0))/1.0e6
    nchans      = len(chan_freqs)
    wmsmd.done()

    print("Mean channel width in MHz = ",chan_wmhz)
    nedgechan   = int(pars['EdgeMhz'] / chan_wmhz) + 1

    print("\nFlagging %d edge channels...\n"%(nedgechan)) 
    ct.flagdata(vis=fitsname+".ms", mode="manual", spw="0:0~"+str(nedgechan)+";"+str(nchans-nedgechan-1)+"~"+str(nchans-1) )

    if ((rfifreq != None) and os.path.exists(rfifreq)):        

        rfifreqs    = np.loadtxt(rfifreq)
        
        if ( (len(rfifreqs.shape) == 2) and (rfifreqs.shape[0] >= 2)):

            print("Flagging RFI frequencies...\n")
            chanstr     = "0:"

            for i in range (1, rfifreqs.shape[0]):
                cl      = np.argmin(np.abs(chan_freqs - rfifreqs[i,0])) 
                cr      = np.argmin(np.abs(chan_freqs - rfifreqs[i,1])) 
                chanstr = chanstr+str(min(cl,cr))+"~"+str(max(cl,cr) )+";"
        
            chanstr     = chanstr[:-1]
            print(chanstr)
            ct.flagdata(vis=fitsname+".ms", mode="manual", spw=chanstr )    

    cstart   = np.argmin(np.abs(chan_freqs - pars["FreqRange"][0])) 
    cend     = np.argmin(np.abs(chan_freqs - pars["FreqRange"][1])) 

    print(f"\n Extracting channel range {cstart} - {cend}\n")
    ct.mstransform(
        vis=fitsname+".ms", \
        outputvis=fitsname+"_temp.ms", \
        datacolumn="DATA", \
        keepflags=False, \
        spw="0:"+str(cstart)+"~"+str(cend), \
        correlation=pars['CorrProds']
    )

    os.system("rm -rf "+fitsname+".ms")
    os.system("mv "+fitsname+"_temp.ms "+fitsname+".ms")  

    print("\n Done!\n")

    return (0)
#   -----------------------------------------------------------------------------------------------------





def makesinglechan(fitsname, pars = None, ovrt =False):
    
    #   Isolate channel = chan0 from the maultichannel MS

    wmsmd   = casatools.msmetadata()
    wmsmd.open(fitsname+".ms")
    chan_freqs  = wmsmd.chanfreqs(0)/1.0e6
    wmsmd.done()

    chan0   = np.argmin(np.abs(chan_freqs - pars["SingleChan"])) 

    chan0file   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.ms"

    if (os.path.exists(chan0file)):
        if (ovrt):
            print("Clearing existing "+chan0file)
            os.system("rm -rf "+chan0file)
        else:
            print("Single channel file exists. use --overwrite to clear it.")
            return (1)

    print(f"\n Creating single channel {chan0} file... \n")
    ct.mstransform(vis=fitsname+".ms", outputvis=chan0file, datacolumn="DATA", keepflags=False, \
                   spw="0:"+str(chan0), correlation=pars['CorrProds'], uvrange=pars['CalUvLim'], \
                    field=pars['FluxCal']+","+pars['PhaseCal'])
    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def setfluxsinglechan(pars = None):
    
    #   Set flux scale for the channel 0 file

    chan0file   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.ms"

    print("Setting flux density of single channel file...")
    setjyout = ct.setjy(vis=chan0file, field=pars['FluxCal'])
    print(pars['FluxCal']," flux density ",setjyout)
    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def calsinglechan(pars = None):
    
    #   Calibrate the channel 0 file

    chan0file   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.ms"
    calfile     = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.cal"
    fluxfile    = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.fl"

    if (os.path.exists(calfile)):
        os.system("rm -rf "+calfile)
    
    if (os.path.exists(fluxfile)):
        os.system("rm -rf "+fluxfile)

    print("Calibrating single channel file...\n")
    
    ct.gaincal(
        vis=chan0file, \
        caltable=calfile, \
        field=pars['FluxCal']+","+pars['PhaseCal'], \
        solint=pars['GainInt'], \
        refant=pars['RefAntenna'], \
        minsnr=pars['MinSNR'], \
        solmode='R', \
        rmsthresh=pars['OutThresh']
    )
    
    print("\nFlux scaling...\n")
    fsout = ct.fluxscale(vis=chan0file, caltable=calfile, fluxtable=fluxfile, reference=pars['FluxCal'], transfer=pars['PhaseCal'])
    print(pars['PhaseCal']," flux density ",fsout)

    print("\nApplying calibration...\n")
    ct.applycal(vis=chan0file, gaintable=[fluxfile], applymode='calonly')

    plotms(
        vis=calfile, \
        xaxis="time", \
        yaxis="amp", \
        gridrows=2, \
        height=1000, \
        width=1000, \
        gridcols=1, \
        coloraxis='antenna1', \
        showgui=False
    )

    plotms(
        vis=calfile, \
        xaxis="time", \
        yaxis="phase", \
        gridrows=2, \
        gridcols=1, \
        rowindex=1, \
        plotindex=1, \
        clearplots=False, \
        plotfile=pars['WorkDir']+pars['LogDir']+"/cal_"+pars['ReducedName']+"_ch0.png", \
        height=1000, \
        width=1000, \
        coloraxis='antenna1', \
        overwrite=True, \
        showgui=False
    )

    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def flagsinglechan (pars=None, ankdir=None, ankin=None, ovrt=False):
    
    #   Flag calibrator data in the channel 0 file

    chan0file   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.ms"

    fcalfile    = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0_fcal"
    pcalfile    = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0_pcal"
    
    if (os.path.exists(fcalfile+".fits") and ovrt):
        os.system("rm -rf "+fcalfile+".fits")
    if (os.path.exists(pcalfile+".fits") and ovrt):
        os.system("rm -rf "+pcalfile+".fits")


    #   ----------------------------------
    #   Flag calibrators with aNKflag
    #   ----------------------------------

    if ( (ankin != None) and (os.path.exists(ankin+'.yml')) ):

        print("Exporting calibrator FITS...\n")
        ct.exportuvfits(vis=chan0file, fitsfile=fcalfile+".fits", datacolumn='corrected', field=pars['FluxCal'], overwrite=ovrt)
        ct.exportuvfits(vis=chan0file, fitsfile=pcalfile+".fits", datacolumn='corrected', field=pars['PhaseCal'], overwrite=ovrt)

        
        print("Flagging calibrators with aNKflag...\n")        
    
        if (not os.path.exists("glogout.dat")):
            os.system("cp "+ankdir+"/glogout.dat .")

        fcalcmd = "python3 " + ankdir + "/runank.py --ankdir " + ankdir + " --scratchdir ankscratch/ " + \
                    " --parfile " + ankin + " --infilename " + fcalfile + " --outfilename " + fcalfile+"_f" + \
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/fcal_"+pars['FluxCal'] + \
                    " --flagmode uvbin --targetype=calch0 --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + fcalcmd)
        os.system(fcalcmd)

        pcalcmd = "python3 " + ankdir + "/runank.py --ankdir " + ankdir + " --scratchdir ankscratch/ " + \
                    " --parfile " + ankin + " --infilename " + pcalfile + " --outfilename " + pcalfile+"_f" + \
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/pcal_"+pars['PhaseCal'] + \
                    " --flagmode uvbin --targetype=calch0 --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + pcalcmd)
        os.system(pcalcmd)

        if (os.path.exists(fcalfile+"_f.ms")):
            os.system("rm -rf "+fcalfile+"_f.ms")
        if (os.path.exists(pcalfile+"_f.ms")):
            os.system("rm -rf "+pcalfile+"_f.ms")

        print("Converting calibrator FITS back to MS...\n")
        ct.importuvfits(vis=fcalfile+"_f.ms", fitsfile=fcalfile+"_f.fits")
        ct.importuvfits(vis=pcalfile+"_f.ms", fitsfile=pcalfile+"_f.fits")


        print("Generating diagnostic plots...")

        plotms(vis=fcalfile+"_f.ms", xaxis="row", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=fcalfile+"_f.ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/fcal_"+pars['ReducedName']+"_row.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)

        plotms(vis=pcalfile+"_f.ms", xaxis="row", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=pcalfile+"_f.ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/pcal_"+pars['ReducedName']+"_row.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)



        #   Open and edit the flags in the MS files
        print("Copying flags to the single channel file...\n")
        wms     = casatools.ms()
        wmsmd   = casatools.msmetadata()

        wms.open(fcalfile+"_f.ms")
        wms.selectinit(datadescid=0)
        fcalflgs  = wms.getdata(["flag"])["flag"]
        #print(fcalflgs.shape)
        wms.close()

        wms.open(pcalfile+"_f.ms")
        wms.selectinit(datadescid=0)
        pcalflgs  = wms.getdata(["flag"])["flag"]
        #print(pcalflgs.shape)
        wms.close()

        wmsmd.open(chan0file)
        fcalfld = wmsmd.fieldsforname(pars['FluxCal'])
        pcalfld = wmsmd.fieldsforname(pars['PhaseCal'])
        wmsmd.done()

        wms.open(chan0file, nomodify=False)
        wms.selectinit(datadescid=0)
        wms.select({'field_id':fcalfld})
        fldflg  = wms.getdata(["flag"])
        fldflg["flag"] = fcalflgs
        #print(fldflg["flag"].shape)
        wms.putdata(fldflg)
        wms.close()

        wms.open(chan0file, nomodify=False)
        wms.selectinit(datadescid=0)
        wms.select({'field_id':pcalfld})
        fldflg  = wms.getdata(["flag"])
        fldflg["flag"] = pcalflgs
        #print(fldflg["flag"].shape)
        wms.putdata(fldflg)
        wms.close()

    print(" Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def exbpcal (fitsname, bpcal, pars=None):
    
    #   Extract the bandpass calibrator

    fluxfile    = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.fl"
    bpcalfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_bpcal_"+bpcal+".ms"

    os.system("rm -rf "+bpcalfile)
    os.system("rm -rf "+bpcalfile+".*")

    print("\nApplying calibration...\n")
    ct.applycal(vis=fitsname+".ms", field=bpcal, gaintable=[fluxfile], applymode='')

    print("Exporting BP cal...\n")
    ct.mstransform(vis=fitsname+".ms", outputvis=bpcalfile, datacolumn="corrected", keepflags=False, \
                   correlation=pars['CorrProds'], uvrange=pars['CalUvLim'], field=bpcal)

    print("Setting flux density of BP cal file...")
    setjyout = ct.setjy(vis=bpcalfile, field=bpcal)
    print(bpcal," flux density ",setjyout)

    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def calbpcal (bpcal, pars=None):
    
    #   Calibrate bandpass

    bpassfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_bpcal_"+bpcal+".bp"
    bpcalfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_bpcal_"+bpcal+".ms"

    if (os.path.exists(bpassfile)):
        os.system("rm -rf "+bpassfile)

    print("\nCalculating bandpass...\n")
    ct.bandpass(vis=bpcalfile, caltable=bpassfile, field=bpcal, refant=pars['RefAntenna'], minsnr=float(pars['MinSNR']))

    print("\nApplying bandpass...\n")
    ct.applycal(vis=bpcalfile, gaintable=[bpassfile], applymode='')

    plotms(
        vis=bpassfile, \
        xaxis="frequency", \
        yaxis="amp", \
        gridrows=2, \
        height=1000, \
        width=1000, \
        gridcols=1, \
        coloraxis='antenna1', \
        showgui=False
    )

    plotms(
        vis=bpassfile, \
        xaxis="frequency", \
        yaxis="phase", \
        gridrows=2, \
        gridcols=1, \
        rowindex=1, \
        plotindex=1, \
        clearplots=False, \
        plotfile=pars['WorkDir']+pars['LogDir']+"/bpcal_"+pars['ReducedName']+".png", \
        height=1000, \
        width=1000, \
        coloraxis='antenna1', \
        overwrite=True, \
        showgui=False
    )

    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def flagbpcal (bpcal, pars=None, ankdir=None, ankin=None, ovrt=False):
    
    #   Flag bandpass calibrator data 

    bpcalfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_bpcal_"+bpcal
    
    if (os.path.exists(bpcalfile+".fits") and ovrt):
        os.system("rm -rf "+bpcalfile+".fits")
    

    #   ----------------------------------
    #   Flag calibrators with aNKflag
    #   ----------------------------------
    
    if ( (ankin != None) and (os.path.exists(ankin+'.yml')) ):

        print("Exporting calibrator FITS...\n")
        ct.exportuvfits(vis=bpcalfile+".ms", fitsfile=bpcalfile+".fits", datacolumn='corrected', field=bpcal, overwrite=ovrt)

        
        print("Flagging calibrators with aNKflag...\n")        
    
        if (not os.path.exists("glogout.dat")):
            os.system("cp "+ankdir+"/glogout.dat .")

        bpcalcmd = "python3 " + ankdir + "/runank.py --ankdir " + ankdir + " --scratchdir ankscratch/ " + \
                    " --parfile " + ankin + " --infilename " + bpcalfile + " --outfilename " + bpcalfile+"_f" + \
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/bpcal_"+bpcal + \
                    " --flagmode uvbin --targetype=calbp --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + bpcalcmd)
        os.system(bpcalcmd)

        if (os.path.exists(bpcalfile+"_f.ms")):
            os.system("rm -rf "+bpcalfile+"_f.ms")

        print("Converting BP calibrator FITS back to MS...\n")
        ct.importuvfits(vis=bpcalfile+"_f.ms", fitsfile=bpcalfile+"_f.fits")
        
        print("Generating diagnostic plots...")

        plotms(vis=bpcalfile+"_f.ms", xaxis="frequency", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=bpcalfile+"_f.ms", xaxis="frequency", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/bpcal_"+pars['ReducedName']+"_freq.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)

        plotms(vis=bpcalfile+"_f.ms", xaxis="row", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=bpcalfile+"_f.ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/bpcal_"+pars['ReducedName']+"_row.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)

        #   Open and edit the flags in the MS files
        print("Copying flags to the BP cal file...\n")
        wms     = casatools.ms()

        wms.open(bpcalfile+"_f.ms")
        wms.selectinit(datadescid=0)
        bpcalflgs  = wms.getdata(["flag"])["flag"]
        #print(bpcalflgs.shape)
        wms.close()        

        wms.open(bpcalfile+".ms", nomodify=False)
        wms.selectinit(datadescid=0)
        fldflg  = wms.getdata(["flag"])
        fldflg["flag"] = bpcalflgs
        #print(fldflg["flag"].shape)
        wms.putdata(fldflg)
        wms.close()

    
    print(" Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def extarget (fitsname, bpcal, pars=None):
    
    #   Extract calibrated target visibilities

    fluxfile    = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_ch0.fl"
    bpassfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_bpcal_"+bpcal+".bp"
    tarfile     = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_"+pars['TargetName']+".ms"

    if (os.path.exists(tarfile)):
        os.system("rm -rf "+tarfile)

    print("\nApplying calibration...\n")
    ct.applycal(vis=fitsname+".ms", field=pars['TargetName'], gaintable=[fluxfile,bpassfile], applymode='')

    print("Exporting target file...\n")
    ct.mstransform(
        vis=fitsname+".ms", \
        outputvis=tarfile, \
        datacolumn="corrected", \
        uvrange=pars['TarUvLim'], \
        keepflags=False, \
        correlation=pars['CorrProds'], \
        field=pars['TargetName']
    )
    
    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def flagtarget (targetname, pars=None, ankdir=None, ankin=None, ovrt=False):
    
    #   Flag calibrated target data 

    tarfile   = pars['WorkDir']+pars['UvMsDir']+pars['ReducedName']+"_"+targetname
    
    if (os.path.exists(tarfile+".fits") and ovrt):
        os.system("rm -rf "+tarfile+".fits")
    

    #   ----------------------------------
    #   Flag target with aNKflag
    #   ----------------------------------
    
    if ( (ankin != None) and (os.path.exists(ankin+'.yml')) ):

        print("Exporting target FITS...\n")
        ct.exportuvfits(vis=tarfile+".ms", fitsfile=tarfile+".fits", datacolumn='corrected', overwrite=ovrt)

        
        print("Flagging the target aNKflag...\n")        
    
        if (not os.path.exists("glogout.dat")):
            os.system("cp "+ankdir+"/glogout.dat .")

        tarcmd = "python3 " + ankdir + "/runank.py --ankdir " + ankdir + " --scratchdir ankscratch/ " + \
                    " --parfile " + ankin + " --infilename " + tarfile + " --outfilename " + tarfile+"_f" + \
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/target_"+targetname + \
                    " --flagmode uvbin --targetype=normal --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + tarcmd)
        os.system(tarcmd)

        if (os.path.exists(tarfile+"_f.ms")):
            os.system("rm -rf "+tarfile+"_f.ms")

        print("Converting target FITS back to MS...\n")
        ct.importuvfits(vis=tarfile+"_f.ms", fitsfile=tarfile+"_f.fits")
        
    
    print(" Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------


