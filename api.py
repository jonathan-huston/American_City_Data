from flask import Flask, render_template, json, redirect, request, flash
import os
import main


api = Flask(__name__)
api.config["DEBUG"] = True


@api.route('/', methods=['GET'])
def home():
    return "<h1>API is running. Put list of vars here?</h1>"

@api.route('/api', methods=['GET'])
def api_all():
    return main.api_request_by_state("S1701_C03_001E", "01")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 54546)) 
    
    api.run(port=port, debug=True) 