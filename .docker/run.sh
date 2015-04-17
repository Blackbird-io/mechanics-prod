/opt/ve/django/bin/python3.4 /opt/apps/django/manage.py migrate --noinput
/opt/ve/django/bin/python3.4 /opt/apps/django/manage.py collectstatic --noinput
/opt/ve/django/bin/python3.4 /opt/apps/django/manage.py createsu

supervisord -c /opt/supervisor.conf -n
