#!/bin/sh  

sudo ./scripts/apply_django_patches /home/vagrant/virtualenv/python2.7/lib/python2.7/site-packages/django
fab --set run_local=True install_solr upgrade_to_solr3 install_solr_2155
fab --set run_local=True install_solr_config:instance=travis,solr_multicore=,project_root=`pwd`
fab --set run_local=True enable_jetty_start
createdb -T template_postgis atlas_travis -U postgres
python manage.py build_solr_schema --settings=settings.travis > config/travis/solr/schema.xml
sudo cp config/travis/solr/schema.xml /usr/local/share/solr3/conf/
sudo sed -i.bak -r -e "s/#JDK_DIRS=.*/JDK_DIRS=\"\/usr\/lib\/jvm\/java-6-openjdk-i386\"/g" /etc/default/jetty
echo "DEBUG: trying to find JDK"
ls /usr/lib/jvm
echo "END DEBUG"
fab --set run_local=True update_solr_jetty_config
sudo service jetty restart
# If running browser tests, uncomment these lines
#export DISPLAY=:99.0
#sh -e /etc/init.d/xvfb start

