from fabric.api import env, roles

from fusionbox.fabric.django.new import stage, deploy

def dev():
    env.project_name = 'floodlightproject.dev'
    env.vassal_name = 'floodlightproject_dev'
    return ['fusionbox@floodlightproject.dev.fusionbox.com']

env.roledefs['dev'] = dev

stage = roles('dev')(stage)

# """Fabric tasks to deploy atlas

# Tested on Ubuntu 12.04

# """
# import os
# import os.path
# from pprint import pprint
# import sys

# from fabric.api import env, execute, local, settings, task
# from fabric.context_managers import cd as _cd, lcd, prefix
# from fabric.contrib.files import exists as _exists
# from fabric.operations import put, run as _run, sudo as _sudo
# from fabric.utils import abort, puts

# # Set up some default environment

# env['instance'] = env.get('instance', 'atlas')
# """Name of instance, used to create paths and name certain config files"""

# env['instance_root'] = env.get('instance_root',
#                                os.path.join('/srv/www/', env['instance']))
# """Directory where all the app assets will be put

# Tasks assume that this directory already exists and that you
# have write permissions on it. This is what I did to get started:

#     $ sudo addgroup atlas
#     $ sudo adduser ghing atlas
#     # Add Apache's user to the group so it can write to the log directory
#     $ sudo usermod -g atlas www-data
#     $ sudo mkdir /srv/www/atlas_dev
#     $ sudo chgrp atlas /srv/www/atlas_dev
#     $ sudo chmod g+rwxs /srv/www/atlas_dev

# """

# env['project_root'] = env.get('project_root',
#                               os.path.join(env['instance_root'], 'atlas'))
# """The path to this Django project"""

# env['production'] = env.get('production', False)
# """Flag to indicate whether an instance is production"""

# env['repo_uri'] = env.get('repo_uri',
#     'git://github.com/PitonFoundation/atlas.git' if env['production'] else 'git@github.com:PitonFoundation/atlas.git')
# """URI of Git repository for this project

# If the production flag is set, a read-only URI is chosen.
# """

# env['repo_branch'] = env.get('repo_branch',
#                              'master' if env['production'] else 'develop')
# """The branch of the Git repository to pull from"""

# env['db_auth_config'] = env.get('db_auth_config',
#                                 '/etc/postgresql/9.1/main/pg_hba.conf')
# """Path to PostgreSQL's client authentication configuration file"""

# env['solr_root'] = env.get('solr_root', '/usr/local/share/solr')
# env['solr_core_root'] = env.get('solr_core_root',
#     os.path.join(env['solr_root'], 'multicore'))
# env['solr_data_root'] = env.get('solr_data_root',
#                                 env['solr_core_root'])
# env['solr_conf_root'] = env.get('solr_conf_root',
#                                 env['solr_core_root'])
# env['solr_lib_root'] = env.get('solr_conf_root',
#                                 env['solr_core_root'])

# env['run_local'] = env.get('run_local', False)

# def _get_config_dir():
#     """Get the path for an instance's local configuration"""
#     return os.path.join(os.getcwd(), 'config', env['instance']) + '/'

# def _escape_slashes(value):
#     """Convert '/' to '\\/'"""
#     import re
#     return re.sub(r'/', r'\\/', value)

# def local_sudo(command, capture=False, user=None):
#     """Naive wrapper for running local commands with sudo.

#     This allows keeping the same command string for both local and remote
#     execution.

#     """
#     sudo_prefix = "-u %s " % user if user is not None else ""
#     local("sudo %s%s" % (sudo_prefix, command), capture)

# def local_exists(path, use_sudo=False, verbose=False):
#     """Check if a local path exists"""
#     if os.path.exists(path):
#         return True
#     else:
#         return False

# # Command running functions should default to their remote versions
# sudo = _sudo
# run = _run
# cd = _cd
# exists = _exists

# def get_sudo(run_local=env['run_local']):
#     """
#     Return a function that executes a command using sudo

#     If ``run_local`` is True, return a function that executes
#     the command on the local host.  Otherwise return Fabric's
#     default ``sudo()`` function.

#     """
#     return _sudo if not run_local else local_sudo

# def get_run(run_local=env['run_local']):
#     """
#     Return a function that executes a command

#     If ``run_local`` is True, returns Fabric's ``local()``.
#     Otherwise return Fabric's default ``run()`` function.

#     """
#     return run if not run_local else local

# def get_cd(run_local=env['run_local']):
#     """
#     Return a function that changes the context to a particular
#     directory.

#     If ``run_local`` is True, returns Fabric's ``lcd()``,
#     otherwise returns ``cd()``

