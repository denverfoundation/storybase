"""Fabric tasks to deploy atlas

Tested on Ubuntu 11.10

"""
import os
from fabric.api import env, execute, local, settings, task
from fabric.context_managers import cd, lcd, prefix
from fabric.operations import put, run, sudo
from fabric.utils import abort, puts
from pprint import pprint

# Set up some default environment

env['instance'] = env.get('instance', 'atlas')
"""Name of instance, used to create paths and name certain config files"""

env['instance_root'] = env.get('instance_root', 
                               os.path.join('/srv/www/', env['instance']))
"""Directory where all the app assets will be put

Tasks assume that this directory already exists and that you
have write permissions on it. This is what I did to get started:
 
    $ sudo addgroup atlas
    $ sudo adduser ghing atlas
    $ sudo mkdir /srv/www/atlas_dev
    $ sudo chgrp atlas /srv/www/atlas_dev
    $ sudo chmod g+rwxs /srv/www/atlas_dev

"""

env['production'] = env.get('production', False)
"""Flag to indicate whether an instance is production"""

env['repo_uri'] = env.get('repo_uri', 
    'git://github.com/PitonFoundation/atlas.git' if env['production'] else 'git@github.com:PitonFoundation/atlas.git')
"""URI of Git repository for this project

If the production flag is set, a read-only URI is chosen.
"""

env['repo_branch'] = env.get('repo_branch', 
                             'master' if env['production'] else 'develop')
"""The branch of the Git repository to pull from"""

env['db_auth_config'] = env.get('db_auth_config',
                                '/etc/postgresql/9.1/main/pg_hba.conf')
"""Path to PostgreSQL's client authentication configuration file"""

env['solr_root'] = env.get('solr_root', '/usr/local/share/solr3')
env['solr_data_root'] = env.get('solr_data_root', '/usr/local/lib/solr3')

env['run_local'] = env.get('run_local', False)

def _get_config_dir():
    """Get the path for an instance's local configuration"""
    return os.path.join(os.getcwd(), 'config', env['instance']) + '/'

def local_sudo(command, capture=False):
    """Naive wrapper for running local commands with sudo.

    This allows keeping the same command string for both local and remote
    execution.

    """
    local("sudo %s" % (command), capture)

@task
def check_local_config(config_dir=None):
    """Check that the required configuration files exist for an instance

    This does not check the syntax of the files, just that they exist

    """
    if config_dir is None:
        config_dir = _get_config_dir()
    config_files = [('apache', 'site'),
                    ('nginx', 'site'),
                    ('settings.py',),
                    ('solr', 'protwords.txt'),
                    ('solr', 'solrconfig.xml'),
                    ('solr', 'stopwords.txt'),
                    ('solr', 'synonyms.txt')]

    with settings(warn_only=True):
        output = local("[ -d %s ]" % config_dir)
        if output.failed:
            err_msg = ("Local configuration directory %s doesn't exit" %
                       config_dir)
            abort(err_msg)

        for path in config_files:
            filename = os.path.join(config_dir,
                                    os.path.join(*path))
            output = local("[ -f %s ]" % filename)
            if output.failed:
                err_msg = ("Local configuration file %s doesn't exit" %
                           filename)
                abort(err_msg)

@task
def check_instance_root():
    """Check that the root directory for an instance exists"""
    with settings(warn_only=True):
        output = run("[ -d %s ]" % env['instance_root'])

        if output.failed:
            err_msg = ( 
                "The instance root directory %s doesn't exist.  You must "
                "create it before running further tasks." %
                env['instance_root'])
            abort(err_msg)

        output = run("[ -w %s ]" % env['instance_root'])

        if output.failed:
            err_msg = (
                "You don't have write access to the instance root "
                "directory %s.  You must grant write permissions on the "
                "directory before running further tasks." %
                env['instance_root'])
            abort(err_msg)

@task
def check_db_auth_config(username=env['instance'], dbname=env['instance']):
    """Check that an entry for the instance's database user exists
    
    I think it's dangerous to programatically write config files, 
    especially ones that might already have human configuration tweaks.
    So, we should just check that an entry for the instance exists
    in pg_hba.conf.

    """
    with settings(warn_only=True):
        output = sudo("grep %s %s" % 
                      (username, env['db_auth_config']))
        if output.failed:
            example_entry = "local\t%s\t%s\t\tmd5" % (username, dbname) 
            err_msg = ("Entry for database user %s doesn't exit in "
                       "%s. You should make one that looks like:\n\n"
                       "%s\n\n"
                       "Also be sure to restart the postgres service "
                       "after editing the config " % 
                       (username, env['db_auth_config'],
                        example_entry))
            abort(err_msg)

