import gpxpy
import pandas as pd


class GpxFile(object):
    def __init__(self, filename):
        self.filename = filename

        data = []
        gpx2 = gpxpy.parse(open(self.filename, 'r'))
        # Loop through tracks
        flat_point_index = 0
        for track_idx, track in enumerate(gpx2.tracks):
            track_name = track.name
            track_time = track.get_time_bounds().start_time
            track_length = track.length_3d()
            track_duration = track.get_duration()
            track_speed = track.get_moving_data().max_speed

            for seg_idx, segment in enumerate(track.segments):
                segment_length = segment.length_3d()
                for point_idx, point in enumerate(segment.points):
                    flat_point_index += 1
                    data.append([
                        0,
                        self.filename,
                        track_idx,
                        track_name,
                        track_time,
                        track_length,
                        track_duration,
                        track_speed,
                        seg_idx,
                        segment_length,
                        point_idx,
                        flat_point_index,
                        point.time,
                        point.latitude,
                        point.longitude,
                        point.elevation,
                        segment.get_speed(point_idx)
                    ])

        self.gpx = gpx2
        self.df = pd.DataFrame(data, columns=[
            'File_Index',
            'File_Name',
            'Track_Index',
            'Track_Name',
            'Track_Time',
            'Track_Length',
            'Track_Duration',
            'Track_Max_Speed',
            'Segment_Index',
            'Segment_Length',
            'Point_Index',
            'Point_Index_Flat',
            'Point_Time',
            'Point_Latitude',
            'Point_Longitude',
            'Point_Elevation',
            'Point_Speed'
        ])
        pass

    def __str__(self):
        return self.filename
