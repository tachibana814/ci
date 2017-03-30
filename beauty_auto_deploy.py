# -*- encoding: utf-8 -*-
'''
Created on 2017.1.5

@author: hzdingweiwei
'''
import logging
import time
import sys
from logging.handlers import RotatingFileHandler
from omad_proinfo import *
from deploy_result import DeployResult

# 生产者服务
BEAUTY_PROVIDER = ['beauty-user',
                   'beauty-ic',
                   'beauty-content',
                   'beauty-ugc',
                   'beauty-sns']

# 消费者服务
BEAUTY_CONSUMER = ['beauty-mainsite-web',
                   'beauty-wap-web',
                   'beauty-oms-web',
                   'beauty-app-web',
                   'beauty-datams-web',  # 数据平台，cms
                   'beauty-job-web']  # 异步调度服务

# 前端应用
BEAUTY_FRONT_WEB = ['beauty-datams-node',
                    'beauty-wap-node',
                    'beauty-mainsite-node',
                    'beauty-oms-node']

# 保存部署过程中启动失败的应用服务
failed_app_list = []
succ_app_list = []
timeout_app_list = []

# 环境部署成功的两种状态
env_succ_state = ['success', 'build_succ']

# 初始化部署结果
deploy_result = DeployResult()


def deploy_target_app(product, env, targetapp, version='', instanceId=''):
    '''一件部署指定的应用服务,重新部署之前'''
    if targetapp in product.modules.keys():
        if env in product.modules[targetapp].envs.keys():
            httpresult = product.modules[targetapp].envs[env].deploy_all()
            if httpresult.status_code == 200:
                logging.info("执行一件部署%s成功!" % targetapp)
            else:
                logging.warn("执行意见部署%s失败!" % targetapp)
        else:
            logging.warn("%s应用下没有找到%s环境信息!" % (targetapp, env))
    else:
        logging.warn("在%s项目下没有找到%s应用!" % (product.productName, targetapp))


def deploy_target_group_apps(product, env, groupapps, targetapps, version='', instanceId=''):
    '''一键部署指定组别的服务'''
    if targetapps == 'all':
        for app in groupapps:
            deploy_target_app(product, env, app)
    elif type(targetapps) is type([]) and targetapps:
        for app in targetapps:
            if app in groupapps:
                deploy_target_app(product, env, app)
    else:
        return


def stop_module_service(product, env, module):
    '''停止指定的应用服务'''
    httpresult = product.modules[module].envs[env].stop_instance()
    if httpresult.status_code == 200:
        time.sleep(5)
        module_state = get_app_status(product, env, module)[0]
        print module_state
        if 'stop' == module_state:
            logging.info("应用服务%s被停止!" % module)
            return module_state
    logging.error("停止%s应用服务失败!" % module)


def deploy_provider_apps(product, env, targetapps='', version='', instanceId=''):
    '''一键部署生产者应用服务'''
    deploy_target_group_apps(product, env, BEAUTY_PROVIDER, targetapps)


def deploy_consumer_apps(product, env, targetapps='', version='', instanceId=''):
    '''一键部署消费者应用服务'''
    deploy_target_group_apps(product, env, BEAUTY_CONSUMER, targetapps)


def deploy_front_web(product, env, targetapps='', version='', instanceId=''):
    '''一键部署前端服务'''
    deploy_target_group_apps(product, env, BEAUTY_FRONT_WEB, targetapps)


def wait_until_app_startup(product, env, app, timeout='200', retry_interval='20'):
    '''检查和等待指定app启动'''
    maxtime = time.time() + float(timeout)
    error = None
    while not error:
        try:
            return check_app_status(product, env, app)
        except StatusFailure, err:
            if err.dont_continue:
                raise
            if time.time() > maxtime:
                error = unicode(err)
            else:
                time.sleep(float(retry_interval))
    msg = "Waiting for Module %s startup timeout!" % app
    logging.error(msg)
    deploy_result.set_deploy_timeout_apps(app)
    raise AssertionError(msg)


def wait_until_apps_startup(product, env, applist='all'):
    '''检查和等待指定一组app启动'''
    if applist:
        for app in applist:
            app_append = ''
            try:
                instance_status, deploy_status = wait_until_app_startup(product, env, app)
                if instance_status in ['stop', 'undeploy'] or deploy_status in ['build_fail', 'deploy_fail']:
                    app_with_branch = app + '[' + product.modules[app].envs[env].vcBranch + ']'
                    deploy_result.set_deploy_failed_apps(app_with_branch)
                else:
                    app_with_branch = app + '[' + product.modules[app].envs[env].vcBranch + ']'
                    deploy_result.set_deploy_succ_apps(app_with_branch)
            except Exception, e:
                continue


class StatusFailure(Exception):
    """应用服务状态异常时抛出异常."""

    def __init__(self, message, timeout=False, return_value=None):
        if '\r\n' in message:
            message = message.replace('\r\n', '\n')
        Exception.__init__(self, message)
        self.timeout = timeout
        self.return_value = return_value

    @property
    def dont_continue(self):
        return self.timeout

    def get_errors(self):
        return [self]


def logging_setup():
    '''logging初始化'''
    logging.basicConfig(level=logging.DEBUG,
                        encode='utf-8',
                        format='%(asctime)s [%(levelname)s]: %(message)s',
                        datefmt='%d %b %Y %H:%M:%S',
                        filename='autodeploy.log',
                        filemode='w')  # w

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s [%(levelname)s]: %(message)s")
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    Rthandler = RotatingFileHandler('autodeploy_record.log', maxBytes=10 * 1024 * 1024, backupCount=5)
    Rthandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(filename)s [line %(lineno)d] %(levelname)s %(message)s')
    Rthandler.setFormatter(formatter)
    logging.getLogger('').addHandler(Rthandler)


