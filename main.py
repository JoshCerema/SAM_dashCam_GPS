import local_functions as lf


folder1 = "G:/SAM/Videos a analizar/files gpx/"
folder2 = "G:/SAM/Videos a analizar/files gpx2/"
folder3 = "G:/SAM/Videos a analizar/For_test/"
file_fmt = "G:/SAM/Notas de las reuniones/gpx_format.txt"
file1 = "20220113_162829_164930_EF.gpx"
file2 = "20220113_164930_NF.gpx"
file2_cleaned = "20220113_164930_NF_cleaned.gpx"



############# For GPX data #############

## 1. List all recorded days available inside the folder
list_of_days_recorded = lf.list_recorder_days(folder3)

## 2. For the days in list, extract the gpx files and use them to report the position of the autonomous vehicle
# The output report is an excel file (one file by day)
lf.create_gps_report_by_day(folder3, file_fmt, list_of_days_recorded)


############# For Accelerometers data #############

## 1. From a list of recorded days, extract acceleration data and create excel report from them
lf.create_accelerometers_report_by_day(folder3, list_of_days_recorded)