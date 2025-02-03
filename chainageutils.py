import geojson
from shapely.geometry import shape, mapping, LineString, MultiLineString
from shapely.geometry import shape, LineString, MultiLineString
from geopy.distance import geodesic
from geojson import Point
import os




def add_start_end_chainage_markers(input_geojson_path, output_geojson_path, start_chainage=36.6, end_chainage=None, segment_length=100):
    """
    Adds chainage markers every 100 meters, naming the starting point as the given start_chainage.
    Stops adding markers if end_chainage is specified.
    
    Args:
        input_geojson_path (str): Path to the input GeoJSON file.
        output_geojson_path (str): Path to the output GeoJSON file.
        start_chainage (float): Starting chainage value in kilometers.
        end_chainage (float, optional): Ending chainage value in kilometers. Default is None (no limit).
        segment_length (int): Distance between chainage markers in meters.
    """
    try:
        with open(input_geojson_path) as f:
            geojson_data = geojson.load(f)

        features = geojson_data.get('features', [])
        if not features:
            raise ValueError("Input GeoJSON file has no features.")

        new_features = []
        current_chainage_km = start_chainage  # Starting point for chainage
        chainage_set = set()

        for feature in features:
            geometry = shape(feature['geometry'])
            
            if not isinstance(geometry, (LineString, MultiLineString)):
                raise ValueError("Feature geometry must be LineString or MultiLineString.")
            
            line_strings = [geometry] if isinstance(geometry, LineString) else list(geometry.geoms)
            
            for line in line_strings:
                coordinates = list(line.coords)
                total_distance = 0  # Distance traveled along the current line
                chainage_markers = []
                
                first_point = coordinates[0]
                chainage_str = format_chainage(current_chainage_km)
                if chainage_str not in chainage_set:
                    chainage_markers.append(create_chainage_marker(first_point, chainage_str + " (Start)"))
                    chainage_set.add(chainage_str)
                
                for i in range(len(coordinates) - 1):
                    start, end = coordinates[i], coordinates[i + 1]
                    segment_distance = geodesic((start[1], start[0]), (end[1], end[0])).meters
                    
                    while total_distance + segment_distance >= (current_chainage_km * 1000) - (start_chainage * 1000):
                        if end_chainage and current_chainage_km > end_chainage:
                            break  # Stop if we reach the end chainage
                        
                        remaining_distance = (current_chainage_km * 1000) - (start_chainage * 1000) - total_distance
                        ratio = remaining_distance / segment_distance
                        intermediate_point = interpolate_point(start, end, ratio)
                        
                        chainage_str = format_chainage(current_chainage_km)
                        if chainage_str not in chainage_set:
                            chainage_markers.append(create_chainage_marker(intermediate_point, chainage_str))
                            chainage_set.add(chainage_str)
                        
                        current_chainage_km += segment_length / 1000.0
                    
                    total_distance += segment_distance
                
                final_point = coordinates[-1]
                chainage_str = format_chainage(current_chainage_km) + " (Final)"
                if chainage_str not in chainage_set:
                    chainage_markers.append(create_chainage_marker(final_point, chainage_str))
                    chainage_set.add(chainage_str)
                
                new_features.append(feature)
                new_features.extend(chainage_markers)
        
        geojson_data['features'] = new_features
        
        with open(output_geojson_path, 'w') as f:
            geojson.dump(geojson_data, f, indent=4)

        print(f"✅ Process completed. Output saved to {output_geojson_path}")
    
    except Exception as e:
        print(f"❌ Error processing GeoJSON data: {e}")



def format_chainage(chainage_km):
    km, meter = divmod(int(chainage_km * 1000), 1000)
    if meter >= 990:
        km += 1
        meter = 0
    return f"{km}+{meter:03d}"

def interpolate_point(start, end, ratio):
    lon = start[0] + ratio * (end[0] - start[0])
    lat = start[1] + ratio * (end[1] - start[1])
    return (lon, lat)

def create_chainage_marker(point, chainage_label):
    return {
        "type": "Feature",
        "geometry": geojson.Point(point),
        "properties": {"chainage": chainage_label}
    }



#input_geojson = "C:/Users/tanmay.mishra/Desktop/siddhantpawar/infra/infra_solutions/Bhorkhedi_to_Wadner_Route/Bhorkhedi_to_Wadner_Route_new.kml.geojson"
#output_geojson = "output_with_chainage_every_100m.geojson"
#add_start_end_chainage_markers(input_geojson, output_geojson, start_chainage=36.6, end_chainage=174.510, segment_length=100)
