from flask import Flask, render_template, json, redirect, request, flash
import os
import main


api = Flask(__name__)
api.config["DEBUG"] = True


@api.route('/', methods=['GET'])
def home():
    return "<h1>API is running. Put list of vars here?</h1>"

@api.route('/api/data', methods=['GET'])
def api_state_val():
    print(request.args)
    if 'state' in request.args:
        state= request.args['state']
    else:
        return "Error: No state specified"
    if 'var' in request.args:
        var = request.args['var']
    return main.api_request_by_state(var, state)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 54546)) 
    
    api.run(port=port, debug=True) 