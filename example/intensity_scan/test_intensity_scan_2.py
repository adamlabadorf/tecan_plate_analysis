#!python

import os
import sys

import numpy

from subprocess import call

from matplotlib.pyplot import *

from reStUtil import *
from tecan_reader import parse

if __name__ == '__main__' :

    fn = 'All_FPs_intensity_scans.xlsx'
    p = parse(fn)

    print "found sheets: %s"%(', '.join(p.runs.keys()))

    blank_plate1 = ('D1','E1')
    blank_plate2 = ('A2','B2')
    wt_plate1 = ('D2','E2')
    wt_plate2 = ('A3','B3')

    sn_ratios = {'RFP': (('D3','E3'),wt_plate1),
                 'mCherry': (('A6','B6'),wt_plate2),
                 'mOrange': (('D5','E5'),wt_plate1),
                 'YFP': (('D7','E7'),wt_plate1),
                 'Venus': (('D9','E9'),wt_plate1),
                 'EYFP': (('A8','B8'),wt_plate2),
                 'CFP': (('D11','E11'),wt_plate1),
                 'ECFP': (('A12','B12'),wt_plate2),
                 'GFPm3': (('A4','B4'),wt_plate2),
                 'YGFP': (('A10','B10'),wt_plate2),
                }

    for name, (expt, cntl) in sn_ratios.items() :

        # now do the Fluorescence Scan worksheet
        fl_sheet = p.runs.get(name)

        if fl_sheet is None :
            print "Couldn't find sheet named %s, skipping"%name
            continue

        print "Analyzing S/N ratios for",name
        #print "Labels found:"," ,".join(fl_sheet['labels'])

        fl_scans = zip(fl_sheet['labels'],fl_sheet['scans'])

        # OD was the first thing
        od_scan = fl_sheet['plates'][0]

        sn_ratios = []
        for label, scans in fl_scans :
            if label == 'OD' :
                continue
            sn_ratio_row = []
            expt_avgs = []
            cntl_avgs = []
            for scan in scans :
                normed_scan = scan/od_scan

                # add a little noise to avoid numerical errors
                expt_avg = normed_scan.get(*expt).mean()+1e-5
                cntl_avg = normed_scan.get(*cntl).mean()+1e-5

                sn_ratio_row.append(numpy.log2(expt_avg/cntl_avg))

            sn_ratios.append(sn_ratio_row)
        
        wavelens = ['%d'%s.metadata.get('Emission Wavelength') for s in fl_sheet['scans'][0]]

        pcolor(numpy.array(sn_ratios))
        xticks(numpy.arange(len(fl_sheet['labels'][1:]))+0.5,wavelens)
        yticks(numpy.arange(len(fl_sheet['labels'][1:]))+0.5,fl_sheet['labels'][1:])
        axis('tight')
        colorbar()
        title(name+' Emission Scan S/N')
        plot_fn = os.path.splitext(fn)[0]+'_%s_sn_ratios.png'%name
        savefig(plot_fn)
        clf()


    # who loves copy and paste programming?!
    fold_change = {'RFP': (('D3','E3'),('D4','E4')),
                 'mCherry': (('A6','B6'),('A7','B7')),
                 'mOrange': (('D5','E5'),('D6','E6')),
                 'YFP': (('D7','E7'),('D8','E8')),
                 'Venus': (('D9','E9'),('D10','E10')),
                 'EYFP': (('A8','B8'),('A9','B9')),
                 'CFP': (('D11','E11'),('D12','E12')),
                 'ECFP': (('A12','B12'),('C1','D1')),
                 'GFPm3': (('A4','B4'),('A5','B5')),
                 'YGFP': (('A10','B10'),('A11','B11')),
                }

    for name, (expt, cntl) in fold_change.items() :

        # now do the Fluorescence Scan worksheet
        fl_sheet = p.runs.get(name)

        if fl_sheet is None :
            print "Couldn't find sheet named %s, skipping"%name
            continue

        print "Analyzing fold change for",name
        #print "Labels found:",", ".join(fl_sheet['labels'])

        fl_scans = zip(fl_sheet['labels'],fl_sheet['scans'])

        # OD was the first thing
        od_scan = fl_sheet['plates'][0]

        sn_ratios = []
        for label, scans in fl_scans :
            if label == 'OD' :
                continue
            sn_ratio_row = []
            expt_avgs = []
            cntl_avgs = []
            for scan in scans :
                normed_scan = scan/od_scan

                # add a little noise to avoid numerical errors
                expt_avg = normed_scan.get(*expt).mean()+1e-5
                cntl_avg = normed_scan.get(*cntl).mean()+1e-5

                sn_ratio_row.append(numpy.log2(expt_avg/cntl_avg))

            sn_ratios.append(sn_ratio_row)

        wavelens = ['%d'%s.metadata.get('Emission Wavelength') for s in fl_sheet['scans'][0]]

        pcolor(numpy.array(sn_ratios))
        xticks(numpy.arange(len(fl_sheet['labels'][1:]))+0.5,wavelens)
        yticks(numpy.arange(len(fl_sheet['labels'][1:]))+0.5,fl_sheet['labels'][1:])
        axis('tight')
        colorbar()
        title(name+' Induced/Uninduced Fold Change')
        plot_fn = os.path.splitext(fn)[0]+'_%s_fc.png'%name
        savefig(plot_fn)
        clf()
