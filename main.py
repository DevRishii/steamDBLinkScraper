import pandas as pd
import os
from SteamDBScraper import Scraper
import logging

if os.path.exists('DLC_scraper.log'):
    os.remove('DLC_scraper.log')
logging.basicConfig(filename='DLC_scraper.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


print('Setting up Scraper')
logging.info('Setting up Scraper')
scraper: Scraper = Scraper('https://steamdb.info/search/?a=app&q=&type=1&category=2')


folder_path = './csv-backup'

# List all CSV files in the folder and sorts them in ascending order
csv_files = sorted([file for file in os.listdir(folder_path) if file.endswith('.csv')])

# Initialize an empty dictionary to store dataframes
dataframes = {}

#Iterate over the list of files and read each CSV
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    dataframes[file] = pd.read_csv(file_path)

count = 0
i = 0
for df in dataframes:
    pt_ids = []
    df = dataframes[df]

    print(f'Getting PlayTracker IDs for {csv_files[i]}')
    logging.info(f'Getting PlayTracker IDs for {csv_files[i]}')
    
    for id in df['ID']:
        
        if isinstance(id, str):
            # ex: "236450,246250,246251,246252,246253,246254,246255,246256,246257"
            id = id.split(',')[0]
            url = 'https://steamdb.info/app/' + id
        else:
            url = 'https://steamdb.info/app/' + str(id)
        
        pt_ids.append(scraper.get_pt_id(url))
        
        count += 1
        
        if count % 1000 == 0:
            logging.info(f'Total saved games: {count} games')
            scraper.saveToCSV(df, f'./saved-info/{csv_files[i]}')
        
    df['PlayTrackerID'] = pt_ids
    
    
    print(f'Saving info to ./saved-info/{csv_files[i]}.csv')
    logging.info(f'Saving info to ./saved-info/{csv_files[i]}')
    scraper.saveToCSV(df, f'./saved-info/{csv_files[i]}')
    
    i += 1