#     """
#     return _cd if not run_local else lcd

# @task
# def check_local_config(config_dir=None):
#     """Check that the required configuration files exist for an instance

#     This does not check the syntax of the files, just that they exist

#     """
#     if config_dir is None:
#         config_dir = _get_config_dir()
#     config_files = [('apache', 'site'),
#                     ('nginx', 'site'),
#                     ('settings.py',),
#                     ('solr', 'protwords.txt'),
#                     ('solr', 'solrconfig.xml'),
#                     ('solr', 'stopwords.txt'),
#                     ('solr', 'synonyms.txt')]

#     with settings(warn_only=True):
#         output = local("[ -d %s ]" % config_dir)
#         if output.failed:
#             err_msg = ("Local configuration directory %s doesn't exit" %
#                        config_dir)
#             abort(err_msg)

#         for path in config_files:
#             filename = os.path.join(config_dir,
#                                     os.path.join(*path))
#             output = local("[ -f %s ]" % filename)
#             if output.failed:
#                 err_msg = ("Local configuration file %s doesn't exit" %
#                            filename)
#                 abort(err_msg)

# @task
# def check_instance_root():
#     """Check that the root directory for an instance exists"""
#     with settings(warn_only=True):
#         output = run("[ -d %s ]" % env['instance_root'])

#         if output.failed:
#             err_msg = (
#                 "The instance root directory %s doesn't exist.  You must "
#                 "create it before running further tasks." %
#                 env['instance_root'])
#             abort(err_msg)

#         output = run("[ -w %s ]" % env['instance_root'])

#         if output.failed:
#             err_msg = (
#                 "You don't have write access to the instance root "
#                 "directory %s.  You must grant write permissions on the "
#                 "directory before running further tasks." %
#                 env['instance_root'])
#             abort(err_msg)

# @task
# def check_db_auth_config(username=env['instance'], dbname=env['instance']):
#     """Check that an entry for the instance's database user exists

#     I think it's dangerous to programatically write config files,
#     especially ones that might already have human configuration tweaks.
#     So, we should just check that an entry for the instance exists
#     in pg_hba.conf.

#     """
#     with settings(warn_only=True):
#         output = sudo("grep %s %s" %
#                       (username, env['db_auth_config']))
#         if output.failed:
#             example_entry = "local\t%s\t%s\t\tmd5" % (username, dbname)
#             err_msg = ("Entry for database user %s doesn't exit in "
#                        "%s. You should make one that looks like:\n\n"
#                        "%s\n\n"
#                        "Also be sure to restart the postgres service "
#                        "after editing the config " %
#                        (username, env['db_auth_config'],
#                         example_entry))
#             abort(err_msg)

# @task
# def print_env():
#     """ Output the configuration environment for debugging purposes """
#     pprint(env)

# @task
# def install_python_tools(run_local=env['run_local']):
#     """ Install python tools to make deployment easier """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install python-setuptools')
#     sudo('easy_install pip')
#     sudo('pip install virtualenv')

# @task
# def mkvirtualenv(run_local=env['run_local']):
#     """Create the virtualenv for the deployment"""
#     run = get_run(run_local)
#     with cd(env['instance_root']):
#         run('virtualenv --distribute --no-site-packages venv')

# @task
# def install_apache(run_local=env['run_local']):
#     """ Install the Apache 2 webserver """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install apache2')

# @task
# def install_mod_wsgi(run_local=env['run_local']):
#     """ Install Apache mod_wsgi """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install libapache2-mod-wsgi')
#     sudo('a2enmod wsgi')

# @task
# def install_postgres(run_local=env['run_local']):
#     """ Installs Postgresql package """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install postgresql postgresql-server-dev-9.1')

# @task
# def install_spatial(run_local=env['run_local']):
#     """ Install geodjango dependencies """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install binutils gdal-bin libproj-dev postgresql-9.1-postgis')

# @task
# def install_pil_dependencies(run_local=env['run_local']):
#     sudo = get_sudo(run_local)
#     """ Install the dependencies for the PIL library """
#     sudo('apt-get install python-dev libfreetype6-dev zlib1g-dev libjpeg8-dev')

# @task
# def make_pil_dependency_symlinks(run_local=env['run_local']):
#     """ Make symlinks so PIL finds correct libraries

#     See http://www.jayzawrotny.com/blog/django-pil-and-libjpeg-on-ubuntu-1110
#     """
#     sudo = get_sudo(run_local)
#     sudo('ln -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib')
#     sudo('ln -s /usr/lib/i386-linux-gnu/libfreetype.so /usr/lib')
#     sudo('ln -s /usr/lib/i386-linux-gnu/libz.so /usr/lib')
#     sudo('ln -s /lib/i386-linux-gnu/libpng12.so.0 /usr/lib')

