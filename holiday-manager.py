from datetime import date
import datetime
import json
from re import T
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import config

# get properties from the config file

json_holidays = getattr(config, 'holidays', 'no_file_found')
urls = getattr(config, 'api_urls', 'no_urls_found')

# Setup:

saved = True

holidays = []

confirmation = ['y','n']

separator = (len('Holiday Management') + 1) * '='

month_to_num = {
    'Jan': '01',
    'Feb': '02',
    'Mar': '03',
    'Apr': '04',
    'May': '05',
    'Jun': '06',
    'Jul': '07',
    'Aug': '08',
    'Sep': '09',
    'Oct': '10',
    'Nov': '11',
    'Dec': '12'
}

years = [2020, 2021, 2022, 2023, 2024]

# Data Classes:

@dataclass
class Holiday:
    name: str
    date: datetime
    #weather: str

    def __iter__(self):
        return iter(self.name)

class HolidayList:

    def __init__(self):
       self.inner_holidays = []
       self.dateformat = '%Y-%m-%d'

    def add_holiday(self, holiday_obj):
        new_date = holiday_obj.date.strftime(self.dateformat)
        a_holiday = self.findHoliday(holiday_obj.name, new_date)
        if type(a_holiday) == Holiday:
            print('\nThis holiday already exists')
        else:
            print(f'\nSuccess:\n{added_holiday} ({added_date}) has been added to the holiday list.')
            #not changing these when addibg in program
            saved == False
            adding == True
            self.inner_holidays.append(holiday_obj)

    def add_scraped_holiday(self, holiday_obj):
        new_date = holiday_obj.date.strftime(self.dateformat)
        a_holiday = self.findHoliday(holiday_obj.name, new_date)
        if type(a_holiday) != Holiday:
            self.inner_holidays.append(holiday_obj)

    def remove_holiday(self, holiday_obj):
        new_date = holiday_obj.date.strftime(self.dateformat)
        a_holiday = self.findHoliday(holiday_obj.name, new_date)
        if type(a_holiday) == Holiday:
            print('\nHoliday successfully removed')
            self.inner_holidays.remove(holiday_obj)
            removing == True
            saved == False
        else:
            print('\nNo such holiday exists')

    def size_holiday(self):
        print(f'There are {len(self.inner_holidays)} holidays stored in the system.')

    def findHoliday(self, HolidayName, HolidayDate):
        for a_holiday in self.inner_holidays:
            if HolidayName == a_holiday.name and a_holiday.date.strftime(self.dateformat) == HolidayDate:
                return a_holiday

total_holidays = HolidayList()

# Web Scraping:

# Does not include weather api

def get_request(url):
    return requests.get(url)

def get_html(res):
    return res.text

for holiday in json_holidays['holidays']:
    new_date = holiday['date']
    holiday_object = Holiday(holiday['name'], datetime.datetime.strptime(new_date, '%Y-%m-%d'))
    total_holidays.add_scraped_holiday(holiday_object)

for url in urls:
    year = 2020 + urls.index(url)
    res = get_request(url)
    soup = BeautifulSoup(get_html(res),'html.parser')

    all_holidays = soup.find('tbody').find_all('tr')
    holiday_name = ''
    for holiday in all_holidays:
        if holiday.find('td') == None:
            all_holidays.remove(holiday)
        elif holiday.find_all('td')[1].find('a').string == holiday_name:
            all_holidays.remove(holiday)
        else:
            holiday_date_place = holiday.find('th').string
            holiday_date_place = holiday_date_place.split(' ')
            if len(holiday_date_place[1]) == 2:
                holiday_date = f'{year}-{month_to_num[holiday_date_place[0]]}-{holiday_date_place[1]}'
            else:
                holiday_date = f'{year}-{month_to_num[holiday_date_place[0]]}-0{holiday_date_place[1]}'
            holiday_name = holiday.find_all('td')[1].find('a').string
            holiday_object = Holiday(holiday_name, datetime.datetime.strptime(holiday_date, '%Y-%m-%d'))
            total_holidays.add_scraped_holiday(holiday_object)

# Application Start:

print('\nHoliday Management')
print(separator)
total_holidays.size_holiday()

menu = False
while not menu:
    print(f'\nHoliday Menu\n{separator}\n1. Add a Holiday\n2. Remove a Holiday\n3. Save Holiday List\n4. View Holidays\n5. Exit')
    try:
        selection = int(input('\nEnter Selection: '))
        if selection not in range(1,6):
            print('\nPlease choose one of the listed selections')
        elif selection == 1:
            print(f'\nAdd a Holiday\n{separator}')
            adding = False
            while not adding:
                # Checking for a valid date does not work as intended
                added_holiday = input('Holiday: ')
                added_date = input('Date (year-month-day): ')
                holiday_object = Holiday(added_holiday, datetime.datetime.strptime(added_date, '%Y-%m-%d'))
                total_holidays.add_holiday(holiday_object)
                # saved = False
                # adding = True
        elif selection == 2:
            print(f'\nRemove a Holiday\n{separator}')
            finished = False
            removing = False
            while not removing:
                removed_holiday = input('Holiday: ')
                removed_date = input('Date (year-month-day): ')
                holiday_object = Holiday(removed_holiday, datetime.datetime.strptime(removed_date, '%Y-%m-%d'))
                total_holidays.remove_holiday(holiday_object)
                # saved = False
                # removing = True
        elif selection == 3:
            print(f'\nSaving Holiday List\n{separator}')
            saving = False
            while not saving:
                save_holiday = input('Are you sure you want to save your changes? [y,n] ')
                if save_holiday not in confirmation:
                    print('\nPlease choose from the listed selections')
                elif save_holiday == 'y':
                    holiday_library = HolidayList(inner_holidays = holidays)
                    holidays_list = [day.__dict__ for day in holiday_library.inner_holidays]
                    with open('holidays.json', 'w') as f:
                        json.dump(holidays_list, f)
                    print('\nSuccess:\nYour changes have been saved')
                    saved = True
                    saving = True
                else:
                    print('\nCancelled:\nHoliday list file save cancelled')
                    saving = True
        elif selection == 4:
            print(f'\nView Holidays\n{separator}')
            view = False
            while not view:
                # Viewing holidays does not work as intended
                try:
                    year_selection = int(input('Which year?: '))
                    week_selection = int(input('Which week? #[1-52]: '))
                    if year not in years:
                        print('Please select a year from 2020 to 2024')
                    elif week_selection not in range(1,53):
                        print('please choose a week between 1 and 52')
                    else:
                        # for i in range(1,8):
                        #     selected_view = date.fromisocalendar(year_selection, week_selection, i)
                        view = True
                except ValueError:
                    print('\nPlease choose a year or week number')
        else:
            exiting = False
            while not exiting:
                exit = input(f'\nExit\n=====\nAre you sure you want to exit? [y/n] ')
                if exit not in confirmation:
                    print ('\nPlease choose from the listed selections')
                elif exit == 'y' and saved == False:
                    confirming = False
                    while not confirming:
                        confirm = input('\nAre you sure you want to exit?\nYour changes will be lost.[y/n] ')
                        if exit not in confirmation:
                            print ('\nPlease choose from the listed selections')
                        elif confirm == 'y':
                            confirming = True
                            exiting = True
                            menu = True
                        else:
                            confirming = True
                            exiting = True
                elif exit == 'y':
                    exiting = True
                    menu = True
                else:
                    exiting = True
    except ValueError:
        print('\nPlease choose one of the listed selections')

print('\nGoodbye')