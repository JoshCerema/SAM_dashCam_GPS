from datetime import datetime, timedelta, date, time
import numpy as np
import pandas as pd
import cv2 as cv
import glob
import gpxpy
from gpxpy import gpx
from numpy import loadtxt
from openpyxl import load_workbook

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


def find_navette(folder,file,x1,y1,x2,y2,x3,y3,x4,y4):
    ## columns for excel file
    excel_columns = ["GPS Date/Time", "GPS Latitude", "GPS Longitude", "GPS Speed"]
    df = pd.DataFrame(columns=excel_columns)
    row_number = 0

    gpx_file = open(folder+file, 'r')
    # for track in gpx.tracks:
    #     for segment in track.segments:
    #         for point in segment.points:
    #             print('Point at ({0},{1}) -> {2}'.format(point.latitude, point.longitude, point.elevation))
    for waypoint in gpx.waypoints:
        print('waypoint {0} -> ({1},{2})'.format(waypoint.name, waypoint.latitude, waypoint.longitude))


#folder = "D:/SAM/Videos a analizar/files txt/"
#make_excel_gps_acc(folder)
folder = "D:/SAM/Videos a analizar/files gpx/"
file = "20220113_163129_NF.gpx"
x1,y1 = 1.429921560957295,43.55506695489137
x2,y2 = 1.429906208488139,43.55493144671023
x3,y3 = 1.429499460263077,43.55510140183409
x4,y4 = 1.429490370788564,43.55495948841669

find_navette(folder,file,x1,y1,x2,y2,x3,y3,x4,y4)