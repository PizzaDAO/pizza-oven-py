# Pizza Kitchen

Welcome Paisano to the Pizza Kitchen!

## 🍕 Pizza Shud B free

This repository makes pizzas. More specifically, it accepts json input, transforms it and then passes it into the rendering pieline for some 🤌 fresh apizza pie. A Chainlink oracle is also included that can fire off requests to bake a pizza. The application is developed in python and uses modern python development tools (e.g. Poetry for dependency management and FastAPI for serving up the api).

## 💻 Requirements

Be running Linux or MacOS

- 🐳🐍 [GNU Make](https://www.gnu.org/software/make/manual/make.html) is used to simplify the commands and GitHub Actions. This approach is recommended to simplify the command line experience. This is built in for MacOS and Linux. We arent supporting windoze right meow
- 🐍 [Python 3.8](https://www.python.org/downloads/) is <ins>**required**</ins> to develop this API. If you uses multiple versions of python, dont. But if you insist, [pyenv](https://github.com/pyenv/pyenv) will make your life easier.
- [postman](https://www.postman.com/downloads/) is used for issuing requests during development and testing
- [Docker](https://docs.docker.com/get-docker/) is used to make environment configuration easier
- - If you're running Ubuntu, you'll need to install [docker compose](https://docs.docker.com/compose/install/#install-compose-on-linux-systems)
- [Natron](https://github.com/NatronGitHub/Natron/releases/tag/v2.4.0) is used for rendering. ONLY NEEDED IF you plan to develop locally.

## 🐳 Running with Docker

The best way to get up and running quickly is to use docker.

### Verifying Access

The data in this application is primarily driven by a google sheet. You nheed to have access to that. or create your own.

Make sure you have access to the following Google sheets:

[**Pizza Types/Recipes**](https://docs.google.com/spreadsheets/d/1wHfP2I1m8_TV5tZt3FchI_zYgzZg9AomU7GOkof7TW8/edit?pli=1#gid=194105029) (owned by OmakaseChef)

[**Ingredient List**](https://docs.google.com/spreadsheets/d/1xN149zkgSXPfJhDwQrIzlMzcU9gB--ihdoO_XJXCqf0/edit#gid=656807894) (owned by Snax)

### Configuring Your Environment

The application uses python 3.8 or higher. There is a makefile to make configuration easier.

from the command line, run:

```bash
make environment
```

### 🐳 Developing locally with Docker

Copy the `.env.example` file and rename it `.env`. You must fill in the `ETHEREUM_RINKEBY_SOCKET_SERVER` with a Rinkeby websocket from [Alchemy.com](http://alchemy.com) or Infura.

Run Docker on your machine and make sure that the RAM in docker is set to at least 4gb

Run the dev deployment:

```bash
make docker-dev
```

the `docker-compose.dev.yml` file will spin up all of the infrastructure and will keep running until you exit (CTRL-C to exit.) The dev deployment also includes hot reloading and mounts folders in the proejct so you can see the data.

You will find the API running at http://127.0.0.1:8000

### 📮 Postman

A Postman collection is also available to test the API located in the `.postman` folder. This collection lets you call the api directly

1. Download and install - [**Postman Downloads**](https://www.postman.com/downloads/)
2. follow [Import into Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman) but steps generally are:
3. In Postman, import the collection from the .postman folder in the root directory - 'Pizza Kitchen.postman_collection.json' (this folder is hidden by default)
4. You should see a list of calls in your collection. You are ready to run pies!
5. Pull all the remote Google sheets data and store it locally<br>
   Send `dining_room —> dining_setup`<br>
   if URL is blank use: <i>({{pizza-kitchen-url}}/api/{{version}}/dining_setup)</i><br>
   You only need to do this once. Run it again to update the local json recipes if remotes have changed

6. Make a pizza pie<br>
   Send `dining_room —> orderPizza`<br>
   Might take a minute or so, but you should see a pizza show up in the output folder in the root directory. Naming convention is unique-id_recipe-type_randomseed.png (0_Raw pies_4D01DE56.png)

### Chainlink Oracle

A chainlink node is included, which can call the API directly using a web interface, or it can also be invoked from a blockchain deployment (more on that later).

Make sure the docker dev deployment is running if it isn't already.

```
make docker-dev
```

navigate to `http://localhost:6688` and log into the chainlink interface (using the info in `./chainlink/.api`).

#### Chainlink Bridge

First, we need to create a new bridge so the chainlink node can talk to the api. Select `Bridges` from the top menu bar and create a new bridge:

```
Name	orderpizzav1
URL	http://pizza-oven:8000/api/v1/diningroom/order
Confirmations	0
Minimum Contract Payment	0
```

**important** make note of the incoming and outgoing access tokens, we'll need them later!

#### Chainlink Web Job

In order to invoke the api from the chainlink web interface, we need to create a new web job.

Select the Jobs tab from the top menu bar and create a new job (same file as `./chainlink/job.order.web.json`):

```json
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
        "address": "0xSOMETHING",
        "recipe_index": 0
      }
    },
    {
      "type": "Copy",
      "params": {
        "copyPath": ["artwork"]
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
      "artwork": "Z4q72eVU3bX95GXwMXLrguybKLKavmStLWEWVJZ1jeyz"
    },
    "error": null
  },
```

#### Chainlink Blockchain Job

If yo uare jsut testing the api code, you do not need to do this step.

In order for the chainlink node to handle requests that come from the blockchain, another job must be created. Create a new job and drop in the contests of the `./chainlink/job.order.runLog.json` file.

Configuring the blockchain job requires deploying a chainlink node to rinkeby. refer to the smart contract repository to continue these steps.

### Configuring the API to communicate with chainlink

When you set up the bridge, you received an incoming and outgoing web token. We must configure the API to respond to the chainlink node correctly.

### 🧪 Testing

#### Just test with postman (the easy way)

The easiest way to test the application is to use postman to issue requests directly to the api. If you do this, the console output of the `make docker-dev` command will include a printout that looks like this:

```bash
pizza-oven_1         |  --------- YOUR PIZZA IS COMPLETE ----------
pizza-oven_1         |
pizza-oven_1         |
pizza-oven_1         | ipfs image: ipfs://QmRmaqodXJ4xe684iwgvv8UnbdMjoe3RhjceqL1hYrM8ec
pizza-oven_1         |
pizza-oven_1         |
pizza-oven_1         |  -------------------------------------------
```

go to the ipfs location and get your pizza!

## 🐍 Running locally with just Python

### Python OrderAPI

The python api can also simply be run locally on your machine without docker or chainlink. In this mode, you must have natron installed

make sure the environment is configured correctly:

```bash
make environment
```

Start the local server

```bash
make start
```

### 🐛 Debugging

For local debugging with Visual Studio Code, just run it from the dropdown in the Run menu. Once the server is up, you can easily hit your breakpoints.

If the code fails to run, [make sure your Python interpreter is set](https://code.visualstudio.com/docs/python/environments) to use your poetry environment.

##### All done. Enjoy!

Google Authentication error:
A google login is required to pull data from a shared sheet. There is currently a token stored in /data to be used for this. It sometimes expires, and the app flow to login again fails. Make sure you have the latest token from the repo. Eventually we will need to fiugre out a better solution here… Suggestions welcome.
