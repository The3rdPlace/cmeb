import json
import os
import shutil
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests


def rest_error(status_code, url, content):
    print(" - Error " + str(status_code) + " in call to " + url)
    print("  ", end="")
    print(content)
    exit()


def get_data_access_token():
    if os.path.isfile(".token") is False:
        print("No token. Please go to https://eloverblik.dk and add a new token, "
              "then place the content in the file '.token'")
        exit()

    with open('.token', mode='r') as file:
        refresh_token = file.read().strip()

    headers = {'Authorization': 'Bearer ' + refresh_token}
    url = 'https://api.eloverblik.dk/CustomerApi/api/token'
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        rest_error(response.status_code, url, response.content)

    return response.json()["result"]


def backup_data_file(file):
    if os.path.isfile("data/" + file + ".csv"):
        if os.path.exists("data/history") is False:
            os.mkdir("data/history")
        src = "data/" + file + ".csv"
        dst = 'data/history/' + file + "." + str(datetime.timestamp(datetime.now())) + '.csv'
        print("+ Backup existing " + file + ".csv as '" + dst + "'")
        shutil.copy(src, dst)


def fetch_meter_data(access_token, metering_point):
    backup_data_file("Meterdata")

    headers = {'Authorization': 'Bearer ' + access_token,
               'Content-Type': 'application/json',
               'Accept': '*/*'}
    from_date = (datetime.today() - relativedelta(months=3)).strftime('%Y-%m-%d')
    to_date = datetime.today().strftime('%Y-%m-%d')
    url = 'https://api.eloverblik.dk/CustomerApi/api/meterdata/gettimeseries/%s/%s/Hour' % (from_date, to_date)
    metering_point = '{"meteringPoints": {"meteringPoint": ["' + metering_point + '"]}}'

    response = requests.post(url, headers=headers, data=metering_point)
    if response.status_code != 200:
        rest_error(response.status_code, url, response.content)
    with open('data/Meterdata.csv', mode='w') as file:
        print("+ Received meter data for the period %s - %s" % (from_date, to_date))
        file.write(json.dumps(response.json()))


def fetch_metering_points(access_token):
    backup_data_file("MeteringPoints")

    headers = {'Authorization': 'Bearer ' + access_token,
               'Content-Type': 'application/json',
               'Accept': '*/*'}
    url = 'https://api.eloverblik.dk/CustomerApi/api/meteringpoints/meteringpoints'

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        rest_error(response.status_code, url, response.content)
    with open('data/MeteringPoints.csv', mode='w') as file:
        print("+ Received metering points")
        file.write(json.dumps(response.json()))


def fetch_metering_charges(access_token, metering_point):
    backup_data_file("Price")

    headers = {'Authorization': 'Bearer ' + access_token,
               'Content-Type': 'application/json',
               'Accept': '*/*'}
    url = 'https://api.eloverblik.dk/CustomerApi/api/meteringpoints/meteringpoint/getcharges'
    metering_point = '{"meteringPoints": {"meteringPoint": ["' + metering_point + '"]}}'

    response = requests.post(url, headers=headers, data=metering_point)
    if response.status_code != 200:
        rest_error(response.status_code, url, response.content)
    with open('data/Price.csv', mode='w') as file:
        print("+ Received metering charges")
        file.write(json.dumps(response.json()))


def fetch_data(meteringpoint):

    if os.path.isfile(".last") is True:
        with open(".last", mode='r') as file:
            last = file.read()
        last_timestamp = datetime.fromtimestamp(float(last))
        if datetime.now().timestamp() - last_timestamp.timestamp() < (12 * 60 * 60):
            print("+ Using cached data less than 12 hours old")
            return

    if meteringpoint is None:
        if os.path.isfile(".meteringpoint") is True:
            with open('.meteringpoint', mode='r') as file:
                meteringpoint = file.read().strip()
        else:
            print("Meteringpoint is unknown, please lookup your id at https://eloverblik.dk"
                  " and run cmeb again with the '--metering-point' option")
            exit()
    else:
        with open('.meteringpoint', mode='w') as file:
            file.write(meteringpoint)

    if os.path.exists("data") is False:
        os.mkdir("data")
    access_token = get_data_access_token()
    fetch_meter_data(access_token, meteringpoint)
    fetch_metering_points(access_token)
    fetch_metering_charges(access_token, meteringpoint)

    with open(".last", mode='w') as file:
        file.write(str(datetime.timestamp(datetime.now())))
