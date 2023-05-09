from flask import Flask, render_template, json, redirect, request, flash
import os
import main
import json


api = Flask(__name__)
api.config["DEBUG"] = True


@api.route('/', methods=['GET'])
def home():
    return "<h1>API is running.</h1>"

@api.route('/api/data', methods=['GET'])
def api_state_val():
    if 'state' in request.args:
        state= request.args['state']
    else:
        return "Error: No state specified"
    if 'var' in request.args:
        var_code = request.args['var']
    return main.api_request_by_state( var_code = var_code, state = state)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 54546)) 
    
    api.run(port=port, debug=True) 