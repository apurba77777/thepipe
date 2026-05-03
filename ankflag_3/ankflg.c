#	include <stdio.h>
#	include <stdlib.h>	
#	include	<ankhead.h>
#	include <math.h>
#	include <string.h>


//	-----------------------------------------------------------------------------------

int main (int argc, char* argv[])
{
	int				i,j,k;
	
	int				ants, flagmode, done;
	char			statusfile[100],binfiles[100],flagparfile[100],scanfile[100],badbasename[100];
	int				nbase	=	0;
	
	sprintf(flagparfile,"%s/flagpars.pars",argv[1]);
	sprintf(badbasename,"%s/badbase.list",argv[1]);
	sprintf(scanfile,"%s/scandetails.txt",argv[1]);
	
	FILE		*fp,*badbasefile;
	fp		=	fopen(flagparfile,"r");
	badbasefile	=	fopen(badbasename,"w");
	
	fscanf (fp,"%d	%d",&ants,&flagmode);
	
	fclose(fp);
	
	if (flagmode) {
		sprintf(statusfile,"%s/uvbin_status.txt",argv[1]);
		sprintf(binfiles,"%s/uvbin",argv[1]);	
	}
	else {
		sprintf(statusfile,"%s/baseline_status.txt",argv[1]);
		sprintf(binfiles,"%s/baseline",argv[1]);
	}
	
	printf("\nFlagmode	= %d	Antennas	= %d\n\n",flagmode,ants);
	
	done	=	processbaselines (ants, statusfile, &nbase, binfiles, flagparfile, badbasefile, scanfile);	
	
	printf("Total baselines / uvbins		%d\n",nbase);
		
	fclose (badbasefile);
	
	return 0;
}

























