# Pizza Kitchen

Welcome Paisano to the Pizza Kitchen!

## 🍕 Pizza Shud B free

This repository makes pizzas. More specifically, it accepts json input, transforms it and then passes it into the rendering pieline for some 🤌 fresh apizza pie. A Chainlink oracle is also included that can fire off requests to bake a pizza.

## 💻 Requirements

> NOTE:<br>
> 🐳 = required for running with Docker.<br>
> 🐍 = required for running with Python.

- 🐳🐍 [GNU Make](https://www.gnu.org/software/make/manual/make.html) is used to simplify the commands and GitHub Actions. This approach is recommended to simplify the command line experience. This is built in for MacOS and Linux. We arent supporting windoze right meow
- 🐍 [Python 3.8](https://www.python.org/downloads/) is <ins>**required**</ins> to develop this API. If you uses multiple versions of python, dont. But if you insist, [pyenv](https://github.com/pyenv/pyenv) will make your life easier.
- https://www.postman.com/downloads/

## 🐳 Running with Docker

### Developing locally with Docker

Copy the .env.example file and rename it .env. You must fill in the Ethereum socket server with a Rinkeby websocket from [Alchemy.com](http://alchemy.com).

Run Docker on your machine before the next step.

Run the dev deployment:

```bash
make docker-dev
```

After either command, you will find the API running at http://127.0.0.1:8000

### 📮 Postman

A Postman collection is also available to test the API located in the `.postman` folder. You can do a few things with this:

- [Import into Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman) for easy manual testing.
- Also, import the default environment to get you started 👆 RTFM

// TODO: add autmoated test instructions

## 🧪 Testing

### Testing the chainlink oracle

Spin everything up:

```
make docker-dev
```

navigate to `http://localhost:6688` and log into the chainlink interface (using the info in `./chainlink/.api.credentials.rinkeby`).
Select Bridges from the top menu bar and create a new bridge:

```
Name	orderpizzav1
URL	http://pizza-oven:8000/api/v1/diningroom/order
Confirmations	0
Minimum Contract Payment	0
```

make note of the incoming and outgoing access tokens, we'll need them later!

Select the Jobs tab from the top menu bar and create a new job:

```
{
  "name": "Order Pizza Web Initiator",
  "initiators": [
    {
      "type": "web"
    }
  ],
  "tasks": [
    {
      "type": "orderpizzav1",
      "params": {
        "address": "0xSOMETHING"
      }
    }
  ]
}
```

run the job, and then inspect the json response and verify that it is set to "pending".

TODO: verify that the job posts back and completes when finished and the result looks lomething like this:

```
"result": {
    "data": {
      "address": "0xSOMETHING",
      "artwork": "QmZ4q72eVU3bX95GXwMXLrguybKLKavmStLWEWVJZ1jeyz"
    },
    "error": null
  },
```



##  Python OrderAPI

### Rendering local test pies with Postman

We will spin up a server on your local machine running the pizza oven python app. Postman will allow you to send requests to the app to build out a test pie.

#### Checkout and start server
1. Checkout the feature/Gsheets branch
2. Make sure you have access to the following Google sheets:

	[**Pizza Types/Recipes**](https://docs.google.com/spreadsheets/d/1wHfP2I1m8_TV5tZt3FchI_zYgzZg9AomU7GOkof7TW8/edit?pli=1#gid=194105029) (owned by OmakaseChef)

	[**Ingredient List**](https://docs.google.com/spreadsheets/d/1xN149zkgSXPfJhDwQrIzlMzcU9gB--ihdoO_XJXCqf0/edit#gid=656807894) (owned by Snax)


3. Navigate to the root project folder and make the python environmernt
```bash
make environment
```
4. Start the local server
```bash
make start
```

#### Postman Setup
1. Download and install - [**Postman Downloads**](https://www.postman.com/downloads/)
2. In Postman, import the collection from the .postman folder in the root directory - 'Pizza Kitchen.postman_collection.json' (this folder is hidden by default)
3. You should see a list of calls in your collection. You are ready to run pies!
4. Pull all the remote Google sheets data and store it locally<br>
Send  `dining_room —> dining_setup`<br>
if URL is blank use:  <i>({{pizza-kitchen-url}}/api/{{version}}/dining_setup)</i><br>
You only need to do this once. Run it again to update the local json recipes if remotes have changed

5. Make a pizza pie<br>
	Send  `dining_room —> orderPizza`<br>
Might take a minute or so, but you should see a pizza show up in the output folder in the root directory. Naming convention is unique-id_recipe-type_randomseed.png (0_Raw pies_4D01DE56.png)


##### All done. Enjoy!



Google Authentication error:
A google login is required to pull data from a shared sheet. There is currently a token stored in /data to be used for this. It sometimes expires, and the app flow to login again fails. Make sure you have the latest token from the repo. Eventually we will need to fiugre out a better solution here… Suggestions welcome.

Note:
-If you receive a “file not found” error related to the “output” folder you may need to manually create a folder named “output” in the root directory of the project
-The pizza will render, but the app will finish the process by throwing an ipfs error. Chances are, there is no ipfs service up and running, so the app will complain. This is ok, you can continue to generate pizzas.

## 🐍 Running with Python

### 🏃🏽 Quick Start

Using [**make**](https://www.gnu.org/software/make/manual/make.html), installation and startup can be run with one command:

To set up the environment:

```bash
make environment
```

To start the api:

```bash
make start
```

### 🐛 Debugging

For local debugging with Visual Studio Code, just run it from the dropdown in the Run menu. Once the server is up, you can easily hit your breakpoints.

If the code fails to run, [make sure your Python interpreter is set](https://code.visualstudio.com/docs/python/environments) to use your poetry environment.
