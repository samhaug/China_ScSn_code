#!/home/samhaug/anaconda2/bin/python

'''
==============================================================================

File Name : radon_transform.py
Purpose : apply radon transform to trace.
Creation Date : 19-03-2018
Last Modified : Mon 07 May 2018 09:35:31 AM EDT
Created By : Samuel M. Haugland

==============================================================================
'''

import numpy as np
from matplotlib import pyplot as plt
import h5py
import obspy
import argparse
import Radon
from PIL import Image,ImageDraw

def main():
    parser = argparse.ArgumentParser(description='Radon transform')
    parser.add_argument('-s','--synth', metavar='H5_FILE',type=str,
                        help='h5 stream')
    parser.add_argument('-d','--data', metavar='H5_FILE',type=str,
                        help='h5 stream')
    parser.add_argument('--read', metavar='T/F',type=str,
                        help='read from existing radon datfile',default='False')
    args = parser.parse_args()

    std = obspy.read(args.data)
    sts = obspy.read(args.synth)
    sts,std = even_streams(sts,std)

    std = block_stream(std)
    std.write('st_T_block.h5',format='H5')

    sts = block_stream(sts)
    sts.write('sts_T_block.h5',format='H5')

    if args.read != 'False':
        f = h5py.File(args.read,'r')
        dR = f['data']['R'][:]
        dt = f['data']['t'][:]
        dp = f['data']['p'][:]
        ddelta = f['data']['delta'][:]
        dweights = f['data']['weights'][:]
        dref_dist = np.mean(ddelta)

        sR = f['synth']['R'][:]
        st = f['synth']['t'][:]
        sp = f['synth']['p'][:]
        sdelta = f['synth']['delta'][:]
        sweights = f['synth']['weights'][:]
        sref_dist = np.mean(sdelta)
        f.close()
    else:
        print('synth Radon_inverse')
        st,sdelta,sM,sp,sweights,sref_dist = prepare_input(sts)
        sR = Radon.Radon_inverse(st,sdelta,sM,sp,sweights,
                                 sref_dist,'Linear','L2',[5e2])
        print('data Radon_inverse')
        dt,ddelta,dM,dp,dweights,dref_dist = prepare_input(std)
        dR = Radon.Radon_inverse(dt,ddelta,dM,dp,dweights,
                                 dref_dist,'Linear','L2',[5e2])
    mask = make_mask(sR)

    if args.read == 'False':
        f = h5py.File('Radon.h5','w')
        write_h5(f,dR,dt,dp,ddelta,dweights,
                 sR,st,sp,sdelta,sweights,mask)
        f.close()

    print('synth Radon_forward')
    sd = Radon.Radon_forward(st,sp,sR*mask,sdelta,sref_dist,'Linear')
    print('Radon_forward')
    dd = Radon.Radon_forward(dt,dp,dR*mask,ddelta,dref_dist,'Linear')

    stsc = sts.copy()
    for idx,tr in enumerate(stsc):
        stsc[idx].data = sd[idx]
    stsc.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    stsc.write('sts_T_radon.h5',format='H5')

    stdc = std.copy()
    for idx,tr in enumerate(stdc):
        stdc[idx].data = dd[idx]
    stdc.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    stdc.write('st_T_radon.h5',format='H5')

def even_streams(sta,stb):
    a = []
    b = []
    for tr in sta:
        if tr.stats.station in a:
            sta.remove(tr)
        else:
            a.append(tr.stats.station)
    for tr in stb:
        if tr.stats.station in b:
            stb.remove(tr)
        else:
            b.append(tr.stats.station)
    c = set(a).intersection(set(b))
    for tr in sta:
        if tr.stats.station not in c:
            sta.remove(tr)
    for tr in stb:
        if tr.stats.station not in c:
            stb.remove(tr)
    return sta,stb

def make_mask(R):
    plt.imshow(np.log10(np.abs(R)),aspect='auto')
    ax = plt.gca()
    coord_list = []
    cc = clicker_class(ax)
    plt.show()
    polygon = cc.pt_lst
    img = Image.new('L',(R.shape[1],R.shape[0]),0)
    ImageDraw.Draw(img).polygon(polygon,outline=1,fill=1)
    mask = np.array(img)
    return mask

def write_h5(f,dR,dt,dp,ddelta,dweights,sR,st,sp,sdelta,sweights,mask):
    f.create_group('synth')
    f.create_group('data')
    f.create_dataset('mask',data=mask)
    f['synth'].create_dataset('R',data=sR)
    f['synth'].create_dataset('t',data=st)
    f['synth'].create_dataset('p',data=sp)
    f['synth'].create_dataset('delta',data=sdelta)
    f['synth'].create_dataset('weights',data=sweights)
    f['data'].create_dataset('R',data=dR)
    f['data'].create_dataset('t',data=dt)
    f['data'].create_dataset('p',data=dp)
    f['data'].create_dataset('delta',data=ddelta)
    f['data'].create_dataset('weights',data=dweights)

def prepare_input(st):
    p = np.arange(-10.0,10.1,0.1)
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
    st.interpolate(2)
    st.filter('bandpass',freqmin=1./100,freqmax=1./10,zerophase=True)
    for idx,tr in enumerate(st):
        if tr.stats.o < 0:
            z = np.zeros(int(np.abs(tr.stats.o)*tr.stats.sampling_rate))
            st[idx].data = np.hstack((z,tr.data))
        elif tr.stats.o > 0:
            d = tr.data[int(tr.stats.o*tr.stats.sampling_rate)::]
            st[idx].data = d
        else:
            d = tr.data[int(tr.stats.o*tr.stats.sampling_rate)::]
        st[idx].stats.starttime += st[idx].stats.o
        st[idx].stats.o = 0
        l = tr.stats.endtime-tr.stats.starttime
        if l <= 4000:
            z = np.zeros(int(tr.stats.sampling_rate*(4000-l)))
            st[idx].data = np.hstack((tr.data,z))
        elif l > 4000:
            st[idx].data = tr.data[0:int(4000*tr.stats.sampling_rate)]
        st[idx].data = tr.data[0:int(4000*tr.stats.sampling_rate)]
    return st

class clicker_class(object):
    '''
    This is used to interactively draw a mask around the ScS reverberation
    time/slowness branch
    '''
    def __init__(self, ax, pix_err=1):
        self.canvas = ax.get_figure().canvas
        self.cid = None
        self.pt_lst = []
        self.pt_plot = ax.plot([],[],marker='o',color='r',
                               linestyle='none',zorder=5)[0]
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



