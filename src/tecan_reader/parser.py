import logging

import numpy
import xlrd

from collections import defaultdict

from base import IntensityRead

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
            logging.info(sheet.name)
            d = self.runs[sheet.name]

            row_i = 0
            curr_label = None
            curr_metadata = {}
            while row_i < sheet.nrows :

                first_val = sheet.cell(row_i,0).value

                if first_val.startswith('Label') :
                    tag, curr_label = first_val.split(':')
                    curr_label = curr_label.strip()
                    d.setdefault('labels',[]).append(curr_label)
                    # blank the metadata
                    curr_metadata = {}
                elif first_val.startswith('Wavel.') :
                    logging.debug('wavelength scan detected')
                    plate_inds = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]
                    row_i += 1

                    scans = []
                    while sheet.cell_value(row_i,0) != '' :

                        wavelen = sheet.cell_value(row_i,0)
                        logging.debug('processing scan wavelength %s'%wavelen)

                        intensity_row = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]

                        intensities = numpy.zeros(shape=(8,12))
                        empty = numpy.ones_like(intensities,dtype=bool)
                        error = numpy.zeros_like(intensities,dtype=bool)

                        for ind, val in zip(plate_inds,intensity_row) :

                            if ind == '' :
                                continue

                            row, col = ind[0], int(ind[1:])

                            if val == 'OVER' :
                                error[BaseParser.letter_ind_map[row],col-1] = True
                            elif val != '' :
                                empty[BaseParser.letter_ind_map[row],col-1] = False
                                intensities[BaseParser.letter_ind_map[row],col-1] = val

                        this_metadata = curr_metadata.copy()
                        this_metadata['Emission Wavelength'] = wavelen
                        scans.append(IntensityRead('%s: %d'%(curr_label,wavelen),intensities, empty, error, this_metadata))

                        row_i += 1
                    d.setdefault('scans',[]).append(scans)


                elif first_val.startswith('<>') :
                    logging.debug('intensity readings detected')
                    plate_inds = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]
                    row_i += 1

                    intensities = numpy.zeros(shape=(8,12))
                    empty = numpy.ones_like(intensities,dtype=bool)
                    error = numpy.zeros_like(intensities,dtype=bool)

                    while sheet.cell_value(row_i,0) != '' :
                        row = sheet.cell_value(row_i,0)
                        intensity_row = [sheet.cell_value(row_i,i) for i in xrange(1,sheet.ncols)]

                        for plate_ind, val in zip(plate_inds,intensity_row) :
                            if plate_ind == '' :
                                continue
                            if val == 'OVER' :
                                error[BaseParser.letter_ind_map[row],plate_ind-1] = True
                            elif val != '' :
                                empty[BaseParser.letter_ind_map[row],plate_ind-1] = False
                                intensities[BaseParser.letter_ind_map[row],plate_ind-1] = val
                        row_i += 1

                    plate_read = IntensityRead(curr_label,intensities, empty, error, curr_metadata)
                    d.setdefault('plates',[]).append(plate_read)
                elif first_val != '' :
                    row = [sheet.cell_value(row_i,i) for i in xrange(sheet.ncols)]
                    row = [v for v in row if v != '']
                    curr_metadata[row[0]] = row[1:]

                row_i += 1


