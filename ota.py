import requests
import os
import machine
import hashlib


class OTAUpdater:
    def __init__(self, repo_url):
        self.repo_url = repo_url
        if "www.github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent")
            self.repo_url = self.repo_url.replace("www.github","raw.githubusercontent")
        elif "github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent'")
            self.repo_url = self.repo_url.replace("github","raw.githubusercontent")            

    def update(self, filename):
        print(f"Checking for updates {filename}...")
        url = self.repo_url + filename
        print(f'Fetching file: {url}...')
        response = requests.get(url)
        print(f'Status code: {response.status_code}')
        print("Response:")
        print(response.text)
        if response.status_code != 200:
            return False

        new_file_hash = hashlib.sha256(response.text).digest()
        with open(filename, 'rb') as f:
            current_file_hash = hashlib.sha256(f.read()).digest()

        print(f'Current version is {current_file_hash}')
        print(f'Latest version is: {new_file_hash}')

        if current_file_hash != new_file_hash:
            print('New updates available.')
            print(f'Overwriting {filename}...')
            with open('latest_code.py', 'w') as f:
                f.write(response.text)
            os.rename('latest_code.py', filename)
            # print('Restarting device...')
            # machine.reset()
        else:
            print('No new updates available.')
            return False
