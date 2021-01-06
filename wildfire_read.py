"""
Read the database of wildfire database
"""
import datetime
import sqlite3
import pprint


MONTH = ('January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December')


def get_years_wildfire(begin_year: int, end_year: int, show_process: bool = True):
    """Read_the_wild_fire data from begin_year to end_year
    show the reading process when show_process ia True
    """
    years_wildfire = {}
    years = end_year - begin_year + 1
    for year in range(begin_year, end_year + 1):
        if show_process:
            print('\r\033[33mreading wildfire data in', str(year) +
                  f' ({year - begin_year + 1}/{years})...\033[0m', end='')
        years_wildfire = {**years_wildfire, **get_year_wildfire(year)}
    if show_process:
        print('\r\033[32mfinished reading wildfire data\033[0m')
    return years_wildfire


def get_year_wildfire(year: int) -> dict:
    """Read_the_wild_fire data in a year show the reading
    process when show_process ia True.
    Represent the data in a dict.
    """
    year_dict = {year: {month: () for month in MONTH}}
    fire_database = sqlite3.connect('FPA_FOD_20170508.sqlite')
    fire_cursor = fire_database.cursor()

    # read the data from the sqlite dataset using sql language
    fire_data = fire_cursor.execute("select DISCOVERY_DATE, "
                                    "DISCOVERY_TIME, "
                                    "CONT_DATE, "
                                    "CONT_TIME, "
                                    "FIRE_SIZE, "
                                    "FIRE_SIZE_CLASS, "
                                    "LATITUDE, "
                                    "LONGITUDE "
                                    "from Fires"
                                    f" where FIRE_YEAR == {year} and STATE == 'CA'")

    # convert the data into a organized dictionary
    for line in fire_data:
        if None not in line:
            start = value_to_datetime(line[0], line[1])
            end = value_to_datetime(line[2], line[3])
            fire_size = line[4]
            fire_class = line[5]
            lat_and_lon = (line[6], line[7])
            year_dict[year][MONTH[start.month - 1]] += ((start, end, fire_size, fire_class, lat_and_lon),)
    return year_dict


def value_to_datetime(date_value: float, time_value: str):
    """Convert the datetime value in the sqlite dataset into
    a datetime.datetime() object in python
    """
    base_date = datetime.datetime(2008, 1, 1, 0, 0, 0)
    delta = datetime.timedelta(days=int(date_value - 2454466.5),
                               hours=int(time_value[0:2]),
                               minutes=int(time_value[2:]))
    return base_date + delta


if __name__ == '__main__':
    data = get_years_wildfire(2007, 2015)
