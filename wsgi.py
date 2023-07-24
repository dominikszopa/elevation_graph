from flask import Flask, request, render_template
from elevation import calculate_grade, plot_grade_graph
import gpxpy
import gpxpy.gpx

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Input page with file and km increment form, and output page with graph
    """

    # If the request method is POST, process the form
    if request.method == "POST":

        # Get the uploaded GPX file and km increment from the form
        gpx_file = request.files["gpx_file"]
        km_increment = float(request.form["km_increment"])

        # Read the GPX file
        gpx_contents = gpx_file.read()

        # Parse the GPX file using the gpxpy library
        gpx = gpxpy.parse(gpx_contents)

        # Calculate the grade and plot the graph
        colour_dict, distance = calculate_grade(gpx, km_increment)

        fig = plot_grade_graph(colour_dict, distance)

        return fig.to_html(full_html=False)

    # If the request method is GET, display the form
    return render_template("index.html")
