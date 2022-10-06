from dataclasses import dataclass
import json
import time
import sys
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import numpy as np



def read_credentials():
    # secrets JSON file reader
    secrets = 'secrets.json'
    with open(secrets) as f:
        keys = json.loads(f.read())
        return keys


@dataclass
class Task:
    name: str
    link: str


class FXBookScraper():
    def __init__(self, login, password) -> None:
        self.login = login
        self.password = password
        self.base_url = "https://www.myfxbook.com/login?"
        # set_browser_as_incognito(options)
        self.COMMAND_OR_CONTROL = Keys.COMMAND if sys.platform == 'darwin' else Keys.CONTROL

        service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)

    
    def try_code(self):
        self.login_to_fxbook()
        self.open_correlation_page()
        self.get_that_data()
        self.driver.quit()


    def login_to_fxbook(self):
        self.driver.get(self.base_url)
        self.put_credentials_to_form()
        self.deal_with_popup()

    
    def put_credentials_to_form(self):
        try:
            self.driver.find_element(By.ID,"loginEmail").send_keys(self.login)
            time.sleep(3)
            password_field = self.driver.find_element(By.ID,"loginPassword")
            password_field.send_keys(self.password)
            time.sleep(3)
            password_field.submit()
            time.sleep(3)
        
        except NoSuchElementException:
            print("Exception No Such Element Exists")


    def deal_with_popup(self):
        try:
            time.sleep(5)
            self.driver.find_element(By.XPATH,'//a[contains(@class,"bold color-white")]').click()
            print("Element found")
            time.sleep(5)

        except NoSuchElementException:
            print("Incorrect page")
    
    # DON'T NEED THIS FOR FINAL CODE
    def open_correlation_page(self):
        try:
            self.driver.find_element(By.LINK_TEXT,"Correlation").click()
            print("Correlation page opened")
            time.sleep(5)
        except NoSuchElementException:
            print("cannot find page")


    def get_that_data(self):
        url = "https://www.myfxbook.com/forex-market/correlation"
        page = requests.get(url)

        # Verify successful get request
        if page.status_code == requests.codes.ok:
            print('Page found')
            # Get the whole page
            soup = BeautifulSoup(page.text, 'lxml')
        else:
            print("Can't open page")
        
        table1 = soup.find('table', id='correlationTable')

        # Obtain every title of columns with tag <th>
        headers = []
        for i in table1.find_all('th'):
            title = i.text
            headers.append(title)
        
        mydata = pd.DataFrame(columns=headers)

        # Create a for loop to fill mydata
        for j in table1.find_all('tr')[0:]:
            row_data = j.find_all('td')
            row = [i.text for i in row_data]
            length = len(mydata)
            mydata.loc[length] = row

        mydata.to_csv('fxbook_scrapetest.csv', index=False)

        print("Code Completed")


        
if __name__ == '__main__':
    credentials = read_credentials()
    bot = FXBookScraper(credentials['username'], credentials['password'])
    bot.try_code()

