from dotenv import load_dotenv
import os
from os.path import join, dirname
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import speedtest
import json
from ping3 import ping
import time

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

INFLUXDB_ADDRESS_WITH_PORT = os.environ.get("INFLUXDB_ADDRESS_WITH_PORT")
INFLUXDB_TOKEN = os.environ.get("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.environ.get("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.environ.get("INFLUXDB_BUCKET")
INTERVAL = int(os.environ.get("INTERVAL"))

dictionary = {}

def speed():
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    print(json.dumps(test.results.dict(), indent=4, sort_keys=True))
    dictionary['download'] = test.results.dict()['download']/1000000
    dictionary['upload'] = test.results.dict()['upload']/1000000
    dictionary['speedtest_ping'] = test.results.dict()['ping']



def pinger():
    ping_result_google_array = []
    ping_result_cloudflare_array = []
    for _ in range(1, 10):
        ping_result_google = ping('8.8.8.8')
        if ping_result_google is not None:
            ping_result_google_array.append(ping_result_google)
        ping_result_cloudflare = ping('1.1.1.1')
        if ping_result_cloudflare is not None:
            ping_result_cloudflare_array.append(ping_result_cloudflare)
    avg_google = sum(ping_result_google_array)/len(ping_result_google_array)
    avg_cloudflare = sum(ping_result_cloudflare_array)/len(ping_result_cloudflare_array)
    dictionary['google_ping'] = avg_google*1000
    dictionary['cloudflare_ping'] = avg_cloudflare*1000
    print(f'Google: {dictionary["google_ping"]} ms | Cloudflare: {dictionary["cloudflare_ping"]} ms')


# for debugging
# print(dictionary)
def writeData():
    with InfluxDBClient(url=str(INFLUXDB_ADDRESS_WITH_PORT), token=INFLUXDB_TOKEN, org=INFLUXDB_ORG) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        data = {'measurement':"speedtest",'fields':dictionary,"host":"speedtest"}
        write_api.write(INFLUXDB_BUCKET, INFLUXDB_ORG, data)

if __name__ == "__main__":
    while True:
        speed()
        pinger()
        writeData()
        print(f'{datetime.now()} | {dictionary}',flush=True)
        dictionary.clear()
        print('------------------------------------',flush=True)
        time.sleep(INTERVAL)