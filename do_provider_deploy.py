# -*- encoding: utf-8 -*-
'''
Created on 2017年1月5日

@author: Hzdingweiwei
'''
import sys
import logging
import argparse
from beauty_source_filter import *
from beauty_auto_deploy import *
from beauty_auto_deploy import deploy_result

logging_setup()  # 配置logging规则

# ------------------------------------------------------------------------------------------------
product_name = ''
env_name = ''
depmethod = ''
redeploy = 'false'
accessKey = ''
accessSecret = ''

parser = argparse.ArgumentParser()
parser.add_argument('--productname', required=product_name is None, default=product_name)
parser.add_argument('--envname', required=env_name is None, default=env_name)
parser.add_argument('--depmethod', required=depmethod is None, default=depmethod)
parser.add_argument('--redeploy', required=redeploy is None, default=redeploy)
parser.add_argument('--accessKey', required=accessKey is None, default=accessKey)
parser.add_argument('--accessSecret', required=accessSecret is None, default=accessSecret)
args = parser.parse_args()

logging.info(3 * '\n')
logging.info(15 * '-' + "执行自动化部署" + 15 * '-')
logging.info("获得输入信息,产品:%s,环境:%s,部署规则:%s." % (args.productname, args.envname, args.depmethod))

# -----------------------------------------------------------------------------------------------
deploy_app = ''  # 需要部署的应用服务
if args.depmethod == 'all':
    deploy_app = 'all'  # 默认部署所有的应用服务
elif args.depmethod == 'codeupdate':
    changed_files = get_changed_files_list()
    deploy_app = get_deploy_websiteapp_by_source_changed(changed_files)
else:
    pass
logging.info("获得需要部署的服务列表: %s" % ','.join(deploy_app))

# ------------------------------------------------------------------------------------------------
if args.productname and args.envname:
    # 用户登录名和密码，由外部输入
    # accessKey = "ae31b1b0c9154bf2ba857f8feaee846b"
    # accessSecret = "85f87ed7c4b2428a91e86f00a2727ddd"
    omad_login(args.accessKey, args.accessSecret)

    vstore = Product(args.productname)  # 实例化产品信息
    if args.depmethod in ['all', 'codeupdate'] and deploy_app != '':
        deploy_beauty_product_apps(vstore, args.envname, deploy_app)  # 部署环境
    elif args.depmethod == 'appstatecheck':
        check_vstore_service_status(vstore, args.envname, 'all')
    else:
        pass

    # --------------------------------------------------------------------------------------------------
    # 根据变量值尝试重新部署
    redeploy_list = []
    redeploy_list = deploy_result.get_deploy_timeout_apps() + deploy_result.get_deploy_failed_apps()
    if 'false' != redeploy and len(redeploy_list):
        logging.info(15 * '-' + "失败应用执行重新部署" + 15 * '-')
        logging.info("重新部署的服务列表: %s" % ','.join(redeploy_list))
        deploy_result.init_deploy_result()  # 重置全局变量的值
        deploy_beauty_product_apps(vstore, args.envname, redeploy_list)  # 重新部署失败的APP
    # 退出程序
    fail_apps = deploy_result.get_deploy_failed_apps() + deploy_result.get_deploy_timeout_apps()
    sys.exit(len(fail_apps))
