# Install project local
## Requirements
### Python version: 3.10.8
### MySQL Server Community
### ----------------------------------------------
## Clone repository
### git clone: https://github.com/jmerazo/sara.git
### Create enviroment: pip install pipenv
### Execute: pipenv shell
###          pipenv install
###          or pip install -r requirements.txt
### Configure credentials database in settings
### Execute: python manage.py runserver
## Local Host
### http:127.0.0.1:8000
### endpoint:
### - api
###     - /especie_forestal
###         - /suggestions/<str:types>
### etc..
### -----------------------------------------------