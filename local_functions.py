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
import glob
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time
import limits_on_cameras as loc

# function to produce an excel file that contains gps and acceleration information
# it uses 'function make_excel_gps_acc'
def create_excel_gps_acc(folder,day):
    # if the list of txt files to consider for the report is not providen, then search all txt files
    list_of_files = glob.glob(folder + day + '*F.txt')
    make_excel_gps_acc(folder,list_of_files,day)

# function used to produce excel file with two sheets... GPS information, and Acceleretion data
# it takes as input the txt file that contains all the gps and acc data.
# the output will be the excel with both gps and acceleration from the three acceleromenters
# IMPORTANT. It can produces an excel file from information coming from a single mp4 video OR a list of videos
def make_excel_gps_acc(folder,list_of_files,day):
    ## columns for excel file
    excel_columns = ["Sample Time", "GPS Date/Time", "GPS Latitude", "GPS Longitude", "GPS Speed", "GPS Altitude", "File source"]
    excel_columns_2 = ["Time Code", "Time", "Accelerometer 1", "Accelerometer 2", "Accelerometer 3", "File source"]
    df = pd.DataFrame(columns=excel_columns)
    df2 = pd.DataFrame(columns=excel_columns_2)
    row_number = 0
    row_number_2 = 0
    start_time = 0

    for file_txt in list_of_files:
        with open(file_txt) as file:
            for line in file:
                aux = line.split(": ")
                aux0 = aux[0].strip(' ')
                aux1 = aux[1].strip('\n')
                if aux0 == "Sample Time":
                    df.loc[row_number, "Sample Time"] = aux1
                elif aux0 == 'Start Time':
                    save_date = aux1.split(' ')[0]
                    save_date = save_date.replace(':','-')
                    start_time = pd.to_datetime(save_date+' '+aux1.split(' ')[1])  # remove time zone
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
                    df.loc[row_number, "File source"] = file_txt
                    row_number = row_number + 1
                elif aux0 == "Time Code":
                    df2.loc[row_number_2, "Time Code"] = float(aux1)
                    df2.loc[row_number_2, "Time"] = start_time + timedelta(seconds=float(aux1))
                elif aux0 == "Accelerometer":
                    accs = aux[1].split(' ')
                    df2.loc[row_number_2, "Accelerometer 1"] = float(accs[0])
                    df2.loc[row_number_2, "Accelerometer 2"] = float(accs[1])
                    df2.loc[row_number_2, "Accelerometer 3"] = float(accs[2])
                    df2.loc[row_number_2, "File source"] = file_txt
                    row_number_2 = row_number_2 + 1
                elif aux0 == "Media Data Size":
                    break
    #timestr = time.strftime("%d%m%Y_%H%M%S")
    timestr = day
    with pd.ExcelWriter(folder + "report gps and acc " + timestr + ".xlsx") as writer1:
        df.to_excel(writer1, sheet_name='gps data', columns=excel_columns, index=False)
        df2.to_excel(writer1, sheet_name='acc data', columns=excel_columns_2, index=False)
    print("saved file: " + folder + "report gps and acc " + timestr + ".xlsx")

# function used to remove redundancy from all gpx files inside a folder and that follow the pattern
def clean_gpx_files_in_folder(folder,pattern):
    # find all gpx files in folder
    list_of_files = find_files_with_pattern(folder, pattern, '.gpx')
    # clean file by file
    for file_to_clean in list_of_files:
        clean_gpx_file(folder,file_to_clean)

# This function is used to clean a gpx file (if required)
# it is used to remove the repeated part of the gpx file coming from dashcam
# this function is very specific for the gxp file produced from the dashcam and the exiftool
# PS. Repetition is linked to the time stamp
# input - file coming from exiftool (video dashcam passing throw exiftool)
# output - A gpx file without the repeated data (same_filename+_cleaned at the end)
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

