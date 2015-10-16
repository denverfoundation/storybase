from fabric.api import env, roles

from fusionbox.fabric.django.new import stage, deploy

def dev():
    env.project_name = 'floodlightproject.dev'
    env.vassal_name = 'floodlightproject_dev'
    return ['fusionbox@floodlightproject.dev.fusionbox.com']

env.roledefs['dev'] = dev

stage = roles('dev')(stage)
