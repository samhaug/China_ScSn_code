import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def rad_to_pressure(radius,rho):
   '''
   takes two axes (radius and density), and finds pressure at each point in radius

   args:
        radius: numpy array. given in assending order. units:km
        rho: density values corresponding to radius. units: g/cm^3

   returns: pressures (Pa)
   '''
   debug=False

   r = radius*1000.0
   dr = np.diff(r)
   rho *= 1000.0
   g = np.zeros(len(r))
   mass = np.zeros(len(r))
   p_layer = np.zeros(len(r))
   p = np.zeros(len(r))
   G = 6.67408e-11

   for i in range(1,len(r)):
       mass[i] = 4.0*np.pi*r[i]**2*rho[i]*dr[i-1] #mass of layer
   for i in range(1,len(r)):
       g[i] = G*np.sum(mass[0:i])/(r[i]**2)
   for i in range(1,len(r)):
       p_layer[i] = rho[i]*g[i]*dr[i-1]
   for i in range(0,len(r)):
       p[i] = np.sum(p_layer[::-1][0:len(r)-i])

   if debug:
      for i in range(0,len(r)):
          print 'r(km),rho,g,p',r[i]/1000.0,rho[i],g[i],p[i]

   p[0] = 0.0

   return p

class seismodel_1d(object):
   '''
   class for dealing with various 1d seismic models
   '''
   def init():
      self.r   = np.zeros(1)
      self.vp  = np.zeros(1)
      self.vs  = np.zeros(1)
      self.rho = np.zeros(1)

   def get_vp(self,depth):
       r_here = 6371.0 - depth
       interp_vp = interp1d(self.r,self.vp)
       vp_here = interp_vp(r_here)
       return vp_here

   def get_vs(self,depth):
       r_here = 6371.0 - depth
       interp_vs = interp1d(self.r,self.vs)
       vs_here = interp_vs(r_here)
       return vs_here

   def get_rho(self,depth):
       r_here = 6371.0 - depth
       interp_rho = interp1d(self.r,self.rho)
       rho_here = interp_rho(r_here)
       return rho_here

   def get_p(self,depth):
       r_here = 6371.0 - depth
       interp_p = interp1d(self.r,self.p)
       p_here = interp_p(r_here)
       return p_here

   def plot(self,var='all'):
       if var == 'all':
           plt.plot(self.vp,self.r,label='Vp')
           plt.plot(self.vs,self.r,label='Vs')
           plt.plot(self.rho/1000.0,self.r,label='rho')
       elif var == 'vp':
           plt.plot(self.vp,self.r,label='Vp')
       elif var == 'vs':
           plt.plot(self.vs,self.r,label='Vs')
       elif var == 'rho':
           plt.plot(self.rho/1000.0,self.r,label='rho')
       else:
           raise ValueError('Please select var = "all","vp","vs",or "rho"')

       plt.xlabel('velocity (km/s), density (g/cm$^3$)')
       plt.ylabel('radius (km)')
       plt.legend()
       plt.show()

# model ak135--------------------------------------------------------------------

def ak135():
   ak135 = seismodel_1d()
   ak135.r=[ 6371.0, 6351.0, 6351.0, 6336.0, 6336.0,
             6293.5, 6251.0, 6251.0, 6206.0, 6161.0,
             6161.0, 6111.0, 6061.0, 6011.0, 5961.0,
             5961.0, 5911.0, 5861.0, 5811.0, 5761.0,
             5711.0, 5711.0, 5661.0, 5611.0, 5561.5,
             5512.0, 5462.5, 5413.0, 5363.5, 5314.0,
             5264.5, 5215.0, 5165.5, 5116.0, 5066.5,
             5017.0, 4967.5, 4918.0, 4868.5, 4819.0,
             4769.5, 4720.0, 4670.5, 4621.0, 4571.5,
             4522.0, 4472.5, 4423.0, 4373.5, 4324.0,
             4274.5, 4225.0, 4175.5, 4126.0, 4076.5,
             4027.0, 3977.5, 3928.0, 3878.5, 3829.0,
             3779.5, 3731.0, 3681.0, 3631.0, 3631.0,
             3581.3, 3531.7, 3479.5, 3479.5, 3431.6,
             3381.3, 3331.0, 3280.6, 3230.3, 3180.0,
             3129.7, 3079.4, 3029.0, 2978.7, 2928.4,
             2878.3, 2827.7, 2777.4, 2727.0, 2676.7,
             2626.4, 2576.0, 2525.7, 2475.4, 2425.0,
             2374.7, 2324.4, 2274.1, 2223.7, 2173.4,
             2123.1, 2072.7, 2022.4, 1972.1, 1921.7,
             1871.4, 1821.1, 1770.7, 1720.4, 1670.1,
             1619.8, 1569.4, 1519.1, 1468.8, 1418.4,
             1368.1, 1317.8, 1267.4, 1217.5, 1217.5,
             1166.4, 1115.7, 1064.9, 1014.3,  963.5,
             912.83, 862.11, 811.40, 760.69, 709.98,
             659.26, 608.55, 557.84, 507.13, 456.41,
             405.70, 354.99, 304.28, 253.56, 202.85,
             152.14, 101.43,  50.71, 0.0 ]

   ak135.vp= [5.800000, 5.800000, 6.500000, 6.500000, 8.040000,
             8.045000, 8.050000, 8.050000, 8.175000, 8.300700,
             8.300700, 8.482200, 8.665000, 8.847600, 9.030200,
             9.360100, 9.528000, 9.696200, 9.864000, 10.032000,
             10.200000, 10.790900, 10.922200, 11.055300, 11.135500,
             11.222800, 11.306800, 11.389700, 11.470400, 11.549300,
             11.626500, 11.702000, 11.776800, 11.849100, 11.920800,
             11.989100, 12.057100, 12.124700, 12.191200, 12.255800,
             12.318100, 12.381300, 12.442700, 12.503000, 12.563800,
             12.622600, 12.680700, 12.738400, 12.795600, 12.852400,
             12.909300, 12.966300, 13.022600, 13.078600, 13.133700,
             13.189500, 13.246500, 13.301700, 13.358400, 13.415600,
             13.474100, 13.531100, 13.589900, 13.649800, 13.649800,
             13.653300, 13.657000, 13.660100, 8.000000, 8.038200,
             8.128300, 8.221300, 8.312200, 8.400100, 8.486100,
             8.569200, 8.649600, 8.728300, 8.803600, 8.876100,
             8.946100, 9.013800, 9.079200, 9.142600, 9.204200,
             9.263400, 9.320500, 9.376000, 9.429700, 9.481400,
             9.530600, 9.577700, 9.623200, 9.667300, 9.710000,
             9.751300, 9.791400, 9.830400, 9.868200, 9.905100,
             9.941000, 9.976100, 10.010300, 10.043900, 10.076800,
             10.109500, 10.141500, 10.173900, 10.204900, 10.232900,
             10.256500, 10.274500, 10.285400, 10.289000, 11.042700,
             11.058500, 11.071800, 11.085000, 11.098300, 11.116600,
             11.131600, 11.145700, 11.159000, 11.171500, 11.183200,
             11.194100, 11.204100, 11.213400, 11.221900, 11.229500,
             11.236400, 11.242400, 11.247700, 11.252100, 11.255700,
             11.258600, 11.260600, 11.261800, 11.262200]
      
   ak135.vs=[3.460000, 3.460000, 3.850000, 3.850000, 4.480000,
             4.490000, 4.500000, 4.500000, 4.509000, 4.518400,
             4.518400, 4.609400, 4.696400, 4.783200, 4.870200,
             5.080600, 5.186400, 5.292200, 5.398900, 5.504700,
             5.610400, 5.960700, 6.089800, 6.210000, 6.242400,
             6.279900, 6.316400, 6.351900, 6.386000, 6.418200,
             6.451400, 6.482200, 6.513100, 6.543100, 6.572800,
             6.600900, 6.628500, 6.655400, 6.681300, 6.707000,
             6.732300, 6.757900, 6.782000, 6.805600, 6.828900,
             6.851700, 6.874300, 6.897200, 6.919400, 6.941600,
             6.962500, 6.985200, 7.006900, 7.028600, 7.050400,
             7.072200, 7.093200, 7.114400, 7.136800, 7.158400,
             7.180400, 7.203100, 7.225300, 7.248500, 7.248500,
             7.259300, 7.270000, 7.281700, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 0.000000,
             0.000000, 0.000000, 0.000000, 0.000000, 3.504300,
             3.518700, 3.531400, 3.543500, 3.555100, 3.566100,
             3.576500, 3.586400, 3.595700, 3.604400, 3.612600,
             3.620200, 3.627200, 3.633700, 3.639600, 3.645000,
             3.649800, 3.654000, 3.657700, 3.660800, 3.663300,
             3.665300, 3.666700, 3.667500, 3.667800]
   
   ak135.rho=[2.720000, 2.720000, 2.920000, 2.920000, 3.320000,
             3.345000, 3.371000, 3.371100, 3.371100, 3.324300,
             3.324300, 3.366300, 3.411000, 3.457700, 3.506800,
             3.931700, 3.927300, 3.923300, 3.921800, 3.920600,
             3.920100, 4.238700, 4.298600, 4.356500, 4.411800,
             4.465000, 4.516200, 4.565400, 4.592600, 4.619800,
             4.646700, 4.673500, 4.700100, 4.726600, 4.752800,
             4.779000, 4.805000, 4.830700, 4.856200, 4.881700,
             4.906900, 4.932100, 4.957000, 4.981700, 5.006200,
             5.030600, 5.054800, 5.078900, 5.102700, 5.126400,
             5.149900, 5.173200, 5.196300, 5.219200, 5.242000,
             5.264600, 5.287000, 5.309200, 5.331300, 5.353100,
             5.374800, 5.396200, 5.417600, 5.438700, 5.693400,
             5.719600, 5.745800, 5.772100, 9.914500, 9.994200,
             10.072200, 10.148500, 10.223300, 10.296400, 10.367900,
             10.437800, 10.506200, 10.573100, 10.638500, 10.702300,
             10.764700, 10.825700, 10.885200, 10.943400, 11.000100,
             11.055500, 11.109500, 11.162300, 11.213700, 11.263900,
             11.312700, 11.360400, 11.406900, 11.452100, 11.496200,
             11.539100, 11.580900, 11.621600, 11.661200, 11.699800,
             11.737300, 11.773700, 11.809200, 11.843700, 11.877200,
             11.909800, 11.941400, 11.972200, 12.000100, 12.031100,
             12.059300, 12.086700, 12.113300, 12.139100, 12.703700,
             12.728900, 12.753000, 12.776000, 12.798000, 12.818800,
             12.838700, 12.857400, 12.875100, 12.891700, 12.907200,
             12.921700, 12.935100, 12.947400, 12.958600, 12.968800,
             12.977900, 12.985900, 12.992900, 12.998800, 13.003600,
             13.007400, 13.010000, 13.011700, 13.012200]

   return ak135

