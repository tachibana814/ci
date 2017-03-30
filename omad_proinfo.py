# -*- encoding: utf-8 -*-
'''
Created on 2015年4月13日

@author: hzdingweiwei

@summary: omad数据建模与接口实现
'''

import requests
import logging

TOKEN = ''  # 用户登录后得到的TOKEN信息，用于之后的所有omad操作
global TOKEN


def omad_login(accessKey, accessSecret):
    '''用户登录，返回一个通用的TOKEN信息'''
    url = "cli/login"
    params = {'appId': accessKey, 'appSecret': accessSecret}
    r = call_omad_api(url, params)
    if r.json() and r.status_code == 200:
        token = r.json()['params']['token']
        TOKEN = token
        global TOKEN
        logging.info("Login omad successed!")
    else:
        logging.error("Login omad failed! with error code %s." % str(r.status_code))
        raise


def call_omad_api(url, params):
    '''omad的接口实现'''
    api_url = "http://omad.hz.netease.com/api/"
    r = requests.post(api_url + url, params)
    try:
        r.json()
    except ValueError:
        requrl = api_url + url
        logging.error("执行%s失败,没有返回json()字串." % requrl)
    return r


class MoEnvironment(object):
    '''MoEnvironment类用例实例化应用服务所配置的环境信息。
    TODO:一个环境下面可能配置多个应用实例，本例中只提取了一个实例信息，需要随实际项目扩展。
    '''

    def __init__(self):
        '''环境属性信息'''
        self.envId = ''
        self.moduleId = ''
        self.envName = ''
        self.envDesc = ''
        self.vcType = ''  # 代码类型 svn,git,none
        self.vcPaht = ''  # 代码路径
        self.vcBranch = ''  # 分支路径
        self.vcAccount = ''
        self.vcPasswd = ''
        self.dependenceIds = ''
        self.packageId = ''
        self.directorAccount = ''  # 报警账号
        self.configuration = ''
        self.currentVersion = ''
        self.loginAccount = ''
        self.createTime = ''
        self.updateTime = ''
        self.status = ''
        # 该应用环境下的实例信息，
        # 注意:为了简化脚本，我们这里只提取一个实例信息,实际情况下一套环境下会有多个应用实例
        self.instanceStatus = ''
        self.instanceId = ''
        self.instanceHostname = ''
        self.instanceCurrentveriosn = ''
        self.instanceHttpport = ''

    def set_env_info(self, envinfo):
        '''初始换环境信息'''
        self.envId = envinfo['envId']
        self.moduleId = envinfo['moduleId']
        self.envName = envinfo['envName']
        self.envDesc = envinfo['envDesc']
        self.vcBranch = envinfo['vcBranch']
        self.status = envinfo['status']
        # 初始化该环境下实例信息，
        # 注意:为了简化脚本，我们这里只提取一个实例信息,实际情况下一套环境下会有多个应用实例
        if envinfo['instances'].__len__() >= 1:
            self.set_env_instanceinfo(envinfo['instances'][0])

    def set_env_instanceinfo(self, instanceinfo):
        '''初始化环境中的实例信息'''
        self.instanceId = instanceinfo['instanceId']
        self.instanceStatus = instanceinfo['status']
        self.instanceHostname = instanceinfo['hostName']
        # self.instanceCurrentveriosn = instanceinfo['currentVersion']
        # self.instanceHttpport = instanceinfo['configuration']['httpPort']

    # ------------------------OMAD 接口实现-----------------------
    # TODO: this a beta version without testing.
    def copy_environment(self, envId, envName, hosts='',
                         conf='', branch='', version=''):
        '''复制环境信息'''
        url = 'cli/copy'
        params = {'token': TOKEN, 'hosts': hosts, 'envId': envId, 'envName': envName,
                  'conf': conf, 'branch': branch, 'version': version}
        call_omad_api(url, params)

    def build_version(self, version=''):
        '''构建版本'''
        url = 'cli/build'
        if self.moduleId and self.envId:
            params = {'token': TOKEN, 'moduleId': self.moduleId, 'envId': self.envId}
            if version: params['version'] = version
            logging.info("module %s build version %s." % (str(self.moduleId), self.envName))
            return call_omad_api(url, params).status_code  # result.json {u'code': 200, u'params': {}, u'success': True}
        logging.error("try to do build version failed, since module id or environment id info missed.")

    def deploy_all(self, version='', instanceId=''):
        '''一键部署'''
        url = 'cli/deploy'
        if self.moduleId and self.envId:
            params = {'token': TOKEN, 'moduleId': self.moduleId, 'envId': self.envId}
            if version: params['version'] = version
            if instanceId: params['instanceId'] = instanceId
            logging.info("module %s do deploy all of environment %s." % (str(self.moduleId), self.envName))
            return call_omad_api(url, params)  # result.json {u'code': 200, u'params': {}, u'success': True}
        logging.error("try to do deploy all instances failed, since module id or environment id info missed.")

    def start_instance(self):
        '''启动实例'''
        url = 'cli/start'
        if self.instanceId:
            params = {'token': TOKEN, 'envId': self.envId, 'instanceId': self.instanceId}
            return call_omad_api(url, params)  # result.json {u'code': 200, u'params': {}, u'success': True}
        logging.warn("module %s have no instances in environment %s." % (self.moduleId, self.envName))

    def stop_instance(self):
        '''停止实例'''
        url = 'cli/stop'
        if self.instanceId:
            params = {'token': TOKEN, 'envId': self.envId, 'instanceId': self.instanceId}
            return call_omad_api(url, params)  # result.json {u'code': 200, u'params': {}, u'success': True}
        logging.warn("module " + self.moduleId + " have no instances in environment " + self.envName + ".")

    def get_instance_status(self):
        '''获取实例状态'''
        url = 'cli/istatus'
        if self.instanceId and self.envId:
            params = {'token': TOKEN, 'envId': self.envId, 'instanceId': self.instanceId}
            return call_omad_api(url, params).json()['status']  # return status: running, stop, ''
        logging.warn("module " + str(self.moduleId) + " has no instances.")
        return ''

    # TODO: this is a beta version without testing
    def update_static_resource(self, productId, version=''):
        '''更新静态资源'''
        url = 'cli/istatus'
        params = {'token': TOKEN, 'envId': self.envId, 'moduleId': self.moduleId, 'productId': productId}
        if version: params['version'] = version
        return call_omad_api(url, params)

    # TODO: this is a beta version without testing.
    def get_static_resource(self, productId):
        '''获得静态资源'''
        url = 'cli/getstatic'
        params = {'token': TOKEN, 'envId': self.envId, 'moduleId': self.moduleId, 'productId': productId}
        return call_omad_api(url, params)

    # TODO: this is a beta version without testing.
    def change_vcbranch(self, productId, path='', branch=''):
        '''根据产品名和环境名更新所有应用的分支或代码库地址'''
        url = 'cli/vcchange'
        params = {'token': TOKEN, 'productId': productId, 'envName': self.envName}
        if path: params['path'] = path
        if branch: params['branch'] = branch
        return call_omad_api(url, params)

    def change_vcbranch_by_envid(self, productId, path='', branch=''):
        '''根据产品或环境id来更新分支或代码库地址'''
        url = 'cli/vcchange'
        params = {'token': TOKEN, 'productId': productId, 'envId': self.envId}
        if path: params['path'] = path
        if branch: params['branch'] = branch
        return call_omad_api(url, params)

    def get_env_status(self):
        '''获取环境状态'''
        url = "cli/estatus"
        params = {'token': TOKEN, 'envId': self.envId}
        # return env.status value is success or fail, (build_succ, build_fail, building)
        return call_omad_api(url, params).json()['status']


