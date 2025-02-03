import os
import json
import logging
import simplekml

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

def geojson_to_kml(input_path, output_path='output.kml'):
    """
    Converts a GeoJSON file to a KML file, using properties to name features.
    
    Args:
        input_path (str): Path to the input GeoJSON file.
        output_path (str): Path to save the output KML file (default: 'output.kml').
    """
    try:
        # Check if input file exists
        if not os.path.isfile(input_path):
            logging.error(f"❌ ERROR: File not found: {input_path}")
            return
        
        # Open and parse the GeoJSON file
        with open(input_path, encoding='utf-8') as f:
            data = json.load(f)

        # Initialize KML object
        kml = simplekml.Kml()

        # Iterate over each feature in the GeoJSON
        for feature in data.get('features', []):
            geom = feature.get('geometry', {})
            geom_type = geom.get('type')
            coords = geom.get('coordinates', [])
            properties = feature.get('properties', {})

            name = properties.get('name') or properties.get('chainage') or "Unnamed"
            description = properties.get('description', 'No description available')

            # Convert geometry types to KML
            if geom_type == 'Polygon' and coords:
                if len(coords) > 0:  # Ensure valid polygon coordinates
                    kml.newpolygon(
                        name=name,
                        description=description,
                        outerboundaryis=coords[0]
                    )
                else:
                    logging.warning(f"⚠️ Invalid coordinates for Polygon: {name}")
            elif geom_type == 'LineString' and coords:
                if len(coords) > 1:  # Ensure valid line coordinates
                    kml.newlinestring(
                        name=name,
                        description=description,
                        coords=coords
                    )
                else:
                    logging.warning(f"⚠️ Invalid coordinates for LineString: {name}")
            elif geom_type == 'Point' and coords:
                if len(coords) == 2:  # Ensure valid point coordinates (longitude, latitude)
                    kml.newpoint(
                        name=name,
                        description=description,
                        coords=[coords]
                    )
                else:
                    logging.warning(f"⚠️ Invalid coordinates for Point: {name}")
            else:
                logging.warning(f"⚠️ Unsupported geometry type: {geom_type} for {name}")

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            logging.info(f"Creating output directory: {output_dir}")
            os.makedirs(output_dir)

        # Save the KML file
        kml.save(output_path)
        logging.info(f"✅ KML file successfully created: {output_path}")

    except json.JSONDecodeError:
        logging.error(f"❌ ERROR: Invalid JSON format in file: {input_path}", exc_info=True)
    except Exception as e:
        logging.error(f"❌ ERROR: An unexpected error occurred: {str(e)}", exc_info=True)