def prem():
   '''
   prem_iso model
   adapted from C code written by Andreas Fichtner in SES3D
   '''
   prem = seismodel_1d()
   prem.r = np.arange(0,6372,1)
   prem.vp = np.zeros((len(prem.r)))
   prem.vs = np.zeros((len(prem.r)))
   prem.rho = np.zeros((len(prem.r)))
   
   #crust:
   for i in range(0,len(prem.r)):
      r = prem.r[i]/6371.0
      r2 = r**2
      r3 = r**3

      if prem.r[i] <= 6371.0 and prem.r[i] >= 6356.0:    #0 - 15 km
         prem.rho[i] = 2.6
         prem.vp[i] = 5.8
         prem.vs[i] = 3.2
      elif prem.r[i] <= 6356.0 and prem.r[i] >= 6346.6:  #15 - 24.4 km
         prem.rho[i] = 2.9
         prem.vp[i] = 6.8
         prem.vs[i] = 3.9
      elif prem.r[i] <= 6346.6 and prem.r[i] >= 6291.0:  #24.4 - 80 km
         prem.rho[i] = 2.6910 + 0.6924*r
         prem.vp[i] = 4.1875 + 3.9382*r
         prem.vs[i] = 2.1519 + 2.3481*r
      elif prem.r[i] <= 6291.0 and prem.r[i] >= 6151.0:  #80 - 220 km
         prem.rho[i] = 2.6910 + 0.6924*r
         prem.vp[i] = 4.1875 + 3.9382*r
         prem.vs[i] = 2.1519 + 2.3481*r
      elif prem.r[i] <= 6151.0 and prem.r[i] >= 5971.0:  #220 - 400 km
         prem.rho[i] = 7.1089 - 3.8045*r
         prem.vp[i] = 20.3926 - 12.2569*r
         prem.vs[i] = 8.9496 - 4.4597*r
      elif prem.r[i] <= 5971.0 and prem.r[i] >= 5771.0:  #400 - 600 km
         prem.rho[i] = 11.2494 - 8.0298*r
         prem.vp[i] = 39.7027 - 32.6166*r
         prem.vs[i] = 22.3512 - 18.5856*r
      elif prem.r[i] <= 5771.0 and prem.r[i] >= 5701.0:  #600 - 670 km
         prem.rho[i] = 5.3197 - 1.4836*r 
         prem.vp[i] = 19.0957 - 9.8672*r
         prem.vs[i] = 9.9839 - 4.9324*r
      elif prem.r[i] <= 5701.0 and prem.r[i] >= 5600.0:  #670 - 771 km
         prem.rho[i] = 7.9565 - 6.4761*r + 5.5283*r2 - 3.0807*r3
         prem.vp[i] = 29.2766 - 23.6026*r + 5.5242*r2 - 2.5514*r3
         prem.vs[i] = 22.3459 - 17.2473*r - 2.0834*r2 + 0.9783*r3
      elif prem.r[i] <= 5600.0 and prem.r[i] >= 3630.0:  #771 - 2741 km
         prem.rho[i] = 7.9565 - 6.4761*r + 5.5283*r2 - 3.0807*r3
         prem.vp[i] = 24.9520 - 40.4673*r + 51.4832*r2 - 26.6419*r3
         prem.vs[i] = 11.1671 - 13.7818*r + 17.4575*r2 - 9.2777*r3
      elif prem.r[i] <= 3630.0 and prem.r[i] >= 3480.0:  #2741 - 2756 km
         prem.rho[i] = 7.9565 - 6.4761*r + 5.5283*r2 - 3.0807*r3
         prem.vp[i] = 15.3891 - 5.3181*r + 5.5242*r2 - 2.5514*r3
         prem.vs[i] = 6.9254 + 1.4672*r - 2.0834*r2 + 0.9783*r3
      elif prem.r[i] <= 3480.0 and prem.r[i] >= 1221.5:  #outer core
         prem.rho[i] = 12.5815 - 1.2638*r - 3.6426*r2 - 5.5281*r3
         prem.vp[i] = 11.0487 - 4.0362*r + 4.8023*r2 - 13.5732*r3 
         prem.vs[i] = 0.0
      elif prem.r[i] <= 1221.5:  #inner core
         prem.rho[i] = 13.0885 - 8.8381*r2
         prem.vp[i] = 11.2622 - 6.3640*r2
         prem.vs[i] = 3.6678 - 4.4475*r2

   prem.p = rad_to_pressure(prem.r,prem.rho)

   return prem

