from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import subprocess
import os
import requests
import json

app = Flask(__name__)
api = Api(app)

lock_file_path = 'lock_file.txt'
scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')

parser = reqparse.RequestParser()
parser.add_argument('location', type=int)

# Replace this with your actual authentication token
AUTH_TOKEN = "AUTH_TOKEN"

class UpdateList(Resource):
    def post(self):
        if "Authorization" not in request.headers:
            return {"message": "Authentication required"}, 401
        if request.headers["Authorization"] != f"Bearer {AUTH_TOKEN}":
            return {"message": "Invalid token"}, 401
        if request.headers["Authorization"] == f"Bearer {AUTH_TOKEN}":
            output_message = runScript()
            print(output_message)
            return output_message
        
def executeScript():
    script_path = "Kroger_v2.py"
    output = ""
    script_path = os.path.join(scripts_dir, 'Kroger_v2.py')
    try:
        try:
            process = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
            output = process.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running {script_path}: {e}")
        return {"message": "Script executed successfully", "output": output}, 200
    except Exception as e:
        return {"message": f"Error executing the script: {str(e)}"}, 500

def runScript():
    if not is_script_running():
        # If the script is not running, acquire the lock and run the script
        acquire_lock()
        result = executeScript()
        release_lock()
        print(result)
        return result
    else:
        return {"message": f"Script already running"}, 500

def is_script_running():
    return os.path.exists(lock_file_path)

def acquire_lock():
    with open(lock_file_path, 'w') as lock_file:
        lock_file.write(str(os.getpid()))

def release_lock():
    os.remove(lock_file_path)

class LocationResource(Resource):
    def post(self):
        if "Authorization" not in request.headers:
            return {"message": "Authentication required"}, 401
        if request.headers["Authorization"] != f"Bearer {AUTH_TOKEN}":
            return {"message": "Invalid token"}, 401
        if request.headers["Authorization"] == f"Bearer {AUTH_TOKEN}":
            try:
                # Parse the 'location' argument from the URL
                args = request.get_json()
                
                new_location = args.get('location', None)
                
                location_data = []
    
                if new_location is not None:
                    # Update the location_id variable with the new location
                    location_data.append(f"Location: {new_location}")
                    with open('variables/variables.json', "w") as json_file:
                        json.dump(location_data, json_file, indent=4)
                    return jsonify({"message": f"Location changed to {new_location} successfully"})
                else:
                    return jsonify({"message": "Invalid location data"})
            except Exception as e:
                return jsonify({"message": str(e)})


api.add_resource(UpdateList, "/updatelist")
api.add_resource(LocationResource, '/location')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=100, debug=True)
