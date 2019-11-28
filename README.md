# Squirrel Electricity Management

This project was created during the Design4Green #3 in 2019.
Contributors:
  - Campan Nathaniel
  - Chaumeil Thomas
  - [Fieber Théo](https://github.com/Fienberber)
  - Mousseau Louise
  
# Installation
To get started:
```
git clone https://github.com/lyghtnox/d4g
cd d4g/
python3 -m venv .
source bin/activate
pip install -r requirements.txt
```
You will need to create a secrets.py file with the following variables:
```
SMTP_USER=''
SMTP_PASS=''
SECRET_KEY=''
```
You can use the following to generate a random secret key:
```
python -c 'import os; print(os.urandom(64))'
```

You will also have to create a cnl.db file in app/ as I can't include mine

You can then start the web site with:
```
python d4g.py
```
It will be available on http://127.0.0.1:8000
