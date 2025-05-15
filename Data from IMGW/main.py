import pandas as pd
import requests
import os
import zipfile
from io import BytesIO

# WARNING: Assumes that the downloaded files fit comfortably into RAM for processing.

# Specify the years to download data for.
# Valid range is 1951 to 2022.
# For example, setting YEAR_START = YEAR_END = 2012
# will download data for the entire year 2012.
YEAR_START = 2008
YEAR_END = 2012


# Do not modify the base URL or scope.
BASE_URL = "https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_hydrologiczne/"
SCOPE = "dobowe"


def getData(url):
    try:
        # Download the ZIP file from the given URL
        response = requests.get(url)
        response.raise_for_status()
        # Load the ZIP content into RAM as bytes
        zip_bytes = BytesIO(response.content)

        # Open the ZIP archive from in-memory bytes
        with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
            # Extract the first file from the ZIP archive (assumed to be a CSV)
            csv_name = zip_ref.namelist()[0]
            
            with zip_ref.open(csv_name) as csv_file:
                # Attempt to read the CSV file into a pandas DataFrame using different encodings
                try:
                    df_new = pd.read_csv(csv_file, usecols=range(10), header=None)  # Try utf-8
                except UnicodeDecodeError:
                    csv_file.seek(0)
                    try:
                        df_new = pd.read_csv(csv_file, usecols=range(10), header=None, encoding='cp1250')  # Try Windows-1250 encoding (Central European)
                    except UnicodeDecodeError:
                        csv_file.seek(0)
                        df_new = pd.read_csv(csv_file, usecols=range(10), header=None, encoding='iso-8859-2')  # Try ISO-8859-2 encoding (alternative Central European)
        
        df_new = df_new.dropna(axis=1, how='all')
        if df_new.shape[1] != 10:
            print(f"Error with number of colums:\n{url}\n")

        return df_new
    

    except requests.exceptions.RequestException as e:
        print(f"Error with the request: {e}")
        raise
    
    except zipfile.BadZipFile:
        print(f"Error: The downloaded file is not a valid ZIP file.")
        raise
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise



################# main #################

# cols = ["Kod stacji", "Nazwa stacji", "Nazwa rzeki/jeziora", "Rok hydrologiczny", "Wskaźnik miesiąca w roku hydrologicznym", "Dzień", "Stan wody [cm]", "Przepływ [m^3/s]", "Temperatura wody [st. C]", "Miesiąc kalendarzowy"]
dfs = []

for year in range(YEAR_START, YEAR_END+1):
    for month in range(1, 13):
        # Construct ZIP filename based on year and month
        zip_name = f"codz_{year}_{month:02d}.zip"
        url_to_zip = f"{BASE_URL}{SCOPE}/{year}/{zip_name}"

        try:
            dfs.append(getData(url_to_zip))

        except Exception as e:
            print(f"Error while processing file {zip_name}: {e}")
            continue


result = pd.concat(dfs, ignore_index=True)

# Directory to save files (same location as this script)
base_dir = os.path.dirname(os.path.abspath(__file__))
downloads_dir = os.path.join(base_dir, "downloads")
os.makedirs(downloads_dir, exist_ok=True)


# Write the combined DataFrame to a CSV file in the 'downloads' folder
output_file_name = f"{SCOPE}_from_{YEAR_START}_to_{YEAR_END}.csv"
output_path = os.path.join(downloads_dir, output_file_name)
result.to_csv(output_path, index=False)

print(f"Zapisano do: {output_path}")