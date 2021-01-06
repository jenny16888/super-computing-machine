"""
Analysis the wildfire
"""
import datetime
from typing import List, Tuple
from temp_download import get_date_temp
from wildfire_read import get_years_wildfire
from full_temp_data import TEMP_DATA
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import statistics

FIRE_DATASET = get_years_wildfire(2007, 2015)
MONTH = ('January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December')


# **************************************************************************
#                  Functions for Calculation before plot
# **************************************************************************

def convert_points(points: list) -> tuple:
    """Return a tuple of two lists, containing the x
    and y-coordinates as pair of the given points.
    """
    x_list = [xy[0] for xy in points]
    y_list = [xy[1] for xy in points]
    return (x_list, y_list)


def plot_points_and_line(x_coords: list,
                         y_coords: list,
                         a: float,
                         b: float,
                         top_title: str,
                         x_title: str,
                         y_title: str) -> None:
    """Plot the given x- and y-coordinates and a line using plotly
    Display results in a web browser.
    """
    # Create a blank figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_coords, y=y_coords, mode='markers', name='Data'))
    fig.add_trace(go.Scatter(x=[min(x_coords), max(x_coords)], y=[a + b * min(x_coords), a + b * max(x_coords)],
                             mode='lines', name='Regression line'))
    fig.update_layout(title=top_title, yaxis_title=y_title, xaxis_title=x_title)
    fig.show()


def simple_linear_regression(points: list) -> tuple:
    """Generate a linear regression on the given points.
    where the line y = a + bx
    """
    amount = len(points)
    x_average = sum(xy[0] for xy in points) / amount
    y_average = sum(xy[1] for xy in points) / amount
    b_up = sum((xy[0] - x_average) * (xy[1] - y_average) for xy in points)
    b_down = sum((xy[0] - x_average) ** 2 for xy in points)
    b = b_up / b_down
    a = y_average - b * x_average
    return (a, b)


# **************************************************************************
#                     Plot temp to intensity Function
# **************************************************************************

def get_fire_intensity(fire_info: Tuple[datetime.datetime,
                                        datetime.datetime,
                                        float,
                                        str,
                                        Tuple[float, float]]) -> float:
    """Return the fire intensity of a wildfire calculated by
    intensity = fire_size(acres) * duration(day)
    """
    return fire_info[2] * (fire_info[1] - fire_info[0]).total_seconds() / (3600 * 24)


def generate_temp_vs_intensity(max_or_min: str) -> List[Tuple]:
    """Generate the points of maximum temperature and intensity,
    or minimum temperature and intensity according to the
    parameter max_or_min
    """
    temp_intensity = []
    for year in FIRE_DATASET:
        for month in FIRE_DATASET[year]:
            for fire_info in FIRE_DATASET[year][month]:
                if get_fire_intensity(fire_info) != 0:  # get rid if the data with zero intensity
                    temp_intensity.append((get_date_temp(fire_info[0],
                                                         TEMP_DATA)[{'max': 0, 'min': 1}[max_or_min]],
                                           get_fire_intensity(fire_info) ** 0.1))
    return temp_intensity


def plot_temp_vs_fire_intensity(max_or_min: str) -> None:
    """plot the relationship between maximum or minimum temperature
    of a day and fire intensity according to the parameter max_or_min"""
    temp_intensity = generate_temp_vs_intensity(max_or_min)
    points = convert_points(temp_intensity)
    ab = simple_linear_regression(temp_intensity)
    plot_points_and_line(points[0],
                         points[1],
                         ab[0],
                         ab[1],
                         f'The relationship between the {max_or_min} temperature of a day'
                         f' and the wildfire intensity on that day if fire happened',
                         f'The {max_or_min} temperature of a day / F',
                         f'The 10th root of wildfire intensity if fire happened')


# **************************************************************************
#                         Plot Year to Temp Function
# **************************************************************************

def generate_year_to_avg_temperature(max_or_min: str) -> List[Tuple]:
    """Generate the points of year and average maximum temperature,
    or average minimum temperature and intensity according to the
    parameter max_or_min
    """
    year_temp = []
    for year in TEMP_DATA:
        temp = []
        for month in TEMP_DATA[year]:
            temp += [data[{'max': 1, 'min': 2}[max_or_min]] for data in TEMP_DATA[year][month]]
        avg = sum(temp) / len(temp)
        year_temp.append((year, avg))
    return year_temp


