#!python3
import json
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import time
import sys
from datetime import datetime
import signalfx
import irsdk
import argparse
import requests
import eel

# Syntax:
# python3 iracing_send.py -name <YOUR_NAME_HERE> -token <YOUR_TOKEN_HERE> -i <YOUR_SPLUNK_ENTERPRISE_IP_HERE> -e <YOUR_SPLUNK_ENTERPRISE_HEC_TOKEN_HERE>
#
#parser = argparse.ArgumentParser(description="DataDrivers - iRacing Metric Sender")
#parser.add_argument("-n", "--name", help="Your iRacing Racer Name", required=True)
#parser.add_argument("-t", "--token", help="Splunk SIM Ingest Token", required=True)
#parser.add_argument("-i", "--ip", help="Splunk Enterprise IP Address", required=True)
#parser.add_argument("-e", "--enterprisetoken", help="Splunk Enterprise HEC Token", required=True)
#args = vars(parser.parse_args())

#################################
# Don't touch anything below this#
#################################

# SIM variables
client = signalfx.SignalFx(ingest_endpoint="https://ingest.datadrivers.racing")

global ingest
global driver_team
global driver_name


eel.init('app_contents/')
@eel.expose
def set_racing_parameters(driver_name_cs, driver_team_cs, token):
    driver_name = driver_name_cs
    driver_team = driver_team_cs
    ingest = client.ingest(token)
    print("Set Driver name to: " + str(driver_name))
    print("Set Driver team to: " + str(driver_team))
    print("Set token to: " + str(token))



# Uncomment the following line to enable debug logging
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# create dict for values of txt from github pyirsdk repo
# dictionary for metrics data

metrics_dict = {
    "AirDensity": "",
    "AirPressure": "",
    "AirTemp": "",
    "BrakeRaw": "",
    "EngineWarnings": "",
    "FastRepairAvailable": "",
    "FastRepairUsed": "",
    "FogLevel": "",
    "FrameRate": "",
    "FuelLevel": "",
    "FuelLevelPct": "",
    "FuelUsePerHour": "",
    "Gear": "",
    "Lap": "",
    "LapBestLap": "",
    "LapBestLapTime": "",
    "LapCompleted": "",
    "LapCurrentLapTime": "",
    "LapDeltaToBestLap_DD": "",
    "LapDeltaToBestLap": "",
    "LapDeltaToOptimalLap_DD": "",
    "LapDeltaToOptimalLap": "",
    "LapDeltaToSessionBestLap_DD": "",
    "LapDeltaToSessionBestLap": "",
    "LapDeltaToSessionLastlLap_DD": "",
    "LapDeltaToSessionLastlLap": "",
    "LapDeltaToSessionOptimalLap_DD": "",
    "LapDeltaToSessionOptimalLap": "",
    "LapDist": "",
    "LapDistPct": "",
    "LapLasNLapSeq": "",
    "LapLastLapTime": "",
    "LapLastNLapTime": "",
    "LFtempCL": "",
    "LFtempCM": "",
    "LFtempCR": "",
    "LFwearL": "",
    "LFwearM": "",
    "LFwearR": "",
    "LRtempCL": "",
    "LRtempCM": "",
    "LRtempCR": "",
    "LRwearL": "",
    "LRwearM": "",
    "LRwearR": "",
    "OilLevel": "",
    "OilPress": "",
    "OilTemp": "",
    "PlayerCarClassPosition": "",
    "PlayerCarDriverIncidentCount": "",
    "PlayerCarIdx": "",
    "PlayerCarMyIncidentCount": "",
    "PlayerCarPosition": "",
    "PlayerCarTeamIncidentCount": "",
    "PlayerCarTowTime": "",
    "PlayerTireCompound": "",
    "PlayerTrackSurface": "",
    "PlayerTrackSurfaceMaterial": "",
    "RaceLaps": "",
    "RelativeHumidity": "",
    "RFtempCL": "",
    "RFtempCM": "",
    "RFtempCR": "",
    "RFwearL": "",
    "RFwearM": "",
    "RFwearR": "",
    "Roll": "",
    "RollRate": "",
    "RPM": "",
    "RRtempCL": "",
    "RRtempCM": "",
    "RRtempCR": "",
    "RRwearL": "",
    "RRwearM": "",
    "RRwearR": "",
    "SessionFlags": "",
    "SessionLapsRemain": "",
    "SessionNum": "",
    "SessionState": "",
    "SessionTime": "",
    "SessionTimeRemain": "",
    "SessionUniqueID": "",
    "ShiftGrindRPM": "",
    "ShiftIndicatorPct": "",
    "ShiftPowerPct": "",
    "Skies": "",
    "Speed": "",
    "SteeringWheelAngle": "",
    "SteeringWheelAngleMax": "",
    "SteeringWheelPctDamper": "",
    "SteeringWheelPctTorque": "",
    "SteeringWheelPctTorqueSign": "",
    "SteeringWheelPctTorqueSignStops": "",
    "SteeringWheelPeakForceNm": "",
    "SteeringWheelTorque": "",
    "ThrottleRaw": "",
    "TireSetsAvailable": "",
    "TireSetsUsed": "",
    "TrackTemp": "",
    "TrackTempCrew": "",
    "WeatherType": "",
    "WindDir": "",
    "WindVel": "",
}
# dictionary for bool data
bool_dict = {
    "IsInGarage": "",
    "IsOnTrack": "",
    "IsOnTrackCar": "",
    "OnPitRoad": "",
    "PitstopActive": "",
    "PlayerCarInPitStall": "",
}

