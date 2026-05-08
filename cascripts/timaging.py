import os,sys
import numpy as np
import casatasks as ct
import casatools
from casaplotms import plotms
from astropy.io import fits





def maketime (visfile):

    #   Make a list of time stamps in the given visibility dataset

    mjdfile = visfile+"_mjds.txt"
    
    msmd    = casatools.msmetadata()
    msmd.open(visfile+".ms")
    times   = msmd.timesforfield(0)
    msmd.done()    

    mjds    = times/86400

    print(f"Writing to {mjdfile}\n")    
    np.savetxt(mjdfile, np.array([times,mjds]).T, fmt="%.2f   %.6f")

    return(0)
#   -----------------------------------------------------------------------------------------------------





def makehdr (fitshdr, imdhr, tmjds):

    #   Build a FITS header from image header


    dtsec   = np.nanmedian(tmjds[1:,0] - tmjds[:-1,0])
    print(f"\n Time resolution = {dtsec} seconds\n")


    fitshdr['TIMESYS']  = imdhr['TIMESYS']
    fitshdr['RADESYS']  = imdhr['RADESYS']

    fitshdr['CTYPE1']   = imdhr['CTYPE'][0]
    fitshdr['CTYPE2']   = imdhr['CTYPE'][1]
    fitshdr['CTYPE3']   = imdhr['CTYPE'][3]
    fitshdr['CTYPE4']   = ('TIME', 'The time values are in an extension table')

    fitshdr['CUNIT1']   = imdhr['CUNIT1']
    fitshdr['CUNIT2']   = imdhr['CUNIT2']
    fitshdr['CUNIT3']   = imdhr['CUNIT4']
    fitshdr['CUNIT4']   = 'MJDSEC'

    fitshdr['CRPIX1']   = imdhr['CRPIX'][0]
    fitshdr['CRPIX2']   = imdhr['CRPIX'][1]
    fitshdr['CRPIX3']   = imdhr['CRPIX'][3]
    fitshdr['CRPIX4']   = 1.0

    fitshdr['CRVAL1']   = imdhr['CRVAL'][0]
    fitshdr['CRVAL2']   = imdhr['CRVAL'][1]
    fitshdr['CRVAL3']   = imdhr['CRVAL'][3]
    fitshdr['CRVAL4']   = 0.0

    fitshdr['CDELT1']   = imdhr['CDELT'][0]
    fitshdr['CDELT2']   = imdhr['CDELT'][1]
    fitshdr['CDELT3']   = imdhr['CDELT'][3]
    fitshdr['CDELT4']   = dtsec

    return(0)
#   -----------------------------------------------------------------------------------------------------





def timager (visfile, impre, tmjds, pars=None, ntime=-1):

    #   Make a time series of image cubes 

    casq    = casatools.quanta()

    dtsec   = np.nanmedian(tmjds[1:,0] - tmjds[:-1,0])
    print(f"\n Time resolution = {dtsec} seconds\n")

    mjdlims = np.array([ (tmjds[:,0] - (dtsec/2.0)) / 86400 , (tmjds[:,0] + (dtsec/2.0)) / 86400 ]).T

    if (ntime >= 3):
        mjdlims = mjdlims[:ntime]

    print(f"\n Imaging {mjdlims.shape[0]} time intervals...\n")

    for ki in range(0,len(mjdlims)):

        os.system("rm -rf tcube_"+str(ki)+"*")

        mjdlim  = mjdlims[ki]
        
        startm  = casq.time(casq.quantity(mjdlim[0], 'd'),form=["ymd"]) 
        stoptm  = casq.time(casq.quantity(mjdlim[1], 'd'),form=["ymd"]) 

        tstring = startm[0]+"~"+stoptm[0]
        print(f"\n\n  Imaging time range {ki} / {len(mjdlims)}: {tstring}\n")

        ct.tclean(
            vis=visfile+".ms", \
            imagename="tcube_"+str(ki), \
            datacolumn="corrected", \
            imsize=pars['TimgSize'], \
            cell=pars['TcellSize'], \
            selectdata=True, \
            field=pars['TargetName'],\
            uvrange=pars['FinUvLim'], \
            timerange=tstring, \
            specmode='cubedata', \
            width=pars['TavgChan'], \
            gridder='widefield', \
            wprojplanes=pars['TwprojPln'], \
            pblimit=-0.1, \
            deconvolver='hogbom', \
            weighting='briggs',\
            robust=pars['TwtRobust'], \
            niter=0
        )
        

    casq.done()

    return(0)
#   -----------------------------------------------------------------------------------------------------






def makefits (tmjds, cubename, ntime=-1):

    #   Combine image time series into a single FITS



    iman    = casatools.image()

    if (ntime >= 3):
        mjdarr  = tmjds[:ntime]
    else:
        mjdarr  = tmjds

    tfcube  = []
    beamtf  = []

    for ki in range(0,len(mjdarr)):
        
        print(f"Reading image {ki}")
        iman.open("tcube_"+str(ki)+".image")

        timecube    = iman.getchunk(dropdeg=True)
        imgchan     = timecube.shape[2]
        #print(timecube.shape)
        tfcube.append(np.transpose(timecube, (2,0,1)))
            
        chbeam  = iman.restoringbeam()
        beamarr = []

        for c in range(0, imgchan):

            cbeam   = chbeam['beams']['*'+str(c)]['*0']
            beamarr.append([cbeam['major']['value'], cbeam['minor']['value'], cbeam['positionangle']['value']])

        beamtf.append(beamarr)

        iman.done()


    iman.open("tcube_0.image")
    imhdr   = iman.fitsheader()
    iman.done()
    
    iman.close()
    
    tfcube  = np.array(tfcube).astype('float32')
    print(f"\n  Cube dimensions = {tfcube.shape} \n")

    #   Image 4d cube
    tfhdu       = fits.PrimaryHDU()
    tfhdu.data  = tfcube    
    makehdr(tfhdu.header, imhdr, tmjds)

    hdulist     = fits.HDUList([tfhdu])

    beamtf      = np.array(beamtf).astype('float32')

    #   Beam image in time-frequency
    beamhdu     = fits.ImageHDU(data=np.transpose(beamtf, (2,1,0)))
    beamhdu.header['EXTNAME']   = "BEAMS"
    beamhdu.header['CTYPE1']    = ('TIME', 'The time values are in an extension table')
    beamhdu.header['CTYPE2']    = imhdr['CTYPE'][3]
    beamhdu.header['CUNIT2']    = imhdr['CUNIT4']
    beamhdu.header['CRPIX2']    = imhdr['CRPIX'][3]
    beamhdu.header['CRVAL2']    = imhdr['CRVAL'][3]
    beamhdu.header['CDELT2']    = imhdr['CDELT'][3]
    beamhdu.header['CTYPE3']    = ('BEAM', 'arcsec, arcsec, deg')

    hdulist.append(beamhdu)

    #   Time table
    tcol    = fits.Column(name='MJDSEC', format='D', unit='MJDSEC', array=mjdarr[:,0])
    coldefs = fits.ColDefs([tcol])
    tabhdu  = fits.BinTableHDU.from_columns(coldefs)
    tabhdu.header['EXTNAME']   = "TIME"
    tabhdu.header['TIMESYS']  = imhdr['TIMESYS']

    hdulist.append(tabhdu)
    
    hdulist.writeto(cubename+".fits", overwrite=True)

    print("\n    Clearing images...\n")
    for ki in range(0,len(mjdarr)):
        os.system("rm -rf tcube_"+str(ki)+"*")


    return(0)
#   -----------------------------------------------------------------------------------------------------
