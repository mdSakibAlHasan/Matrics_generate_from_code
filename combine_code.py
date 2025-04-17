import os
import requests
from tqdm import tqdm
import time
import subprocess
import shutil
import sys
import pandas as pd
import tarfile

from os.path import join
from requests.exceptions import RequestException

# ----------- Metrics Generator Class -----------
class MetricsGenerator(object):
    def generate_metrics(self, folder_path, languages):
        und_db_path = f"{folder_path}.und"

        subprocess.check_output(f'und create -languages "{languages}" -db "{und_db_path}"', shell=True)
        subprocess.check_output(f'und add -db "{und_db_path}" "{folder_path}"', shell=True)
        subprocess.check_output(f'und analyze -db "{und_db_path}"', shell=True)

        with os.add_dll_directory("C:/Program Files/SciTools/bin/pc-win64"):
            sys.path.append("C:/Program Files/SciTools/bin/pc-win64/Python")
            import understand

            db = understand.open(und_db_path)
            metrics = db.metric(db.metrics())
            shutil.rmtree(und_db_path)

        version_name = os.path.basename(folder_path)
        metrics["version"] = version_name
        print(metrics)
        return metrics

# ----------- Download & Processing Functions -----------

def read_versions(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def generate_download_links(versions):
    links = []
    for version in versions:
        version_num = version.replace('v', '')
        major = version_num.split('.')[0]
        url = f"https://cdn.kernel.org/pub/linux/kernel/v{major}.x/linux-{version_num}.tar.xz"
        links.append((url, version_num))
    return links

def download_file(url, dest_path, max_retries=5, timeout=30):
    headers = {'User-Agent': 'Mozilla/5.0'}
    attempt = 0
    while attempt < max_retries:
        try:
            print(f"Attempting to download: {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, headers=headers, stream=True, timeout=timeout)
            response.raise_for_status()
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
            print(f"Successfully downloaded: {url}")
            return True
        except (RequestException, TimeoutError) as e:
            print(f"Error downloading {url}: {e}")
            attempt += 1
            wait_time = 2 ** attempt
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    print(f"Failed to download {url} after {max_retries} attempts.")
    return False

def extract_tar_xz(tar_path, extract_to):
    print(f"Extracting: {tar_path}")
    with tarfile.open(tar_path, 'r:xz') as tar:
        tar.extractall(path=extract_to)

# ----------- Main Logic -----------

def main():
    file_path = 'Linux_v5-6.txt'
    versions = read_versions(file_path)
    download_links = generate_download_links(versions)
    download_directory = r'D:/mahir/product specific exploit prediction/Script for zip/script for Linux zip/linux_zip_files'
    report_path = os.path.join(download_directory, "metrics_report.csv")
    os.makedirs(download_directory, exist_ok=True)

    metrics_generator = MetricsGenerator()
    header_written = os.path.exists(report_path)

    for url, version in tqdm(download_links, desc="Processing versions"):
        file_name = f"linux-{version}.tar.xz"
        tar_path = os.path.join(download_directory, file_name)
        extract_folder = os.path.join(download_directory, f"linux-{version}")

        # Download
        if not download_file(url, tar_path):
            continue  # Skip to next version if download fails

        # Extract
        extract_tar_xz(tar_path, extract_folder)

        # Analyze and get metrics
        try:
            data = metrics_generator.generate_metrics(extract_folder, languages="C++")
            df = pd.DataFrame([data])
            df.to_csv(report_path, mode='a', header=not header_written, index=False)
            header_written = True
        except Exception as e:
            print(f"Failed to process metrics for {version}: {e}")

        # Cleanup
        print(f"Cleaning up {extract_folder} and {tar_path}")
        shutil.rmtree(extract_folder)
        os.remove(tar_path)

        time.sleep(3)

if __name__ == "__main__":
    main()
