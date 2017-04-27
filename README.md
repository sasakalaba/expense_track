# Expense track app.

## Install:

```
git clone https://github.com/sasakalaba/expense_track
mkvirtualenv expense_track
pip install --upgrade pip
pip install -r expense_track/requirements.txt
```

## Setup:

```
cd expense_track/expense_track
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Run tests:

```
coverage run --source='.'  manage.py test
```


## Technologies used:

    - Django
    - Django REST framework
    - Bootstrap (SB Admin 2 theme https://startbootstrap.com/template-overviews/sb-admin-2/)
