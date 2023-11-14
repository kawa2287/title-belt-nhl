import json
import csv
from datetime import date,timedelta

# Open the JSON config file
with open('config.json', 'r') as file:
    config = json.load(file)

# Open the CSV schedule file
with open('schedule.csv', 'r') as file:
    csv_reader = csv.reader(file)

    # Convert the CSV data to a list of lists 
    schedule_array = [row for row in csv_reader]

# Remove the header
schedule_array.pop(0)

# Create the current Serial date
base_date = date(1900, 1, 1)
current_date = date.today() 
serial_date = (current_date - base_date).days + 1

# Filter dates 
filtered_dates=[]
for i in schedule_array:
    if int(i[1]) >= int(serial_date):
        filtered_dates.append(i)

def FindMatch(tbh,date):
    nearest_tb_matchup = []
    for i in filtered_dates:
        if (i[2] == tbh or i[3] == tbh) and int(date) < int(i[1]):
            nearest_tb_matchup = i
            break
    return nearest_tb_matchup

def ConvertMatchToString (match):
    return "["+ match[2] + " vs " + match [3] + "]"

def FindNearestPath ( teams,date,pathString ):
    found = False
    newTeams = []
    for tm in teams:
        splits = tm.split(" -> ")
        curMatch = FindMatch(splits[-1],date)
        if curMatch[2] == config["myTeam"] or curMatch[3] == config["myTeam"]:
            found = True
            pathString = tm + " -> " + ConvertMatchToString(curMatch)
            break
        else:
            newTeams.append(tm + " -> " + ConvertMatchToString(curMatch) + " -> " + curMatch[2])
            newTeams.append(tm + " -> " + ConvertMatchToString(curMatch) + " -> " + curMatch[3])

    if found :
        return pathString
    else :
        pathString = FindNearestPath(newTeams,int(curMatch[1]),pathString)
    return pathString

curHolder = config["currentHolder"]
myTeam  = config["myTeam"]
path = FindNearestPath([curHolder],int(serial_date), curHolder)
games = path.split("vs")

print("=========================")
print(f"CURRENT BELT HOLDER: {curHolder}")
print(f"{len(games)-1} GAMES UNTIL `{myTeam}` HAS A SHOT AT THE BELT")
print(path)