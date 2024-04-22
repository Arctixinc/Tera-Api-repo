import os
import asyncio
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


async def teraBoxDl(url: str) -> str:
    baseurl = f'https://teradownloader.com/download?link={quote(url)}'
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    try:
        browser.get(baseurl)
        WebDriverWait(browser, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, 'div.p-5')))
        elements = browser.find_elements(By.CSS_SELECTOR, 'div.p-5 > a')
        download_link = elements[2].get_attribute('href')
        return download_link
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return ""
    finally:
        browser.quit()
