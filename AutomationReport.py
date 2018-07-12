# Takes a JSON file and pulls data about issues
# Reports it in a CSV file to be imported to Excel/Google Sheets

import sys
import os
import pprint
import json
import requests
import math
import csv
from datetime import datetime
from collections import defaultdict, Counter, OrderedDict

DATE_INPUT = sys.argv[1]
twoDatesGiven = False
CSV_HEADER = "Number|Title|Start|End|Type"

if ".." in DATE_INPUT:
    split = DATE_INPUT.split("..")
    fromDate = split[0]
    toDate = split[1]
    twoDatesGiven = True
elif "<=" in DATE_INPUT:
    singleDate = DATE_INPUT.replace("<=", "")
elif ">=" in DATE_INPUT:
    singleDate = DATE_INPUT.replace(">=", "")
else:
    print("Must include [..][<=] or [>=]")
    quit()

try:
    if twoDatesGiven:
        datetime.strptime(fromDate, '%Y-%m-%d')
        datetime.strptime(toDate, '%Y-%m-%d')
    else:
        datetime.strptime(singleDate, '%Y-%m-%d')
except ValueError:
    print("Incorrect data format, try again!")
    quit()

try:
    TOKEN = os.environ['GIT_API_KEY']
except KeyError:
    try:
        TOKEN = sys.argv[2]
    except IndexError:
        print("Could not find local env variable and no token was given. Try again!")
        quit()



def gitToJson(fromToDate, pageNumber, token):
    r = requests.get("https://github.ifit-dev.com/api/v3/search/issues?page="+str(pageNumber) +
                     "&per_page=100&sort=created&order=asc&q=repo:Sparky/SparkyMasterlib+is:issue+created:" + fromToDate, headers={'Authorization': 'token ' + token})
    with open("data"+str(pageNumber)+".json", "w") as json_file:
        json.dump(r.json(), json_file)
        print("Writing " + str(json_file.name))


def pageCalc(jsonFile):
    with open(jsonFile) as f:
        jsonObj = json.load(f)
        numPages = math.ceil((jsonObj["total_count"] / 100.0))
        return int(numPages)


def jsonToCsv(jsonFile):
    print("Converting " + str(jsonFile) + " -> CSV")
    with open(jsonFile) as f:
        jsonObj = json.load(f)
    csvFileName = 'issues['+DATE_INPUT + "].csv"

    with open(csvFileName, "a+") as csvFile:
        writer = csv.writer(csvFile, escapechar=",", quoting=csv.QUOTE_NONE)
        issues = []
        # Character that seperates data
        seperate = "|"
        for issue in jsonObj['items']:
            idNumber = str(issue['number']) + seperate
            title = str(issue['title']) + seperate
            startDate = datetime.strptime(
                issue["created_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
            startTime = datetime.strptime(
                issue["created_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate
            upDate = datetime.strptime(
                issue["updated_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
            upTime = datetime.strptime(
                issue["updated_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate

            # Label is initially set to 'None" incase labels[] is empty and the loop is never executed.
            label = "None"
            for i in range(len(issue["labels"])):
                if issue["labels"][i]['name'] == "enhancement":
                    label = "Feature"
                    break
                elif issue["labels"][i]['name'] == "bug":
                    label = "Bug"
                    break
                # If "enhancement" and "bug" weren't found, name the string after the first label in the array
                else:
                    label = issue["labels"][0]['name']
            if(issue["closed_at"] == None):
                endDate = "Still"
                endTime = "Open" + seperate
            else:
                endDate = datetime.strptime(
                    issue["closed_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
                endTime = datetime.strptime(
                    issue["closed_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate
            # Ignore pull requests
            if('pull_request' not in issue):
                issues.append(idNumber+title+startDate+startTime +
                              upDate+upTime+endDate+endTime+label)
        # If the CSV file is empty, write a header
        if os.stat(csvFileName).st_size == 0:
            writer.writerow([CSV_HEADER])
        for key in issues:
            writer.writerow([key])


gitToJson(DATE_INPUT, 1, TOKEN)
pages = pageCalc("data1.json")
for index in range(2, pages+1):
    gitToJson(DATE_INPUT, index, TOKEN)
for index in range(1, pages+1):
    jsonToCsv("data"+str(index)+".json")

for index in range(1, pages+1):
    if os.path.isfile("data"+str(index)+".json"):
        os.remove("data"+str(index)+".json")
        print("Deleted " + "data"+str(index)+".json")
    else:  # Show an error ##
        print("Error: file not found")
print("Goodbye!")
