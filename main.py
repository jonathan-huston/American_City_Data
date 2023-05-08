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


def load_metro_area_json(json_file):
    '''Loads a json file containing metro area names and locations and convers it to a dictionary'''
    with open(json_file, 'r') as f:
        data = json.load(f)
    return data


def find_metro_area_num(city, metro_area_dict):
    '''Return value for metro area code to be used in request given a text input.
    Value is a 3 digit number.'''
    if city == '*':
        return city
    matches = []
    mult_match_index = 0
    mult_match_found = False
    ma_code = ''
    for metro_area in metro_area_dict.keys():
        if city.lower() in metro_area.lower():
            matches.append(metro_area)  # Append if text entry is a substring of a metro area
    if len(matches) == 0:
        print('Metro area not found. Please check spelling')
        return None
    elif len(matches) == 1:
        ma_code = metro_area_dict[matches[0]]['id']
    else:
        print("Multiple matches found. Which metro area would you like to select?")
        for match in matches:
            print(f"[{mult_match_index}]: {match}, {metro_area_dict[match]['state']}")
            mult_match_index +=1
        while not mult_match_found:
            selection = int(input('Enter value: '))
            if 0<=selection<=mult_match_index-1:
                ma_code=metro_area_dict[matches[selection]]['id']
                mult_match_found = True
            else:
                print('Please enter a valid number.')
    return ma_code

def find_variable_name(var_text_entry):
    pass


def build_query(variable, metro_area_input):
    '''Takes a variable and metro area and return a request query'''
    metro_area = find_metro_area_num(metro_area_input)
    request_str = ('/'.join((host, year, dataset,
                             get))) + ',' + variable + '&for=' + geography + ':' + metro_area + '&key=' + api_key
    return request_str


def submit_query(request_str):
    response = requests.get(request_str)
    return response.json()


def build_table():
    pass


if __name__ == '__main__':
    # request_str = build_query('S0101_C01_001E','*')
    # response_json = submit_query(request_str)
    # build_metro_area_json()
    metro_area_dict = load_metro_area_json('metro_area_codes.json')
    ma_code = find_metro_area_num('Portland', metro_area_dict)
    print(ma_code)


    #prompt user, enter * for all cities