def plot_year_to_temp(max_or_min: str) -> None:
    """The relationship between the year and average maximum temperature
    or average minimum temperature according to the parameter max_or_min.
    """
    year_temp = generate_year_to_avg_temperature(max_or_min)
    points = convert_points(year_temp)
    ab = simple_linear_regression(year_temp)
    plot_points_and_line(points[0],
                         points[1],
                         ab[0],
                         ab[1],
                         f'The relationship between the average {max_or_min}'
                         f' temperature and the year',
                         'year',
                         f'The average {max_or_min} temperature / F')


# **************************************************************************
#                           Prediction Function
# **************************************************************************

def make_prediction(year: int) -> str:
    """Return the predicted wildfire intensity if a wildfire appeared on a day
     in the year. Use year to find average temperature, use temperature to find
     wildfire intensity.
    """

    max_and_min_intensity = []

    for t in ('min', 'max'):
        # find regression between year and avg_temp then use regression to
        # calculate average_temp of a year.
        year_max_temp = generate_year_to_avg_temperature(t)
        year_max_temp_ab = simple_linear_regression(year_max_temp)
        max_temp = year_max_temp_ab[0] + year_max_temp_ab[1] * year

        # find regression between temp and wildfire intensity then use
        # regression to calculate the intensity of a avg_temp.
        max_temp_intensity = generate_temp_vs_intensity(t)
        max_temp_intensity_ab = simple_linear_regression(max_temp_intensity)
        intensity = (max_temp_intensity_ab[0] + max_temp_intensity_ab[1] * max_temp) ** 10

        max_and_min_intensity.append(intensity)

    # since we have two regression (max and min), we got two predicted intensity.
    # find the average of them

    message = f"Prediction: If wildfire appears in a day in {year}, \nits intensity is expected" \
              f" to be about {round(sum(max_and_min_intensity) / 2, 3)} " \
              f"\nwhere intensity = fire_size(acres) * duration(day)"

    return message


# **************************************************************************
#                           Drawing Map Function
# **************************************************************************

def fire_data_by_month(year: int, month: str) -> dict:
    """Return a dictionary mapping fire properties to lists of the data of each fire in the given month and year.
    """

    fires = [fire for fire in FIRE_DATASET[year][month]]
    data = {'fire_size_value': [],
            'Latitude': [],
            'Longitude': [],
            'marker_size': []}

    for fire in fires:
        fire_size = fire[2]
        duration = (fire[1] - fire[0]).days + (fire[1] - fire[0]).seconds / (3600 * 24)
        location = fire[4]
        data['fire_size_value'].append(fire_size * duration)
        data['Latitude'].append(location[0])
        data['Longitude'].append(location[1])
        data['marker_size'].append(get_marker(fire_size * duration))

    return data


def get_marker(fire_data: int) -> float:
    """Return an int value of the marker size corresponding to the value of fire_data.
    """
    return (fire_data * 1000) ** (1 / 10)


def average_max_temp_month(year: int, month: str) -> float:
    """Return the average maximum temperature of a given month."""
    max_temp = [temp[1] for temp in TEMP_DATA[year][month]]
    return statistics.mean(max_temp)


def plot(month: str, year: int) -> None:
    """Plot the wildfire map of California in the given month of given year.
    """

    df = pd.DataFrame(fire_data_by_month(year, month))  # store the fire data
    map = gpd.read_file('CA_counties.shp')  # read the shape file of California in project folder using geopandas
    fig, ax = plt.subplots(figsize=(8, 8))  # set the size of the figure to be drawn

    ax.xaxis.set_label_text('Longitude')  # label x axis
    ax.yaxis.set_label_text('Latitude')  # label y axis
    ax.set_title("Wildfires in California in "
                 + month + ", " + str(year)
                 + ", Average Max.Temp = "
                 + str(round(average_max_temp_month(year, month), 2)))  # add title of the figure

    # store fire location as data points on GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    # plot base map and fire data points
    map.plot(ax=ax, alpha=1, color='grey')  # set base map transparency to 1 and color to grey
    # set size of scatter points to 50, transparency to 0.85, and color to 'hot_r' color map
    gdf.plot(ax=ax, markersize=50, alpha=0.85, column=df.marker_size, cmap='hot_r', legend=True)

    plt.show()  # show the graph
