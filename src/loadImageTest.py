# -*- coding: utf-8 -*-
"""
HISTORY:
    Created on Thu Sep 17 13:21:44 2020

Project: Vortex Upper Layer

Author: DIVE-LINK (www.dive-link.net), dive-link@mail.ru
        Shustov Aleksey (SemperAnte), semte@semte.ru
 
TODO:
    
DESCRIPTION:
"""

import matplotlib.image as mpimg
import numpy as np

fileName = '..\\img\\prop_small.png'

imageSource = mpimg.imread(fileName) 
# remove alpha channel
if imageSource.shape[2] == 4:
    imageSource = imageSource[:, :, 0:3]
imageSource = (imageSource * np.iinfo(np.uint8).max).astype(np.uint8)

dataType = 2
dataType = np.atleast_1d(np.uint8(dataType)) # for image data
imageWidth = imageSource.shape[0]
if imageWidth > np.iinfo(np.uint16).max:
    raise ValueError('Too much width of image.')
else:
    imageWidth = np.atleast_1d(np.uint16(imageWidth)).view(np.uint8)
imageHeight = imageSource.shape[1]
if imageHeight > np.iinfo(np.uint16).max:
    raise ValueError('Too much height of image.')
else:
    imageHeight = np.atleast_1d(np.uint16(imageHeight)).view(np.uint8)    
imageLine = np.ravel(imageSource)
dataSizeByte = 1 + 2 + 2 + imageSource.size
if dataSizeByte > np.iinfo(np.uint32).max:
    raise ValueError('Too much size of image.')
else:
    dataSizeByte = np.atleast_1d(np.uint32(dataSizeByte)).view(np.uint8)
 
dataSource = np.concatenate((dataType, imageHeight, imageWidth, imageLine))
PACKET_SIZE = 8192
dataPacket = []
for n in np.arange(np.ceil(dataSource.size / PACKET_SIZE)):
    n = int(n)
    dataPacket.append(dataSource[n*PACKET_SIZE:(n+1)*PACKET_SIZE])
    
for n in dataPacket:
    print(n.tobytes())
    

