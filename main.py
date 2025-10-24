from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

app = FastAPI(title="Selenium Scraper API")


def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


@app.get("/scrape/startradingagency")
def scrape_star_trading():
    driver = get_driver()
    driver.get("https://www.startradingagency.com/")

    time.sleep(5)  #wait for JS to load images

    selectors = [
        ".prdRngImg.dflx.bdr1.mb15.brds5",
        ".hPi.dflx.bd.pa.zi2",
    ]

    image_urls = set()
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for el in elements:
            imgs = el.find_elements(By.TAG_NAME, "img")
            for img in imgs:
                src = img.get_attribute("src")
                if src:
                    image_urls.add(src)

    driver.quit()
    return {"source": "StarTradingAgency", "count": len(image_urls), "images": list(image_urls)}


@app.get("/scrape/tradeindia")
def scrape_trade_india():
    driver = get_driver()
    driver.get("https://www.tradeindia.com/")

    wait = WebDriverWait(driver, 15)

    #Product Cards
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "div.col-md-4.col-lg-4.col-xl-2.col-6.mb-4.custom-width")
    ))
    cards = driver.find_elements(By.CSS_SELECTOR, "div.col-md-4.col-lg-4.col-xl-2.col-6.mb-4.custom-width")

    products = []
    for div in cards:
        title, img = None, None
        try:
            img = div.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            pass
        try:
            title = div.find_element(By.CSS_SELECTOR, "h2.sc-3b1eb120-11.RqywW.mb-1.card_title.Body3R").text
        except:
            pass
        if title or img:
            products.append({"title": title, "img": img})

    #Category Blocks
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.sc-d85ada4f-0.lkGGgy")))
    categories = driver.find_elements(By.CSS_SELECTOR, "div.sc-d85ada4f-0.lkGGgy")

    category_data = []
    for cat in categories:
        try:
            img_url = cat.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            img_url = None

        try:
            head_text = cat.find_element(By.CSS_SELECTOR, "a.head").text
        except:
            head_text = None

        try:
            subcats = [a.text for a in cat.find_elements(By.CSS_SELECTOR, "a.sub-cat") if a.text.strip()]
        except:
            subcats = []

        category_data.append({
            "head": head_text,
            "img": img_url,
            "subcategories": subcats
        })

    driver.quit()
    return {
        "source": "TradeIndia",
        "products": products,
        "categories": category_data
    }
