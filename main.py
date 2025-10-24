from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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

    time.sleep(5)  # wait for JS to load images

    # prdRngPrdWrap elements stored in a list of dicts
    products = []
    product_wraps = driver.find_elements(By.CSS_SELECTOR, ".prdRngPrdWrap.p10.pb35.mb40.pr.brds5")
    for wrap in product_wraps:
        product_data = {"image": [], "title": "", "bullets": []}

        # Images
        imgs = wrap.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src")
            if src:
                product_data["image"].append(src)

        # Title
        try:
            title_el = wrap.find_element(By.CSS_SELECTOR, ".fwb.fs20.clr2.lh6.pl20.pr20.mb15.ls1.prdRngHdng h3 a")
            product_data["title"] = title_el.text.strip()
        except:
            pass

        # Bullets
        try:
            bullets = wrap.find_elements(By.CSS_SELECTOR, "ul.ls1.pb10 li a")
            for b in bullets:
                text = b.text.strip()
                if text:
                    product_data["bullets"].append(text)
        except:
            pass

        products.append(product_data)

    # .hPi.dflx.bd.pa.zi2 images stored in a set 
    special_images = set()
    special_elements = driver.find_elements(By.CSS_SELECTOR, ".hPi.dflx.bd.pa.zi2")
    for el in special_elements:
        imgs = el.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src")
            if src:
                special_images.add(src)

    driver.quit()
    return {
        "source": "StarTradingAgency",
        "detailed_count": len(products),
        "detailed_data": products,
        "images_only_count": len(special_images),
        "only_images": list(special_images)
    }

@app.get("/scrape/tradeindia")
def scrape_trade_india():
    driver = get_driver()
    driver.get("https://www.tradeindia.com/")

    wait = WebDriverWait(driver, 60)

    #Product Cards
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.col-md-4.col-lg-4.col-xl-2.col-6.mb-4.custom-width")))
    except TimeoutException:
        driver.quit()
        return {"error": "Could not load page, maybe blocked by site"}

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
