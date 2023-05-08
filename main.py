#! python3
import requests
import configparser
import json

# retrive api key from credentials.cfg
cfg = configparser.ConfigParser()
cfg.read('credentials.cfg')
api_key = cfg.get('KEYS', 'census_api_key', raw='')

# For now, data is limited to the 2021 American Community survey
host = 'https://api.census.gov/data'
year = '2021'
dataset = 'acs/acs1'
get = 'subject?get=NAME'
geography = 'combined%20statistical%20area'


def build_metro_area_json():
    '''Builds a json containing metro area codes.'''
    request_str = build_query('S0101_C01_001E', '*')
    response_json = submit_query(request_str)
    metro_area_dict = {}
    for item in response_json[1:]:
        metro_area = item[0].split(',')[0]
        area_id = item[-1]
        state = item[0].split(',')[1].split(' ')[1]
        metro_area_dict[metro_area] = {'state': state, 'id':area_id}
    with open("metro_area_codes.json", "w") as f:
        json.dump(metro_area_dict, f)

def build_variable_json():
    ''''Build a json containing selected variables'''
    acs_var_dict = {
        'S1701_C03_001E': 'Percent of population below poverty level',
        'S2301_C04_001E': 'Unemployment rate (16 years and older)',
        'S1902_C03_001E': 'Mean household income',
        'S0102_C01_037E': 'Percent of population with bachelor\'s degree (25 years and older)'
    }
    with open("variable_codes.json", "w" ) as f:
        json.dump(acs_var_dict, f)



def load_metro_area_json(json_file):
    '''Loads a json file containing metro area names and locations and convers it to a dictionary'''
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data

def load_variable_json(json_file):
    '''Loads a json file containing ACS variable codes and convert it to a dictionary'''
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def get_user_input_metro_area(metro_area_dict):
    '''Return value for metro area code to be used in request, given a text input.
    Value is a 3 digit number.'''
    while True:
        matches = []
        mult_match_index = 0
        mult_match_found = False
        ma_code = ''
        city = input(
            "Please enter the name of a metro area.\nInput: ")
        if city == '*':
            return city
        for metro_area in metro_area_dict.keys():
            if city.lower() in metro_area.lower():
                matches.append(metro_area)  # Append if text entry is a substring of a metro area
        if len(matches) == 0:
            print('Metro area not found. Please check spelling')
        elif len(matches) == 1:
            ma_code = metro_area_dict[matches[0]]['id']
            break
        else:
            print("Multiple matches found. Which metro area would you like to select?")
            for match in matches:
                print("[{0}]: {1}, {2}".format(mult_match_index, match, metro_area_dict[match]['state']))
                mult_match_index +=1
            while not mult_match_found:
                selection = input('Enter value: ')
                try:
                    ma_code=metro_area_dict[matches[int(selection)]]['id']
                    mult_match_found = True
                except (TypeError, IndexError, ValueError):
                    print('Please enter a valid number.')
            if mult_match_found:
                break
    return ma_code

def get_metro_area_set(metro_area_dict):
    '''Get a list of metro areas for comparison'''
    ma_code_set = set()
    while True:
        ma_code = get_user_input_metro_area(metro_area_dict)
        ma_code_set.add(ma_code)
        continue_input = input("Type 'Y' to add another city to your city. Otherwise, "
                               "hit any key to finish.\nInput: ")
        if continue_input.lower() != 'y':
            break
    return ma_code_set


def build_var_selection_dict(variable_dict):
    '''Iterate through items in dict and assign a value to each item for use with user input.'''
    selection_dict = {}
    var_counter = 1
    for item in variable_dict:
        selection_dict[str(var_counter)] = {'code': item, 'description': variable_dict[item]}
        var_counter +=1
    return selection_dict

def get_user_input_var(var_dict_for_selection):
    print("Please select a variable from the list below:")
    for item in var_dict_for_selection:
        print("[{0}] {1}".format(item, var_dict_for_selection[item]['description']))
    while True:
        user_inp = input('Selection: ')
        try:
            var_code = var_dict_for_selection[user_inp]['code']
            break
        except KeyError:
            print('Invalid entry, Ensure your entry is an integer listed in the selection below')
    return var_code

def build_query(var_code, ma_code):
    '''Takes a variable and metro area and return a request query'''
    request_str = ('/'.join((host, year, dataset,
                             get))) + ',' + var_code + '&for=' + geography + ':' + ma_code + '&key=' + api_key
    return request_str

def build_query_state(var_code, state):
    '''Takes a variable and stateand return a request query'''
    request_str = ('/'.join((host, year, dataset,
                             get))) + ',' + var_code + '&for=state:' + state + '&key=' + api_key
    return request_str


def build_query_list(var_code, ma_code_set):
    request_str_list = []
    for ma_code in ma_code_set:
        request_str = build_query(var_code, ma_code)
        request_str_list.append(request_str)
    return request_str_list

def submit_query(request_str):
    response = requests.get(request_str, verify=False) #TODO: This will return an insecure request warning, set to false for now.
    return response.json()

def get_response_list(request_str_list):
    response_list = []
    for request_str in request_str_list:
        response = submit_query(request_str)
        response_list.append(response)
    return response_list


def parse_responses(response_list):
    results_dict = {}
    for item in response_list:
        results = item[1]
        results_dict[results[0]] = results[1]
    return results_dict

def build_results_json(results_dict):
    return json.dumps(results_dict)


def api_request_by_state(state, variable):
    '''Request a single category for a single state'''
    request_str = build_query_state(state, variable)
    response_json = submit_query(request_str)
    results_dict = parse_responses([response_json])
    return build_results_json(results_dict)

def main():
    metro_area_dict = load_metro_area_json('metro_area_codes.json') #import metro area codes
    var_dict = load_variable_json('variable_codes.json') #import variable codes
    var_dict_for_selection = build_var_selection_dict(var_dict) #Dict used for purposes of allowing selection via command line
    var_code = get_user_input_var(var_dict_for_selection) #Get variable from user
    ma_code_set = get_metro_area_set(metro_area_dict) #Get ma_list from user
    request_str_list = build_query_list(var_code, ma_code_set) #Build all request strings
    response_list = get_response_list(request_str_list) #Get list containing all responses
    results_dict = parse_responses(response_list) #Build dict containing all responses
    results_json = build_results_json(results_dict) #Return query results in JSON format
    return results_json


if __name__ == '__main__':
    results = main()
    # results = api_request_by_state("S1701_C03_001E", "01")
    print(results)


