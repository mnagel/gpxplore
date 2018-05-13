import math
import os
import subprocess

import matplotlib.pyplot as plt
import mplleaflet
from PyQt5.QtWidgets import QPushButton

from data_explorer.gui import InlineHTML, EvaluateOnUiThread
from data_explorer.rating import Rater, RaterValueEquals, RaterColorScale
from data_explorer.testlet import Testlet
from gpxplore.gpxfile import GpxFile


def white_to_red(p):
    f = min(1, 1.7 - p)
    return [1 * f, (1 - p) * f, (1 - p) * f]


def white_to_blue(p):
    f = min(1, 1.7 - p)
    return [(1 - p) * f, (1 - p) * f, 1 * f]


def dist_format(float_meter):
    return "%.2f m" % float_meter


def speed_format(float_meter_per_second):
    return "%.2f km/h" % (float_meter_per_second * 3600.0 / 1000.0)


def time_format(float_seconds):
    minutes = math.floor(float_seconds / 60.0)
    hours = math.floor(minutes / 60.0)
    return '%s:%s:%s' % (
        str(int(hours)).zfill(2), str(int(minutes % 60)).zfill(2), str(int(float_seconds % 60)).zfill(2))


class NameTestlet(Testlet):
    def __str__(self):
        return "Filename"

    def evaluate(self, data: GpxFile):
        mainpart = os.path.splitext(os.path.basename(data.filename))[0]
        mainpart = mainpart.replace("_", " ")
        return data.filename, mainpart

    def get_result_rater(self) -> Rater:
        return RaterValueEquals("foo")


class Length2dTestlet(Testlet):
    def __str__(self):
        return "Length 2d"

    def evaluate(self, data: GpxFile):
        length = data.gpx.length_2d()
        return length, dist_format(length)

    def get_result_rater(self):
        return RaterColorScale(0, 20000, white_to_blue)


class Length3dTestlet(Testlet):
    def __str__(self):
        return "Length 3d"

    def evaluate(self, data: GpxFile):
        length = data.gpx.length_3d()
        return length, dist_format(length)

    def get_result_rater(self):
        return RaterColorScale(0, 20000, white_to_blue)


class MovingTimeTestlet(Testlet):
    def __str__(self):
        return "Moving Time"

    def evaluate(self, data: GpxFile):
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = data.gpx.get_moving_data()
        return moving_time, time_format(moving_time)

    def get_result_rater(self):
        return RaterColorScale(0, 5 * 60 * 60, white_to_blue)


class StoppedTimeTestlet(Testlet):
    def __str__(self):
        return "Stopped Time"

    def evaluate(self, data: GpxFile):
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = data.gpx.get_moving_data()
        return stopped_time, time_format(stopped_time)

    def get_result_rater(self):
        return RaterColorScale(0, 1 * 60 * 60, white_to_blue)


class MovingDistanceTestlet(Testlet):
    def __str__(self):
        return "Moving Distance"

    def evaluate(self, data: GpxFile):
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = data.gpx.get_moving_data()
        return moving_distance, dist_format(moving_distance)

    def get_result_rater(self):
        return RaterColorScale(0, 20000, white_to_blue)


class StoppedDistanceTestlet(Testlet):
    def __str__(self):
        return "Stopped Distance"

    def evaluate(self, data: GpxFile):
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = data.gpx.get_moving_data()
        return stopped_distance, dist_format(stopped_distance)

    def get_result_rater(self):
        return RaterColorScale(0, 10000, white_to_blue)


class MaxSpeedTestlet(Testlet):
    def __str__(self):
        return "Max Speed"

    def evaluate(self, data: GpxFile):
        moving_time, stopped_time, moving_distance, stopped_distance, max_speed = data.gpx.get_moving_data()
        return max_speed, speed_format(max_speed)

    def get_result_rater(self):
        return RaterColorScale(0, 30 * 3600.0 / 1000.0, white_to_blue)


class UphillTestlet(Testlet):
    def __str__(self):
        return "Uphill"

    def evaluate(self, data: GpxFile):
        uphill, downhill = data.gpx.get_uphill_downhill()
        return uphill, dist_format(uphill)

    def get_result_rater(self):
        return RaterColorScale(0, 1000, white_to_blue)


