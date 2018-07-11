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

Date_Input = sys.argv[1]
fromDate = ""
toDate = ""

# If it contains ".."
    # Seperate the two elements and make sure they are valid
    # Initialize as fromDate and toDate
# If it contains "date.."
    # Pull from that date to current date
    # Initialize fromDate
# If it contains "..date"
    # Pull up until given date
    # Initialize toDate
try:
    datetime.strptime(fromDate, '%Y-%m-%d')
except ValueError:
    print("Incorrect data format, try again!")
else:
    # Don't accept if year is before creation of Github
    if int(datetime.strptime(fromDate, '%Y-%m-%d').date().strftime('%Y')) < 2008:
        print("That was before GitHub was created, try again!")
    # Don't accept if date given is in the future
    elif datetime.strptime(fromDate, '%Y-%m-%d').date().strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
        print("That date is in the future, try again!")

try:
    datetime.strptime(toDate, '%Y-%m-%d')
except ValueError:
    print("Incorrect data format, try again!")
else:
    # Don't accept if date is before fromDate
    if datetime.strptime(toDate, '%Y-%m-%d').date().strftime('%Y-%m-%d') < datetime.strptime(fromDate, '%Y-%m-%d').date().strftime('%Y-%m-%d'):
        print("That date is before the start date, try again!")
    # Don't accept if date given is in the future
    elif datetime.strptime(toDate, '%Y-%m-%d').date().strftime('%Y-%m-%d') > datetime.now().strftime('%Y-%m-%d'):
        print("That date is in the future, try again!")

# Format global variable FROM_TO_DATE using fromDate and toDate so that Github API reads it as a span between the dates
FROM_TO_DATE = "{}..{}".format(fromDate, toDate)
# Pulls token from saved env variable "GIT_API_KEY"
try:
    TOKEN = os.environ['GIT_API_KEY']
# If there is no local var saved, allow the user to enter it manually
except KeyError:
    TOKEN = sys.argv[2]


# Is given fromDate,toDate, GitHub page #, and Global TOKEN variable
#Makes a GET request to GitHub and saves to Json file named with page #
def gitToJson(fromToDate, pageNumber, token):
    r = requests.get("https://github.ifit-dev.com/api/v3/search/issues?page="+str(pageNumber) +
                     "&per_page=100&sort=created&order=asc&q=repo:Sparky/SparkyMasterlib+is:issue+created:" + fromToDate, headers={'Authorization': 'token ' + token})
    with open("data"+str(pageNumber)+".json", "w") as json_file:
        json.dump(r.json(), json_file)
        print("Writing " + str(json_file.name))

# Is given a jsonFile(must be first page) and calculates how many pages are required via total issue count


def pageCalc(jsonFile):
    with open(jsonFile) as f:
        jsonObj = json.load(f)
        numPages = math.ceil((jsonObj["total_count"] / 100.0))
        return numPages

# Converts jsonFile to CSV and pulls idNumber+title+startDate+startTime+upDate+upTime+endDate+endTime+label


def jsonToCsv(jsonFile):
    print("Converting " + str(jsonFile) + " -> CSV")
    with open(jsonFile) as f:
        jsonObj = json.load(f)
    csvFileName = 'issues['+FROM_TO_DATE + "].csv"

    # Open CSV File to write data
    with open(csvFileName, "a+") as csvFile:
        # Instantiate csv writer
        writer = csv.writer(csvFile, escapechar="E", quoting=csv.QUOTE_NONE)
        # Create an array of issues
        issues = []
        # Character that seperates data
        seperate = "|"
        # Iterates through all issues in the 'items' of the Json Object
        for issue in jsonObj['items']:
            # Pulls ID Number
            idNumber = str(issue['number']) + seperate
            # Pulls Title
            title = str(issue['title']) + seperate
            # Pulls Start Date and Start Time
            startDate = datetime.strptime(
                issue["created_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
            startTime = datetime.strptime(
                issue["created_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate
            # Pulls Updated Date and Time
            upDate = datetime.strptime(
                issue["updated_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
            upTime = datetime.strptime(
                issue["updated_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate

            # Iterates through each label list. If it finds a bug or enhancement label it breaks, if not it takes the first label
            # Label is initially set to 'None" incase labels[] is empty and the loop is never executed.
            label = "None"
            for i in range(len(issue["labels"])):
                # If label is named "enhancement", save string as "Feature" and move on to next labels array
                if issue["labels"][i]['name'] == "enhancement":
                    label = "Feature"
                    break
                # If label is named "bug", save string as "Bug" and move on to next labels array
                elif issue["labels"][i]['name'] == "bug":
                    label = "Bug"
                    break
                # If "enhancement" and "bug" weren't found, name the string after the first label in the array
                else:
                    label = issue["labels"][0]['name']
            # If the issue hasn't been closed, set the endDate and endTime to "Still" + "Open"
            if(issue["closed_at"] == None):
                endDate = "Still"
                endTime = "Open" + seperate
            # If the issue is closed save endDate and endTime
            else:
                endDate = datetime.strptime(
                    issue["closed_at"], '%Y-%m-%dT%H:%M:%SZ') .date().strftime('%m/%d/%Y')
                endTime = datetime.strptime(
                    issue["closed_at"], '%Y-%m-%dT%H:%M:%SZ') .time().strftime(' %H:%M:%S') + seperate
            # Ignore pull requests
            if('pull_request' not in issue):
                issues.append(idNumber+title+startDate+startTime +
                              upDate+upTime+endDate+endTime+label)
        # Write to CSV file
        for key in issues:
            writer.writerow([key])


# Pull first page from GitHub
gitToJson(FROM_TO_DATE, 1, TOKEN)
# Calculate how many pages necessary from first page
pages = pageCalc("data1.json")
# Pull the rest of the pages and save those JSON files
for index in range(2, pages+1):
    gitToJson(FROM_TO_DATE, index, TOKEN)
# Iterate through all of the json files and write to one csv
for index in range(1, pages+1):
    # Convert data.json to issues.csv
    jsonToCsv("data"+str(index)+".json")

# Ask user if they'd like to delete json files
deleteResponse = input(
    "Finished! Would You Like To Delete Those Pesky Json Files?[Y][N]: ")
if deleteResponse == "Y" or deleteResponse == "y":
    # For loop that goes through each JSON file previously downloaded
    for index in range(1, pages+1):
        # If file exists, delete it
        if os.path.isfile("data"+str(index)+".json"):
            os.remove("data"+str(index)+".json")
            print("Deleted " + "data"+str(index)+".json")
        else:  # Show an error ##
            print("Error: file not found")
    print("Goodbye!")
else:
    print("Suit yourself, goodbye!")