@task
def print_env():
    """ Output the configuration environment for debugging purposes """
    pprint(env)

@task
def install_python_tools():
    """ Install python tools to make deployment easier """
    sudo('apt-get install python-setuptools')
    sudo('easy_install pip')
    sudo('pip install virtualenv')

@task
def mkvirtualenv():
    """Create the virtualenv for the deployment""" 
    with cd(env['instance_root']):
        run('virtualenv --distribute --no-site-packages venv') 

@task
def install_apache():
    """ Install the Apache 2 webserver """
    sudo('apt-get install apache2')
        
@task
def install_mod_wsgi():
    """ Install Apache mod_wsgi """
    sudo('apt-get install libapache2-mod-wsgi')
    sudo('a2enmod wsgi')

@task
def install_postgres():
    """ Installs Postgresql package """
    sudo('apt-get install postgresql postgresql-server-dev-9.1')

@task
def install_spatial():
    """ Install geodjango dependencies """
    sudo('apt-get install binutils gdal-bin libproj-dev postgresql-9.1-postgis')

@task
def install_pil_dependencies():
    """ Install the dependencies for the PIL library """
    sudo('apt-get install python-dev libfreetype6-dev zlib1g-dev libjpeg8-dev')

@task
def make_pil_dependency_symlinks():
    """ Make symlinks so PIL finds correct libraries 
    
    See http://www.jayzawrotny.com/blog/django-pil-and-libjpeg-on-ubuntu-1110
    """
    sudo('ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib')
    sudo('ln -s /usr/lib/i386-linux-gnu/libfreetype.so /usr/lib')
    sudo('ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib')
    sudo('ln -s /lib/i386-linux-gnu/libpng12.so.0 /usr/lib')

@task
def install_python_package_depencies():
    """ Install libraries needed by Python packages that will be installed later """
    # Splinter needs lxml, which needs libxml2-dev and libxslt-dev
    # Django's translations need gettext
    sudo('apt-get install libxml2-dev libxslt-dev gettext')

@task
def install_nginx():
    """ Install the nginx webserver, used to serve static assets. """
    sudo('apt-get install nginx')
    # Disable the default nginx site
    sudo('rm /etc/nginx/sites-enabled/default') 

@task
def install_solr(run_local=env['run_local']):
    """ Install the Solr search server """
    runner = run if not run_local else local
    sudo_runner = sudo if not run_local else local_sudo
    # Solr doesn't work with openjdk-7-jdk, we need to install oepnjdk-6-jdk
    # as a workaround. See https://bugs.launchpad.net/ubuntu/+source/solr/+bug/901165
    sudo_runner('apt-get install openjdk-6-jdk')
    sudo_runner('apt-get install solr-jetty')
    print "You'll probably need to edit /etc/default/jetty"

@task
def upgrade_to_solr3(solr_version='3.6.0', run_local=env['run_local']):
    """
    Upgrade Solr to version 3.5+ as the version supported in the
    Ubuntu packages don't support spatial queries
    """
    runner = run if not run_local else local
    sudo_runner = sudo if not run_local else local_sudo
    sudo_runner('mkdir /usr/local/share/solr3')
    sudo_runner('mkdir /usr/local/etc/solr3')
    sudo_runner('mkdir -p /usr/local/lib/solr3/data')
    sudo_runner('chown -R jetty /usr/local/lib/solr3/data')
    runner('wget -P /tmp http://www.reverse.net/pub/apache/lucene/solr/%s/apache-solr-%s.tgz' % (solr_version, solr_version))
    runner('tar --directory=/tmp -zxf /tmp/apache-solr-%s.tgz' % (solr_version))
    sudo_runner('unzip -d /usr/local/share/solr3/ /tmp/apache-solr-%s/dist/apache-solr-%s.war' % (solr_version, solr_version))
    
    # Make symlinks to mirror Ubuntu/Debian layout
    sudo_runner('ln -s /usr/local/etc/solr3/conf /usr/local/share/solr3/conf')
    sudo_runner('ln -s /usr/local/etc/solr3/ /etc/solr3')
    sudo_runner('ln -s /usr/local/lib/solr3/ /var/lib/solr3')

    # Copy existing configuration
    sudo_runner('cp -a /etc/solr/* /usr/local/etc/solr3/')
    print ("You need to manually edit "
           "/usr/local/etc/solr3/conf/solrconfig.xml and set the dataDir "
           "element to /usr/local/lib/solr3/data")
    sudo_runner('cp /usr/share/solr/solr.xml /usr/local/share/solr3/')
    print ("You need to manually edit "
           "/usr/local/share/solr3/solr.xml and set eacho core's dataDir "
           "element to a subdirectory of /usr/lib/solr3")

    # Copy jetty JARs to new solr directory
    sudo_runner("cp /usr/share/solr/WEB-INF/lib/jetty* /usr/local/share/solr3/WEB-INF/lib/")
    # Copy jetty config 
    sudo_runner("cp /usr/share/solr/WEB-INF/jetty-web.xml /usr/local/share/solr3/WEB-INF/")
    print ("You need to manually edit "
           "/usr/local/share/solr3/WEB-INF/jetty-web.xml to reflect the new "
           "Solr location")

    # Make Solr3 instance available to Jetty
    sudo_runner("ln -s /usr/local/share/solr3/ /usr/share/jetty/webapps")
    # Remove symlink to old Solr
    sudo_runner("rm /usr/share/jetty/webapps/solr")

    # Clean up downloaded files
    runner('rm -rf /tmp/apache-solr-%s' % (solr_version))
    runner('rm /tmp/apache-solr-%s.tgz' % (solr_version))

    print ("Next, you'll need to create configuration and data directories "
           "for each instance's core by runing the make_solr_data_dir and "
           "make_solr_config_dir tasks.  Finally, restart Jetty using the "
           "restart_jetty task")