def get_app_status(product, env, module):
    '''获得应用服务实例的状态,如何omad上没有配置该应用或者环境直接返回失败状态.'''
    instance_status = "stop"
    deploy_status = "build_fail"
    instance_status = product.modules[module].envs[env].get_instance_status()
    deploy_status = product.modules[module].envs[env].get_env_status()
    return instance_status, deploy_status


def check_app_status(product, env, module):
    '''检查应用服务实例的状态,如果不是working状态则抛出异常.'''
    instance_status, deploy_status = get_app_status(product, env, module)
    if instance_status in ['stop', 'undeploy'] or deploy_status in ['build_fail', 'deploy_fail']:
        if module.moduleType == 3:  # Node.js类型的应用重启过程中会先stop,所以不返回中间的stop状态
            return deploy_status
        return instance_status, deploy_status
    elif instance_status != 'running' or deploy_status not in env_succ_state:
        msg = "Module %s Instance is %s env in %s state!" % (module, instance_status, deploy_status)
        logging.warn(msg)
        raise StatusFailure, msg
    else:
        logging.info("[PASS]Module %s is already running!" % module)
    return instance_status, deploy_status


def deploy_beauty_product_apps(product, env, targetapps):
    '''一键部署美妆项目的所有应用服务。
    targetapps: [] or ['app1','app2'] or 'all'
    '''
    if targetapps:
        # 部署生产者工程
        deploy_provider_apps(product, env, targetapps)
        time.sleep(2)
        if targetapps == 'all':
            wait_until_apps_startup(product, env, BEAUTY_PROVIDER)
        else:
            wait_until_apps_startup(product, env, get_contain_list(BEAUTY_PROVIDER, targetapps))

        # 部署消费者工程
        deploy_consumer_apps(product, env, targetapps)
        time.sleep(2)
        if targetapps == 'all':
            wait_until_apps_startup(product, env, BEAUTY_CONSUMER)
        else:
            wait_until_apps_startup(product, env, get_contain_list(BEAUTY_CONSUMER, targetapps))

        '''2017.2.22注释掉前端的部署，前端代码人为操作部署和管理
        #部署前端工程
        deploy_front_web(product, env, BEAUTY_FRONT_WEB)
        time.sleep(2)
        if targetapps == 'all':
            wait_until_apps_startup(product, env, BEAUTY_FRONT_WEB)
        else:
            wait_until_apps_startup(product, env, get_contain_list(BEAUTY_FRONT_WEB, targetapps))
        '''
        print_app_deploy_result()
    else:
        logging.warn("没有找到需要更新部署的应用!")


def get_contain_list(sourceList, taragetList):
    resultList = []
    for ta in taragetList:
        if ta in sourceList:
            resultList.append(ta)
    return resultList


def print_app_deploy_result():
    '''打印应用部署状态结果。
    '''
    return_app_list = []
    succ_app_list = deploy_result.get_deploy_succ_apps()
    if succ_app_list:
        succ_app_list = list(set(succ_app_list))
        logging.info("Deployed result SUCCEED APP List:\n%s" % ',\n'.join(succ_app_list))
    failed_app_list = deploy_result.get_deploy_failed_apps()
    if failed_app_list:
        failed_app_list = list(set(failed_app_list))
        failed_msg = "Deployed result FAILED APP List:\n%s" % ',\n'.join(failed_app_list)
        logging.error(failed_msg)
        write_file(failed_msg, "deploy.result")
    timeout_app_list = deploy_result.get_deploy_timeout_apps()
    if timeout_app_list:
        timeout_app_list = list(set(timeout_app_list))
        logging.error("Deployed result TIMEOUT APP List:\n%s" % ',\n'.join(timeout_app_list))


def write_file(message, filename="tmp.properties"):
    '''数据持久化到本地'''
    infile = open(filename, 'w')
    infile.write(message)
    infile.close()


def check_vstore_service_status(product, env, targetapps):
    '''检查产品应用状态'''
    if targetapps == 'all':
        wait_until_apps_startup(product, env, BEAUTY_PROVIDER)
        wait_until_apps_startup(product, env, BEAUTY_CONSUMER)
        wait_until_apps_startup(product, env, BEAUTY_FRONT_WEB)
    else:
        wait_until_apps_startup(product, env, targetapps)
    print_app_deploy_result()


def main():
    logging_setup()

    # 用户登录名和密码，由外部输入
    accessKey = "ae31b1b0c9154bf2ba857f8feaee846b"
    accessSecret = "85f87ed7c4b2428a91e86f00a2727ddd"
    omad_login(accessKey, accessSecret)

    vstore = Product('vstore')
    check_vstore_service_status(vstore, 'test', 'all')


#     code_compile(vstore, 'feature1')
##    deploy_apps=['vstore-itemcenter-web','wap-web']
##    deploy_vstore_product_apps(vstore, 'performance', deploy_apps)
#     stop_module_service(vstore, 'feature1', 'vstore-order-web')
#     vstore.modules['vstore-order-web'].envs['feature1'].deploy_all()
#     time.sleep(2)
#     wait_until_app_startup(vstore, 'feature1', 'vstore-order-web')


if __name__ == '__main__':
    main()



