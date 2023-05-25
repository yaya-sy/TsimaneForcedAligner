#!usr/bin/env python
# -*- coding: utf8 -*-
import logging
import os.path
import re
import sys
import json
import requests
from bs4 import BeautifulSoup
from distutils.util import strtobool
from urllib.parse import urlparse
from time import sleep

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)
DATA_MARKER = '__NEXT_DATA__'
DATA_PATTERN = r'__NEXT_DATA__\s*?=\s*?({.*?});'


class WaitUntilAttributeContains:
    def __init__(self, locator, attr, value):
        self._locator = locator
        self._attribute = attr
        self._attribute_value = value

    def __call__(self, driver):
        element = driver.find_element(*self._locator)
        if self._attribute_value in element.get_attribute(self._attribute):
            return element
        else:
            return False

def _get_selenium_cookies(driver):
    driver_cookies = driver.get_cookies()
    cookies = {cookie['name']:cookie['value'] for cookie in driver_cookies}
    return cookies


def _get_selenium_driver():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver


def _download_audio(driver, audio_src, output_directory, skip_done):
    parsed_url = urlparse(audio_src)

    # Get filename
    audio_filename = os.path.basename(parsed_url.path)
    raw_audio_filename = os.path.splitext(audio_filename)[0]

    try:
        data = requests.get(audio_src, cookies=_get_selenium_cookies(driver))
        if data.status_code == 200:
            output_path = os.path.join(output_directory, audio_filename)
            if not os.path.exists(output_path) or not skip_done:
                with open(output_path, 'wb') as out_mp3:
                    out_mp3.write(data.content)
        return True, raw_audio_filename
    except:
        return False, raw_audio_filename


def _parse_json_data(payload):
    bible_books = re.match(DATA_PATTERN, payload)

    if not bible_books:
        return False

    # Get JSON data
    bible_data = json.loads(bible_books.group(1))
    return bible_data


def _find_json_payload(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    res = soup.find_all('script')

    for script_tag in res:
        script_tag_value = script_tag.text

        if DATA_MARKER not in script_tag_value: continue

        return _parse_json_data(script_tag_value)
    return False


def _dump_transcriptions(raw_transcriptions, output_directory, raw_filename, skip_done):
    lines = []
    for verse in raw_transcriptions:
        verse_id = verse['verse_start']
        verse_text = verse['verse_text']

        verse_text = verse_text.strip().replace('', '').replace('\r', '')
        lines.append('{}\t{}'.format(verse_id, verse_text))

    full_outpath = os.path.join(output_directory, '{}.txt'.format(raw_filename))
    if not os.path.exists(full_outpath) or not skip_done:
        with open(full_outpath, 'w') as out_file:
            out_file.write('\n'.join(lines))


def generate_urls(data):
    urls = []

    bible_language_code = data['bible_language_code']
    for book in data['books']:
        book_id = book['book_id']
        for chapter in book['chapters']:
            url_value = '{}/{}/{}'.format(bible_language_code, book_id, chapter)
            urls.append(url_value)
    return urls


def download_data(url_root, urls, output_directory, skip_done):
    driver = _get_selenium_driver()

    errors_audio = []
    errors_text = []
    for i_url, target_url in enumerate(urls, 1):
        full_url = '{}/{}'.format(url_root, target_url)

        driver.get(full_url)
        WebDriverWait(driver, 30).until(WaitUntilAttributeContains((By.CLASS_NAME, "audio-player"), 'data-src', '.mp3'))

        # Download data
        try:
            # Download audio
            audio_player = driver.find_element(By.CLASS_NAME, 'audio-player')
            audio_src = audio_player.get_attribute('src')
            download_status, chapter_name = _download_audio(driver, audio_src, output_directory, skip_done)

            if not download_status:
                logger.error("[{}/{}] AUDIO URL '{}': KO".format(i_url, len(urls), full_url))
                errors_audio.append(full_url)
            else:
                logger.info("[{}/{}] AUDIO URL '{}': OK".format(i_url, len(urls), full_url))
            # Download text
            page_source = driver.page_source
            json_payload = _find_json_payload(page_source)

            if not json_payload:
                return False

            raw_transcriptions = json_payload['props']['pageProps']['chapterText']
            if raw_transcriptions:
                _dump_transcriptions(raw_transcriptions, output_directory, chapter_name, skip_done)
                logger.info("[{}/{}] TEXT URL '{}': OK".format(i_url, len(urls), full_url))
            else:
                logger.info("[{}/{}] TEXT URL '{}': KO".format(i_url, len(urls), full_url))
                errors_text.append(full)

        except:
            logger.error("Error while trying to locate audio player for URL '{}'".format(full_url))
            continue
        sleep(3)

    logger.info('Text Errors:\n{}'.format('\n'.join(errors_text)))
    logger.info('Audio Errors:\n{}'.format('\n'.join(errors_audio)))
    logger.info('Num. Text Errors = {}\nNum. Audio Errors={}'.format(len(errors_text), len(errors_audio)))


def get_language_data(url_page):
    page = requests.get(url_page)

    if page.status_code != 200:
        return False, False

    page_source = page.content

    raw_language_data = _find_json_payload(page_source)
    if raw_language_data:
        # Store the data we want
        bible_language_code = raw_language_data['props']['pageProps']["activeTextId"]
        iso_language_code = raw_language_data['props']['pageProps']["activeIsoCode"]
        language_name = raw_language_data['props']['pageProps']["activeLanguageName"]
        books = raw_language_data['props']['pageProps']['books']

        language_data = {
            'bible_language_code' : bible_language_code,
            'iso_language_code' : iso_language_code,
            'language_name': language_name,
            'books': books
        }

        url_root = url_page.split(bible_language_code)[0].rstrip('/') # Get first part of URL
        return language_data, url_root

    return False, False


def get_bible_language_data(page, output_directory, skip_done):
    # Try to see if we can any information on the language given the link
    language_data, url_root = get_language_data(page)
    if not language_data:
        logger.error("No data found!")
        sys.exit(0)

    logger.info("Found data for langauge '{}' (Bible code: '{}', ISO code '{}')".format(
        language_data['language_name'], language_data['bible_language_code'], language_data['iso_language_code']
    ))

    # Generate URLs
    generated_urls = generate_urls(language_data)
    logger.info("Generated {} URLs.".format(len(generated_urls)))

    # Ask for download
    download = strtobool(input('Download (y/n)? '))
    if download:
        full_output_directory = os.path.join(output_directory, language_data['bible_language_code'])
        os.makedirs(full_output_directory, exist_ok=True)
        download_data(url_root, generated_urls, full_output_directory, skip_done)


def main(**kwargs):
    get_bible_language_data(**kwargs)


def _parse_args(argv):
    import argparse

    parser = argparse.ArgumentParser(description='Download Bible.is data.')
    parser.add_argument('--page', required=True,
                        help='URL to a Bible.is Bible')
    parser.add_argument('--output-directory', default='',
                        help="Path where the output directory should be store. Default: '.'.")
    parser.add_argument('--skip-done', action="store_true", default=False,
                        help="If --skip-done, existing files are skipped rather than re-downloaded.")
    args = parser.parse_args(argv)

    return vars(args)


if __name__ == '__main__':
    import sys
    pgrm_name, argv = sys.argv[0], sys.argv[1:]
    args = _parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    main(**args)