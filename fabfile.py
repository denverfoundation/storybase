from fabric.api import env, roles, run, task
from fusionbox.fabric.django.new import cd_project, get_latest_src_dir


def dev():
    env.project_name = 'floodlightproject.dev'
    env.vassal_name = 'floodlightproject_dev'
    return ['fusionbox@floodlightproject.dev.fusionbox.com']

env.roledefs['dev'] = dev

@task
@roles('dev')
def stage(*args, **kwargs):
    from fusionbox.fabric.django.new import stage
    stage(*args, **kwargs)
    return npm('install')

@task
@roles('live')
def deploy(*args, **kwargs):
    from fusionbox.fabric.django.new import deploy
    deploy(*args, **kwargs)
    return npm('install')

@task
def npm(command):
    """
    Run an npm command

    You have to specify the role with -R <live,dev>
    """
    src_directory = get_latest_src_dir()
    with cd_project(src_directory):
        run("npm {}".format(command))
