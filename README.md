# Portfoliology

Replacement for Google Finance portfolios, since apparently they're getting rid of that in November, and it was always kind of useful. 

### Usage
Add a CSV named `positions.csv` with the columns "Name,Symbol,Shares,Cost basis" to `portfolio/static/portfolio/` and then run `python manage.py collectstatic`. Then you should be able to run it on localserver and visit any of the url routes mapped out in `urls.py`.

### Requirements
- Django==1.11.6
- numpy==1.13.3\n
- pandas==0.20.3
- python-dateutil==2.6.1
- pytz==2017.2
- simplejson==3.11.1
- six==1.11.0
- yahoo-finance==1.4.0