@task
def install_solr_2155(solr_root=env['solr_root'], run_local=env['run_local']):
    """Install the Solr-2155 Plugin to allow multivalue spatial fields"""
    runner = sudo if not run_local else local_sudo
    runner("wget -P %s/WEB-INF/lib/ https://github.com/downloads/dsmiley/SOLR-2155/Solr2155-1.0.5.jar" % (solr_root))

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
    print "local\t%s\t%s\t\tmd5" % (dbname, username)

@task 
def clone():
    """ Clone the application repository """
    with cd(env['instance_root']):
        run("git clone %s atlas" % (env['repo_uri']))

@task
def checkout(branch=env['repo_branch']):
    """ Checkout a particular repository branch """
    with cd(os.path.join(env['instance_root'], 'atlas')):
        run("git checkout %s" % (branch))

@task
def pull():
    """ Fetch updates from remote repo """
    with cd(os.path.join(env['instance_root'], 'atlas')):
        run('git pull')

@task
def fetch():
    """ Fetch updates from remote repo """
    with cd(os.path.join(env['instance_root'], 'atlas')):
        run('git fetch')

@task
def install_requirements():
    """ Install application's Python requirements into the virtualenv """
    with cd(env['instance_root']):
        with prefix('source venv/bin/activate'):
            run('pip install --requirement ./atlas/REQUIREMENTS')

@task
def make_log_directory(instance=env['instance']):
    """ Create directory for instance's logs """
    with cd(env['instance_root']):
        run('mkdir logs')

@task
def make_media_directory(instance=env['instance']):
    """ Create the Django media directory """
    with cd(env['instance_root'] + '/atlas'):
        run('mkdir media')
        sudo('chown www-data media')

@task
def upload_config(config_dir=None):
    """ Upload a local config directory """
    if config_dir is None:
        config_dir = _get_config_dir()
    remote_dir = os.path.join(env['instance_root'], 'atlas', 'config')
    put(config_dir, remote_dir)

@task
def install_config(instance=env['instance'], solr_root=env['solr_root']):
    """ Install files that were uploaded via upload_local_config to their final homes """
    with cd(env['instance_root'] + '/atlas/'):
        run("cp config/%s/settings.py settings/%s.py" % (instance, instance))
        run("cp config/%s/wsgi.py wsgi.py" % (instance))
        sudo("cp config/%s/apache/site /etc/apache2/sites-available/%s" %
             (instance, instance))
        sudo("cp config/%s/nginx/site /etc/nginx/sites-available/%s" %
             (instance, instance))

    install_solr_config(instance, solr_root)

@task
def install_solr_config(instance=env['instance'], solr_root=env['solr_root'],
                        solr_multicore=True, run_local=env['run_local']):
    sudo_runner = sudo if not run_local else local_sudo
    solr_conf_dir = "%s/%s/conf" % (solr_root, instance) if solr_multicore else "%s/conf" % (solr_root)
    do_cd = cd if not run_local else lcd
    with do_cd(env['instance_root'] + '/atlas/'):
        sudo_runner("cp config/%s/solr/solrconfig.xml %s/" %
             (instance, solr_conf_dir))
        sudo_runner("cp config/%s/solr/protwords.txt %s/" % (instance, solr_conf_dir))
        sudo_runner("cp config/%s/solr/stopwords.txt %s/" % (instance, solr_conf_dir))
        sudo_runner("cp config/%s/solr/stopwords_en.txt %s/" %
             (instance, solr_conf_dir))
        sudo_runner("cp config/%s/solr/synonyms.txt %s/" % (instance, solr_conf_dir))

