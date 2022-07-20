# TraCI business logic - just one Sumo
# "main"    - used for main simulation
import argparse
import socket
from cads.server import socketlib
import json
import os, shutil


def get_json_file(scenario, name):
    with open('cads/scenarios/' + scenario + '/' + name + '.json') as f:
        data = json.load(f)

    return data


# get the settings from result5.json
parser = argparse.ArgumentParser(description='Run the batched microsim python server.')
parser.add_argument(
    '-c', '--configuration-file', dest='configuration_file', default='result5',
    help='Run CMDA with a specific configuration.')

parser.add_argument(
    '-s', '--scenario', dest='scenario', default='4xi440',
    help='Simulation Folder.')

args = parser.parse_args()
config_file = args.configuration_file
scenario = args.scenario

simulation_settings = json.load(open("batch_settings.json"))
# todo: check where default sign is


def run(settings, name):
    msg = ""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 17778))

            # send simulation_settings
            socketlib.send_data(s, settings)
            print("simulation running")

            simulation_running = 1
            # print()  # add a blankspace

            # receive data
            (msg, remainder) = socketlib.receive_data(s)
            # print(msg, remainder)

            # print(f"Simulation ({id}) End with Result: ", msg)
    except Exception as e:
        print("TRACI Runner Error", e)

    finally:
        if msg == "ok":
            print(f"Simulation {name} Successfully Ran!!!!!")
            return True
        else:
            print(f"Something wrong happened! ({name})")
            return False


def batch():
    batch_size = 30
    src = os.getcwd()
    for tv_compliance in range(25, 100, 25):
        simulation_settings["cars_ratio"]["tvratio"] = f"{tv_compliance}% : {100 - tv_compliance}%"
        simulation_settings["trucks_ratio"]["tvratio"] = f"{tv_compliance}% : {100 - tv_compliance}%"
        for ctv_compliance in range(25, 100, 25):
            simulation_settings["cars_ratio"]["ctvratio"] = f"{ctv_compliance}% : {100-ctv_compliance}%"
            simulation_settings["trucks_ratio"]["ctvratio"] = f"{ctv_compliance}% : {100-ctv_compliance}%"
            for i in range(batch_size):
                identifier = f"{tv_compliance}/{ctv_compliance}-{i+1}"
                print("being run", identifier)
                ok = run(simulation_settings, identifier)
                if not ok:
                    quit()
                result = get_json_file(scenario, config_file)
                with open(f"{src}/results/{identifier}.json", "w") as out:
                    json.dump(result, out)


if __name__ == '__main__':
    batch()
