import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json
import time
import logging


class Scraper:
    
    '''
    default init function
    '''
    def __init__(self, url):
        self.url = 'https://steamdb.info/search/?a=app&q=&type=1&category=2'
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=2560,1440")
        chrome_options.add_argument("--disable-gpu")
        
        # Using Dylan's user agent
        chrome_options.add_argument('--user-agent=SteamDB-Educational-Access; patel.4091@osu.edu')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("https://steamdb.info")
  
        cookies_list = [
        {'name':'__Host-steamdb', 'value':'0%3B5950181%3B35582c901f5518c7dfc98cb81395104d591cc4b2'},
        {'name':'cf_clearance', 'value':'PIW03jIrwTlESFuH8w5gXWW62vDk3RYrA8kQT_jz.gs-1707324281-1-ASg1nLhSHce6ClZlNpk7On/O0KCTYKum6JeYu4yc6PDMtOXMTk10SLTcZySog29tGSGBVVkyBC4bwfbxGl/ZD+c='},
        {'name':'__cf_bm', 'value':'0ZuOoVjeoHeaOT8b80uo90dZtD7Hcd0HmJGtW9NfFKE-1707324269-1-AafHYnSiWmnUl0giaQVV+eZXOUKBZ+/CfbXByf7GAg1unzWKMRyJueeZw9KPtxIuMIhEnfnaTsun0gVFwqwUTlA='}
        ]

        for cookie in cookies_list:
            self.driver.add_cookie(cookie)
        
        self.driver.get(url)
        
        #self.state: dict = self.get_state()

    '''
    Gets the state of the scraper from the state.json file
    '''
    def get_state(self):
        with open('state.json', 'r') as f:
            state = json.load(f)
        return state
    
    '''
    Saves the state of the scraper to the state.json file
    '''
    def save_state(self):
        with open('state.json', 'w') as f:
            json.dump(self.state, f)
        logging.info('State saved')
    
    '''
    Get links to all games
    '''
    def get_links(self):
        input_options = self.driver.find_element(By.ID, 'inputCategory').find_elements(By.TAG_NAME, 'option')
        input_options = [option.get_attribute('value') for option in input_options]
        input_options.remove('0')
        input_options = ["https://steamdb.info/search/?a=app&q=&type=1&category=" + option for option in input_options]
        
        for option in input_options:
            self.get_links_from_category(option)
        
        
        # return print("Started")
        
    '''
    Get links to all games in a category
    '''
    def get_links_from_category(self, category) -> list:
        all_IDs, pageCount = [], 0
        try:
            while True:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'ble-sortable')))
                appIDs = self.driver.find_element(By.ID, 'ble-sortable').find_elements(By.TAG_NAME, 'tr')
                appIDs = [appID.get_attribute('data-appid') for appID in appIDs]
                
                pageNum = int(self.driver.find_element(By.CSS_SELECTOR, '#table-sortable_paginate > nav > a.paginate_button.active').text)

                if pageNum == pageCount:
                    all_IDs += appIDs
                    if not self.next_page():
                        break
            
        except:
            logging.error('Could not find the table')
            return print('Could not find the table')
        self.driver.get(category)
        
    '''
    Clicks the next button to go to the next page
    '''
    def next_page(self):
        try:
            next_button = self.driver.find_element(By.ID, 'table-sortable_next')
            next_button.click()
            return True
            
        except:
            logging.error('Could not find the next button')
            return False
        
    '''
    Get the PlayTracker ID of a game
    '''
    def get_pt_id(self, url):
        time.sleep(2)
        self.driver.get(url)
        
        try:
            WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.ID, 'tab-charts')))
            self.driver.find_element(By.ID, 'tab-charts').click()
            pt_link = self.driver.find_elements(By.CLASS_NAME, 'app-chart-numbers')[-1]
            pt_link = [link.get_attribute('href') for link in pt_link.find_elements(By.TAG_NAME, 'a') if 'playtracker' in link.get_attribute('href')][0]
            return pt_link.split('/')[-1].rstrip('?utm_source=SteamDB')
        
        except NoSuchElementException as e: #NoSuchElementException
            logging.error('Could not find the PlayTracker ID for ' + url, "error: ", e)
            return "None"
        except TimeoutException as e: #TimeoutException
            logging.error('Timed out while looking for the PlayTracker ID for ' + url, "error: ", e)
            return "None"
        except Exception as e: #Any other exceptions
            logging.error('An error occurred while looking for the PlayTracker ID for ' + url, "error: ", e)
            return "None"
        

    '''
    Save a dataframe to a CSV file
    '''
    def saveToCSV(self, df, path):
        df.to_csv(path, index=False)
        logging.info('Dataframe saved to ' + path)
        print('Dataframe saved to ' + path)