# Decathlon Products Availability Alert

## 1. Install Python3

You need to have Python3 installed on your OS to make this bot work. Follow some online tutorial to set it up (example: <https://realpython.com/installing-python/>)

## 2. Install browser drivers

Install browser drivers based on your operating system, architecture and browser version:

* Chrome: <https://chromedriver.chromium.org/downloads>

* Firefox: <https://github.com/mozilla/geckodriver/releases>

Remember to change permissions:

        chmod 775 <path/to/driver>

## 3. Install dependencies

        pip install -r requirements.txt

## 4. Setup Discord webhook

* Open Discord and go to your server
* Create a new channel named _alerts_
* Right click on the channel name and click _Modifiy channel_
* Click on _Integrations_ and then on _New Webhook_
* Choose a name for your bot, then click on _Copy webhook url_
* This url is the `DISCORD_WEBHOOK_URL` parameter on the `.env` file

## 5. Run bot

        python main.py --item <item_name>

If you want to track more items, you can run as many bots you want. A new browser instance will be opened for every item the bot is tracking.

## 6. Track a new item

You need to add the new item to the `items.json` file:

        "<item_name>": {
            "url": "<item_url>",
            "target_size": "<id of the html element that wraps the size you want>"
        }

* **item_name**: the name you will use when you run the bot to track the item
* **item_url**: the decathlon web store url of the item you want to track
* **target_size**: this is the less user-friendly parameter to get. On the webpage of the item you want to track, open the dropdown list that shows all the sizes available. Here, right click with your mouse over the size you want and click _Inspect_ (or _Inspect Item_, or _Analyze_, depends on the browser you are using). The developer console will open and you will see something like this:

        <li id="option-product-size-selection-2" tabindex="0" role="option" data-index="2" aria-selected="true" class="svelte-h9duyn selected">
            <div class="size-option">
                <span class="size">M</span>
                <span class="stock no" aria-hidden="false">
                Indisponibile
                </span>
            </div>
        </li>

Double check that `<span class="size">M</span>` contains your target size (in this case _M_). The value we are looking for is the `id` inside the first HTML element  

    <li id="option-product-size-selection-2" tabindex="0" role="option" data-index="2" aria-selected="true" class="svelte-h9duyn selected">

so in our case `option-product-size-selection-2`.

Now you can track your new item by running:

        python main.py --item <new_item_name>

## 7. Deploy with Heroku (WORK IN PROGRESS)

At the moment, the app will run without args, so the bot will check the default item set on the enviroment variable. This means that to check multiple items, you need multiple apps deployed on Heroku with different env.

* Create a new Heroku app

* Go to settings and add to _Config Vars_ all the variables that were inside `.env`

* Deploy the app with Heroku CLI or directly from your forked/cloned GitHub repo

## 8. Deploy with Docker (WORK IN PROGRESS)

At the moment, the app will run without args, so the bot will check the default item set on the enviroment variable. This means that to check multiple items, you need multiple containers with different env. This is easier to do with Docker Compose.

        example docker-compose TODO