@task 
def syncdb(instance=env['instance']):
    """ Run syncdb management command in the instance's Django environment """
    with cd(env['instance_root']):
        with prefix('source venv/bin/activate'):
            run("python atlas/manage.py syncdb --settings=atlas.settings.%s" % (env['instance']))

@task 
def migrate(instance=env['instance']):
    """ Run South migrations in the instance's Django environment """
    with cd(env['instance_root']):
        with prefix('source venv/bin/activate'):
            run("python atlas/manage.py migrate --settings=atlas.settings.%s" % (env['instance']))

@task
def a2ensite(instance=env['instance']):
    """ Enable the site for the instance in Apache """
    sudo("a2ensite %s" % (instance))

@task
def nginxensite(instance=env['instance']):
    """ Enable the site for the instance's static files in Nginx """
    sudo("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s" % (instance, instance))

@task
def apache2_reload():
    """ Reload the Apache configuration """
    sudo('service apache2 reload')

@task
def nginx_reload():
    """ Reload the Nginx configuration """
    sudo('service nginx reload')

@task 
def collectstatic():
    """ Collect static files in the instance's Django environment """
    with cd(env['instance_root']):
        with prefix('source venv/bin/activate'):
            run("python atlas/manage.py collectstatic "
                "--settings=atlas.settings.%s" % (env['instance']))


@task
def collectstatic_no_tinymce():
    """Collect static files excluding TinyMCE

    This is just a convenience for me because I need to not clobber
    the TinyMCE scripts modified to accomodate serving TinyMCE and
    other static assets from a different subdomain than the app.

    """
    with cd(env['instance_root']):
        with prefix('source venv/bin/activate'):
            run("python atlas/manage.py collectstatic "
                "--ignore='*tinymce*' --settings=atlas.settings.%s" %
                (env['instance']))

@task
def write_solr_xml(instance=env['instance']):
    """ Make an entry in the global solr.xml for our instance """
    # TODO: Make a core entry in /usr/share/solr/solr.xml
    # It should look something like this:
    #<core name="atlas_dev" instanceDir="atlas_dev" dataDir="/var/lib/solr/atlas_dev/data" /> 
    raise NotImplemented

@task
def make_solr_data_dir(instance=env['instance'], 
                       solr_data_root=env['solr_data_root']):
    """ Make the directory for the instance's Solr core data """
    solr_data_dir = "%s/%s" % (solr_data_root, instance)
    sudo("mkdir -p %s/data" % (solr_data_dir))
    sudo("chown -R jetty %s/" % (solr_data_dir))

@task
def make_solr_config_dir(instance=env['instance'], solr_root=env['solr_root'],
                         run_local=env['run_local']):
    """ Make the directory for the instance's Solr core configuration """
    sudo_runner = sudo if not run_local else local_sudo
    solr_conf_dir = "%s/%s/conf" % (solr_root, instance)
    sudo_runner("mkdir -p %s/" % (solr_conf_dir))

@task
def restart_jetty():
    """ Restart the Jetty application server (effictively restarting Solr) """
    sudo("service jetty restart")

@task
def manual_configuration_msg():
    """Print a message telling the user about needed manual configuration"""
    msg = ("\n"
           "You may need to make the following manual configuration "
           "changes:\n\n"
           "    * Set up a Site in the Django admin for your domain\n"
           "    * Enable/configure oEmbed providers\n"
           "    * Configure TinyMCE to allow cross-domain use\n")
    puts(msg)


@task
def create_instance():
    """Run all tasks to make a new, deployed instance of the software"""
    execute(check_local_config)
    execute(check_instance_root)
    execute(check_db_auth_config)
    execute(make_log_directory)
    execute(make_solr_data_dir)
    execute(make_solr_config_dir)
    execute(mkvirtualenv)
    execute(createdb)
    execute(createuser)
    execute(clone)
    execute(checkout)
    execute(make_media_directory)
    execute(install_requirements)
    execute(upload_config)
    execute(install_config)
    execute(syncdb)
    execute(migrate)
    execute(collectstatic)
    execute(a2ensite)
    execute(nginxensite)
    execute(apache2_reload)
    execute(nginx_reload)
    execute(restart_jetty)
