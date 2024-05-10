python midserver/manage.py makemigrations --noinput
python midserver/manage.py migrate --noinput
python midserver/manage.py collectstatic --noinput

cd midserver
export REPLICATE_API_TOKEN=r8_UfTVVVWDoB0E0uPIzQppBFMLsqZzDpR0aqOSh
export PROTONMAIL_SMTP_TOKEN=QV6VNKDHYNFLBGV1
export DJANGO_SECRET_KEY=Jzl5TaIHiKQGz2GdVTDpHQpvJabF0Y6VREW2WxuMTfwRn0MhRauCg8Caoc6C5fSN
daphne -b 0.0.0.0 -p 7950 server.asgi:application
#gunicorn server.wsgi:application --bind 0.0.0.0:7950 
