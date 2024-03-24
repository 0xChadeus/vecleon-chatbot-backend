python midserver/manage.py makemigrations --noinput
python midserver/manage.py migrate --noinput
python midserver/manage.py collectstatic --noinput

cd midserver
daphne -b 0.0.0.0 -p 7950 server.asgi:application
#gunicorn server.wsgi:application --bind 0.0.0.0:7950 
