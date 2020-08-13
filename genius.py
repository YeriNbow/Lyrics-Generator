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

    base_url = 'https://genius.com/artists/'

    # selenium webdriver option
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-gpu')

    wd_path = 'D:/IT/mywork/chromedriver.exe'
    xpath = '/html/body/routable-page/ng-outlet/routable-profile-page/ng-outlet/routed-page/profile-page/' \
            'div[3]/div[2]/artist-songs-and-albums/div[3]'

    def __init__(self, artist):
        self.artist_url = GeniusScraper.base_url + artist.replace(' ', '-').lower().capitalize()

    def get_urls(self):
        driver = webdriver.Chrome(GeniusScraper.wd_path, options=GeniusScraper.options)
        driver.get(self.artist_url)

        driver.find_element_by_xpath(GeniusScraper.xpath).click()
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
    page = requests.get(lyrics_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    lyrics1 = soup.find("div", class_="lyrics")
    lyrics2 = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-2 jgQsqn")

    if lyrics1:
        return lyrics1.get_text()
    elif lyrics2:
        return lyrics2.get_text()
    elif lyrics1 and lyrics2 is None:
        return None


def get_title(artist, url):
    artist = artist.capitalize().replace(' ', '-')
    regex = re.compile(artist + '-(.*?)-lyrics')
    title = ''.join(regex.findall(url)).replace('-', ' ')
    return title
