import colorsys

import numpy

import matplotlib
from matplotlib.pyplot import figure


class PlateRead(object) :

    letter_ind_map = dict((c,i) for i,c in enumerate(u'ABCDEFGH'))

    def __init__(self,label,values,empty_mask=None,error_mask=None) :

        self.label = label
        self.values = values

        if empty_mask is None :
            self.empty_mask = numpy.zeros_like(values)
        else :
            self.empty_mask = empty_mask.astype(bool)

        if error_mask is None :
            self.error_mask = numpy.zeros_like(values)
        else :
            self.error_mask = error_mask.astype(bool)

    def __add__(self,other) :
        return self.__op_helper(other,sum)

    def __sub__(self,other) :
        return self.__op_helper(other,lambda x,y: x-y)

    def __div__(self,other) :
        return self.__op_helper(other,lambda x,y: x/y)

    def __mul__(self,other) :
        return self.__op_helper(other,lambda x,y: x*y)

    def __op_helper(self,other,op) :

        #TODO need to change these ops so they only operate on
        # masked values?

        new_values = None
        new_empty_mask = None
        new_error_mask = None

        if isinstance(other,int) or isinstance(other,float) :
            new_values = op(self.values,other)
            new_empty_mask = self.empty_mask.copy()
            new_error_mask = self.error_mask.copy()
        elif isinstance(other,PlateRead) :
            new_values = op(self.values,other.values)
            new_empty_mask = self.empty_mask & other.empty_mask
            new_error_mask = self.error_mask & other.error_mask

        return PlateRead('',new_values,new_empty_mask,new_error_mask)

    def __str__(self) :
        return '%s(%s)'%(self.__class__.__name__,self.label)

    def __repr__(self) :
        return '%s("%s",%s,%s,%s)'%(self.__class__.__name__,
                                    self.label,
                                    repr(self.values),
                                    repr(self.empty_mask),
                                    repr(self.error_mask)
                                   )

    def get(self,item,*addnl) :
        # translate letter-column codes into real indices
        real_coords = []
        for coord in [item]+list(addnl) :
            try :
                row, col = coord[0], int(coord[1:])
            except TypeError :
                print 'could not interpret coordinate %s, skipping'%coord
                continue
            row_i = 'ABCDEFGH'.index(row.upper())
            col_i = col-1
            real_coords.append((row_i,col_i))

        x,y = zip(*real_coords)
        return self.values[x,y]

    def __getitem__(self,item,*addnl) :
        return self.get(item,*addnl)

class IntensityRead(PlateRead) :

    def __init__(self,*args,**kwargs) :
        PlateRead.__init__(self,*args, **kwargs)

    def plot_plate(self,fn) :

        f = figure()
        ax = f.gca()

        x,y = range(12),range(8)[::-1]
        xy = numpy.transpose([numpy.tile(x,len(y)),numpy.repeat(y,len(x))])

        # no reading
        xy_noread = xy[self.empty_mask.ravel()]
        ax.scatter(xy_noread[:,0],xy_noread[:,1],marker='x')

        # over reading
        xy_over = xy[self.error_mask.ravel()]
        ax.scatter(xy_over[:,0],xy_over[:,1],s=240,c='r',marker='s')

        # intensities
        # sometimes there are no intensity values
        vals = self.values.ravel()
        if (vals[~self.empty_mask.ravel() & ~self.error_mask.ravel()] >= 0).sum() > 0 :
            xy_int = xy[ ~self.empty_mask.ravel() & ~self.error_mask.ravel() ]
            int_vals = vals[ ~self.empty_mask.ravel() & ~self.error_mask.ravel() ]

            cm = matplotlib.cm.get_cmap('Reds')
            #ax.scatter(xy_int[:,0],xy_int[:,1],c=val_colors,s=320,linewidths=1)
            sc = ax.scatter(xy_int[:,0],xy_int[:,1],c=int_vals,s=320,marker='o',cmap=cm,vmin=None)

            try :
                f.colorbar(sc)
            except Exception, e:
                print 'colorbar died for some reason:',e

        ax.set_title(fn)
        #ax.set_frame_on(False)

        ax.set_xlim(-1,12)
        ax.set_ylim(-1,8)

        ax.set_xticks(xrange(12))
        ax.set_xticklabels(xrange(1,13))

        ax.set_yticklabels('ABCDEFGH '[::-1])

        f.savefig(fn)