# Function used to determine for which cameras the autonomous bus is seen
def navette_infront_of_cameras(limits_on_cameras,point):
    cameras = [1,2,3,4,5,6]
    for camera in cameras:
        row_number = limits_on_cameras[(limits_on_cameras["Camera_number"] == camera)].index[0]
        x1 = limits_on_cameras['x1'][row_number]
        y1 = limits_on_cameras['y1'][row_number]
        x2 = limits_on_cameras['x2'][row_number]
        y2 = limits_on_cameras['y2'][row_number]
        x3 = limits_on_cameras['x3'][row_number]
        y3 = limits_on_cameras['y3'][row_number]
        x4 = limits_on_cameras['x4'][row_number]
        y4 = limits_on_cameras['y4'][row_number]
        camera_limits = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4], [x1, y1]])
        limits_on_cameras.loc[row_number,"Inside FOV"] = navette_infront_of_specific_camera(point, camera_limits)

# Function used to determine when the autonomous bus is in front of a certain camera
# output is an excel file
def find_navette(folder, limits_on_cameras, day, list_of_files='none'):
    ## columns for excel file
    excel_columns = ["GPS Date/Time", "GPS Latitude", "GPS Longitude",
                     "Visible on Camera 1", "Visible on Camera 2", "Visible on Camera 3",
                     "Visible on Camera 4", "Visible on Camera 5", "Visible on Camera 6", "File"]
    df = pd.DataFrame(columns=excel_columns)
    row_number = 0
    # if the list of files is not provided, then search all gpx files
    # that follows the pattern '*_cleaned.gpx'
    if (list_of_files == 'none'):
        list_of_files = glob.glob(folder + '*_cleaned.gpx')
    ## all the list of files will be resumed in a single excel file
    for file in list_of_files:
        # open the gpx file (input file)
        gpx_file = open(file, 'r')
        gpx = gpxpy.parse(gpx_file)
        # for each point gps, find if the bus was inside or outside the limits. If it is inside, report it in the excel file
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    navette_infront_of_cameras(limits_on_cameras,point)
                    df.loc[row_number, "GPS Date/Time"] = pd.to_datetime(point.time).tz_localize(None)  # remove time zone
                    df.loc[row_number, "GPS Latitude"] = point.latitude
                    df.loc[row_number, "GPS Longitude"] = point.longitude
                    df.loc[row_number, "Visible on Camera 1"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 1)][0]
                    df.loc[row_number, "Visible on Camera 2"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 2)][1]
                    df.loc[row_number, "Visible on Camera 3"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 3)][2]
                    df.loc[row_number, "Visible on Camera 4"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 4)][3]
                    df.loc[row_number, "Visible on Camera 5"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 5)][4]
                    df.loc[row_number, "Visible on Camera 6"] = limits_on_cameras["Inside FOV"][(limits_on_cameras["Camera_number"] == 6)][5]
                    df.loc[row_number, "File"] = file
                    row_number += 1
    #timestr = time.strftime("%d%m%Y_%H%M%S")
    timestr = day
    with pd.ExcelWriter(folder + "report position navette " + timestr + ".xlsx") as writer1:
        df.to_excel(writer1, sheet_name='all cameras', columns=excel_columns, index=False)
    print("saved file: " + folder + "report position navette " + timestr + ".xlsx")

# Function used to find the lapse time at which the autonomous bus passes in front of a specific camera
# i.e., given a gps traject and the four coordinates corresponding to the limits of a camera (ROI),
# this function returns the initial and (optional) end time at which the bus was in front of the corresponding camera
# input - gpx_file, camera_number, limits(coordinates in gps, from left to right)
# output - excel file with the time at which the bus was in front
def navette_infront_of_specific_camera(point, camera_limits):
    # check for all cameras if the bus is inside the field of view
    inside = evaluate_if_camera_can_see_it(point, camera_limits)
    return inside

# Evaluate if the bus is inside the field of view of the camera
# the field of view is represented as a polygon created from 4 gps positions
def evaluate_if_camera_can_see_it(point, camera_limits):
    x = point.longitude
    y = point.latitude
    P = Point(x,y)
    polygon = Polygon(camera_limits)
    if polygon.contains(P):
        return True
    else:
        return False

# This function returns a list of all files inside "path" that match "pattern" and "extension"
# i.e.  path/pattern.extension
# extension have to include the dot: extension=".mp4"
# the output format is: "file.extension" (no path)
def find_files_with_pattern(path,pattern,extension):
    files_with_pattern = []
    for file in glob.glob(path+pattern+extension):
        file = os.path.basename(file)
        files_with_pattern.append(file)
    return(files_with_pattern)

