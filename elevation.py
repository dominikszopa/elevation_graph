import gpxpy
import gpxpy.gpx
from geopy import distance
import plotly.graph_objects as go
import plotly.express as px
import sys


def add_grade(interval_list, elevation_list, grade_list, colour_dict,
              increment, km_increment, elevation):
    """
    Calculates the grade and adds values to the appropriate lists

    :param interval_list: list of distance intervals (for x axis)
    :param elevation_list: list of elevations (for y axis)
    :param grade_list: list of grades (for colour)
    :param colour_dict: stores area graph values by colour
    :param increment: current distance interval
    :param km_increment: distance between intervals
    :param elevation: elevation at current point
    """

    # if first point, just add the elevation
    if increment == 0:
        interval_list.append(increment)
        elevation_list.append(elevation)
        grade_list.append(0)
    else:

        grade = (elevation - elevation_list[-1]) / (10 * km_increment)

        print('{0} {1} {2}'.format(increment, elevation, grade))

        # Choose the colour for the grade
        if round(grade) < 0.5:
            colour_x = 'green_x'
            colour_y = 'green_y'
        elif round(grade) >= 0.5 and round(grade) < 3:
            colour_x = 'blue_x'
            colour_y = 'blue_y'
        elif round(grade) >= 3 and round(grade) < 6:
            colour_x = 'yellow_x'
            colour_y = 'yellow_y'
        elif round(grade) >= 6 and round(grade) < 9:
            colour_x = 'red_x'
            colour_y = 'red_y'
        else:
            colour_x = 'black_x'
            colour_y = 'black_y'

        # add co-ordinates for the area graph in the appropriate colour
        colour_dict[colour_x].append(increment-km_increment)
        colour_dict[colour_y].append(0)
        colour_dict[colour_x].append(increment-km_increment)
        colour_dict[colour_y].append(elevation_list[-1])
        colour_dict[colour_x].append(increment)
        colour_dict[colour_y].append(elevation)
        colour_dict[colour_x].append(increment)
        colour_dict[colour_y].append(0)

        # also store values in appropriate lists
        interval_list.append(increment)
        elevation_list.append(elevation)
        grade_list.append(grade)


def plot_elevation_graph(interval_list, elevation_list) -> go.Figure:
    """
    Plots a basic elevation graph

    :param interval_list: list of distance intervals (for x axis)
    :param elevation_list: list of elevations (for y axis)
    """
    chart_data = {'distance': interval_list, 'elevation': elevation_list}
    fig = px.area(chart_data, x="distance", y="elevation")

    # Return the chart
    return fig


def plot_grade_graph(colour_dict) -> go.Figure:
    """
    Plots an area graph showing the grade of the route

    :param colour_dict: dictionary containing all the colour areas
    :return: the chart object
    """

    # Create a new figure
    fig = go.Figure()

    # Add the traces for each grade
    fig.add_trace(go.Scatter(
        x=colour_dict['green_x'], y=colour_dict['green_y'],
        fill='tozeroy', line=dict(color='green'),
        name='< 0.5%'))

    fig.add_trace(go.Scatter(
        x=colour_dict['blue_x'], y=colour_dict['blue_y'],
        fill='tozeroy', line=dict(color='blue'),
        name='0.5-3%'))

    fig.add_trace(go.Scatter(
        x=colour_dict['yellow_x'], y=colour_dict['yellow_y'],
        fill='tozeroy', line=dict(color='yellow'),
        name='3-6%'))

    fig.add_trace(go.Scatter(
        x=colour_dict['red_x'], y=colour_dict['red_y'],
        fill='tozeroy', line=dict(color='red'),
        name='6-9%'))

    fig.add_trace(go.Scatter(
        x=colour_dict['black_x'], y=colour_dict['black_y'],
        fill='tozeroy', line=dict(color='black'),
        name='9+%'))

    fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=25,
            tickfont=dict(size=20),
        ),
        yaxis=dict(
            tickfont=dict(size=20),
        ),
    )

    # Return the chart
    return fig


def calculate_grade(gpx, km_increment):
    """
    Calculates the grade of the route

    :param gpx: gpx file
    :param km_increment: distance between intervals
    :return: dictionary of color values to plot the area graph
    """

    total_distance = 0              # stores the distance as we go along
    last_point = None               # stores the previous point
    current_increment = 0           # each step of the grade graph

    detailed_distance_list = []     # list of distances for every point
    detailed_elevation_list = []    # list of elevations for every point

    interval_list = []              # list of distance intervals (for x axis)
    elevation_list = []             # list of elevations (for y axis)
    grade_list = []                 # list of grades (for colour)

    colour_dict = {                 # stores area graph values by colour
        'green_x': [],
        'green_y': [],
        'blue_x': [],
        'blue_y': [],
        'yellow_x': [],
        'yellow_y': [],
        'red_x': [],
        'red_y': [],
        'black_x': [],
        'black_y': []
    }

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:

                # print('Point at ({0},{1}) -> {2}'.format(
                #     point.latitude, point.longitude, point.elevation
                # ))

                if last_point:

                    # Calculate the distance between the points
                    flat_distance = distance.distance(
                        (last_point.latitude, last_point.longitude),
                        (point.latitude, point.longitude)
                    ).km
                    # print(flat_distance)

                    # # Calculate Euclidian distance (include elevation)
                    # euclidian_distance = math.sqrt(flat_distance**2 +
                    #   (last_point.elevation - point.elevation)**2)
                    # print(euclidian_distance)

                    total_distance += flat_distance
                    # print('{0} {1}'.format(total_distance, point.elevation))

                    # add each point to the detailed distance and elevation
                    # lists
                    detailed_distance_list.append(total_distance)
                    detailed_elevation_list.append(round(point.elevation))

                    # once we pass the next increment, add the grade
                    if total_distance >= current_increment:

                        # print('{0} {1}'.format(
                        #   total_distance,
                        #   point.elevation))

                        add_grade(
                            interval_list,
                            elevation_list,
                            grade_list,
                            colour_dict,
                            current_increment,
                            km_increment,
                            round(point.elevation)
                        )
                        current_increment += km_increment

                # store the point for the next iteration
                last_point = point

    return colour_dict


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 elevation.py [gpx_file] [km]")
        sys.exit(1)

    args = sys.argv

    # Open the GPX file specified in the first command line argument
    gpx_file = open(args[1], 'r')

    # If there is no second argument, assume the value 1, then
    # try to convert the second command line argument to a float
    # and exit with an error message if it is not a number

    if len(sys.argv) < 3:
        km_increment = 1
    else:
        try:
            km_increment = float(sys.argv[2])
        except ValueError:
            print("Error: km must be a number")
            sys.exit(1)

    # Parse the GPX file using the gpxpy library
    gpx = gpxpy.parse(gpx_file)

    colour_dict = calculate_grade(gpx, km_increment)

    # Print a basic elevation graph
    # chart = plot_elevation(detailed_distance_list, detailed_elevation_list)

    # Print a grade graph
    chart = plot_grade_graph(colour_dict)

    # Display the chart
    chart.show()


if __name__ == "__main__":
    main()
