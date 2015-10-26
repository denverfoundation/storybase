from fabric.api import env, roles, run, task
from fusionbox.fabric.django.new import cd_project, get_latest_src_dir


def dev():
    env.project_name = 'floodlightproject.dev'
    env.vassal_name = 'floodlightproject_dev'
    return ['fusionbox@floodlightproject.dev.fusionbox.com']

def live():
    env.project_name = 'floodlightproject.org'
    env.vassal_name = 'floodlightproject_live'
    return ['fusionbox@floodlightproject.org']

env.roledefs['dev'] = dev
env.roledefs['live'] = live

@task
@roles('dev')
def stage(*args, **kwargs):
    """
    Deploy the current branch to the dev server
    """
    from fusionbox.fabric.django.new import stage
    stage(*args, **kwargs)
    npm('install')

@task
@roles('live')
def deploy(*args, **kwargs):
    """
    Deploy the live branch to the live server
    """
    from fusionbox.fabric.django.new import deploy
    deploy(*args, **kwargs)
    npm('install')

@task
def npm(command):
    """
    Run an npm command

    You have to specify the role with -R <live,dev>
    """
    src_directory = get_latest_src_dir()
    with cd_project(src_directory):
        run("npm {}".format(command))
