import json, time, argparse, os, logging, datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import FirefoxOptions, ChromeOptions
from dotenv import load_dotenv
from os.path import join, dirname
from discord import Webhook, RequestsWebhookAdapter

############
## CONFIG ##
############

# Logging
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format='%(asctime)s %(message)s', 
    datefmt='%d/%m/%Y %I:%M:%S %p',
    level=logging.INFO
)

# Load env
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
DEFAULT_ITEM = os.getenv("DEFAULT_ITEM")
AVAILABILITY_VALUE = os.getenv("AVAILABILITY_VALUES")
TIMEOUT = int(os.getenv("TIMEOUT", 60))
ALERT_DELAY = float(os.getenv("ALERT_DELAY", 6))
ALERT_DELAY = 60 * 60 * ALERT_DELAY # hours to seconds
BROWSER = os.getenv("BROWSER", "Chrome")

# Load items from json
with open('items.json') as f:
  watchlist = json.load(f)
# Global variables
itemName = DEFAULT_ITEM
isAvailableValues = AVAILABILITY_VALUE.split(",") # Values that appear in the website when 1 or more products are available
lastTimestamp = datetime.datetime(1970, 1, 1)

# Browser setup
driver_path = os.path.abspath( os.getcwd())
if (BROWSER == "Firefox"):
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    driver = webdriver.Firefox(executable_path=join(driver_path, "geckodriver"), options=opts)
elif (BROWSER == "Chrome"):
    opts = ChromeOptions()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=join(driver_path, "chromedriver"), options=opts)
else:
    logging.info(f"{BROWSER} browser is not supported yet")
    print(f"{BROWSER} browser is not supported yet")
    os._exit(1)

webhook = Webhook.from_url(WEBHOOK, adapter=RequestsWebhookAdapter())

###############
## FUNCTIONS ##
###############

def startup():
    try:
        driver.get(watchlist[itemName]["url"]) # Downloads HTML page
        time.sleep(2) # Just to be sure the page is loaded and ready
        driver.find_element_by_id("didomi-notice-agree-button").click() # Clicks 'accept cookies'
    except Exception as e:
        logging.error(e)
        driver.refresh()
        time.sleep(1)
        startup()

def parseArgs():
    global itemName
    parser = argparse.ArgumentParser(description='Decathlon Alerts')
    parser.add_argument("--item", default=DEFAULT_ITEM)
    args = parser.parse_args()
    itemName = args.item

def product_checker():
    driver.refresh()
    time.sleep(2) # Just to be sure

    try: 
        # Product info parse
        content = driver.find_element_by_class_name("product-summary").get_attribute("outerHTML") # Gets HTML content
        soup = BeautifulSoup(content, 'html.parser')
        soup.encode('utf-8')
        driver.find_element_by_class_name("svelte-h9duyn").click() # Clicks dropdown list with sizes and availabilities
        time.sleep(0.5)
        title = soup.find(class_="title").get_text() # Name of the product (just to check)
        price = soup.find(class_='prc__active-price')['data-price'] # Price of the product (for additional info)

        # Size availability parse
        size = driver.find_element_by_id(watchlist[itemName]["target_size"]).get_attribute("outerHTML") # Get HTML content of dropdown option with correct size
        partial = BeautifulSoup(size, 'html.parser') # Parse again the new partial content  
        available = partial.find(class_='stock').get_text() # Get InnerHTML text
        size = partial.find(class_='size').get_text() # Get size text
        
        # Availability check
        if available.strip().lower() in isAvailableValues: # Checks if that size is available
            send_notification(title, price, size)
        else:
            logging.info("Product not available yet")
    except Exception as e:
        # Catch errors and refresh. This is needed for example when the website is on maintenance and the parsing fails
        logging.error(e)
        driver.refresh()

def send_notification(title, price, size):
    global lastTimestamp

    if (shoud_send_alert()):
        text = f'{title} (size {size}) is available at {price} €'
        logging.info(text)
        logging.info('Sending notification...')
        webhook.send(text)
        lastTimestamp = datetime.datetime.now()
    else:
        logging.info('Item is available but not enough time is passed since the last notification')

def shoud_send_alert():
    return date_difference() > ALERT_DELAY

def date_difference():
    diff = datetime.datetime.now() - lastTimestamp
    return diff.total_seconds()

################
## ENTRYPOINT ##
################

if __name__ == '__main__':

    logging.info("Bot starting...")
    print("Bot starting...")

    parseArgs()
    startup()

    logging.info(f"Bot will check item '{itemName}' every {TIMEOUT} seconds")
    print(f"Bot will check item '{itemName}' every {TIMEOUT} seconds")

    while(True):
        logging.info("Checking product...")
        product_checker()
        time.sleep(TIMEOUT)