import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S"
)

def create_geojson_dir(filepath: str, separate_folders: bool = True, style_type: str = None) -> str:
    """
    Converts a KML file to a GeoJSON directory using the k2g tool.

    Args:
        filepath (str): Path to the input KML file.
        separate_folders (bool): Whether to create separate folders for each file. Defaults to True.
        style_type (str): Optional; style type for the output GeoJSON.

    Returns:
        str: Path to the generated GeoJSON directory or None on failure.
    """

    # Validate input file
    if not os.path.isfile(filepath):
        logging.error(f"❌ Input file not found: {filepath}")
        return None

    filename = os.path.basename(filepath)
    dirname = os.path.splitext(filename)[0]
    output_dir = os.path.join(os.path.dirname(filepath), dirname)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Construct command
    command = ["k2g", filepath, output_dir]
    if separate_folders:
        command.append("--separate-folders")
    if style_type:
        command.extend(["--style-type", style_type])

    try:
        # Run the command securely
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Log output and errors
        if result.stdout:
            logging.info(result.stdout)
        if result.stderr:
            logging.warning(result.stderr)

        logging.info(f"✅ GeoJSON directory created: {output_dir}")
        return output_dir

    except FileNotFoundError:
        logging.error("❌ 'k2g' command not found. Ensure it is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ GeoJSON conversion failed for '{filename}': {e.stderr}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

    return None
