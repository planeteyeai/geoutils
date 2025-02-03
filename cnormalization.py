import geopandas as gpd
import pandas as pd
import re
import logging

# Configure logging for debugging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.DEBUG,  # Change to DEBUG for detailed logs
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_geojson(file_path):
    """Load a GeoJSON file into a GeoDataFrame."""
    logging.info(f"Loading GeoJSON file from: {file_path}")
    try:
        gdf = gpd.read_file(file_path)
        logging.info(f"GeoDataFrame loaded successfully with {len(gdf)} records.")
        return gdf
    except Exception as e:
        logging.error(f"Error loading GeoJSON file: {e}")
        return None

def drop_columns(gdf, columns_to_drop):
    """Drop specified columns from the GeoDataFrame."""
    logging.info(f"Dropping columns: {columns_to_drop}")
    columns_before = gdf.columns.tolist()
    gdf = gdf.drop(columns=columns_to_drop, errors='ignore')
    columns_after = gdf.columns.tolist()
    logging.info(f"Columns before: {columns_before}")
    logging.info(f"Columns after: {columns_after}")
    return gdf

def normalize_chainage(chainage):
    """Normalize chainage values."""
    if chainage is None:
        logging.warning("Chainage is None, skipping normalization.")
        return None

    match = re.match(r"(\d+)\+(\d+)", str(chainage))
    if not match:
        logging.warning(f"Chainage '{chainage}' does not match the expected format.")
        return chainage

    km = int(match.group(1))
    m = int(match.group(2))
    
    if m == 99:
        normalized_chainage = f"{km+1}+000"
    elif m % 100 == 99:
        normalized_chainage = f"{km}+{m - 99 + 100:03}"
    else:
        normalized_chainage = chainage
    
    logging.debug(f"Normalized chainage: {chainage} -> {normalized_chainage}")
    return normalized_chainage

def normalize_chainage_column(gdf):
    """Normalize the 'chainage' column in the GeoDataFrame."""
    logging.info("Normalizing chainage column.")
    if 'chainage' in gdf.columns:
        gdf['chainage'] = gdf['chainage'].apply(normalize_chainage)
        logging.info("Chainage normalization completed.")
    else:
        logging.error("Chainage column not found in GeoDataFrame.")
    return gdf

def save_geojson(gdf, output_file):
    """Save the GeoDataFrame as a GeoJSON file."""
    logging.info(f"Saving GeoDataFrame to GeoJSON file: {output_file}")
    try:
        gdf.to_file(output_file, driver='GeoJSON')
        logging.info(f"GeoJSON file saved successfully: {output_file}")
    except Exception as e:
        logging.error(f"Error saving GeoJSON file: {e}")

def cnumoptimizer(file_path, output_file):
    """Optimize the chainage number system."""
    logging.info(f"Starting chainage optimization for file: {file_path}")
    
    # Load GeoJSON file
    gdf = load_geojson(file_path)
    if gdf is None:
        return

    # Drop unnecessary columns
    gdf = drop_columns(gdf, ['name', 'styleUrl'])

    # Normalize chainage
    gdf = normalize_chainage_column(gdf)

    # Save the modified GeoDataFrame to a new GeoJSON file
    save_geojson(gdf, output_file)

    return gdf

