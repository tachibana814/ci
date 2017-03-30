# -*- encoding: utf-8 -*-
'''
Created on 2015年4月14日

@author: Hzdingweiwei
'''
import os
from gitjenkinsdiff import *
from beauty_auto_deploy import *

# beauty项目中provider工程源码与应用映射关系
code_service_mapping = {
    "beauty-user": "beauty-user",  # path:app
    "beauty-ugc": "beauty-ugc",
    "beauty-sns": "beauty-sns",
    "beauty-content": "beauty-content",
    "beauty-ic": "beauty-ic"
}


def get_deploy_websiteapp_by_source_changed(changed_filelist):
    '''根据代码变更文件目录和app的映射，列出需要更新的app'''
    applist = []
    if changed_filelist:
        for chfile in changed_filelist:
            file_paths = chfile.split(os.sep)
            try:
                if file_paths[1] in code_service_mapping.keys():
                    applist.append(code_service_mapping[file_paths[1]])
            except IndexError, e:
                print e, "%s.split(os.sep)[1]" % chfile
    applist = list(set(applist))  # 去重
    return applist


def filter_front_end_source_changes(source_files):
    '''过滤掉前端代码的提交，这些提交不影响编译和静态代码检查的结果。'''
    file_types = ['js', 'json', 'mcss', 'css', 'html', 'ftl', 'txt', 'sh', 'bat']
    changed_files = []
    for s_file in source_files:
        if str(s_file).split('.')[-1] not in file_types:
            changed_files.append(s_file)
    return changed_files


if __name__ == '__main__':
    changed_filelist = ['vstore-parent/beauty-ugc/mainsite-web/src/main/resources/public/',
                        'readme.md',
                        'vstore-parent/beauty-content/vstore-itemcenter-provider/src/main/']
    print get_deploy_websiteapp_by_source_changed(changed_filelist)
