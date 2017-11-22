FROM ubuntu
RUN apt-get -qqy update && apt-get -qqy upgrade
RUN apt-get -qqy install python3 python3-pip
COPY src/ /app/catalog
WORKDIR /app/catalog
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
RUN apt-get -qqy install make zip unzip postgresql
RUN /usr/sbin/useradd --create-home --home-dir /home/sysadmin --shell /bin/bash sysadmin && echo sysadmin:dbadmin | chpasswd
RUN service postgresql start && su postgres -c 'createuser -dRs sysadmin' && su sysadmin -c 'createdb' && su sysadmin -c 'createdb catalog'&& su sysadmin -c "psql -c \"CREATE USER webadmin WITH PASSWORD 'admin2017';\""