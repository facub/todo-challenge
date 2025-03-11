Todo-challenge
==============

----
# Download the repository
```sh
# SSH:
git clone git@github.com:facub/todo-challenge.git
# HTTPS:
git clone https://github.com/facub/todo-challenge.git
# Github CLI:
gh repo clone facub/todo-challenge
```

---

<div id="virtualenvs"></div>

# Run locally with virtualenv 
### Python Versions
This repository is tested under Python 3.10

Recomendation: Use python version 3.10

### Installation

#### Install virtualenvwrapper
Virtualenvwrapper should be installed into the same 
global site-packages area where virtualenv is installed. 
You may need administrative privileges to do that. The easiest way to install it is using pip

1. Install virtualenvwrapper using pip
	```sh
	sudo pip install virtualenvwrapper
	```

2. Open .bashrc or .zshrc file and add:
	```sh
	# Virtualenvwrapper
	export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3 # Optional
	export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv  # Or ~/.local/bin/virtualenv
	export PROJECT_HOME=$HOME/Devel
	export WORKON_HOME=$HOME/Envs
	source /usr/local/bin/virtualenvwrapper.sh  # Or ~/.local/bin/virtualenvwrapper.sh
	```
3. Reload startup file
	```sh
	source ~/.bashrc
	```
	or
	```sh
	source ~/.zshrc
	```


### Create an enviroment
1. Create the environment
	```sh
	cd /path/to/repo/todo
	mkvirtualenv -a . --python=python3.10 todo
	deactivate
	```
2. Add to `~/Envs/todo/bin/postactivate`:

	```sh
	export PYTHONPATH=[/path/to/repo/]todo
	```

### Install the requirements
1. Activate the enviroment

	```sh
	workon todo
	```
2. Now install dependecies from:
	```sh
	pip install -r requirements.txt
	```

### Migrations
```sh
python manage.py migrate
```
## Run on port
```sh
python manage.py runserver
```
## Access to Todo-challenge:
```sh
http://localhost:8000/login
```

## Access to Admin and database tables:
### First, create a superuser to manage admin:
```sh
python manage.py createsuperuser
```
### Link to admin: 
```sh
http://localhost:8000/admin
```


---
# Run locally with docker

Update your system before installing docker
```sh
sudo apt update
```

Install Docker and Docker compose
```sh
sudo apt install docker.io
```
Docker Compose:

```sh
sudo apt install docker-compose
```

## Run docker to execute the server:
```sh
docker-compose -f docker-compose.yml up -d
```

### Migrations
```sh
python manage.py migrate
```

# Run tests and check coverage:
On local:
```sh
coverage run -m pytest && coverage report -m
```
On docker:
```sh
docker-compose -f docker-compose.test.yml up
```


# Run docker with Nginx (Production simulation):
```sh
docker-compose -f docker-compose.nginx.yml up -d
```
### Migrations
1. Set production db:
	```
	set -o allexport; source environments/.env.prod; set +o allexport
	```
2. Run migrations:
	```sh
	python manage.py migrate
	```