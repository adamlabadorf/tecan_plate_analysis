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

    blank = ('D1','E1')
    wt = ('D2','E2')

    expt_sets = {'RFP': (('D3','E3'),('D4','E4')),
                 'YFP': (('D7','E7'),('D8','E8')),
                 'Venus': (('D9','E9'),('D10','E10'))
                }

    sn_ratios = {'RFP': (('D3','E3'),wt),
                 'mOrange': (('D5','E5'),wt),
                 'YFP': (('D7','E7'),wt),
                 'Venus': (('D9','E9'),wt),
                 'CFP': (('D11','E11'),wt)
                }

    for name, (expt, cntl) in sn_ratios.items() :

        # now do the Fluorescence Scan worksheet
        fl_sheet = p.runs.get(name)

        if fl_sheet is None :
            print "Couldn't find sheet named %s, skipping"%name
            continue

        print "Analyzing",name
        print "Labels found:"," ,".join(fl_sheet['labels'])

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
                 'mOrange': (('D5','E5'),('D6','E6')),
                 'YFP': (('D7','E7'),('D8','E8')),
                 'Venus': (('D9','E9'),('D10','E10')),
                 'CFP': (('D11','E11'),('D12','E12'))
                }

    for name, (expt, cntl) in fold_change.items() :

        # now do the Fluorescence Scan worksheet
        fl_sheet = p.runs.get(name)

        if fl_sheet is None :
            print "Couldn't find sheet named %s, skipping"%name
            continue

        print "Analyzing",name
        print "Labels found:"," ,".join(fl_sheet['labels'])

        fl_scans = zip(fl_sheet['labels'],fl_sheet['scans'])

        # OD was the first thing
        od_scan = fl_sheet['plates'][0]

        sn_ratios = []
        for label, scans in fl_scans :
            if label == 'OD' :
                print 'found OD label'
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
