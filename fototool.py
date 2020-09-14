#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      EWO
#
# Created:     31-10-2019
# Copyright:   (c) EWO 2019
# Licence:     MIT
#------------------------------------------------------------------------------

import os
import piexif
from fractions import Fraction
import pandas as pd
import simpledbf
import numpy as np
from numpy import nan
from datetime import datetime

def to_deg(value, loc):
    """convert decimal coordinates into degrees, munutes and seconds tuple

    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """

    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    """convert a number to rantional

    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)


def set_gps_location(file_name, lat, lng, altitude):
    """Adds GPS position as EXIF metadata and maintains date data.

    Keyword arguments:
    file_name -- image file
    lat -- latitude (as float)
    lng -- longitude (as float)
    altitude -- altitude (as float)

    """
    # read exif from picture
    exif_dict_old = piexif.load(file_name)
    # try to read image creation date from exif
    try:

        old_date = exif_dict_old['Exif'][36867]
    #    print old_date
    # use file creation date if exif date is not available
    except:

        mtime = os.path.getmtime(file_name)
        # convert binary date format to exif date format
        old_date = datetime.fromtimestamp(mtime).strftime('%Y:%m:%d %H:%M:%S')


    lat_deg = to_deg(lat, ["S", "N"])
    lng_deg = to_deg(lng, ["W", "E"])

    exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
    exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
        piexif.GPSIFD.GPSAltitudeRef: 1,
        piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude)),
        piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
        piexif.GPSIFD.GPSLatitude: exiv_lat,
        piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
        piexif.GPSIFD.GPSLongitude: exiv_lng,
    }

    exif_ifd = {piexif.ExifIFD.DateTimeOriginal: old_date
    }
  #  print file_name
  #  print exif_ifd

    exif_dict = {"Exif":exif_ifd, "GPS": gps_ifd}
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, file_name)

class RDWGSConverter:

    """Converts RD_new to WGS84.

    Keyword arguments:


    """

    X0      = 155000
    Y0      = 463000
    phi0    = 52.15517440
    lam0    = 5.38720621

    def fromRdToWgs( self, coords ):

        Kp = [0,2,0,2,0,2,1,4,2,4,1]
        Kq = [1,0,2,1,3,2,0,0,3,1,1]
        Kpq = [3235.65389,-32.58297,-0.24750,-0.84978,-0.06550,-0.01709,-0.00738,0.00530,-0.00039,0.00033,-0.00012]

        Lp = [1,1,1,3,1,3,0,3,1,0,2,5]
        Lq = [0,1,2,0,3,1,1,2,4,2,0,0]
        Lpq = [5260.52916,105.94684,2.45656,-0.81885,0.05594,-0.05607,0.01199,-0.00256,0.00128,0.00022,-0.00022,0.00026]

        dX = 1E-5 * ( coords[0] - self.X0 )
        dY = 1E-5 * ( coords[1] - self.Y0 )

        phi = 0
        lam = 0

        for k in range(len(Kpq)):
            phi = phi + ( Kpq[k] * dX**Kp[k] * dY**Kq[k] )
        phi = self.phi0 + phi / 3600

        for l in range(len(Lpq)):
            lam = lam + ( Lpq[l] * dX**Lp[l] * dY**Lq[l] )
        lam = self.lam0 + lam / 3600

        return [phi,lam]

def importExcel(name):

    """ Retrieves RD coordinates from pandas dataframe, returns WSG84.

    Keyword arguments:


    """


    # name = name.replace('-','_')

    #df_select = df.loc[df.iloc[:,0].apply(str) == name.lower()]
    df_select = df[pd.Series(df.loc[:,fotocol]).str.contains(name, case=False)]
  #  print df_select
    # df_select_row = df_select[['XIN', 'YIN']]
    df_select_row = df_select[[xstring, ystring]]


    coords = [0.0, 0.0]


    try:
        coords = [df_select_row[xstring].item(), df_select_row[ystring].item()]

        coords = [float(i) for i in coords]


    except:
       # global fail
     #   fail = fail + 1
     #   print name + 'fail2'
        pass

    nan = 0.0
   # print coords
    if coords == [u'null', u'null'] or coords == [0.0, 0.0] or coords == [np.nan, np.nan] or coords == [nan, nan] or df_select_row.isnull().values.any():

        global nocoords
        nocoords = nocoords + 1
        return False
    else:

        conv = RDWGSConverter()
        wgsCoords = conv.fromRdToWgs( coords )

        return wgsCoords

# .CSV, .XLS or GBD containing RD coordinates and image name
file_name = r'C:\...'# path to file + file name
# folder with itmages
folderPath = r"C:\..."

#file_name_path = r'C:\\'

#folderList_path = os.listdir(file_name_path)

#file_name = file_name_path+'\\'+folderList_path[2]

fail = 0
succes = 0
nocoords = 0

# df = "test"
fotocol = 'FOTONR' # column name with foto id or object id
xstring = 'X' # column with X coordinates.
ystring = 'Y' # column with Y coordinates.

if 'eilschalen' in file_name or 'eilschaal' in file_name:
    xstring = 'X_PEIL'
    ystring = 'Y_PEIL'

elif 'uiker' in file_name or 'yphon' in file_name or 'ifon' in file_name or 'luizen' in file_name:
    xstring = 'XIN'
    ystring = 'YIN'

elif 'rug' in file_name:
    xstring = 'X'
    ystring = 'Y'

elif 'ut' in file_name:
    xstring = 'XPUT'
    ystring = 'YPUT'

elif 'dam' in file_name:
    xstring = 'XLINKS'
    ystring = 'YLINKS'

else:
    xstring = 'X' # column with X coordinates.
    ystring = 'Y' # column with Y coordinates.

sheet = 1 # sheet name or sheet number or list of sheet numbers and names

# try to read table
# df = pd.read_csv(file_name, sep = ';', thousands='.', decimal=",")

try:
    df = pd.read_excel(io=file_name, sheet_name=sheet)
   # print df
    df = df.stack().str.replace(',','.').unstack()
    print df
except:
   try:
    df = pd.read_csv(file_name, sep = ';', thousands='.', decimal=",")
 #   df = df.stack().str.replace(',','.').unstack()

    df[xstring] = pd.to_numeric(df[xstring],errors='coerce')
    df[ystring] = pd.to_numeric(df[ystring],errors='coerce')
   except:
      print 'ok'
      dbf = simpledbf.Dbf5(file_name, codec='utf-8')
      print dbf
      df = dbf.to_dataframe()
      df = df.stack().str.replace(',','.').unstack()
      print df
   print df

#list all  files in directory

folderList = os.listdir(folderPath)

print folderList

for i in folderList:

        print i
        coord = importExcel(i.lstrip("0")[:-4])
       # print coord

        if (coord != False):

            fotoUrl = folderPath+'\\'+i
            set_gps_location(fotoUrl,coord[0],coord[1],0)
            succes = succes + 1

        else:

            print i +' fail'
            print coord
            fail = fail + 1

print 'fail ' + str(fail-nocoords)
print 'nocoords ' + str(nocoords)
print 'succes ' + str(succes)



