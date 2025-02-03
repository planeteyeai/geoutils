from geojson_to_kml import geojson_to_kml
from kmltogeojson import create_geojson_dir
from chainageutils import add_start_end_chainage_markers
from cnormalization import cnumoptimizer
import json
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_user_input(prompt: str) -> str:
    """Get user input and strip leading/trailing whitespace."""
    return input(prompt).strip()

def validate_file_path(path: str) -> bool:
    """Check if the given file path exists."""
    if not os.path.exists(path):
        logging.error(f"❌ File not found: {path}")
        return False
    return True

def process_kml_to_geojson():
    """Handle KML to GeoJSON conversion."""
    kml_path = get_user_input("Enter the path to the KML: ")
    if not validate_file_path(kml_path):
        return
    try:
        output_dir = create_geojson_dir(kml_path, separate_folders=True, style_type="leaflet")
        logging.info(f"✅ GeoJSON directory generated: {output_dir}")
    except Exception as e:
        logging.error(f"❌ Error generating GeoJSON directory: {e}")

def process_geojson_to_kml():
    """Handle GeoJSON to KML conversion."""
    geojson_path = get_user_input("Enter the path to the GeoJSON: ")
    if not validate_file_path(geojson_path):
        return
    try:
        geojson_to_kml(geojson_path)
        logging.info(f"✅ Successfully converted {geojson_path} to KML.")
    except Exception as e:
        logging.error(f"❌ Error converting GeoJSON to KML: {e}")

def process_chainage_addition():
    """Add chainage markers to a GeoJSON file."""
    input_geojson = get_user_input("Enter the input path to the GeoJSON: ")
    output_geojson = get_user_input("Enter the output path to the GeoJSON: ")

    if not validate_file_path(input_geojson):
        return

    try:
        add_start_end_chainage_markers(input_geojson, output_geojson, segment_length=100)
        logging.info(f"✅ Chainage markers added and saved to {output_geojson}")
    except Exception as e:
        logging.error(f"❌ Error adding chainage markers: {e}")

def process_chainage_optimization():
    """Optimize chainage number system."""
    input_geojson = get_user_input("Enter the input path to the GeoJSON: ").strip()
    output_geojson = get_user_input("Enter the output path to the GeoJSON: ").strip()

    # Validate input file
    if not validate_file_path(input_geojson):
        logging.error("❌ Invalid input file path. Please check the file and try again.")
        return

    try:
        optimized_geojson = cnumoptimizer(input_geojson, output_geojson)

        if optimized_geojson.empty or not validate_file_path(output_geojson):
            logging.error("❌ Chainage optimization failed. No valid output generated.")
            return

        
        logging.info(f"✅ Chainage optimization completed. Output saved to {output_geojson}")

        # Ask user if they want to convert to KML
        user_choice = get_user_input("Do you want to convert the output to KML? (yes/no): ").strip().lower()
        if user_choice in ("yes", "y"):
            try:
                geojson_to_kml(output_geojson)  # Using output_geojson instead of optimized_geojson for clarity
                logging.info("✅ Optimized GeoJSON converted to KML.")
            except Exception as e:
                logging.error(f"❌ Error converting to KML: {e}")
        else:
            logging.info("✅ Optimization complete. Check the optimized GeoJSON output.")

    except Exception as e:
        logging.error(f"❌ Error optimizing chainage number system: {e}", exc_info=True)
        
def main():
    """Main program loop for GeoJSON/KML processing."""
    while True:
        print("\nChoose an option:")
        print("1. Convert KML to GeoJSON")
        print("2. Convert GeoJSON to KML")
        print("3. Add chainage markers to GeoJSON")
        print("4. Optimize chainage number system")
        print("5. Quit")

        user_choice = get_user_input("Enter your choice: ")

        actions = {
            "1": process_kml_to_geojson,
            "2": process_geojson_to_kml,
            "3": process_chainage_addition,
            "4": process_chainage_optimization,
            "5": exit,
        }

        action = actions.get(user_choice)
        if action:
            action()
        else:
            logging.error("❌ Invalid choice. Please choose a valid option.")

if __name__ == "__main__":
    main()
