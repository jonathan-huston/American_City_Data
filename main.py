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


state_code_list = [ 'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
           'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME',
           'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
           'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX',
           'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

state_dict = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}


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

def load_json(json_file):
    '''Loads a json file convert it to a dictionary'''
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

def parse_response_state(response_json):
    results_dict = {}
    response = response_json[0]
    results_dict['state'] = response[1][0]
    results_dict['var_name'] = response[0][1]
    results_dict['value'] = response[1][1]
    return results_dict

def build_results_json(results_dict):
    return json.dumps(results_dict)


def api_request_by_state(state, var_code):
    '''Request a single category for a single state'''
    state_dict = load_json('state_codes.json')
    state_code = state_dict[state]
    request_str = build_query_state(state = state_code, var_code = var_code)
    response_json = submit_query(request_str)
    results_dict = parse_response_state([response_json])
    return build_results_json(results_dict), results_dict

def get_state_or_ma():
    match_found = 0
    print("Would you like to compare states or metro areas?\n[1] Metro Areas\n[2] States")
    while not match_found:
        selection = input('Enter selection: ')
        if selection not in ['1','2']:
            print("Invalid entry. Please enter 1 or 2")
        else:
            if selection == '1':
                return('ma')
            return('state')

def get_crime_data():
    response = requests.get('http://flip2.engr.oregonstate.edu:54544/state_crime', verify=False)
    return response.json()

def parse_crime_data(json_response):
    '''Returns a dictionary containing the crime statistics '''
    crime_data_dict = {}
    for item in json_response:
        state = item['State']
        crime_rates = {}
        prop_crime_dict = item['Data']['Rates']['Property']
        viol_crime_dict = item['Data']['Rates']['Violent']
        for prop_crime in prop_crime_dict:
            if prop_crime != 'All':
                crime_rates[prop_crime] = prop_crime_dict[prop_crime]
        for viol_crime in viol_crime_dict:
            if viol_crime != 'All':
                crime_rates[viol_crime] = viol_crime_dict[viol_crime]
        crime_data_dict[state]=crime_rates
    return crime_data_dict


def get_state_set():
    '''Get a list of states for comparison'''
    state_code_set = set()
    while True:
        state_tup = get_state_name()
        state_code_set.add(state_tup)
        continue_input = input("Type 'Y' to add another state. Otherwise, "
                               "hit any key to finish.\nInput: ")
        if continue_input.lower() != 'y':
            break
    return state_code_set

def get_state_name():
    complete = 0
    match = 0
    while not match:
        response = input("Enter two digit state code: ")
        if response.upper() not in state_code_list:
            print("Invalid entry.")
        else:
            return response.upper(),state_dict[response]

def main():

    #load data
    metro_area_dict = load_json('metro_area_codes.json') #import metro area codes
    var_dict_ma = load_json('variable_codes.json') #import variable codes
    var_dict_for_selection_ma = build_var_selection_dict(var_dict_ma) #Dict used for purposes of allowing selection via command line
    var_dict_state = load_json('variable_codes_states.json') #import variable codes
    var_dict_for_selection_state = build_var_selection_dict(var_dict_state)
    raw_crime_data = get_crime_data()
    crime_data_dict = parse_crime_data(raw_crime_data)
    
    #get user input
    state_or_ma = get_state_or_ma()

    #metro area loop
    if state_or_ma == 'ma':
            ma_code_set = get_metro_area_set(metro_area_dict) #Get ma_list from user
            var_code = get_user_input_var(var_dict_for_selection_ma) #Get variable from user
            request_str_list = build_query_list(var_code, ma_code_set) #Build all request strings
            response_list = get_response_list(request_str_list) #Get list containing all responses
            results_dict = parse_responses(response_list) #Build dict containing all responses
            results_json = build_results_json(results_dict) #Return query results in JSON format
            return results_json
    
    #state loop
    else:
        state_set = get_state_set()
        var_code = get_user_input_var(var_dict_for_selection_state) #Get variable from user

        #Requests to US Census API routred through here
        if var_code not in ["Burglary", "Larceny","Motor", "Assault", "Rape", "Murder", "Robbery"]:
            results_list = []
            for tup in state_set:
                results_list.append(api_request_by_state(tup[0], var_code))
            print("Here are your results:")
            for item in results_list:
                state = item[1]['state']
                var_name = item[1]['var_name']
                value = item[1]['value']
                print(f"State: {state}\nCategory: {var_name}\nValue: {value}\n")
                return results_list

        #Requests to partner microservice API
        else:
            results_dict = {}
            for tup in state_set:
                result = (crime_data_dict[tup[1]][var_code])
                results_dict[tup[1]] = result

            print(f"{var_code} per 100,000 results:")
            for state,num in results_dict.items():
                print(f"{state}: {num}")



    #return results_json





if __name__ == '__main__':
    #raw_crime_data = get_crime_data()
    results = main()
    #print(get_state_name())