# @task
# def install_python_pkg_dependencies(run_local=env['run_local']):
#     """ Install libraries needed by Python packages that will be installed later """
#     sudo = get_sudo(run_local)
#     # Splinter needs lxml, which needs libxml2-dev and libxslt-dev
#     # Django's translations need gettext
#     sudo('apt-get install libxml2-dev libxslt-dev gettext')

# @task
# def install_nginx(run_local=env['run_local']):
#     """ Install the nginx webserver, used to serve static assets. """
#     sudo = get_sudo(run_local)
#     sudo('apt-get install nginx')
#     # Disable the default nginx site
#     sudo('rm /etc/nginx/sites-enabled/default')

# @task
# def install_jetty_script(dest_file="/etc/init.d/jetty", run_local=env['run_local']):
#     """Install jetty start/stop script"""
#     sudo = get_sudo(run_local)
#     jetty_sh = os.path.join('scripts', 'jetty.sh')
#     if not os.path.exists(dest_file):
#         sudo('cp %s %s' % (jetty_sh, dest_file))
#         sudo('chmod 0755 %s' % dest_file)
#     else:
#         sys.stderr.write("%s already exists\n" % (dest_file))

# @task
# def install_jetty_config(jettyrc_dest="/etc/default/jetty",
#         jetty_logging_dest=os.path.join(env['solr_root'], 'etc'),
#         run_local=env['run_local']):
#     sudo = get_sudo(run_local)
#     jettyrc = os.path.join('config', 'template', 'jettyrc')
#     if not os.path.exists(jettyrc_dest):
#         sudo('cp %s %s' % (jettyrc, jettyrc_dest))
#     else:
#         sys.stderr.write("%s already exists\n" % (jettyrc_dest))

#     jetty_logging = os.path.join('config', 'template', 'jetty-logging.xml')
#     sudo('cp %s %s' % (jetty_logging, jetty_logging_dest))


# @task
# def install_solr_example(solr_version='3.6.2', run_local=env['run_local']):
#     """
#     Install the Solr search server using the example shipped with Solr as
#     a starting point
#     """
#     run = get_run(run_local)
#     sudo = get_sudo(run_local)
#     sudo('apt-get install openjdk-7-jdk')
#     solr_download_base = "https://archive.apache.org/dist"
#     run('wget -P /tmp %s/lucene/solr/%s/apache-solr-%s.tgz' %
#         (solr_download_base, solr_version, solr_version))
#     run('tar --directory=/tmp -zxf /tmp/apache-solr-%s.tgz' % (solr_version))
#     sudo('cp -r /tmp/apache-solr-%s/example/ %s' %
#          (solr_version, env['solr_root']))

#     # Clean up downloaded files
#     run('rm -rf /tmp/apache-solr-%s' % (solr_version))
#     run('rm /tmp/apache-solr-%s.tgz' % (solr_version))

#     install_jetty_script(run_local=run_local)
#     install_jetty_config(run_local=run_local)

#     sys.stdout.write("You may need to edit the settings for starting Jetty "
#            "by default these are in /etc/default/jetty. "
#            "Next, you'll need to create configuration and data directories "
#            "for each instance's core by runing the make_solr_data_dir and "
#            "make_solr_conf_dir tasks.  Finally, restart Jetty using the "
#            "restart_jetty task")

# @task
# def install_solr(solr_version='3.6.2', run_local=env['run_local']):
#     """Install the Solr search server"""
#     install_solr_example(solr_version, run_local)

# @task
# def install_solr_2155(instance=env['instance'],
#         solr_lib_root=env['solr_lib_root'], run_local=env['run_local']):
#     """Install the Solr-2155 Plugin to allow multivalue spatial fields"""
#     sudo = get_sudo(run_local)
#     plugin_url = "https://github.com/downloads/dsmiley/SOLR-2155/Solr2155-1.0.5.jar"
#     solr_lib_dir = os.path.join(solr_lib_root, instance, 'lib')
#     sudo("wget -P %s %s" % (solr_lib_dir, plugin_url))

# @task
# def create_spatial_db_template():
#     """ Create the spatial database template for PostGIS """
#     # Upload the spatial template creation script
#     put('scripts/create_template_postgis-debian.sh', '/tmp')

#     # Run the script
#     sudo('bash /tmp/create_template_postgis-debian.sh', user='postgres')

#     # Delete the script
#     run('rm /tmp/create_template_postgis-debian.sh')

