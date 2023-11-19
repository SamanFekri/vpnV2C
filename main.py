import subprocess
import os
import json
import sys

DATA_PATH = 'config.data.json'
CLIENTS = 'clients'

def command_chisel(client: dict, section: dict) -> str:
    """
    Function to create chisel client command
    :param client: client data
    :param section: section of data for chisel client
    """
    result = ""
    result = section['template'].format(ip=section['ip'], port=section['port'])
    for p in client['protocol']:
        result += f" {client['ip']}:{client['port']}/{p}:{client['ip']}:{client['port']}/{p}"
    return result

def is_screen_exists(name: str) -> bool:
    """
    Function to check if the screen exists
    :param name: name of the screen
    """
    result = subprocess.run(["screen", "-ls"], stdout=subprocess.PIPE)
    return name in result.stdout.decode('utf-8')



if __name__ == '__main__':
    commands = {
        "chisel": command_chisel,
    }
    # Read the arguments from the command line
    # If the argument is force, then kill the screen before create the new one else just create the new one
    is_force = False
    if len(sys.argv) > 1:
        if sys.argv[1].lower == "force":
            is_force = True
    
    # Read the config.data.json file
    with open(DATA_PATH) as json_file:
        data = json.load(json_file)
        # read all the clients 
        for client in data[CLIENTS]:
            print("-------------------------")
            print(f"Client {client['name']} type {client['type']}")
            if client['type'] not in commands:
                print(f"Client {client['name']} type {client['type']} not supported")
                continue
            try: 
                command = commands[client['type']](client, data[client['type']])
            except Exception as e:
                print(f"Error creating command for client {client['name']}")
                print(e)
                continue
            print(f"Command: {command}")
            screen_exists = is_screen_exists(client['screen_name'])
            if screen_exists:
                if is_force:
                    print(f"Killing screen {client['screen_name']}")
                    subprocess.run(["screen", "-X", "-S", client['screen_name'], "quit"])
                else:
                    print(f"Screen {client['screen_name']} already exists")
                    continue
            print(f"Creating screen {client['screen_name']}")
            subprocess.run(["screen", "-dmS", client['screen_name'], "bash", "-c", command])
            print(f"Screen {client['screen_name']} created")