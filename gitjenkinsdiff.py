#-*- encoding: utf-8 -*-
'''
Created on 2015年4月29日

@author: hzdingweiwei
'''

import os
import subprocess
import requests
import logging

def changed_files(workdir, prevcommit, commit, cmd='git'):
    '''git diff HEAD HEAD~ --name-status'''
    p = subprocess.Popen([cmd, 'diff', '--name-status', prevcommit, commit],
        cwd=workdir, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return stdout.splitlines()

def get_apiurl(buildurl):
    buildurl = str(buildurl).replace('http://ci.hz.netease.com', 'http://qa34.server.163.org:8282/')
    return os.path.join(buildurl, 'api/json')

def get_build_data(buildurl):
    apiurl = get_apiurl(buildurl)
    return requests.get(apiurl).json()

def find_last_built_revision(data):
    for action in data['actions']:
        last_built = action.get('lastBuiltRevision')
        if last_built is not None:
            return last_built['SHA1']

class JenkinsBuild(object):
    def __init__(self, buildurl):
        self.url = buildurl
        self.number = None
        self.commit = None
        if buildurl:
            data = get_build_data(buildurl)
            self.number = data['number']
            self.commit = find_last_built_revision(data)

def get_last_successful_build(joburl):
    jobdata = get_build_data(joburl)
    return JenkinsBuild(jobdata['lastSuccessfulBuild']['url'])


def get_changed_files_list():
    files_list = []
    workspace = os.environ.get('WORKSPACE')
    commit = os.environ.get('GIT_COMMIT')
    prevcommit = os.environ.get('GIT_PREVIOUS_COMMIT')
    joburl = os.environ.get('JOB_URL')

    last_build = get_last_successful_build(joburl)
    logging.info('========== CHANGED FILES ============')
    logging.info('Current Revision: %s \nPrevious Revision: %s \nPrevious Build Url: %s' % (commit,last_build.commit,last_build.url))
    files_list = changed_files(workspace, last_build.commit, commit)
    if files_list:
        logging.info('\n'.join(files_list))
    else:
        logging.warn('No file changes found from git pull!')
    return files_list


def get_changed_files_list_old():
    import argparse
    files_list = []
    workspace = os.environ.get('WORKSPACE')
    commit = os.environ.get('GIT_COMMIT')
    prevcommit = os.environ.get('GIT_PREVIOUS_COMMIT')
    joburl = os.environ.get('JOB_URL')

    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace',  required=workspace is None, default=workspace)
    parser.add_argument('--joburl',     required=joburl is None,    default=joburl)
    parser.add_argument('--commit',     required=commit is None,    default=commit)
    parser.add_argument('--prevcommit',                             default=prevcommit)
    args = parser.parse_args()

    last_build = get_last_successful_build(args.joburl)
    logging.info('========== CHANGED FILES ============')
    logging.info('Current Revision: %s \nPrevious Revision: %s \nPrevious Build Url: %s' % (args.commit,last_build.commit,last_build.url))
    files_list = changed_files(args.workspace, last_build.commit, args.commit)
    if files_list:
        logging.info('\n'.join(files_list))
    else:
        logging.warn('No file changes found from git pull!')
    return files_list

if __name__ == '__main__':
    get_changed_files_list()
