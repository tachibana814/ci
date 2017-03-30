#-*- encoding: utf-8 -*-
'''
Created on 2015年5月14日

@author: Hzdingweiwei

@summary: 修改产品某套环境的代码部署分支
'''

import sys
from omad_proinfo import *
import logging
import argparse
from beauty_auto_deploy import *

logging_setup()

#source_file, product_name, module_list, env_name, code_branch, accessKey, accessSecret = sys.argv

product_name = ''
module_list = ''
env_name = ''
code_branch = ''
accessKey = ''
accessSecret = ''

parser = argparse.ArgumentParser()
parser.add_argument('--productname',  required=product_name is None, default=product_name)
parser.add_argument('--modulelist',  required=module_list is None, default=module_list)
parser.add_argument('--envname',  required=env_name is None, default=env_name)
parser.add_argument('--codebranch',  required=code_branch is None, default=code_branch)
parser.add_argument('--accessKey',  required=accessKey is None, default=accessKey)
parser.add_argument('--accessSecret',  required=accessSecret is None, default=accessSecret)
args = parser.parse_args()

BRANCH_CHA_MODULES = []

logging.info("")
logging.info("开始切换%s产品%s环境的代码分支为%s应用列表:%s. " % (args.productname, args.envname, args.codebranch, args.modulelist))
logging.info("")
if args.productname and args.modulelist and args.envname:
    #用户登录名和密码，由外部输入
    #accessKey = "ae31b1b0c9154bf2ba857f8feaee846b"
    #accessSecret = "85f87ed7c4b2428a91e86f00a2727ddd"
    omad_login(args.accessKey, args.accessSecret)
    beauty = Product(args.productname)
    logging.info("")
    if ',' in args.modulelist:
        BRANCH_CHA_MODULES = args.modulelist.split(',')
    else:
        BRANCH_CHA_MODULES.append(args.modulelist)

    print BRANCH_CHA_MODULES

    for module in BRANCH_CHA_MODULES:
        if 'all' == module:
            if args.envname in beauty.modules[beauty.modules.keys()[0]].envs.keys():
                beauty.modules[beauty.modules.keys()[0]].envs[args.envname].change_vcbranch(beauty.productId, branch=args.codebranch)
                logging.info("[SUCCEED]Change code branch as [%s] on env [%s] for [all] modules." % (args.codebranch, args.envname))
        if (module in beauty.modules.keys()) and (args.envname in beauty.modules[module].envs.keys()):
            beauty.modules[module].envs[args.envname].change_vcbranch_by_envid(beauty.productId, branch=args.codebranch)
            logging.info("[SUCCEED]Change code branch as [%s] on env [%s] for module [%s]." % (args.codebranch, args.envname, module))
    logging.info("")
