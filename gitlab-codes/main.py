# coding=utf-8
from singer import Singer
import gitlab
import xlwt
import requests
import urllib3


def get_projects():
    config = Singer.config(mode='gitlab')
    host = config.get_config('url')
    token = config.get_config('token')
    session = requests.Session()
    client = gitlab.Gitlab(host, token, session=session, api_version=4,ssl_verify=False)
    client.enable_debug()
    print(client.api_url)
    projects = client.projects.list(all=True)
    urllib3.connectionpool.HTTPConnectionPool
    return projects


def get_branches(project):
    branches = project.branches.list(all=True)
    return branches


def get_commits(project, branch):
    author_commits = []
    commits = project.commits.list(
        all=True, ref_name=branch.name, since='2020-01-01', until='2021-01-01')
    for commit in commits:
        title = commit.title
        message = commit.message
        if ('Merge' in message) or ('Merge' in title):
            print('Merge跳过')
            continue
        else:
            author_commits.append(commit)
    return author_commits


def get_commit_codes(commit, project):
    commit_info = project.commits.get(commit.id)
    code = commit_info.stats
    return code


def get_author_code():
    data = []
    projects = get_projects()
    for project in projects:
        branches = get_branches(project)
        for branch in branches:
            print('获取工程', project.name, '分支', branch.name, "的提交记录")
            branchdata = {}
            branchdata['projectname'] = project.name
            branchdata['branchename'] = branch.name
            author_commits = get_commits(project, branch)
            codes = []
            for commit in author_commits:
                print('获取提交', commit.id, "的代码量")
                code = get_commit_codes(commit, project)
                codes.append(code)
            record = calculate(codes)
            branchdata['commitcount'] = len(author_commits)
            branchdata['codecount'] = record
            data.append(branchdata)
    return data


def wirte_excel(excelPath, data):
    workbook = xlwt.Workbook()
    # 获取第一个sheet页
    sheet = workbook.add_sheet('git')
    row0 = ['工程名称', '分支名称', '提交次数', '新增代码', '删除代码', '总计代码']
    for i in range(0, len(row0)):
        sheet.write(0, i, row0[i])
    addcount = 0
    delcount = 0
    totalcount = 0
    commitcount = 0
    for i in range(0, len(data)):
        recode = data[i]
        j = 0
        sheet.write(i+1, j, recode['projectname'])
        sheet.write(i+1, j+1, recode['branchename'])
        commitcount += (int)(recode['commitcount'])
        sheet.write(i+1, j+2, recode['commitcount'])
        addcount += (int)(recode['codecount']['additions'])
        sheet.write(i+1, j+3, recode['codecount']['additions'])
        delcount += (int)(recode['codecount']['deletions'])
        sheet.write(i+1, j+4, recode['codecount']['deletions'])
        totalcount += (int)(recode['codecount']['total'])
        sheet.write(i+1, j+5, recode['codecount']['total'])
    sheet.write(len(data)+1, 2, commitcount)
    sheet.write(len(data)+1, 3, addcount)
    sheet.write(len(data)+1, 4, delcount)
    sheet.write(len(data)+1, 5, totalcount)
    workbook.save(excelPath)


def calculate(data):
    record = {}
    addacount = 0
    deletecount = 0
    totaolcount = 0
    for i in data:
        addacount += int(i['additions'])
        deletecount += int(i['deletions'])
        totaolcount += int(i['total'])
    record['additions'] = addacount
    record['deletions'] = deletecount
    record['total'] = totaolcount
    return record


if __name__ == '__main__':
    data = get_author_code()
    wirte_excel('d:/gitlab.xls', data)
