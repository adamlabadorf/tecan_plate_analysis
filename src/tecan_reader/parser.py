import colorsys

import numpy
import xlrd

from collections import defaultdict

from matplotlib.pyplot import figure

def parse(fn) :
    p = BaseParser(fn)
    p.parse()
    return p

class BaseParser :

    letter_ind_map = dict((c,i) for i,c in enumerate(u'ABCDEFGH'))

    def __init__(self,fn) :
        self.book = xlrd.open_workbook(fn)

        self.runs = defaultdict(dict)

    def parse(self) :

        # TODO: read all the stuff at the top of the spreadsheet

        for sheet in self.book.sheets() :
            print sheet.name
            d = self.runs[sheet.name]

            row_i = 0
            curr_label = None
            while row_i < sheet.nrows :

                try :
                    first_val = sheet.cell(row_i,0).value
                except :
                    print sheet.name, row_i, sheet.nrows, sheet.ncols
                    break

                if first_val.startswith('Label') :
                    tag, curr_label = first_val.split(':')
                    curr_label = curr_label.strip()
                elif first_val.startswith('Wavel.') :
                    print 'wavelength scan detected'
                    header_row = [sheet.cell(row_i,i) for i in xrange(sheet.ncols)]
                    row_i += 1
                    scan_rows = []
                    while sheet.cell_value(row_i,0) != '' :
                        scan_row = [sheet.cell(row_i,i) for i in xrange(sheet.ncols)]
                        scan_rows.append(scan_row)
                        row_i += 1
                    d.setdefault('scans',[]).append(scan_rows)
                elif first_val.startswith('<>') :
                    print 'intensity readings detected'
                    plate_inds = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]
                    row_i += 1
                    intensity_rows = []
                    intensities = numpy.zeros(shape=(8,12))-2 # -2 means data not set
                    while sheet.cell_value(row_i,0) != '' :
                        row = sheet.cell_value(row_i,0)
                        intensity_row = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]
                        for plate_ind, val in zip(plate_inds,intensity_row) :
                            if val == 'OVER' :
                                val = -1 # -1 means machine could not read intensity
                            if val != '' :
                                intensities[BaseParser.letter_ind_map[row],plate_ind-1] = val
                        row_i += 1
                    d.setdefault('intensities',[]).append(intensity_rows)
                    plot_fn = '%s_%s.png'%(sheet.name.replace(' ','_'),curr_label.replace(' ','_'))
                    plot_plate(intensities,plot_fn)

                row_i += 1

def plot_plate(intensities,fn) :

    f = figure()
    ax = f.gca()

    x,y = range(12),range(7,-1,-1)
    xy = numpy.transpose([numpy.tile(x,len(y)),numpy.repeat(y,len(x))])
    vals = intensities.ravel()
    
    # no reading
    xy_noread = xy[vals==-2]
    ax.scatter(xy_noread[:,0],xy_noread[:,1],marker='x')

    # over reading
    xy_over = xy[vals==-1]
    ax.scatter(xy_over[:,0],xy_over[:,0],c='r',marker='s')

    # intensities
    xy_int = xy[vals>=0]
    int_vals = vals[vals>=0]
    scaled_vals = (int_vals-int_vals.min())/(int_vals.max()-int_vals.min())

    # hsv
    val_colors = [colorsys.hsv_to_rgb(0.25,i,1.) for i in scaled_vals]

    ax.scatter(xy_int[:,0],xy_int[:,1],c=val_colors,s=240,linewidths=1)

    ax.set_title(fn)
    ax.set_frame_on(False)

    ax.set_xticklabels(xrange(1,13))

    ax.set_yticklabels('ABCDEFGH '[::-1])

    ax.set_xlim(0,11)
    ax.set_ylim(0,11)

    f.savefig(fn)
