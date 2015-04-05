FROM ubuntu:14.04
# make sure the package repository is up to date
RUN apt-get -qq update

# supervisor
RUN apt-get -qq install -y supervisor

# need postgres client for psycopg2
RUN apt-get -qq install -y libpq-dev

# install python3 and pip for python3
RUN apt-get -qq install -y python3-pip

RUN pip3 -q install virtualenv
RUN pip3 -q install uwsgi
RUN virtualenv -p python3.4 /opt/ve/django

#log folder
RUN mkdir -p /var/log/django

ADD . /opt/apps/django
ADD .docker/supervisor.conf /opt/supervisor.conf
ADD .docker/run.sh /usr/local/bin/run

RUN /opt/ve/django/bin/pip3 -q install -r /opt/apps/django/requirements.txt

EXPOSE 8080

CMD ["/bin/sh", "-e", "/usr/local/bin/run"]

