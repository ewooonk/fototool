# fototool
Bulk processing of jpg exif data and RD-coordinates data to Geodatabase.

### Fototool.py
Updates exif-info including location and time of all images in a folder using a CSV, XLS or GBD file with RD-coordinates.

### fototoGDB.py
Reads exif info of all images in a folder and parses them to a GDB, so the pictures can be displayed on a map.


### Dependencies
* piexif (for reading and updating exif data)
* simpledbf
* arcpy
