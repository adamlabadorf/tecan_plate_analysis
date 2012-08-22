#!python

import sys

from subprocess import call

from reStUtil import *
from tecan_reader import parse

if __name__ == '__main__' :

    p = parse(sys.argv[1])

    for sheet, d in p.runs.items() :
        print 'Processing',sheet
        sheet_fn = '%s_run.rst'%sheet.replace(' ','_')
        doc = ReStDocument(sheet_fn,title=sheet+' Tecan Reads')
        label_plates = zip(d.get('labels',[]),d.get('plates',[]))
        for label, plate in label_plates :
            print plate
            plot_fn = '%s_%s.png'%(sheet.replace(' ','_'),label.replace(' ','_'))
            plate.plot_plate(''+plot_fn)
            doc.add(ReStImage(plot_fn))
        doc.write()
        doc.close()

        call('rst2pdf %s -o %s'%(sheet_fn,sheet_fn.replace('.rst','.pdf')),shell=True)
