# Pizza Kitchen

Welcome Paisano to the Pizza Kitchen!

## 🍕 Pizza Shud B free

This repository makes pizzas.  More specifically, it accepts json input, transforms it and then passes it into the rendering pieline for some 🤌 fresh apizza pie

## 💻 Requirements

> NOTE:<br>
> 🐳 = required for running with Docker.<br>
> 🐍 = required for running with Python.

- 🐳🐍 [GNU Make](https://www.gnu.org/software/make/manual/make.html) is used to simplify the commands and GitHub Actions. This approach is recommended to simplify the command line experience. This is built in for MacOS and Linux. We arent supporting windoze right meow
- 🐍 [Python 3.8](https://www.python.org/downloads/) is <ins>**required**</ins> to develop this API. If you uses multiple versions of python, dont.  But if you insist, [pyenv](https://github.com/pyenv/pyenv) will make your life easier.
- https://www.postman.com/downloads/

## 🐳 Running with Docker

### Developing locally with Docker

If you run Docker and want to run the code locally without Python dependencies, we provide a Dockerfile and docker-compose.yml.

Run the production deployment

```bash
make docker-run
```

Run the dev deployment with hot reloading enabled

```bash
make docker-dev
```

After either command, you will find the API running at http://127.0.0.1:8000

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

### 📮 Postman

A Postman collection is also available to test the API located in the `.postman` folder. You can do a few things with this:

- [Import into Postman](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-data-into-postman) for easy manual testing.
- Also, import the default environment to get you started 👆 RTFM

// TODO: add autmoated test instructions

## 🧪 Testing

// TODO:
