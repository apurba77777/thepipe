import os,sys
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord





def getdynspec (fitsfile, pars=None):

    #   Make dynamic spectrum at a specific position

    hdulist     = fits.open(fitsfile+".fits")
    imwcs       = WCS(hdulist[0].header, naxis=2)

    skyframe    = hdulist[0].header['RADESYS']
    if (skyframe=='FK5'):
        skyframe= 'fk5'

    skypos      = SkyCoord(str(pars['SrcRA'])+"d "+str(pars['SrcDec'])+"d", frame=skyframe)

    px,py       = imwcs.world_to_pixel(skypos)
    px          = np.rint(px).astype(int)
    py          = np.rint(py).astype(int)
    print(f"\n    Source at {px},{py} pixel \n")

    tfdata      = hdulist[0].data[:,:,px,py]
    mjdtime     = hdulist[2].data['MJDSEC'] / 3600

    plt.imshow(tfdata.T, origin='lower', interpolation='none', aspect='auto', cmap='plasma')
    plt.show()

    plt.plot(mjdtime, np.nanmean(tfdata, axis=1))
    plt.show()

    plt.imshow(np.nanmean(hdulist[0].data[400:420], axis=(0,1)), origin='lower', interpolation='none', aspect='auto', cmap='plasma')
    plt.show()

    plt.imshow(np.nanmean(hdulist[0].data[471:490], axis=(0,1)), origin='lower', interpolation='none', aspect='auto', cmap='plasma')
    plt.show()

    plt.imshow(np.nanmean(hdulist[0].data[590:610], axis=(0,1)), origin='lower', interpolation='none', aspect='auto', cmap='plasma')
    plt.show()
    


    hdulist.close()

    return(0)
#   -----------------------------------------------------------------------------------------------------