def plot(model_name,var):
   '''
   args--------------------------------------------------------------------------
   model_name: name of model, choices- 'ak135'
   '''
   if model_name == 'ak135':
      model = ak135()

   if var == 'vp':
      plt.plot(model.vp,model.r)
   elif var == 'vs':
      plt.plot(model.vs,model.r)
   elif var == 'rho':
      plt.plot(model.rho,model.r)

   plt.show()

def write_prem_tvel(prem_file_in,prem_file_out,discon):
   '''
   prem_file_in: path to standard prem file with no additional discontinuities
   prem_file_out: name of newly created prem tvel file
   discon: depth of discontinuity you wish to add
   '''
   prem1d = prem()
   f_in = np.loadtxt(prem_file_in)
   depth = f_in[:,0]
   vp = f_in[:,1]
   vs = f_in[:,2]
   rho = f_in[:,3]
   vp_disc = prem1d.get_vp(discon)
   vs_disc = prem1d.get_vs(discon)
   rho_disc = prem1d.get_rho(discon)/1000.0
   f_out = open(prem_file_out,'w')
   i = 0
   step = 0.0001

   #write header
   f_out.write('prem{}.tvel -P'.format(discon)+'\n')
   f_out.write('prem{}.tvel -S'.format(discon)+'\n')

   for i in range(0,len(depth)-1):
      #add the disconitnuity 
      if depth[i] < discon and depth[i+1] >= discon and discon != 220 and discon != 400 and discon != 670:
	 if depth[i] != discon:
            f_out.write('{} {} {} {}'.format(depth[i],vp[i],vs[i],rho[i])+'\n')
         f_out.write('{} {} {} {}'.format(discon,vp_disc,vs_disc,rho_disc)+'\n')
         f_out.write('{} {} {} {}'.format(discon,vp_disc+step,vs_disc+step,rho_disc+step)+'\n')
      elif depth[i] != discon and depth[i] != 220 and depth[i] != 400 and depth[i] != 670:
         f_out.write('{} {} {} {}'.format(depth[i],vp[i],vs[i],rho[i])+'\n')
      else:
         f_out.write('{} {} {} {}'.format(depth[i],vp[i],vs[i],rho[i])+'\n')
      #f_out.write('{} {} {} {}'.format(depth[i],vp[i],vs[i],rho[i])+'\n')

   f_out.write('{} {} {} {}'.format(depth[-1],vp[-1],vs[-1],rho[-1])+'\n')

   f_out.close()
