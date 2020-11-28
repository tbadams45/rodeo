from __future__ import print_function
import sys 
import os
import time
import math
from datetime import datetime, timedelta

def is_integer(text):
    try:
        int(text)
        return True
    except ValueError:
        return False

def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        return False

def validate(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

error_message = ""
desired_times = {"00:00", "06:00", "12:00", "18:00"}
desired_sites = {"BNDN5", "ARWN8", "TCCC1", "CARO2", "ESSC2", "NFDC1", "LABW4", "CLNK1", "TRAC2", "NFSW4"}

def validate_forecast(path, target_date, handle):
    global error_message
    error_message = ""
    try:
        if os.path.getsize(path) > 1000000000:
            error_message = "File too large."
            return ""
    except:
        error_message = "Cannot check file size."
        return ""
    try:
        with open(path, "r") as file:
            lines = file.readlines() 
    except:
        error_message = "Cannot open file."
        return ""        
    while len(lines) > 0 and lines[-1].strip() == "":
        lines.pop() 
    if len(lines) == 0:
        error_message = "File is empty."
        return ""
    header = lines[0].strip().split(',')
    if len(header) > 0 and header[0].lower() == "datetime":
        lines = lines[1:]

    output = ""
    testpairs = set()
    for line in lines:
        parts = line.strip().split(',')
        if (len(parts) != 6):
            error_message = f"Each line must contain 6 values, '{line}' does not."
            return ""
          
        if not(is_float(parts[4])):
            error_message = "Cannot convert '" + parts[4] + "' to float."
            return ""
        
        streamflow = float(parts[4])
        if(math.isnan(streamflow)):
            error_message = "Cannot convert '" + parts[4] + "' to float."
            return ""
        
        unit = parts[5]
        if unit != "CFS":
            error_message = "Unknown units '" + unit + "'."
            return ""

        if parts[3] != f"TC+{handle}":
            error_message = "Incorrect vendor ID '" + parts[3] + "'."
            return ""

        site = parts[1]
        if site not in desired_sites:
            error_message = "Unknown site '" + site + "'."
            return ""
        
        datetimestr = parts[0].strip().split('T')
        if (len(datetimestr) != 2):
            error_message = "Cannot convert '" + parts[2] + "' to date and time."
            return ""

        if not(validate(datetimestr[0])):
            error_message = "Cannot convert '" + datetimestr[0] + "' to date."
            return ""
        date = datetime.strptime(datetimestr[0], "%Y-%m-%d")
        
        time = datetimestr[1]
        if len(time) <= 2: time += ":00"
        if time not in desired_times:
            error_message = "Unexpected time '" + time + "'."
            return ""

        if date < target_date or date > target_date + timedelta(days = 10):
            print("  DateTime '" + parts[0] + "' out of forecast range. Ignoring line.")
            continue
            #return ""
        if date == target_date and time != "18:00":    
            print("  DateTime '" + parts[0] + "' before forecast range. Ignoring line.")
            continue
            #return ""
        if date == target_date + timedelta(days = 10) and time == "18:00":    
            print("  DateTime '" + parts[0] + "' after forecast range. Ignoring line.")
            continue
            #return ""

        targetdatetimestr = parts[2].strip().split('T')
        if (len(targetdatetimestr) != 2):
            error_message = "Cannot convert '" + parts[2] + "' to date and time."
            return ""

        if not(validate(targetdatetimestr[0])):
            error_message = "Cannot convert '" + targetdatetimestr[0] + "' to date."
            return ""
        
        if targetdatetimestr[0] != target_date.strftime("%Y-%m-%d"):
            error_message = "Incorrect target date '" + parts[2] + "'."
            return ""

        testpair = f'{date.strftime("%Y-%m-%d")}T{time},{site}'
        if testpair in testpairs:
            error_message = "Multiple occurrence of pair '" + parts[0] + "," + site + "'."
            return ""

        testpairs.add(testpair)
        output += line.strip() + "\n"
    if len(testpairs) != 400:
        error_message = f"Only {len(testpairs)} forecast lines provided."
        return ""
    return output

def main():
    global error_message

    if len(sys.argv) < 4:
        eprint("Usage: python3 validator.py <targe date> <handle> <path to output file>")
        return -1

    target_date = sys.argv[1]
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    handle = sys.argv[2]
    output_file = sys.argv[3]

    validated_text = validate_forecast(output_file, target_date_obj, handle)
    if validated_text != "":
        print(f"OK")
    else:
        print(f"FAILED: {error_message}")
        
    
if __name__ == "__main__":
    main()
    