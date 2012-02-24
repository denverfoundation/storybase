from fabric.api import task, env
from fabric.operations import put, run, sudo
from fabric.context_managers import cd
import os
from pprint import pprint

# Fabric tasks to deploy atlas
# Tested on Ubuntu 11.10

# Set up some default environment
# Name of instance, will be used to create paths and name certain
# config files
env['instance'] = env.get('instance', 'atlas')
# Directory where all the app assets will be put
# Tasks assume that this directory already exists and that you
# have write permissions on it. This is what I did to get started:
# 
# sudo addgroup atlas
# sudo adduser ghing atlas
# sudo mkdir /srv/www/atlas_dev
# sudo chmod g+rwxs /srv/www/atlas_dev
env['instance_root'] = env.get('instance_root', 
    os.path.join('/srv/www/', env['instance']))
env['production'] = env.get('production', False)
# Git repo
# Production environments can only pull from repo
env['repo_uri'] = env.get('repo_uri', 
    'git://github.com/ghing/atlas.git' if env['production'] else 'git@github.com:ghing/atlas.git')

@task
def print_env():
    """ Output the configuration environment for debugging purposes """
    pprint(env)

@task
def mkvirtualenv():
    """ Create the virtualenv for the deployment """ 
    with cd(env['instance_root']):
        run('virtualenv --distribute --no-site-packages venv') 

@task
def install_postgres():
    """ Installs Postgresql package """
    sudo('apt-get install postgresql')

@task
def install_spatial():
    """ Install geodjango dependencies """
    sudo('apt-get install binutils gdal-bin libproj-dev postgresql-9.1-postgis')

@task
def create_spatial_db_template():
    """ Create the spatial database template for PostGIS """
    # Upload the spatial template creation script
    put('scripts/create_template_postgis-debian.sh', '/tmp')

    # Run the script
    sudo('bash /tmp/create_template_postgis-debian.sh', user='postgres')

    # Delete the script
    run('rm /tmp/create_template_postgis-debian.sh')

@task
def createdb(name=env['instance']):
    """ Create the database """
    sudo("createdb -T template_postgis %s" % (name), user='postgres')

@task 
def createuser(username=env['instance'], dbname=env['instance']):
    """ Create a Postgresql user for this instance and grant them the permissions Django needs to the database """
    sudo("createuser --encrypted --pwprompt %s" % (username), user='postgres')
    print "You need to make sure you have a line like one of the following "
    print "in your pg_hba.conf:"
    print ""
    print "local\t%s\t%s\t127.0.0.1/32\tmd5" % (dbname, username)

@task 
def clone_repo():
    with cd(env['instance_root']):
        run("git clone %s atlas" % (env['repo_uri']))

