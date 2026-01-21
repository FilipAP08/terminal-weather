import os
import json
import time
from datetime import datetime, timezone
import subprocess
import sys
import importlib
import argparse

#license info
__author__ = "Filip Piotrowski (FilipAP)"
__license__ = "MIT"
__version__ = "1.0.0"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Terminal Weather
# Copyright (c) 2026 Filip Piotrowski
#
# Licensed under the MIT License.
# See the LICENSE file in the project root for full license information.
#

#############################
### FUNCTIONS DEFINITIONS ###
#############################

#installing dependencies if they're not present
def safe_import(package_name, resource_name=None):
    try:
        #try importing first
        module = importlib.import_module(package_name)
    except ImportError:
        #if there isn't the module, install it
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        #after install we try again
        module = importlib.import_module(package_name)

        #clean-up after pip
        time.sleep(1.5)
        os.system('cls' if os.name == 'nt' else 'clear')

    # if provided a resource name, install it
    if resource_name:
        return getattr(module, resource_name)
    return module

PrettyTable = safe_import("prettytable", "PrettyTable")
requests = safe_import("requests")

#handling backup ability
def save_backup(current_response):
    backup_dir = "backups"

    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    existing_backups = sorted([f for f in os.listdir(backup_dir) if f.endswith(".json")])
    is_duplicate = False

    if existing_backups:
        last_backup_path = os.path.join(backup_dir, existing_backups[-1])
        try:
            with open(last_backup_path, 'r', encoding='utf-8') as f:
                last_backup_data = json.load(f)

            if last_backup_data.get("hourly") == current_response.get("hourly"):
                is_duplicate = True
        except (json.JSONDecodeError, IOError):
            pass

    if not is_duplicate:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"forecast_{timestamp}.json"
        # Removing 'indent' and using 'separators' to strip all whitespace
        with open(os.path.join(backup_dir, filename), 'w', encoding='utf-8') as f:
            json.dump(current_response, f, separators=(',', ':'))
        print(f"Backup saved: {filename}")
    else:
        if dataDownloaded == True:
            print("Data unchanged. Skipping creating backup.")

#################
### MAIN CODE ###
#################

#adding support for arguments
parser = argparse.ArgumentParser()
parser.add_argument("-o","--offline", action="store_true", help="Use cached data instead of calling the API")
parser.add_argument(
    "-c", "--config", 
    type=str, 
    default="config.json", 
    help="Path to the configuration JSON file (default: config.json)"
)

args = parser.parse_args()

#load settings from config.json
config_path = args.config
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Error: Configuration file '{config_path}' not found.")
    exit(1)

with open("tz.txt", "r") as tzs:
    isTzReal = False
    for line in tzs:
        if config["extras"]["timezone"] in line:
            isTzReal = True

if isTzReal == False:
    print("Timezone not found or incorrect in config.json")
    time.sleep(2)
    exit(1)

options = config["options_hourly"]
chosen = ""
for option in options:
    if str(options[option]) == "1":
        chosen = chosen + str(option)+","


#add extras, if they exist
extras = config["extras"]
end = ""
for extra in extras:
    if extra == "timezone":
        extras[extra] = extras[extra].replace("/", "%2F")
    end += f"&{str(extra)}={str(extras[extra])}"


#flag data as not downloaded, if in offline mode
if args.offline:
    dataDownloaded = False

#create url and download, if offline mode not forced
else:
    chosen = chosen.strip(",")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={config['latitude']}&longitude={config['longitude']}&hourly={chosen}&models={config['models']}&timeformat=unixtime{end}"
    print(f"Connecting and downloading from: {url}")

    #try connecting and downloading, and inform if and what went wrong
    try:
        #try downloading and opening data
        re = requests.get(url, timeout=config["timeout"])
        re.raise_for_status()
        response = re.json()

    #check and print what went wrong
    except requests.exceptions.RequestException as e:
        #asking server what went wrong
        print(f"Connection error: {e}")
        dataDownloaded = False
        try:
            error_info = re.json()
            reason = error_info.get('reason', '')

            # Human-readable filter for invalid parameters
            if "invalid String value" in reason:
                # Extracts the specific bad variable name from the server's technobabble
                bad_value = reason.split("invalid String value ")[-1].replace(".", "")
                print(f"\n[!] CONFIG ERROR: The parameter '{bad_value}' is not recognized by the API.")
                print("Please check your spelling in config.json or refer to the Open-Meteo documentation.")
            else:
                #if provided, print server response
                print(f"Server response: {reason}")
        except:
            pass

    #if nothing went wrong flag data as downloaded
    else:
        dataDownloaded = True

print()

#if data not downloaded, try opening last backup
if not dataDownloaded:
    if args.offline:
        print("Attempting to load last backup...")
    else:
        print("Network error or API down. Attempting to load last backup...")
    
    backup_dir = "backups"
    if os.path.exists(backup_dir):
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith(".json")])
        if backups:
            last_backup = os.path.join(backup_dir, backups[-1])
            with open(last_backup, 'r', encoding='utf-8') as f:
                response = json.load(f)
            print(f"OFFLINE MODE: Displaying data from {backups[-1]}")
            plch = response["hourly"]
        else:
            print("No backups available.")
            exit(1)
    else:
        print("Backup directory not found. Exit.")
        exit(1)

#try opening the forecast data
try:
    plch = response["hourly"]
except KeyError:
    print("No hourly data, try checking spelling and names in config.json")
    exit(1)

#save backup
save_backup(response)

#turn unixtime into human-readable time string
t = plch["time"]
dates = []

offset = response.get("utc_offset_seconds", 0)
for time in t:
    local_time = int(time) + offset
    dt_aware = datetime.fromtimestamp(local_time, timezone.utc)
    dates.append(dt_aware.replace(tzinfo=None))

#start creating table column by column
table = PrettyTable()
table.add_column("datetime", dates)

for type in plch:
    if type != "time":
        table.add_column(f"{type} [{response['hourly_units'][type]}]", plch[type])

#display table
table.align = "r"
precision = config.get("decimal_places_in_the_table", 2)
table.float_format = f".{precision}"

print()

try:
    print(f"Forecast for latitude: {round(response['latitude'],3)} and longitude: {round(response['longitude'],3)}, time zone: {response['timezone']}:")
except KeyError:
    print(f"Forecast for latitude: {round(response['latitude'],3)} and longitude: {round(response['longitude'],3)}:")
print(table)

input("\nPress enter to continue...")



exit()
