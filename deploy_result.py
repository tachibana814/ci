#-*- encoding: utf-8 -*-
'''
Created on 2016年5月9日

@author: Hzdingweiwei
'''

class DeployResult:

    def __init__(self):
        '''初始化部署结果'''
        self.succ_app_list = []
        self.failed_app_list = []
        self.timeout_app_list = []

    def get_deploy_failed_apps(self):
        return self.failed_app_list

    def get_deploy_timeout_apps(self):
        return self.timeout_app_list

    def get_deploy_succ_apps(self):
        return self.succ_app_list

    def set_deploy_failed_apps(self, failapp):
        '''设置部署失败到失败应用列表'''
        self.failed_app_list.append(failapp)

    def set_deploy_succ_apps(self, succapp):
        self.succ_app_list.append(succapp)

    def set_deploy_timeout_apps(self, timeoutapp):
        self.timeout_app_list.append(timeoutapp)