class DownhillTestlet(Testlet):
    def __str__(self):
        return "Downhill"

    def evaluate(self, data: GpxFile):
        uphill, downhill = data.gpx.get_uphill_downhill()
        return downhill, dist_format(downhill)

    def get_result_rater(self):
        return RaterColorScale(0, 1000, white_to_blue)


class StartedTestlet(Testlet):
    def __str__(self):
        return "Started"

    def evaluate(self, data: GpxFile):
        start_time, end_time = data.gpx.get_time_bounds()
        return start_time, str(start_time)

    def get_result_rater(self):
        return RaterValueEquals("bar")


class EndedTestlet(Testlet):
    def __str__(self):
        return "Ended"

    def evaluate(self, data: GpxFile):
        start_time, end_time = data.gpx.get_time_bounds()
        return end_time, str(end_time)

    def get_result_rater(self):
        return RaterValueEquals("bar")


class CountTestlet(Testlet):
    def __str__(self):
        return "Count"

    def evaluate(self, data: GpxFile):
        count = len(list(data.gpx.walk(only_points=True)))
        return count, str(count)

    def get_result_rater(self):
        return RaterColorScale(0, 2000, white_to_blue)


class MapTestlet(Testlet):
    def __str__(self):
        return "Map"

    def evaluate(self, data: GpxFile):
        # fig, ax = plt.subplots()

        fig = plt.figure()
        ax = fig.add_subplot(111)

        df = data.df[['Point_Longitude', 'Point_Latitude']].dropna()
        ax.plot(df['Point_Longitude'], df['Point_Latitude'], color="#00A6ED", linewidth=3, alpha=0.9)
        val = mplleaflet.fig_to_html(fig=fig)  # , tiles='esri_aerial')
        """
        attribution = _attribution + ' | ' + tiles[1]
        attribution = "" # :(
        """
        # print(val)
        return val, InlineHTML(val)
        # return fig, fig

    def get_result_rater(self):
        return RaterValueEquals("bar")


class BigMapTestlet(Testlet):
    def __str__(self):
        return "Big Map"

    def evaluate(self, data: GpxFile):
        # fig, ax = plt.subplots()

        def create_button():
            btn = QPushButton()
            btn.setText('Pop Out')

            def btn_clicked():
                # fig, ax = plt.subplots()

                fig = plt.figure()
                ax = fig.add_subplot(111)

                df = data.df[['Point_Longitude', 'Point_Latitude']].dropna()
                ax.plot(df['Point_Longitude'], df['Point_Latitude'], color="#00A6ED", linewidth=3, alpha=0.9)
                mplleaflet.show(fig=fig)  # , tiles='esri_aerial')
                """
                attribution = _attribution + ' | ' + tiles[1]
                attribution = "" # :(
                """
                # print(val)
                print("popping out")

            # noinspection PyUnresolvedReferences
            btn.clicked.connect(btn_clicked)
            return btn

        return 'mplleaflet', EvaluateOnUiThread(create_button)

    def get_result_rater(self):
        return RaterValueEquals("bar")


class GpsPruneTestlet(Testlet):
    def __str__(self):
        return "gpsprune"

    def evaluate(self, data: GpxFile):
        # fig, ax = plt.subplots()

        def create_button():
            btn = QPushButton()
            btn.setText('gpsprune')

            def btn_clicked():
                subprocess.call(['gpsprune', data.filename])

            # noinspection PyUnresolvedReferences
            btn.clicked.connect(btn_clicked)
            return btn

        return 'gpsprune', EvaluateOnUiThread(create_button)


class HeigthmapTestlet(Testlet):
    def __init__(self, x_name, y_names, **kwargs):
        super().__init__()
        self.x_name = x_name
        self.y_names = y_names
        self.kwargs = kwargs

    def __str__(self):
        return "Heightmap"

    def evaluate(self, data: GpxFile):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        df = data.df

        if "ylim" in self.kwargs:
            ax.set_ylim(self.kwargs["ylim"])
        if "xlim" in self.kwargs:
            ax.set_xlim(self.kwargs["xlim"])

        for y in self.y_names:
            df.plot(kind="line", ax=ax, x=self.x_name, y=y, label=y, legend=False,
                    linestyle='solid', marker='', markerfacecolor='#00A6ED', markersize=3, color="#00A6ED")
        x_axis = ax.axes.get_xaxis()
        x_label = x_axis.get_label()
        x_label.set_visible(False)

        fig.tight_layout()
        return fig, fig

    def get_result_rater(self):
        return RaterValueEquals("bar")