# this is our State class, with some helpful variables
class State:
    ir_connected = False
    last_car_setup_tick = -1


# Class used to track lap completions
class Counter:
    def __init__(self, count=1):
        self._count = count

    def get_count(self):
        return self._count

    def set_count(self, x):
        self._count = x

    count = property(get_count, set_count)


# here we check if we are connected to iracing
# so we can retrieve some data
def check_iracing():
    if state.ir_connected and not (ir.is_initialized and ir.is_connected):
        state.ir_connected = False
        # don't forget to reset your State variables
        state.last_car_setup_tick = -1
        # we are shutting down ir library (clearing all internal variables)
        ir.shutdown()
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " irsdk disconnected")
    elif (
        not state.ir_connected
        and ir.startup()
        and ir.is_initialized
        and ir.is_connected
    ):
        state.ir_connected = True
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " irsdk connected")


# Get current lap
def get_lap():
    return ir["Lap"]


# Sends event to SIM when lap is completed
def send_lap_event(counter):
    current_lap = int(get_lap())
    i = counter.count
    if current_lap == i:
        counter.count = current_lap + 1
        print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " new lap")
        ingest.send_event(
            event_type="Lap Complete",
            category="USER_DEFINED",
            dimensions={
                "driver": driver_name,
                "lap": str(metrics_dict["Lap"]),
                "LapTime": str(metrics_dict["LapCurrentLapTime"]),
                "LapDistance": str(metrics_dict["LapDist"]),
            },
            properties={"session_id": str(metrics_dict["SessionUniqueID"])},
            timestamp=time.time() * 1000,
        )


# Sends metrics to SIM
def send_metric(ir_json):
    for key, value in ir_json.items():
        ingest.send(
            gauges=[
                {
                    "metric": "iracing." + key,
                    "value": value,
                    "timestamp": time.time() * 1000,
                    "dimensions": {
                        "driver": driver_name,
                        "lap": str(ir_json["Lap"]),
                        "session_id": str(ir_json["SessionUniqueID"]),
                    },
                }
            ]
        )

# function to send payload to splunk enterprise env
def send_hec(ir_json):
    ir_json['ts_send'] = str(datetime.utcnow())
    event={}
    event['host'] = driver_name
    event['source'] = "iracing"
    event['event'] = ir_json
    url = str("http://" + splunk_hec_ip + ":" + splunk_hec_port + "/services/collector")
    header = {'Authorization' : '{}'.format('Splunk ' + splunk_hec_token)}
    try:
        response = requests.post(
            url=url,
            data=json.dumps(event),
            headers=header)
        response.raise_for_status()

    except requests.exceptions.HTTPError as err:
        print(err)


def loop(json_dict):
    for key, value in json_dict.items():
        value = ir[key]
        json_dict.update({key: value})

    #send_lap_event(lapCounter)
    #send_hec(json_dict)
    #send_metric(json_dict)


if __name__ == "__main__":
    # initializing ir and state
    ir = irsdk.IRSDK()
    state = State()
    print(datetime.now().strftime("%m/%d/%Y %H:%M:%S") + " iRacing started")

    eel.start('static/datadrivers.html', mode='default',
                                     port=8025, block=False)
    # instantiate lap counter for sending lap completion events
    lapCounter = Counter()
    ir.startup()

    # Update lap counter if iRacing is already running
    if ir.is_connected:
        lapCounter.count = ir["Lap"] + 1

    try:
        # infinite loop
        while True:
            # check if we are connected to iracing
            check_iracing()
            # if we are, then process data
            if state.ir_connected:
                loop(metrics_dict)
            # sleep for 0.3 second
            # maximum you can use is 1/60
            # cause iracing updates data with 60 fps
            print(
                datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                + " successfully looped through the script."
            )
            time.sleep(0.3)
    except KeyboardInterrupt:
        # press ctrl+c to exit
        pass
