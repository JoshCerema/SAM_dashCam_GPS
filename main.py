from datetime import datetime, timedelta, date, time
import numpy as np
import pandas as pd
import cv2 as cv
import glob
import gpxpy
import gpxpy.gpx
from gpxpy import gpx
from numpy import loadtxt
from openpyxl import load_workbook
import re

def make_excel_gps_acc(folder):
    ## columns for excel file
    excel_columns = ["Sample Time", "GPS Date/Time", "GPS Latitude", "GPS Longitude", "GPS Speed", "GPS Altitude"]
    excel_columns_2 = ["Time Code", "Accelerometer 1", "Accelerometer 2", "Accelerometer 3"]
    df = pd.DataFrame(columns=excel_columns)
    df2 = pd.DataFrame(columns=excel_columns_2)
    row_number = 0
    row_number_2 = 0

    for file_txt in glob.glob(folder + '*.txt'):
        with open(file_txt) as file:
            for line in file:
                aux = line.split(": ")
                aux0 = aux[0].strip(' ')
                aux1 = aux[1].strip('\n')
                if aux0 == "Sample Time":
                    df.loc[row_number, "Sample Time"] = aux1
                elif aux0 == "GPS Date/Time":
                    df.loc[row_number, "GPS Date/Time"] = aux1
                elif aux0 == "GPS Latitude":
                    df.loc[row_number, "GPS Latitude"] = aux1
                elif aux0 == "GPS Longitude":
                    df.loc[row_number, "GPS Longitude"] = aux1
                elif aux0 == "GPS Speed":
                    df.loc[row_number, "GPS Speed"] = float(aux1)
                elif aux0 == "GPS Altitude":
                    df.loc[row_number, "GPS Altitude"] = aux1
                    row_number = row_number + 1
                elif aux0 == "Time Code":
                    df2.loc[row_number_2, "Time Code"] = float(aux1)
                elif aux0 == "Accelerometer":
                    accs = aux[1].split(' ')
                    df2.loc[row_number_2, "Accelerometer 1"] = float(accs[0])
                    df2.loc[row_number_2, "Accelerometer 2"] = float(accs[1])
                    df2.loc[row_number_2, "Accelerometer 3"] = float(accs[2])
                    row_number_2 = row_number_2 + 1
                elif aux0 == "Media Data Size":
                    break
    #timestr = file_txt.split("\\")[-1]
    #timestr = timestr.split(".txt")[0]
    timestr = "18052022"
    with pd.ExcelWriter(folder + "report gps and acc " + timestr + ".xlsx") as writer1:
        df.to_excel(writer1, sheet_name='gps data', columns=excel_columns, index=False)
        df2.to_excel(writer1, sheet_name='acc data', columns=excel_columns_2, index=False)
    print("report file: " + folder + "report gps and acc " + timestr + ".xlsx")
    print("Report finished...")


# This function is used to clean a gpx file (if required)
# it is used to remove the repeated part of the gpx file coming from dashcam
# this function is very specific for the gxp file produced from the dashcam and the exiftool
# PS. Repetition is linked to the time stamp
# input - file coming from exiftool (video dashcam passing throw exiftool)
def clean_gpx_file(folder,file):
    # Open the gpx file - Lybrary gpxpy required
    gpx_file = open(folder+file, 'r')
    gpx = gpxpy.parse(gpx_file)
    # auxiliar variable
    first_point = 0
    # find the start of repeated data, and then save only the data read until now
    for track in gpx.tracks:
         for segment in track.segments:
             for point in segment.points:
                #print('Point at ({0},{1}) -> {2} {3}'.format(point.latitude, point.longitude, point.elevation, point.time))
                if (first_point == 0):
                    first_point = point
                    # create GPX file
                    #print('GPX:', gpx.to_xml())
                    # Creating a new file:
                    # --------------------
                    gpx = gpxpy.gpx.GPX()
                    # Create first track in our GPX:
                    gpx_track = gpxpy.gpx.GPXTrack()
                    gpx.tracks.append(gpx_track)
                    # Create first segment in our GPX track:
                    gpx_segment = gpxpy.gpx.GPXTrackSegment()
                    gpx_track.segments.append(gpx_segment)
                    # Create points:
                    gpx_segment.points.append(point)
                else:
                    if (first_point.time == point.time):
                        print("Repeated point: lat:{0}, long:{1}, time:{2}".format(point.latitude, point.longitude, point.time))
                        #print('Created GPX:', gpx.to_xml())
                        filename = find_filename_noExtension(file)
                        with open(folder+filename+'_cleaned'+'.gpx', "w") as fpo:
                            print(gpx.to_xml(), file=fpo)
                        break
                    else:
                        # Create points:
                        gpx_segment.points.append(point)


