#!/bin/sh

sudo apt-get install gdal-bin libproj-dev postgis postgresql-9.1-postgis
sudo sed -i.bak -r -e "s/^#JAVA_HOME=/JAVA_HOME=\/usr\/lib\/jvm\/java-7-oracle/g" /etc/default/jetty
sudo bash ./scripts/create_template_postgis-debian.sh