# Create gpx files (and/or txt files) of all MP4 videos inside a folder
# the input is the folder (or path) in which all MP4 videos are
# the output is the folder with all the correspondent gpx files
def execute_commands_exiftool(path,file):
    # read file txt that contains the exiftool commands (read line by line)
    file_to_read = open(path+file, 'r')
    Lines = file_to_read.readlines()
    for line in Lines:
        # execute the line in cmd
        os.system('cmd /c "{}"'.format(line.strip()))

# Create a list of commands to execute exiftool to extract gps information (or accelerometers data) from mp4 file
def list_of_commands_exiftool(path,fmt_file,output_folder,output_file,pattern,output_type="gpx"):
    # find all files mp4
    list_of_mp4_videos = find_files_with_pattern(path, pattern, ".mp4")
    # create the new folder that will contains the gpx files (the outputs)
    newpath = output_folder
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    # write txt with all commands exiftool
    with open(newpath+output_file, 'w') as f:
        for file_mp4 in list_of_mp4_videos:
            file_name = find_filename_noExtension(file_mp4)
            if (output_type == "gpx"):
                line = 'exiftool -p ' + '\"' + fmt_file + '\"' + ' -ee ' + '\"' + path + file_mp4 + '\"' + ' > ' + '\"' + newpath + file_name + '.gpx' + '\"'
            else:
                line = 'exiftool -ee ' + '\"' + path + file_mp4 + '\"' + ' > ' + '\"' + newpath + file_name + '.txt' + '\"'
            f.write(line)
            f.write('\n')

# List all the days availables inside the current folder
def list_recorder_days(path):
    pattern = "*F"
    extension = ".mp4"
    list_of_recorded_days = find_files_with_pattern(path,pattern,extension)
    i = 0
    for element in list_of_recorded_days:
        list_of_recorded_days[i] = element.split('_')[0]
        i = i + 1
    list_of_recorded_days = set(list_of_recorded_days)
    list_of_recorded_days = list(list_of_recorded_days)
    return list_of_recorded_days

# From a list of recorded days, extract gpx files and create excel report from them
def create_gps_report_by_day(folder, file_fmt, list_of_days_recorded):
    ## Folder that will contains the gpx files
    gpx_folder = folder + "gpx_files/"
    ## Set limits on all cameras in terms of gps coordinates
    df = loc.define_limits()

    ## For each day in the list
    for day in list_of_days_recorded:
        ## File that will contains exiftool commands
        file_exiftool = "file_exiftool_" + day + ".txt"
        ## 1. Find all dashcam videos and create the exiftool command for each video (for gpx files)
        list_of_commands_exiftool(folder,file_fmt,gpx_folder,file_exiftool,pattern=day+'*F')
        ## 2. Execute the created commands in cmd to obtain the gpx files (inside the folder gpx_files)
        execute_commands_exiftool(gpx_folder,file_exiftool)
        ## 3. Clean the redundan data in gpx files
        clean_gpx_files_in_folder(gpx_folder,pattern=day+'*F')
        ## 4. Create the excel report from the cleaned files, where detection of the bus in front of the cameras is carried out
        find_navette(gpx_folder, df, day)


# From a list of recorded days, extract acceleration data and create excel report from them
def create_accelerometers_report_by_day(folder, list_of_days_recorded):
    ## Folder that will contains the txt files
    txt_folder = folder + "txt_files/"

    ## For each day in the list
    for day in list_of_days_recorded:
        ## File that will contains exiftool commands
        file_exiftool = "file_exiftool_" + day + ".txt"
        ## file_fmt required by function "list_of_commands_exiftool" but no used for txt files, then set it as 'none'
        file_fmt = 'none'
        ## 1. Find all dashcam videos and create the exiftool command for each one to create the txt files (for accelerometers)
        list_of_commands_exiftool(folder,file_fmt,txt_folder,file_exiftool,pattern=day+'*F',output_type="txt")
        ## 2. Execute the created commands in cmd to obtain the txt files (inside the folder txt_files, for accelerometers)
        execute_commands_exiftool(txt_folder,file_exiftool)
        ## 3. Make the excel report that contains all gps and acceleretion data
        create_excel_gps_acc(txt_folder,day)