# Function used to find the name of a file (removing the extension)
# filename is composed as follows...
# input - filename = name.extension
# output - name
def find_filename_noExtension(filename):
    aux = re.split("[.]", filename)
    return aux[0]

# Function used to find the lapse time at which the autonomous bus passes in front of an especific camera
# i.e., given a gps traject and the four coordinates correspondig to the limits of a camera (ROI),
# this function returns the initial and (optional) end time at which the bus was in front of the corresponding camera
# input - gpx_file, camera_number, limits(coordinates in gps, from left to right)
# output - excel file with the time at which the bus was in front
def navette_infront_of_camera(folder, file, camera_number, camera_limits):
    ## columns for excel file
    excel_columns = ["Camera", "GPS Date/Time", "GPS Latitude", "GPS Longitude", "Inside"]
    df = pd.DataFrame(columns=excel_columns)
    row_number = 0
    # open the gpx file (input file)
    gpx_file = open(folder+file, 'r')
    gpx = gpxpy.parse(gpx_file)
    # define limits
    a_right, b_right = find_parameters_ab(camera_limits[0:2])
    a_left, b_left = find_parameters_ab(camera_limits[2:4])
    # for each point gps, find if the bus was inside or outside the limits. If it is inside, report it in the excel file
    for track in gpx.tracks:
         for segment in track.segments:
             for point in segment.points:
                inside = evaluate_if_camera_can_see_it(point, a_left, b_left, a_right, b_right)
                df.loc[row_number, "Camera"] = int(camera_number)
                df.loc[row_number, "GPS Date/Time"] = pd.to_datetime(point.time).tz_localize(None) # remove time zone
                df.loc[row_number, "GPS Latitude"] = point.latitude
                df.loc[row_number, "GPS Longitude"] = point.longitude
                df.loc[row_number, "Inside"] = inside
                row_number += 1
    timestr = 'today'
    with pd.ExcelWriter(folder + "report position navette " + timestr + ".xlsx") as writer1:
        df.to_excel(writer1, sheet_name='camera '+str(camera_number), columns=excel_columns, index=False)
    print("report file: " + folder + "report position navette " + timestr + ".xlsx" + " finished")

# find parameters a and b used for to know if the bus is inside the field of view of a camera
def find_parameters_ab(positions):
    x1 = positions[0][0]
    y1 = positions[0][1]
    x2 = positions[1][0]
    y2 = positions[1][1]
    a = (y2 - y1) / (x2 - x1)
    b = (y1 - (a * x1))
    return a,b

# Evaluate if the bus is inside the ROI of the camera
def evaluate_if_camera_can_see_it(point, a_left, b_left, a_right, b_right):
    x = point.longitude
    y = point.latitude
    res1 = a_left * x + b_left
    res2 = a_right * x + b_right
    if ( ((y>=res1) and (y>=res2)) or ((y<res1) and (y<res2)) ):
        return False
    else:
        return True




#folder = "D:/SAM/Videos a analizar/files txt/"
#make_excel_gps_acc(folder)
folder1 = "D:/SAM/Videos a analizar/files gpx/"
folder2 = "D:/SAM/Videos a analizar/files gpx2/"
file1 = "20220113_162829_164930_EF.gpx"
file2 = "20220113_164930_NF_cleaned.gpx"
x1,y1 = 1.429921560957295,43.55506695489137
x2,y2 = 1.429906208488139,43.55493144671023
x3,y3 = 1.429499460263077,43.55510140183409
x4,y4 = 1.429490370788564,43.55495948841669
camera_limits = [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

#clean_gpx_file(folder2,file2)
navette_infront_of_camera(folder2, file2, 3, camera_limits)