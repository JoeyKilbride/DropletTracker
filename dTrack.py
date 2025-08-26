# for visualising breath figure data

import matplotlib.pyplot as plt
import numpy as np
import os
import mTrack as mt
import pickle
import sys


# load the data
# should include columns: count, Area, XM, YM, Slice
# ignore the top header row
###############################

def main(config_dir):
    
    if os.path.exists(os.path.join(config_dir,"dTrack_config.py")):
        print("dTrack_config.py - found")
    else:
        print("config_dir may not exist or")
        print("dTrack_config.py - not found")
        print("config_dir must contain the configuration file: \"dTrack_config.py\".")
        return

    c = mt.read_config(config_dir, "dTrack_config")
    if os.path.exists(os.path.join(config_dir,c.filename+".txt")):
        print(c.filename+" - found")
    else:
        print(c.filename+" - not found")
        print("config_dir must contain the file set to the \"filename\" variable in \"dTrack_config.py\".")
        return
    data = mt.readBreath(config_dir,c.filename)

    # find the number of slices (frames)
    # and set up variables to count total Radius, Volume and Particles per slice
    print("Allocating memory")
    n = int(max(data['Slice']))                                      # total number of slices (frames)
    R = np.zeros([n])
    V = np.zeros([n])
    N = np.zeros([n], dtype=int)
    XY = np.zeros([n])
    rwh = np.zeros([len(data['Major'])])


    for i, s in enumerate(data['Slice']): # loop over all rows in text file
        rwh[i] = np.min([data['Major'][i],data['Minor'][i]])/2
    for i, s in enumerate(np.unique(data['Slice'])): # loop over all slices 
        N[i] = len(data['Slice'][data['Slice']==s])
        V[i] = np.sum(data['Slice'][data['Slice']==s])
    
    totalDrops = max(N)

    ## create a proper 2D numpy array of coordinates
    XY=np.transpose(np.asarray((data['X'], data['Y'])))

    ## create an array of the slice/frame value
    S=np.transpose(np.asarray(data['Slice']))

    ## create an array to store the time evolution of the volume of each identified droplet
    ## max(N) columns, for each droplet
    ## n rows, for each slice
    
    if c.centres == "droplets":
        pointlist = np.transpose([list(data['X'][data['Slice']==1]),list(data['Y'][data['Slice']==1])])
    else:
        pointlist  = c.centres
    nreduced = len(range(c.start,c.end,c.steps))
    rdrop = np.zeros([len(pointlist),nreduced])
    xtrack = np.zeros([len(pointlist),nreduced])
    ytrack = np.zeros([len(pointlist),nreduced])
    ## loop over drops to track their evolution
    npoints = len(pointlist)
    try:
        for pdx, point in enumerate(pointlist):
            print("Tracking point: ", pdx,"/",str(npoints)) # x,y coordinates to find the nearest droplet
            ppoint = point
            count=0
            for sl in range(c.start, c.end ,c.steps):
                start= np.where(data['Slice']==sl)[0][0]            # find the start of the current slice
                idx = mt.closest_node(point, XY[S==sl])              # coordinates of the closest droplet in slice
                if sl==1:
                    rj = rwh[start+idx]
                    
                dxy = np.sqrt(( point[0]-data['X'][start+idx] )**2+ ( point[1]-data['Y'][start+idx])**2)
                #print("dxy = ",dxy, "rj = ", rj)
                inside = dxy<rj
                #print(inside)
                #print("r = ", rwh[start+idx])
                rdrop[pdx,count]  = rwh[start+idx]*inside
                xtrack[pdx,count] = data['X'][start+idx]*inside
                ytrack[pdx,count] = data['Y'][start+idx]*inside
                ppoint = [data['X'][start+idx],data['Y'][start+idx]]
                count = count+1
    except:
        print("Loop failed at point "+str(pdx)+" frame "+str(sl))
        print("check this frame exists in file.")
        return

    ## it would be good to define the distance accoridng to the previous centre, rather than the starting one

    Results={}
    Results['radius'] = rdrop
    Results['points'] = pointlist
    Results['xcentre'] = xtrack
    Results['ycentre'] = ytrack
    Results['rwh'] = rwh
    Results['data'] = data
    Results['calibration'] = c.calibration
    Results['FPS'] = c.FPS

    if c.export:
        with open(os.path.join(config_dir,"dTrack_"+c.prefix+".pickle"), 'wb') as handle:
            pickle.dump(Results, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("exported")


    #################                 
    # plot the data #
    #################
    fig, ax = plt.subplots(2,2, figsize=(12,7))
    ax[0,0].plot(N/N[0], label='number of droplets')
    ax[0,0].plot(V/V[0], label='total droplet volume')
    ax[0,0].plot((V/N)/max(V/N), label='average droplet volume')
    ax[0,0].legend()
    ax[0,0].set_ylabel('normalised value')

    ## make histograms for each slice
    for sl in range(1, 600,100):
        H = np.histogram(rwh[data['Slice']==sl], bins=15, range=(0,np.max(rwh)))
        ax[0,1].plot(H[1][0:-1],H[0], label=sl)
    ax[0,1].set_xlabel('droplet radius')
    ax[0,1].set_ylabel('number of droplets')
    ax[0,1].legend()

    #ax[1,0].plot(data['Slice'],(data['Width']+data['Height'])/2,'.', alpha=0.5)
    for point in range(len(pointlist)):
        y = rdrop[point]
        y = y[y>0]
        ax[1,0].plot(y, label='drop %i' % point)

    # ax[1,0].legend()
    ax[1,0].set_xlabel('time')
    ax[1,0].set_ylabel('individual droplet area')


    ## ax[1,1].plot(XY[:,0],XY[:,1],'.')
    posplot = ax[1,1].scatter(XY[:,0],XY[:,1], c=data['Slice'], cmap='viridis', s=(rwh)/4, alpha=0.5)
    plt.colorbar(posplot, ax=ax[1,1])
    ax[1,1].set_xlabel('x')
    ax[1,1].set_ylabel('y')

    ##plt.xlabel('time')
    plt.show()

    ## from https://codereview.stackexchange.com/questions/28207/finding-the-closest-point-to-a-list-of-points
    return

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <directory_path>")
        sys.exit(1)
    
    config_dir = sys.argv[1]
    if not os.path.isdir(config_dir):
        print("Error: The provided path is not a directory.")
        sys.exit(1)
    
main(config_dir)
