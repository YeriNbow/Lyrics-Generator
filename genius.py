import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


class GeniusScraper:
    """
    Scrape lyrics from Genius website 
    """

    WD_PATH = 'D:/IT/mywork/chromedriver.exe'

    BASE_URL = 'https://genius.com/artists/'
    XPATH = '/html/body/routable-page/ng-outlet/routable-profile-page/ng-outlet/routed-page/profile-page/' \
            'div[3]/div[2]/artist-songs-and-albums/div[3]'

    # selenium webdriver option
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument('--headless')
    OPTIONS.add_argument('--no-sandbox')
    OPTIONS.add_argument('--disable-dev-shm-usage')
    OPTIONS.add_argument('disable-gpu')

    def __init__(self, artist):
        self.artist_url = GeniusScraper.BASE_URL + artist.replace(' ', '-').lower().capitalize()

    def get_urls(self):
        driver = webdriver.Chrome(GeniusScraper.WD_PATH, options=GeniusScraper.OPTIONS)
        driver.get(self.artist_url)

        driver.find_element_by_xpath(GeniusScraper.XPATH).click()
        location = By.CSS_SELECTOR, 'a.mini_card.mini_card--small'

        wait(driver, 10).until(EC.visibility_of_element_located(location))
        current_len = len(driver.find_elements(*location))

        while True:
            # scroll down
            driver.find_element(*location).send_keys(Keys.END)
            driver.implicitly_wait(5)

            try:
                wait(driver, 3).until(lambda x: len(driver.find_elements(*location)) > current_len)
                current_len = len(driver.find_elements(*location))
                driver.implicitly_wait(5)
            except TimeoutException:
                lyrics_urls = [song.get_attribute('href') for song in driver.find_elements(*location)]
                driver.quit()
                break

        return lyrics_urls


def get_title_lyrics(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    regex = re.compile(r'– (.*?) Lyrics \| Genius Lyrics')
    title = ''.join(regex.findall(soup.title.get_text()))

    # sometimes web page structures are changing
    lyrics1 = soup.find('div', class_='lyrics')
    lyrics2 = soup.find('div', class_='Lyrics__Container-sc-1ynbvzw-2 jgQsqn')

    if lyrics1:
        return title, lyrics1.get_text()
    elif lyrics2:
        return title, lyrics2.get_text()
    elif lyrics1 and lyrics2 is None:
        return title, None
