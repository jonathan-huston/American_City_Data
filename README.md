#ABOUT THE DATA BEING USED
CS 361 Project - Compare and data for American cities

Data is sourced from the 2021 American Community Survey.
For more information about using the Census Data API, see here: 
https://www.census.gov/data/developers/guidance/api-user-guide.Available_Data.html#list-tab-2080675447

A list of available datasets can be found here: https://api.census.gov/data.html.
For now, only the 2021 American Community Survey is being used (code acs/acs1)

Variable names and descrptions for acs1 data can be found here can be found here: https://api.census.gov/data/2021/acs/acs1/subject/variables.html
Due to the amount of available data, only certain variables are available for selection by the user. Variables can be added as needed.


#REQUEST DATA METHOD:
Data can be requested by sending a request to the following url:
http://flip3.engr.oregonstate.edu:54546/api/data?state=<state_abbreviation>&var=<var_code>
-All 50 states + Puerto Rico + District of Columbia are available (see https://www.faa.gov/air_traffic/publications/atpubs/cnt_html/appendix_a.html for codes)
-Available variables and their codes are shown below (list to be expanded):
    -Percent of population below poverty level: S1701_C03_001E 
    -Unemployment rate (16 years and older): S2301_C04_001E 
    -Mean household income: S1902_C03_001E
    -Percent of population with bachelor's degree (25 years and older): S0102_C01_037E
-A JSON will be returned containing the full name of the state and the requested variable

The following request would return the percent of the population below the poverty line for Virginia: http://flip3.engr.oregonstate.edu:54546/api/data?state=VA&var=S1701_C03_001E
Results:
{'state': 'Virginia', 'var_name': 'S1701_C03_001E', 'value': '10.2'} \

An example file showing how to request and receive data using the API is available in the root directory ('api_request_test.py')
