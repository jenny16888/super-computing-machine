"""
Download data from the website
"""
from typing import Tuple, List, Dict
import re
import time
import pprint
import datetime
import requests
from bs4 import BeautifulSoup

MONTH = ('January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December')


def get_date_temp(date: datetime.datetime, date_temp: dict) -> tuple:
    """Return the temperature of a date from the exist temperature dict
    """
    return date_temp[date.year][MONTH[date.month - 1]][date.day - 1][1:]


def get_years_temp(begin_year: int, end_year: int, show_process: bool = True) -> Dict:
    """Return the temperature as a dictionary from begin_year to end_year,
    show the downloading process iff the show_process is True
    """
    years_temp = {}
    for year in range(begin_year, end_year + 1):
        years_temp = {**years_temp, **get_year_temp(year, show_process)}
    return years_temp


def get_year_temp(year: int, show_process: bool) -> Dict:
    """Return the temperature of a year, show the downloading process
    iff the show_process is True
    """
    month_to_temp = {}
    for month in MONTH:
        if show_process:
            print('\r', 'Collecting temperature in', year, month + '...', end='')
        month_to_temp[month] = get_month_max_min_temp(str(year), month)
        if show_process:
            print('\r', '       Got temperature in', year, month, end='')
        time.sleep(1)
    if show_process:
        print('\r', 'Collected all temperatures in', year, 'successfully')
    return {year: month_to_temp}


def get_month_max_min_temp(year: str, month: str) -> Tuple:
    """Get and process the temperature data from the website.
    """
    # use post method to request temperature data from the url
    url = 'https://www.usclimatedata.com/ajax/load-history-content'
    # try alternative token below if the previous doesn't work
    # 06b3abc901c854325244b9bc3456ef6fB46j+0MkmxhSnpuZE9PZeyXMzcCK4nmw+5awS919iBZy9UfRow==
    token = 'd53b354840835415f751abd5f1ac1bd2ShpyrPAjs1iF3xuZGWfHrLyqo/gqAXYWzP6hcMYXSjZxBF7qHg=='
    data = {'token': token,
            'page': 'climate',
            'location': 'usca0967',
            'month_year': month + ' ' + year,
            'tab': '#history',
            'unit': 'american',
            'unit_required': 0,
            'unit_changed': 0}
    response = requests.post(url, data)
    json_response = response.json()
    html_temp_table = json_response['table']
    soup_table = BeautifulSoup(html_temp_table, "html.parser")

    # temp data is in the class with classname high and low
    all_max = soup_table.find_all('td', class_='high text-right')
    all_min = soup_table.find_all('td', class_='low text-right')
    day_num = len(all_max)
    max_min_temp = form_month_date(int(year), MONTH.index(month) + 1, day_num)

    # use the regular expression to find number in the text (max and min temp)
    for i in range(day_num):
        max_min_temp[i] += ((float(re.search("\d+(\.\d+)?", str(all_max[i])).group()),
                             float(re.search("\d+(\.\d+)?", str(all_min[i])).group())))
    return tuple(max_min_temp)


def form_month_date(year: int, month: int, day_num: int) -> List[Tuple]:
    """Return a list of data in a month
    """
    month_date = []
    for x in range(1, day_num + 1):
        month_date.append((datetime.date(year, month, x),))
    return month_date


if __name__ == '__main__':
    # download temperature data from 2007 to 2019
    x = get_years_temp(2007, 2019, show_process=True)
    pprint.pprint(x)
