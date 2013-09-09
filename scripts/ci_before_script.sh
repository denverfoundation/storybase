#!/bin/sh  

sudo ./scripts/apply_django_patches /home/vagrant/virtualenv/python2.7/lib/python2.7/site-packages/django
createdb -T template_postgis atlas_travis -U postgres
fab --set run_local=True install_solr install_solr_2155
fab --set run_local=True install_jetty_script install_jetty_config
sudo cp config/travis/solr/solr.xml /usr/local/share/solr/multicore/
python manage.py build_solr_schema --settings=settings.travis > config/travis/solr/schema.xml
#sudo sed -i.bak -r -e "s/#JDK_DIRS=.*/JDK_DIRS=\"\/usr\/lib\/jvm\/java-6-openjdk-amd64 \/usr\/lib\/jvm\/java-6-openjdk-i386\"/g" /etc/default/jetty
fab --set run_local=True install_solr_config:instance=travis,solr_multicore=true,project_root=`pwd`
sudo service jetty restart
# If running browser tests, uncomment these lines
#export DISPLAY=:99.0
#sh -e /etc/init.d/xvfb start

