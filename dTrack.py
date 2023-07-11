# for visualising breath figure data

import matplotlib.pyplot as plt
import numpy as np
import os
import mTrack as mt
import pickle


# load the data
# should be in five columns: count, Area, XM, YM, Slice
# ignore the top header row
###############################

def main():
    directory = input("Please input a directory: ")

    if os.path.exists(os.path.join(directory,"dTrack_config.py")):
        print("dTrack_config.py - found")
    else:
        print("config_dir may not exist or")
        print("dTrack_config.py - not found")
        print("config_dir must contain the configuration file: \"dTrack_config.py\".")
        return
            
    c = mt.read_config(directory, "dTrack_config")

    data = mt.readBreath(directory,c.filename)

    # find the number of slices (frames)
    # and set up variables to count total Radius, Volume and Particles per slice
    n = max(data['Slice'])                                      # total number of slices (frames)
    R = np.zeros([n])
    V = np.zeros([n])
    N = np.zeros([n], dtype=int)
    XY = np.zeros([n])
    rwh = np.zeros([len(data['Width'])])

    # loop over data and work out these values
    for i, s in enumerate(data['Slice']):
        rwh[i] = np.mean([data['Width'][i],data['Height'][i]])/2
        N[s-1] = N[s-1] + 1             # add up all the droplets in each slice
        V[s-1] = V[s-1] + rwh[i]**3.0      # add up the total "volume" in each slice

    totalDrops = max(N)

    ## create a proper 2D numpy array of coordinates
    XY=np.transpose(np.asarray((data['BX'], data['BY'])))

    ## create an array of the slice/frame value
    S=np.transpose(np.asarray(data['Slice']))

    ## create an array to store the time evolution of the volume of each identified droplet
    ## max(N) columns, for each droplet
    ## n rows, for each slice
    
    if c.centres == "droplets":
        pointlist = [list(data['BX']),list(data['BY'])]
    else:
        pointlist  = c.centres
    vdrop = np.zeros([len(pointlist),n])
    xtrack = np.zeros([len(pointlist),n])
    ytrack = np.zeros([len(pointlist),n])
    ## loop over drops to track their evolution
    for pdx, point in enumerate(pointlist):
        print("Tacking point: ", pdx) # x,y coordinates to find the nearest droplet
        ppoint = point
        for sl in range(1, max(data['Slice'])):
            start= np.where(data['Slice']==sl)[0][0]                # find the start of the current slice
            idx = mt.closest_node(point, XY[S==sl])              # coordinates of the closest droplet in slice
            dxy = np.sqrt(( ppoint[0]-data['BX'][start+idx] )**2+ ( ppoint[1]-data['BY'][start+idx])**2)
            inside = dxy<2*rwh[start+idx]
            vdrop[pdx,sl-1]=rwh[start+idx]*inside
            xtrack[pdx,sl-1]=data['BX'][start+idx]*inside
            ytrack[pdx,sl-1]=data['BY'][start+idx]*inside
            ppoint = [data['BX'][start+idx],data['BY'][start+idx]]
            
    ## it would be good to define the distance accoridng to the previous centre, rather than the starting one

    Results={}
    Results['radius'] = vdrop
    Results['points'] = pointlist
    Results['xcentre'] = xtrack
    Results['ycentre'] = xtrack

    if c.export:
        with open(os.path.join(directory,"dTrack_"+c.prefix+".pickle"), 'wb') as handle:
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
    for sl in range(1, max(data['Slice']),100):
        H = np.histogram(rwh[(data['Slice'] ==sl)], bins=17, range=(0,1700))
        ax[0,1].plot(H[1][0:-1],H[0], label=sl)
    ax[0,1].set_xlabel('droplet area')
    ax[0,1].set_ylabel('number of droplets')
    ax[0,1].legend()

    #ax[1,0].plot(data['Slice'],(data['Width']+data['Height'])/2,'.', alpha=0.5)
    for point in range(len(pointlist)):
        y = vdrop[point]
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

main()