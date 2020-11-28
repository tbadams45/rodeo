from __future__ import print_function
import sys 
import os
import math
from datetime import datetime, timedelta

EPS = 0.01

PERIOD_LENGTH = 40

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

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

score_error_message = ""
correct = False

desired_times = {"00:00", "06:00", "12:00", "18:00"}

def calculate_score(truth_file, solution_file, target_dates, mode = "verbose"):
    """Returns the average of NSE over all locations and target dates
    """
    global score_error_message
    global correct
    correct = False
    score_error_message = ""
    solution_lines = []
    truth_lines = []
    
    try:
        file = open(solution_file, "r")
        solution_lines = file.readlines()
        file.close() 
    except IOError:
        score_error_message = "Can't open solution file '" + solution_file + "'."
        eprint(score_error_message)
        return -1 
    
    try:
        file = open(truth_file, "r")
        truth_lines = file.readlines()
        file.close() 
    except IOError:
        score_error_message = "Can't open truth file '" + truth_file + "'."
        eprint(score_error_message) 
        return -1
    
    if len(solution_lines) == 0:
        score_error_message = "Solution file '" + solution_file + "' is empty."
        eprint(score_error_message) 
        return -1 

    if len(truth_lines) == 0:
        score_error_message = "Truth file '" + truth_file + "' is empty."
        eprint(score_error_message) 
        return -1 
    
    while len(solution_lines) > 0 and solution_lines[-1].strip() == "":
        solution_lines.pop() 

    while len(truth_lines) > 0 and truth_lines[-1].strip() == "":
        truth_lines.pop() 

    solution_header = solution_lines[0].strip().split(',')
    if len(solution_header) > 0 and solution_header[0] == "DateTime":
        solution_lines = solution_lines[1:]
    
    truth_header = truth_lines[0].strip().split(',')
    if len(truth_header) > 0 and truth_header[0] == "DateTime":
        truth_lines = truth_lines[1:]
    
    # Dictionary with truth data
    truth = {}
    for line in truth_lines:
        parts = line.strip().split(',')
        if (len(parts) != 4):
            score_error_message = "Truth file: Each line must contain 4 values."
            eprint(score_error_message) 
            return -1
          
        if parts[2] == 'Ice': continue
        if parts[2] == '': continue

        if not(is_float(parts[2])):
            score_error_message = "Truth file: Cannot convert '" + parts[2] + "' to float."
            eprint(score_error_message) 
            return -1
        
        streamflow = float(parts[2])
        if(math.isnan(streamflow)):
            score_error_message = "Truth file: Cannot convert '" + parts[2] + "' to float."
            eprint(score_error_message) 
            return -1
        
        site = parts[1]
        datetimestr = parts[0].strip().split('T')
        if (len(datetimestr) != 2):
            score_error_message = "Truth file: Cannot convert '" + parts[0] + "' to date and time."
            eprint(score_error_message) 
            return -1

        if not(validate(datetimestr[0])):
            score_error_message = "Truth file: Cannot convert '" + datetimestr[0] + "' to date."
            eprint(score_error_message) 
            return -1
        date = datetime.strptime(datetimestr[0], "%Y-%m-%d")
        
        time = datetimestr[1]
        if len(time) <= 2: time += ":00"
        if time not in desired_times:
            score_error_message = "Truth file: Unexpected time '" + time + "'."
            eprint(score_error_message) 
            return -1

        if site not in truth: truth[site] = {}
        if date not in truth[site]: truth[site][date] = {}
        if time in truth[site][date]:
            score_error_message = "Truth file: Multiple occurrence of '" + site + "," + parts[1] + "'."
            eprint(score_error_message) 
            return -1

        truth[site][date][time] = streamflow

    # Dictionary with solution data
    solution = {}
    for line in solution_lines:
        parts = line.strip().split(',')
        if (len(parts) != 6):
            score_error_message = "Solution file: Each line must contain 6 values."
            eprint(score_error_message) 
            return -1
          
        if not(is_float(parts[4])):
            score_error_message = "Solution file: Cannot convert '" + parts[4] + "' to float."
            eprint(score_error_message) 
            return -1
        
        streamflow = float(parts[4])
        if(math.isnan(streamflow)):
            score_error_message = "Solution file: Cannot convert '" + parts[4] + "' to float."
            eprint(score_error_message) 
            return -1
        
        site = parts[1]
        datetimestr = parts[0].strip().split('T')
        if (len(datetimestr) != 2):
            score_error_message = "Solution file: Cannot convert '" + parts[2] + "' to date and time."
            eprint(score_error_message) 
            return -1

        if not(validate(datetimestr[0])):
            score_error_message = "Solution file: Cannot convert '" + datetimestr[0] + "' to date."
            eprint(score_error_message) 
            return -1
        date = datetime.strptime(datetimestr[0], "%Y-%m-%d")
        
        time = datetimestr[1]
        if len(time) <= 2: time += ":00"
        if time not in desired_times:
            score_error_message = "Solution file: Unexpected time '" + time + "'."
            eprint(score_error_message) 
            return -1

        targetdatetimestr = parts[2].strip().split('T')
        if (len(targetdatetimestr) != 2):
            score_error_message = "Solution file: Cannot convert '" + parts[2] + "' to date and time."
            eprint(score_error_message) 
            return -1

        if not(validate(targetdatetimestr[0])):
            score_error_message = "Solution file: Cannot convert '" + targetdatetimestr[0] + "' to date."
            eprint(score_error_message) 
            return -1
        targetdate = datetime.strptime(targetdatetimestr[0], "%Y-%m-%d")
        
        #if date not in dates:
        #    continue
        if site not in truth:
            continue
        if date not in truth[site]: 
            continue
        if time not in truth[site][date]: 
            continue
        
        if targetdate not in solution: solution[targetdate] = {}
        if site not in solution[targetdate]: solution[targetdate][site] = {}
        if date not in solution[targetdate][site]: solution[targetdate][site][date] = {}
        if time in solution[targetdate][site][date]:
            score_error_message = "Solution file: Multiple occurrence of '" + site + "," + parts[0] + "' for target date " + parts[2] + "."
            eprint(score_error_message) 
            return -1

        solution[targetdate][site][date][time] = streamflow

    overallscore = 0
    overallgood = {"1_10" : 0, "6_10" : 0}
    overallcount = 0
    overallmissingcount = 0
    for target_date in target_dates:
        if target_date not in solution:
            score_error_message = "Solution file: Forecast for target date " + target_date.strftime("%Y-%m-%d") + " not provided."
            eprint(score_error_message) 
            return -1
        score = {}
        NRNSE_W_Avg = 0
        count = 0
        missingcount = 0
        for site, truthdata in truth.items():
            score[site] = {
                "NSE_W": 0,
                "NRNSE_W": 0,
                "1_10": {"sum": 0, "count": 0, "mean": 0, "nominator": 0, "denominator": 0, "NSE": 0, "RNSE": 0, "NRNSE": 0},
                "6_10": {"sum": 0, "count": 0, "mean": 0, "nominator": 0, "denominator": 0, "NSE": 0, "RNSE": 0, "NRNSE": 0}
            }
            for date, datedata in truthdata.items():
                if (date - target_date).days < 0 or (date - target_date).days > 10: continue
                for time, streamflow in datedata.items():
                    if (date - target_date).days == 10 and time == "18:00": continue
                    if (date - target_date).days == 0 and time != "18:00": continue
                    both = False if (date - target_date).days <= 4 or ((date - target_date).days == 5 and time != "18:00") else True
                    score[site]["1_10"]["sum"] += streamflow
                    score[site]["1_10"]["count"] += 1
                    if both:
                        score[site]["6_10"]["sum"] += streamflow
                        score[site]["6_10"]["count"] += 1
                    if site in solution[target_date] and date in solution[target_date][site] and time in solution[target_date][site][date]:
                        score[site]["1_10"]["nominator"] += (solution[target_date][site][date][time] - streamflow) ** 2
                        if both:
                            score[site]["6_10"]["nominator"] += (solution[target_date][site][date][time] - streamflow) ** 2
                    else:
                        score_error_message = "Solution file: Forecast for '" + site + "," + date.strftime("%Y-%m-%d") + " " + time + "' for target date " + target_date.strftime("%Y-%m-%d") + " not provided."
                        eprint(score_error_message) 
                        return -1
            for part in ["1_10", "6_10"]:
                if score[site][part]["count"] > 0:
                    score[site][part]["mean"] = score[site][part]["sum"] / score[site][part]["count"]
            for date, datedata in truthdata.items():
                if (date - target_date).days < 0 or (date - target_date).days > 10: continue
                for time, streamflow in datedata.items():
                    if (date - target_date).days == 10 and time == "18:00": continue
                    if (date - target_date).days == 0 and time != "18:00": continue
                    both = False if (date - target_date).days <= 4 or ((date - target_date).days == 5 and time != "18:00") else True
                    score[site]["1_10"]["denominator"] += (streamflow - score[site]["1_10"]["mean"]) ** 2
                    if both: score[site]["6_10"]["denominator"] += (streamflow - score[site]["6_10"]["mean"]) ** 2
            for part in ["1_10", "6_10"]:
                if score[site][part]["count"] > 0:
                    score[site][part]["RNSE"] = 1 - score[site][part]["nominator"] / max(score[site][part]["denominator"], score[site][part]["count"] * EPS)
                    score[site][part]["NRNSE"] = 1 / (2 - score[site][part]["RNSE"])
                    #if score[site][part]["denominator"] > 0:
                    #    score[site][part]["NSE"] = 1 - score[site][part]["nominator"] / score[site][part]["denominator"]
                    #else:
                    #    score[site][part]["NSE"] = 1 if score[site][part]["nominator"] == 0 else 0
            #score[site]["NSE_W"] = (score[site]["1_10"]["NSE"] + score[site]["6_10"]["NSE"]) / 2
            score[site]["NRNSE_W"] = (score[site]["1_10"]["NRNSE"] + score[site]["6_10"]["NRNSE"]) / 2
            if mode == "verbose":
                eprint(target_date.strftime("%Y-%m-%d"), site, ": ", score[site]["NRNSE_W"], "(", score[site]["1_10"]["NRNSE"], ", ", score[site]["6_10"]["NRNSE"], ")")
            if score[site]["1_10"]["count"] > 8*PERIOD_LENGTH/10:
                NRNSE_W_Avg += score[site]["NRNSE_W"]
                overallscore += score[site]["NRNSE_W"]
                for part in ["1_10", "6_10"]:
                    if score[site][part]["NRNSE"] > 0.5:
                        overallgood[part] += 1
                count += 1
                overallcount += 1
            else:
                missingcount += 1
                overallmissingcount += 1
        if count > 0:
            NRNSE_W_Avg /= count
    if overallcount > 0:
        overallscore /= overallcount
        if mode == "verbose":
            eprint(overallmissingcount, "(location, date) pairs where skipped due to incomplete data.")
            eprint("NSNSE_1_10 > 0.5: ", overallgood["1_10"], "/", overallcount)
            eprint("NSNSE_6_10 > 0.5: ", overallgood["6_10"], "/", overallcount)
        correct = True
        return overallscore
    else:
        score_error_message = "No ground truth data for any target date."
        eprint(score_error_message) 
        return -1

def main():
    if len(sys.argv) < 4:
        eprint("Usage: python3 scorer.py <target dates> <path to ground truth file> <path to solution file>")
        return -1
    truth_file = sys.argv[2]
    solution_file = sys.argv[3] 
    target_date_str = sys.argv[1]
    target_dates_parts = target_date_str.split(',')
    target_dates = []
    for target_date in target_dates_parts:
        if not validate(target_date):
            eprint("Incorrect target date '" + str(target_date) + "'!")
            return -1
        target_dates.append(datetime.strptime(target_date, "%Y-%m-%d"))

    NRNSE_W_Avg = calculate_score(truth_file, solution_file, target_dates,  "non-verbose")

    if correct:
        #score = 100 / (2 - NSE_W_Avg)
        score = 100 * NRNSE_W_Avg
    else:
        score = -1
    print(score)
if __name__ == "__main__":
    main()
    