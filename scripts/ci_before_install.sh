#!/bin/sh
sudo apt-get update
sudo apt-get install gdal-bin libproj-dev postgis postgresql-9.1-postgis
sudo bash ./scripts/create_template_postgis-debian.sh

