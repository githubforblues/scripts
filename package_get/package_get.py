#!/usr/bin/python
# coding=utf-8
#
#

import subprocess
import re
import os
import datetime
import argparse
import re
import sys

import eteams_serverlist

parser = argparse.ArgumentParser(prog='package_get')
parser.add_argument('-l', dest='list', action='store_true', help='show package list from package source')
parser.add_argument('-i', dest='intelligent', action='store_true', help='upload package intelligent')
parser.add_argument('-p', dest='pattern', help='pattern package filename')
args = parser.parse_args()

package_source = "192.168.0.1"
package_dir = "/data/update"
package_auto_upload_time = "1d"

# 获取所有安装包的文件属性信息
def packageinfo():
    packagelist_get_cmd = 'ssh {0} "{1} {2}/*"'.format(package_source,"stat ",package_dir)

    package_stat = subprocess.Popen('{0}'.format(packagelist_get_cmd), shell=True, stdout=subprocess.PIPE)
    out = package_stat.communicate()[0].split(os.linesep)

    package_info = []

    for i in range(1,len(out)):
        if i%7 == 1:
            m = re.match(r'\W+File:\W+(?P<path>\/.*\.war)\W', out[i-1])
            package_info.append([m.group('path')])
        elif i%7 == 6:
            timestamp = out[i-1].split("Modify: ")[1].split(".")[0]
            package_info[len(package_info)-1].append(datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S"))

    package_info.sort(key=lambda x:x[1], reverse=True)

    return package_info

# 获取表示时间长度的对象
def timehandler(time):
    units = {'m':'minutes', 'h':'hours', 'd':'days'}
    m = re.match(r'(?P<value>\d+)(?P<unit>[a-zA-Z])', time)
    for unit in units.keys():
        if m.group('unit').lower() == unit:
            strtime = {}
            strtime[units[unit]] = int(m.group('value'))
            print('获取最近 {0} 的数据包...'.format(time))
            return datetime.timedelta(**strtime)

# 过滤需要上传的安装包
def packagefilter(package_info, time='', pattern=''):
    packagefiltered_info = []

    # 基于时间过滤
    if time:
        dtime = timehandler(time)
        nowtime = datetime.datetime.now()
        for info in package_info:
            if nowtime - info[1] < dtime:
                packagefiltered_info.append(info)
            else:
                break
        return packagefiltered_info

    # 基于名称匹配过滤
    if pattern:
        for info in package_info:
            pattern_string = r'.*{0}.*'.format(pattern)
            m = re.match(pattern_string, info[0])
            if m != None:
                packagefiltered_info.append(info)
        return packagefiltered_info

# 先备份旧的安装包，然后上传新安装包
def uploadpackage(package_info):
    print('备份安装包...')
    subprocess.call('mv /data/update/ /data/updatebak`date +%Y%m%d%H%M/`; mkdir /data/update/', shell=True)
    for info in package_info:
        scp_cmd = 'scp {0}:{1} {2}/'.format(package_source, info[0], package_dir)
        subprocess.call(scp_cmd, shell=True)

# 显示将要上传的安装包
def showpackage(packageinfo):
    for info in packageinfo:
        print('{0} {1}'.format(info[1].strftime("%Y-%m-%d %H:%M"), info[0]))

# 分发安装包
def packagedist(package_info):
    distlist = []
    for info in package_info:
        packagename = info[0].rsplit('/',1)[1].split('.',1)[0]
        for i in eteams_serverlist.serverlist:
            for j in i[2]:
                if packagename == j:
                    packagepath = '{0}{1}{2}'.format('/data/update/',packagename,'.war')
                    distlist.append([packagepath, i[1], i[0]])

    for distpackage, distip, disthostname in distlist:
        print('{0} -> {1}'.format(distpackage, disthostname))
        dist_cmd = 'scp {0} {1}:{2}'.format(distpackage, distip, '/data/update/')
        subprocess.call(dist_cmd, shell=True)

def main():
    PINFO = packageinfo()

    # 查看所有安装包
    if args.list:
        showpackage(PINFO)
        sys.exit(0)

    # 智能获取安装包
    elif args.intelligent:
        PFINFO = packagefilter(PINFO, time=package_auto_upload_time)
        showpackage(PFINFO)
        choice = raw_input("请确认上传的安装包[y/N]: ")
        sys.exit(0) if choice != "y" else uploadpackage(PFINFO)

    # 通过文件名匹配方式获取安装包
    elif args.pattern:
        pattern = args.pattern
        PFINFO = packagefilter(PINFO, pattern=pattern)
        showpackage(PFINFO)
        choice = raw_input("请确认上传的安装包[y/N]: ")
        sys.exit(0) if choice != "y" else uploadpackage(PFINFO)

    # 向所有服务器分发安装包
    choice = raw_input("是否向对应服务器分发安装包[y/N]: ")
    sys.exit(0) if choice != 'y' else packagedist(PFINFO)

if __name__ == '__main__':
    main()


