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

    BASE_URL = 'https://genius.com/artists/'

    WD_PATH = 'D:/IT/mywork/chromedriver.exe'

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


def get_lyrics(lyrics_url):
    response = requests.get(lyrics_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    lyrics1 = soup.find("div", class_="lyrics")
    lyrics2 = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")

    if lyrics1:
        return lyrics1.get_text()
    elif lyrics2:
        return lyrics2.get_text()
    elif lyrics1 and lyrics2 is None:
        return None


def get_title(url):
    regex = re.compile(r'– (.*?) Lyrics \| Genius Lyrics')

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = ''.join(regex.findall(soup.title.get_text()))

    return title
