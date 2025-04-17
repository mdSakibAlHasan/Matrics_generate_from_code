

import os
import requests
from tqdm import tqdm
import time
from requests.exceptions import RequestException

# Read the version numbers from the file
file_path = 'Linux_v5-6.txt'

def read_versions(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Generate the correct download links for each version
def generate_download_links(versions):
    return [f"https://web.git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/snapshot/linux-{version}.tar.gz" for version in versions]

# Function to download the file with progress bar and retry logic
def download_file(url, dest_path, max_retries=5, timeout=30):
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"Attempting to download: {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, stream=True, timeout=timeout)
            response.raise_for_status()  # Will raise an error for bad status codes (e.g., 4xx, 5xx)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(dest_path, 'wb') as file, tqdm(
                desc=dest_path,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024
            ) as bar:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        bar.update(len(chunk))
            
            # Successfully downloaded the file
            print(f"Successfully downloaded: {url}")
            return
        except (RequestException, TimeoutError) as e:
            print(f"Error downloading {url}: {e}")
            attempt += 1
            wait_time = 2 ** attempt  # Exponential backoff (2^attempt seconds)
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)  # Wait before retrying
    print(f"Failed to download {url} after {max_retries} attempts.")

# Main function
def main():
    versions = read_versions(file_path)
    download_links = generate_download_links(versions)
    download_directory = r'D:\mahir\product specific exploit prediction\Script for zip\script for Linux zip\linux_zip_files'
    os.makedirs(download_directory, exist_ok=True)
    
    for link in tqdm(download_links, desc="Downloading zip files"):
        file_name = link.split('/')[-1]  # Extract file name from URL
        dest_path = os.path.join(download_directory, file_name)
        
        try:
            download_file(link, dest_path)
            time.sleep(3)  # Wait for 3 seconds after each download
        except Exception as e:
            print(f"Failed to download {link}: {e}")

if __name__ == "__main__":
    main()