# @task
# def createdb(name=env['instance'], run_local=env['run_local']):
#     """ Create the database """
#     sudo = get_sudo(run_local)
#     sudo("createdb -T template_postgis %s" % (name), user='postgres')

# @task
# def createuser(username=env['instance'], dbname=env['instance'],
#                run_local=env['run_local']):
#     """ Create a Postgresql user for this instance and grant them the permissions Django needs to the database """
#     sudo = get_sudo(run_local)
#     sudo("createuser --encrypted --pwprompt %s" % (username), user='postgres')
#     print "You need to make sure you have a line like one of the following "
#     print "in your pg_hba.conf:"
#     print ""
#     print "local\t%s\t%s\t\tmd5" % (dbname, username)

# @task
# def clone():
#     """ Clone the application repository """
#     with cd(env['instance_root']):
#         run("git clone %s atlas" % (env['repo_uri']))

# @task
# def checkout(branch=env['repo_branch']):
#     """ Checkout a particular repository branch """
#     with cd(os.path.join(env['instance_root'], 'atlas')):
#         run("git checkout %s" % (branch))

# @task
# def pull():
#     """ Fetch updates from remote repo """
#     with cd(os.path.join(env['instance_root'], 'atlas')):
#         run('git pull')

# @task
# def fetch():
#     """ Fetch updates from remote repo """
#     with cd(os.path.join(env['instance_root'], 'atlas')):
#         run('git fetch')

# @task
# def install_requirements():
#     """ Install application's Python requirements into the virtualenv """
#     with cd(env['instance_root']):
#         with prefix('source venv/bin/activate'):
#             run('pip install --requirement ./atlas/requirements.txt')

# @task
# def make_log_directory(instance=env['instance']):
#     """ Create directory for instance's logs """
#     with cd(env['instance_root']):
#         run('mkdir logs')

# @task
# def make_media_directory(instance=env['instance']):
#     """ Create the Django media directory """
#     with cd(env['instance_root'] + '/atlas'):
#         run('mkdir media')
#         sudo('chown www-data media')

# @task
# def upload_config(config_dir=None):
#     """ Upload a local config directory """
#     if config_dir is None:
#         config_dir = _get_config_dir()
#     remote_dir = os.path.join(env['instance_root'], 'atlas', 'config')
#     put(config_dir, remote_dir)

# @task
# def install_config(instance=env['instance'], project_root=env['project_root'],
#         solr_conf_root=env['solr_conf_root'], solr_multicore=True,
#         run_local=env['run_local']):
#     """ Install files that were uploaded via upload_local_config to their final homes """
#     cd = get_cd(run_local)
#     run = get_run(run_local)
#     sudo = get_sudo(run_local)
#     with cd(project_root):
#         run("cp config/%s/settings.py settings/%s.py" % (instance, instance))
#         run("cp config/%s/wsgi.py wsgi.py" % (instance))
#         sudo("cp config/%s/apache/site /etc/apache2/sites-available/%s" %
#              (instance, instance))
#         sudo("cp config/%s/nginx/site /etc/nginx/sites-available/%s" %
#              (instance, instance))

#     install_solr_config(instance, project_root, solr_conf_root,
#                         solr_multicore, run_local)

# @task
# def install_solr_config(instance=env['instance'], project_root=env['project_root'],
#                         solr_conf_root=env['solr_conf_root'], solr_multicore=True,
#                         run_local=env['run_local']):
#     sudo = get_sudo(run_local)
#     cd = get_cd(run_local)

#     solr_conf_dir = ("%s/%s/conf" % (solr_conf_root, instance)
#                      if solr_multicore else "%s/conf" % (solr_conf_root))
#     with cd(project_root):
#         sudo("cp config/%s/solr/solrconfig.xml %s/" %
#              (instance, solr_conf_dir))
#         sudo("cp config/%s/solr/protwords.txt %s/" % (instance, solr_conf_dir))
#         sudo("cp config/%s/solr/stopwords.txt %s/" % (instance, solr_conf_dir))
#         sudo("cp config/%s/solr/stopwords_en.txt %s/" %
#              (instance, solr_conf_dir))
#         sudo("cp config/%s/solr/synonyms.txt %s/" % (instance, solr_conf_dir))

# @task
# def syncdb(instance=env['instance']):
#     """ Run syncdb management command in the instance's Django environment """
#     with cd(env['instance_root']):
#         with prefix('source venv/bin/activate'):
#             run("python atlas/manage.py syncdb --settings=atlas.settings.%s" % (env['instance']))

