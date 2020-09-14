#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      EWO
#
# Created:     30-12-2019
# Copyright:   (c) EWO 2019
# Licence:     MIT
#-------------------------------------------------------------------------------

import os,sys,fnmatch
import arcpy
import shutil

import os
import piexif
from fractions import Fraction
import pandas as pd
import simpledbf
import numpy as np
from numpy import nan
from datetime import datetime


fldsPhotos = [['FILENAME','text',50],['DATUM','text',10],['WGS84_X','double',10,2],['WGS84_Y','double',10,2],['FILE_PATH','text',128]]



# list all images in folder

imagepath = r"C:\..."
#
folderPath =  r"C:\..."
folderList = os.listdir(folderPath)

print folderList
# read image path, date, location for each i



#-------------------------------------------------------------------------------
def setValue(row,fieldname,val,fieldtype=None):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     11/06/2015  co
    try:
        if val <> None:
            if fieldtype == 'float':
                val = float(val)
            elif fieldtype == 'int':
                val = int(val)
            row.setValue(fieldname,val)
        else:
            row.setValue(fieldname,NV)
    except:
        Log('Error setting field ' + fieldname + ' : '+str(val),1)


def readGps(file_name):

    try:

        exif_dict_new = piexif.load(file_name)

        exif_gps = exif_dict_new['GPS']

        return exif_gps

    except:
        return 'fail'


def convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value[0][0])
    m = float(value[1][0])
    s = float(value[2][0]/ 100000)

    return d + (m / 60.0) + (s / 3600.0)

#-------------------------------------------------------------------------------
def CreateFC(ws,fcnaam,featureType,fields):
#-------------------------------------------------------------------------------
    """
        purpose:
    """
    # Created:     09/06/2015  co
  #  try:
    fc = os.path.join(ws,fcnaam)
    sr = arcpy.SpatialReference(28992)
    if not arcpy.Exists(fc):
        Log('Aanmaken featureclass: '+fcnaam)
        arcpy.CreateFeatureclass_management(ws,fcnaam,featureType,None,'DISABLED','ENABLED',sr)
        for fld in fields:
            if fld[1].lower() == 'text':
                arcpy.AddField_management(fc,fld[0],'text',fld[2])
            elif fld[1] == 'double':
                arcpy.AddField_management(fc,fld[0],'double',fld[2],fld[3])
            elif fld[1] == 'date':
                arcpy.AddField_management(fc,fld[0],'date')
            else:
                print fcnaam + ': Unknown field type: ' + fld[0] + '- ' + fld[1]
        DeleteField(fc,'id')
    else:
     #   Log('Toevoegen aan bestaande featureclass: '+fcnaam)
        print 'ok'
    return fc
 #   except Exception, ErrorMsg:
   #     Log('Onverwachte fout in CreateFC: '+str(ErrorMsg),-1)
   #     return None



def writePhoto(fcb,x,y,date,filename,path):
    z = 0
    cur = arcpy.InsertCursor(fcb)
    row = cur.newRow()
    pt = arcpy.Point(x,y,z)
    setValue(row,'shape',pt)
    setValue(row,'filename',filename)
    setValue(row,'file_path',path)
    setValue(row,'DATUM',date)
    setValue(row,'WGS84_X',x)
    setValue(row,'WGS84_Y',y)
    cur.insertRow(row)

for i in folderList:

    imagepath = folderPath+'\\'+i
    print imagepath
    try:
        x=0
        y=0
        z=0

        exifGps = readGps(imagepath)

        x = convert_to_degress(exifGps[2])
        y = convert_to_degress(exifGps[4])

        exifDate = piexif.load(imagepath)['Exif'][36867].replace(':','-', 2)

        print x, y, exifDate
        outGDB = r'C:\...'

        if not arcpy.Exists(outGDB):

            foldername = os.path.dirname(outGDB)
            fgdName = os.path.basename(outGDB)
            arcpy.CreateFileGDB_management(foldername,fgdName)

        fcb = CreateFC(outGDB,'fotos','POINT',fldsPhotos)

        photoname= os.path.basename(imagepath)
        photodir= os.path.dirname(imagepath)
        print photodir

        writePhoto(fcb,x,y,exifDate,photoname,photodir)

        print 'ok'
    except:
        print 'error'