class Module(object):
    '''Module类用于实例化omad中配置的产品应用or服务信息。'''

    def __init__(self):
        '''module的初始信息'''
        self.moduleName = ''
        self.moduleId = ''
        self.productId = ''
        self.moduleDesc = ''
        self.moduleType = ''
        self.directorAccount = ''
        self.parentId = ''
        self.createTime = ''
        self.updateTime = ''
        self.dependenceIds = ''
        self.envs = {}

    def set_module_info(self, moinfo):
        '''初始化module信息'''
        self.moduleName = moinfo['moduleName']
        self.moduleId = moinfo['moduleId']
        self.productId = moinfo['productId']
        self.parentId = moinfo['parentId']
        if 'dependenceIds' in moinfo.keys():
            self.dependenceIds = moinfo['dependenceIds']

        # 实例化档期module下的环境信息
        envs = moinfo['envs']
        env_str = []
        for envinfo in envs:  # 一个应用服务可能配置了多套环境
            moenvironment = MoEnvironment()
            moenvironment.set_env_info(envinfo)
            self.envs[moenvironment.envName] = moenvironment
            env_str.append(moenvironment.envName)
        logging.debug("Found environment lists of %s: %s." % (self.moduleName, ', '.join(env_str)))


class Product(object):
    '''product类用于实例化omad上配置的产品信息'''

    def __init__(self, prName):
        '''初始化omad下用户的产品信息'''
        self.productName = ''
        self.productId = ''
        self.productDesc = ''
        self.modules = {}
        self.init_product_info(prName)

    def init_product_info(self, prName):
        '''根传入的项目名称prName,初始化在omad中的配置信息'''
        url = 'cli/ls'
        params = {'token': TOKEN}
        results = call_omad_api(url, params)
        logging.info("开始初始化%s项目信息，获得Product信息结果: %s" % (prName, str(results.status_code)))

        tartget_pro = ''
        if results.status_code == 200 and results.json():
            for r in results.json():
                if r['productName'] == prName:
                    tartget_pro = r
                    logging.info("发现%s产品信息!" % prName)
        else:
            logging.error("Get Product List Failed!")

        # 初始化Product信息
        self.productName = tartget_pro['productName']
        self.productId = tartget_pro['productId']
        self.productDesc = tartget_pro['productDesc']

        # 初始化该product下的module信息
        pro_modules = tartget_pro['modules']
        for mo in pro_modules:
            module = Module()
            module.set_module_info(mo)
            self.modules[module.moduleName] = module
            logging.debug("Found the product module named: %s." % module.moduleName)


def main():
    # 用户登录名和密码，由外部输入
    accessKey = "ae31b1b0c9154bf2ba857f8feaee846b"
    accessSecret = "85f87ed7c4b2428a91e86f00a2727ddd"
    omad_login(accessKey, accessSecret)

    vstore = Product('beauty-service-test')


#     print vstore.productName
#     print vstore.modules['vstore-all'].envs['feature1'].get_env_status()
#     for module in vstore.modules.keys():
#         if 'feature1' in vstore.modules[module].envs.keys():
#             if module not in ['storePay','PhotoCenter']:
#                 print module
#                 #vstore.modules[module].envs['feature1'].change_vcbranch(vstore.productId,branch='branch/cache0512')
#                 vstore.modules[module].envs['feature1'].update_static_resource(vstore.productId,'')

if __name__ == '__main__':
    main()