# @task
# def migrate(instance=env['instance']):
#     """ Run South migrations in the instance's Django environment """
#     with cd(env['instance_root']):
#         with prefix('source venv/bin/activate'):
#             run("python atlas/manage.py migrate --settings=atlas.settings.%s" % (env['instance']))

# @task
# def a2ensite(instance=env['instance']):
#     """ Enable the site for the instance in Apache """
#     sudo("a2ensite %s" % (instance))

# @task
# def nginxensite(instance=env['instance']):
#     """ Enable the site for the instance's static files in Nginx """
#     sudo("ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s" % (instance, instance))

# @task
# def apache2_reload():
#     """ Reload the Apache configuration """
#     sudo('service apache2 reload')

# @task
# def nginx_reload():
#     """ Reload the Nginx configuration """
#     sudo('service nginx reload')
# v

# @task
# def collectstatic():
#     """ Collect static files in the instance's Django environment """
#     with cd(env['instance_root']):
#         with prefix('source venv/bin/activate'):
#             run("python atlas/manage.py collectstatic "
#                 "--settings=atlas.settings.%s" % (env['instance']))


# @task
# def collectstatic_no_tinymce():
#     """Collect static files excluding TinyMCE

#     This is just a convenience for me because I need to not clobber
#     the TinyMCE scripts modified to accomodate serving TinyMCE and
#     other static assets from a different subdomain than the app.

#     """
#     with cd(env['instance_root']):
#         with prefix('source venv/bin/activate'):
#             run("python atlas/manage.py collectstatic "
#                 "--ignore='*tinymce*' --settings=atlas.settings.%s" %
#                 (env['instance']))

# @task
# def write_solr_xml(instance=env['instance']):
#     """ Make an entry in the global solr.xml for our instance """
#     # TODO: Make a core entry in /usr/share/solr/solr.xml
#     # It should look something like this:
#     #<core name="atlas_dev" instanceDir="atlas_dev" dataDir="/var/lib/solr/atlas_dev/data" />
#     raise NotImplementedError

# @task
# def make_solr_data_dir(instance=env['instance'],
#                        solr_data_root=env['solr_data_root'],
#                        run_local=env['run_local']):
#     """ Make the directory for the instance's Solr core data """
#     sudo = get_sudo(run_local)
#     solr_data_dir = "%s/%s" % (solr_data_root, instance)
#     sudo("mkdir -p %s/data" % (solr_data_dir))

# @task
# def make_solr_conf_dir(instance=env['instance'],
#         solr_conf_root=env['solr_conf_root'], run_local=env['run_local']):
#     """ Make the directory for the instance's Solr core configuration """
#     sudo = get_sudo(run_local)
#     solr_conf_dir = "%s/%s/conf" % (solr_conf_root, instance)
#     sudo("mkdir -p %s/" % (solr_conf_dir))

# @task
# def make_solr_lib_dir(instance=env['instance'],
#         solr_lib_root=env['solr_lib_root'], run_local=env['run_local']):
#     """ Make the directory for the instance's Solr core configuration """
#     sudo = get_sudo(run_local)
#     solr_lib_dir = "%s/%s/lib" % (solr_lib_root, instance)
#     sudo("mkdir -p %s/" % (solr_lib_dir))

# @task
# def restart_jetty(run_local=env['run_local']):
#     """ Restart the Jetty application server (effictively restarting Solr) """
#     sudo = get_sudo(run_local)
#     sudo("service jetty restart")

# @task
# def manual_configuration_msg():
#     """Print a message telling the user about needed manual configuration"""
#     msg = ("\n"
#            "You may need to make the following manual configuration "
#            "changes:\n\n"
#            "    * Set up a Site in the Django admin for your domain\n"
#            "    * Enable/configure oEmbed providers\n"
#            "    * Configure TinyMCE to allow cross-domain use\n")
#     puts(msg)

# @task
# def create_instance():
#     """Run all tasks to make a new, deployed instance of the software"""
#     execute(check_local_config)
#     execute(check_instance_root)
#     execute(check_db_auth_config)
#     execute(make_log_directory)
#     execute(make_solr_data_dir)
#     execute(make_solr_conf_dir)
#     execute(make_solr_lib_dir)
#     execute(mkvirtualenv)
#     execute(createdb)
#     execute(createuser)
#     execute(clone)
#     execute(checkout)
#     execute(make_media_directory)
#     execute(install_requirements)
#     execute(upload_config)
#     execute(install_config)
#     execute(syncdb)
#     execute(migrate)
#     execute(collectstatic)
#     execute(a2ensite)
#     execute(nginxensite)
#     execute(apache2_reload)
#     execute(nginx_reload)
#     execute(restart_jetty)
