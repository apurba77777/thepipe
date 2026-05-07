import os,sys
import numpy as np
import casatasks as ct
import casatools
from casaplotms import plotms






def avgtarget (targetvis, pars=None):
    
    #   Channel average calibrated target visibilities


    avgvis  = targetvis+"_avg"

    if ( os.path.exists( pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms" ) ):
        os.system("rm -rf "+pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms")


    print("Channel averaging...\n")
    ct.mstransform(
        vis=pars['WorkDir']+pars['UvMsDir']+'/'+targetvis+".ms", \
        outputvis=pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms", \
        datacolumn="data", \
        keepflags=False, \
        hanning=True, \
        chanaverage=True, \
        chanbin=pars['TarChanAvg']
    )



    print("Generating diagnostic plots...")

    plotms(vis=pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms", xaxis="frequency", yaxis="amp", gridrows=2, \
           height=1000, width=1000, gridcols=1, showgui=False)

    plotms(vis=pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms", xaxis="frequency", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
            plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/target_"+avgvis+"_freq.png", \
                height=1000, width=1000, overwrite=True, showgui=False)

    plotms(vis=pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms", xaxis="row", yaxis="amp", gridrows=2, \
           height=1000, width=1000, gridcols=1, showgui=False)

    plotms(vis=pars['WorkDir']+pars['ImgUvDir']+'/'+avgvis+".ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
            plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/target_"+avgvis+"_row.png", \
                height=1000, width=1000, overwrite=True, showgui=False)
    
    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def imgtarget (targetvislist, imgname, dosavemodel=True, dointeractive=False, pars=None):
    
    #   Image calibrated target  
    
    imgpre  = pars['WorkDir']+pars['ImgDir']+'/'+pars['TargetName']+'_'+imgname

    print("\nVisibilities -- ",targetvislist)
    print("Imagename -- ",imgpre)    

    print("Clearing existing image components...\n")
    os.system("rm -rf "+imgpre+".*")

    savemod = 'none'
    if (dosavemodel):
        savemod = 'modelcolumn'


    print("\nMaking image...\n")
    ct.tclean(
        vis=targetvislist, \
        imagename=imgpre, \
        datacolumn="corrected", \
        imsize=pars['ImgSize'], \
        cell=pars['CellSize'], \
        selectdata=True, \
        field=pars['TargetName'],\
        uvrange=pars['ImgUvLim'], \
        startmodel=pars['PreModel'], \
        specmode='mfs', \
        gridder='widefield', \
        wprojplanes=pars['WprojPln'], \
        pblimit=-0.1, \
        deconvolver='mtmfs', \
        scales=pars['DeconScls'], \
        smallscalebias=pars['SclBias'], \
        weighting='briggs',\
        robust=pars['WtRobust'], \
        uvtaper=pars['ImUvTaper'], \
        niter=pars['ImNiter'], \
        nsigma=pars['ClnSigma'], \
        interactive=dointeractive, \
        usemask=pars['HowToMask'], \
        mask=pars['MaskFile'], \
        pbmask=0.2, \
        savemodel=savemod        
    )
    
    print(" Done!\n")

    return (0)
#   -----------------------------------------------------------------------------------------------------





def selfcal (targetvis, calfile, gcmode=None, pars = None):
    
    #   Self-calibrate target visibilities

    if (os.path.exists(calfile)):
        os.system("rm -rf "+calfile)
    
    scmode = "ap"
    apmode = ""
    if (gcmode!=None and gcmode=="p"):
        scmode="p"
        #apmode='calonly'

    print("Self-calibrating in "+scmode+" mode...\n")
    
    ct.gaincal(
        vis=targetvis+".ms", \
        caltable=calfile, \
        uvrange=pars['CalUvLim'], \
        solint=pars['GainInt'], \
        refant=pars['RefAntenna'], \
        minsnr=pars['MinSNR'], \
        calmode=scmode, \
        solmode='R', \
        rmsthresh=pars['OutThresh']
    )

    print("\nApplying calibration...\n")
    ct.applycal(vis=targetvis+".ms", gaintable=[calfile], applymode=apmode)


    print("\nPlotting solutions...\n")

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
        plotfile=pars['WorkDir']+pars['LogDir']+"/selfcal.png", \
        height=1000, \
        width=1000, \
        coloraxis='antenna1', \
        overwrite=True, \
        showgui=False
    )

    print("\n Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def flagcaltarget (tarfile, pars=None, ankdir=None, ankin=None, ovrt=False):
    
    #   Flag calibrated target data 
    
    
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
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/sc_target_"+pars['TargetName'] + \
                    " --flagmode uvbin --targetype=normal --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + tarcmd)
        os.system(tarcmd)

        if (os.path.exists(tarfile+"_f.ms")):
            os.system("rm -rf "+tarfile+"_f.ms")

        print("Converting BP calibrator FITS back to MS...\n")
        ct.importuvfits(vis=tarfile+"_f.ms", fitsfile=tarfile+"_f.fits")
        
        print("Generating diagnostic plots...")

        plotms(vis=tarfile+"_f.ms", xaxis="frequency", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=tarfile+"_f.ms", xaxis="frequency", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/sc_target_"+pars['TargetName']+"_freq.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)

        plotms(vis=tarfile+"_f.ms", xaxis="row", yaxis="amp", gridrows=2, \
               height=1000, width=1000, gridcols=1, showgui=False)

        plotms(vis=tarfile+"_f.ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
                plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/sc_target_"+pars['TargetName']+"_row.png", \
                    height=1000, width=1000, overwrite=True, showgui=False)
        


        #   Open and edit the flags in the MS files
        print("Copying flags to the original file...\n")
        wms     = casatools.ms()

        wms.open(tarfile+"_f.ms")
        wms.selectinit(datadescid=0)
        tarcalflgs  = wms.getdata(["flag"])["flag"]
        #print(bpcalflgs.shape)
        wms.close()        

        wms.open(tarfile+".ms", nomodify=False)
        wms.selectinit(datadescid=0)
        fldflg  = wms.getdata(["flag"])
        fldflg["flag"] = tarcalflgs
        #print(fldflg["flag"].shape)
        wms.putdata(fldflg)
        wms.close()

    
    print(" Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------





def finalimg (targetvislist, dosavemodel=True, pars=None):
    
    #   Attempt to produce the *final* continuum image 
    
    imgpre  = pars['WorkDir']+pars['ImgDir']+'/'+pars['FinImage']

    print("\nVisibilities -- ",targetvislist)
    print("Imagename -- ",imgpre)    

    print("Clearing existing image components...\n")
    os.system("rm -rf "+imgpre+".*")

    savemod = 'none'
    if (dosavemodel):
        savemod = 'modelcolumn'

    hrad    = float(pars['ImgSize'][0])/2
    finmask = 'Circle[['+str(hrad)+'pix, '+str(hrad)+'pix],'+str(hrad)+'pix]'

    print("\nMaking image...\n")
    ct.tclean(
        vis=targetvislist, \
        imagename=imgpre, \
        datacolumn="corrected", \
        imsize=pars['ImgSize'], \
        cell=pars['CellSize'], \
        selectdata=True, \
        field=pars['TargetName'],\
        uvrange=pars['FinUvLim'], \
        specmode='mfs', \
        gridder='widefield', \
        wprojplanes=pars['WprojPln'], \
        pblimit=-0.1, \
        deconvolver='mtmfs', \
        scales=pars['DeconScls'], \
        smallscalebias=pars['SclBias'], \
        weighting='briggs',\
        robust=pars['ImRobust'], \
        uvtaper=pars['ImUvTaper'], \
        niter=pars['FiNiter'], \
        nsigma=pars['FinSigma'], \
        interactive=False, \
        usemask=pars['HowToMask'], \
        mask=finmask, \
        pbmask=0.2, \
        savemodel=savemod        
    )
    
    print(" Done!\n")

    return (0)
#   -----------------------------------------------------------------------------------------------------






def getuvsub (ivis, calfile, pars=None): 

    #   Prepare calibrated and model subtracted visibilities 

    finmodel0   = pars['WorkDir']+pars['ImgDir']+'/'+pars['FinImage']+'.model.tt0'
    finmodel1   = pars['WorkDir']+pars['ImgDir']+'/'+pars['FinImage']+'.model.tt1'

    targetvis   = pars['WorkDir']+pars['UvMsDir']+'/'+ivis+".ms"
    outfits     = pars['WorkDir']+pars['ImgUvDir']+'/'+ivis+"_uvsub.fits"

    print("\nApplying calibration...\n")
    ct.applycal(vis=targetvis, gaintable=[pars['WorkDir']+pars['ImgUvDir']+calfile], applymode='')

    imgpre  = "junk"

    print("\nVisibilities -- ",targetvis)
    print("Imagename -- ",imgpre)    

    os.system("rm -rf "+imgpre+".*")

    hrad    = float(pars['ImgSize'][0])/2
    finmask = 'Circle[['+str(hrad)+'pix, '+str(hrad)+'pix],'+str(hrad)+'pix]'

    print("\nMaking the junk image...\n")
    ct.tclean(
        vis=targetvis, \
        imagename=imgpre, \
        startmodel=[finmodel0, finmodel1], \
        datacolumn="corrected", \
        imsize=pars['ImgSize'], \
        cell=pars['CellSize'], \
        selectdata=True, \
        field=pars['TargetName'],\
        specmode='mfs', \
        gridder='widefield', \
        wprojplanes=pars['WprojPln'], \
        pblimit=-0.1, \
        deconvolver='mtmfs', \
        scales=pars['DeconScls'], \
        smallscalebias=pars['SclBias'], \
        weighting='briggs',\
        robust=pars['ImRobust'], \
        uvtaper=pars['ImUvTaper'], \
        niter=0, \
        nsigma=10.0, \
        interactive=False, \
        usemask='user', \
        mask=finmask, \
        pbmask=0.2, \
        savemodel='modelcolumn'        
    )

    os.system("rm -rf "+imgpre+".*")

    print("\n Subtracting model visibilities...\n")
    ct.uvsub(vis=targetvis)

    print(" Exporting target FITS...\n")
    ct.exportuvfits(vis=targetvis, fitsfile=outfits, datacolumn='corrected', overwrite=True)
    
    print(" Done!\n")

    return (0)
#   -----------------------------------------------------------------------------------------------------






def flagavguvsub (tarfile, pars=None, ankdir=None, ankin=None, ovrt=False):
    
    #   Flag calibrated continuum subtracted visibilities and average in channel
    
    
    if (os.path.exists(tarfile+"_f.fits") and ovrt):
        os.system("rm -rf "+tarfile+"_f.fits")
    
    filetoavg   = tarfile

    #   ----------------------------------
    #   Flag target with aNKflag
    #   ----------------------------------
    
    if ( (ankin != None) and (os.path.exists(ankin+'.yml')) ):
        
        print("Flagging the target aNKflag...\n")        
    
        if (not os.path.exists("glogout.dat")):
            os.system("cp "+ankdir+"/glogout.dat .")

        tarcmd = "python3 " + ankdir + "/runank.py --ankdir " + ankdir + " --scratchdir ankscratch/ " + \
                    " --parfile " + ankin + " --infilename " + tarfile + " --outfilename " + tarfile+"_f" + \
                    " --logfile " +pars['WorkDir']+pars['LogDir']+"/uvsub_"+pars['TargetName'] + \
                    " --flagmode uvbin --targetype=uvsub --clearscratch --nthreads " + str(pars['FlgThreads'])

        print("Running \n" + tarcmd)
        os.system(tarcmd)

        filetoavg   = tarfile+"_f"
    

    if (os.path.exists(filetoavg+".ms")):
        os.system("rm -rf "+filetoavg+".ms")

    print("Converting flagged FITS back to MS...\n")
    ct.importuvfits(vis=filetoavg+".ms", fitsfile=filetoavg+".fits")


    if (os.path.exists(filetoavg+"_avg.ms")):
        os.system("rm -rf "+filetoavg+"_avg.ms")


    print("Channel averaging...\n")
    ct.mstransform(
        vis=filetoavg+".ms", \
        outputvis=filetoavg+"_avg.ms", \
        datacolumn="data", \
        keepflags=False, \
        hanning=True, \
        chanaverage=True, \
        chanbin=pars['FinChanAvg']
    )



    print("Generating diagnostic plots...")

    plotms(vis=filetoavg+"_avg.ms", xaxis="frequency", yaxis="amp", gridrows=2, \
           height=1000, width=1000, gridcols=1, showgui=False)

    plotms(vis=filetoavg+"_avg.ms", xaxis="frequency", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
            plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/uvsub_"+pars['TargetName']+"_freq.png", \
                height=1000, width=1000, overwrite=True, showgui=False)

    plotms(vis=filetoavg+"_avg.ms", xaxis="row", yaxis="amp", gridrows=2, \
           height=1000, width=1000, gridcols=1, showgui=False)

    plotms(vis=filetoavg+"_avg.ms", xaxis="row", yaxis="phase", gridrows=2, gridcols=1, rowindex=1, \
            plotindex=1, clearplots=False, plotfile=pars['WorkDir']+pars['LogDir']+"/uvsub_"+pars['TargetName']+"_row.png", \
                height=1000, width=1000, overwrite=True, showgui=False)


    
    print(" Done!\n")


    return (0)
#   -----------------------------------------------------------------------------------------------------