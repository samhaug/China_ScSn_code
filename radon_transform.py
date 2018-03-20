#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : radon_transform.py
Purpose : apply radon transform to trace.
Creation Date : 19-03-2018
Last Modified : Tue 20 Mar 2018 01:52:56 PM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import h5py
import obspy
import argparse
import seispy
import Radon

def main():
    parser = argparse.ArgumentParser(description='Radon transform')
    parser.add_argument('-f','--stream', metavar='H5_FILE',type=str,
                        help='h5 stream')
    parser.add_argument('--save', metavar='bool',type=str,
                        help='save vespagram',default=False)
    parser.add_argument('--read', metavar='bool',type=str,
                        help='read vespagram',default=False)
    args = parser.parse_args()
    st = obspy.read(args.stream)
    st = block_stream(st)
    t,delta,M,p,weights,ref_dist = prepare_input(st)

    if args.read != False:
        R = np.genfromtxt(args.read)
    else:
        R = Radon.Radon_inverse(t,delta,M,p,weights,
                                ref_dist,'Linear','L2',[5e2])
    if args.save == True:
        np.savetxt('Radon.dat',R)

    plt.imshow(np.log10(np.abs(R)),aspect='auto')
    ax = plt.gca()
    cc = clicker_class(ax)
    plt.show()

    d = Radon.Radon_forward(t,p,R,delta,ref_dist,'Linear')
    stc = st.copy()
    for idx,tr in enumerate(stc):
        stc[idx].data = d[idx]
    #seispy.plot.simple_h5_section(stc)
    stc.write('st_T_radon.h5',format='H5')

def prepare_input(st):
    p = np.arange(-8.0,8.1,0.1)
    delta = []
    M = []
    for tr in st:
        delta.append(tr.stats.gcarc)
        M.append(tr.data)
    M = np.array(M)
    delta = np.array(delta)
    weights = np.ones(len(delta))
    ref_dist = np.mean(delta)
    t = np.linspace(0,4000,num=st[0].stats.npts)
    return t,delta,M,p,weights,ref_dist

def block_stream(st):
    for idx,tr in enumerate(st):
        if tr.stats.o <= 0:
            z = np.zeros(int(np.abs(tr.stats.o)*10))
            st[idx].data = np.hstack((z,tr.data))
        elif tr.stats.o > 0:
            d = tr.data[int(tr.stats.o*10)::]
            st[idx].data = d
        st[idx].stats.starttime += st[idx].stats.o
        l = tr.stats.endtime-tr.stats.starttime
        if l <= 4000:
            z = np.zeros(int(10*(4000-l)))
            st[idx].data = np.hstack((tr.data,z))
        elif l > 4000:
            st[idx].data = tr.data[0:40000]
        st[idx].data = tr.data[0:40000]
    return st

class clicker_class(object):
    def __init__(self, ax, pix_err=1):
        self.canvas = ax.get_figure().canvas
        self.cid = None
        self.pt_lst = []
        self.pt_plot = ax.plot([], [], marker='o',
                               linestyle='none', zorder=5)[0]
        self.pix_err = pix_err
        self.connect_sf()

    def set_visible(self, visible):
        '''sets if the curves are visible '''
        self.pt_plot.set_visible(visible)

    def clear(self):
        '''Clears the points'''
        self.pt_lst = []
        self.redraw()

    def connect_sf(self):
        if self.cid is None:
            self.cid = self.canvas.mpl_connect('button_press_event',
                                               self.click_event)

    def disconnect_sf(self):
        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
            self.cid = None

    def click_event(self, event):
        ''' Extracts locations from the user'''
        if event.key == 'shift':
            self.pt_lst = []
            return
        if event.xdata is None or event.ydata is None:
            return
        if event.button == 1:
            self.pt_lst.append((event.xdata, event.ydata))
        elif event.button == 3:
            self.remove_pt((event.xdata, event.ydata))

        self.redraw()

    def remove_pt(self, loc):
        if len(self.pt_lst) > 0:
            self.pt_lst.pop(np.argmin(map(lambda x:
                                          np.sqrt((x[0] - loc[0]) ** 2 +
                                                  (x[1] - loc[1]) ** 2),
                                          self.pt_lst)))

    def redraw(self):
        if len(self.pt_lst) > 0:
            x, y = zip(*self.pt_lst)
        else:
            x, y = [], []
        self.pt_plot.set_xdata(x)
        self.pt_plot.set_ydata(y)

        self.canvas.draw()

    def return_points(self):
        '''Returns the clicked points in the format the rest of the
        code expects'''
        return np.vstack(self.pt_lst).T


main()






