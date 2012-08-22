#!python

import sys

import numpy

from subprocess import call

from matplotlib.pyplot import *

from reStUtil import *
from tecan_reader import parse

if __name__ == '__main__' :

    p = parse('20120821_4hr.xlsx')

    # these are the experiment and control wells for this specific run
    expt = ('A9','B9')
    cntl = ('A10','B10')

    # first get the average OD
    od_sheet = p.runs['OD Scan']
    od_scans = dict(zip(od_sheet['labels'],od_sheet['scans']))

    # we're gonna just pick 586, which I know to be index 3
    od_scan = od_scans['OD Scan'][3]
    print od_scan

    # now do the Fluorescence Scan worksheet
    fl_sheet = p.runs['Fluorescence Scan']
    fl_scans = zip(fl_sheet['labels'],fl_sheet['scans'])
    sn_ratios = []
    for label, scans in fl_scans :
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

    pcolor(numpy.array(sn_ratios))
    xticks(numpy.arange(12)+0.5,numpy.arange(600,622,2))
    yticks(numpy.arange(len(fl_sheet['labels']))+0.5,fl_sheet['labels'])
    axis('tight')
    colorbar()
    savefig('sn_ratios.png')
