# coding=utf-8
from singer import Singer
import requests
import json
import xlwt

# pip3 install singer xlwt


class GitlabRest(object):
    def __init__(self):
        config = Singer.config(mode='gitlab')

        self.__gateway = config.get_config('url').strip('/')
        self.__api_url = "%s/api/v4" % self.__gateway
        self.__token = config.get_config('token')
        self.__session = requests.session()
        self.__session.keep_alive = False

    def __request(self, api, method='GET', payload={}):
        url = "%s/%s" % (self.__api_url, api)
        payload["private_token"] = self.__token
        response = self.__session.request(method, url, data=payload)
        code = response.status_code
        if code != 200:
            return None
        return json.loads(response.text)

    def __get_all(self, api, payload={}):
        data_list = []
        payload['per_page'] = 100
        page = 1
        while True:
            payload['page'] = page
            items = self.__request(api, payload=payload)
            if items == None or len(items) == 0:
                break
            else:
                page += 1
                data_list.extend(items)
        return data_list

    def get_users(self, page=1, size=20, all=False):
        api = 'users'
        if all:
            return self.__get_all(api)
        else:
            return self.__request(api, payload={
                'page': page,
                'per_page': size
            })

    def get_users_simple(self, page=1, size=20, all=False):
        users = self.get_users(page, size, all)
        data = {}
        for user in users:
            data[user['email']] = user['name']
        return data

    def get_projects(self, page=1, size=20, all=False):
        api = 'projects'
        if all:
            return self.__get_all(api)
        else:
            return self.__request(api, payload={
                'page': page,
                'per_page': size
            })

    def get_branches(self, project_id):
        url = "projects/%d/repository/branches" % project_id
        branches = self.__request(url)
        return branches

    def get_commits(self, project_id, branch, start_time=None, end_time=None, page=1, size=20, all=False):
        api = "projects/%d/repository/commits" % (project_id)
        payload = {
            'ref_name': branch,
            'order_by': 'created_at',
            'sort': 'asc'
        }
        if start_time:
            payload['since'] = start_time
        if end_time:
            payload['until'] = end_time
        if all:
            return self.__get_all(api, payload)
        else:
            payload['page'] = page
            payload['per_page'] = size
            return self.__request(api, payload=payload)

    def get_commit(self, project_id, commit_id):
        api = "projects/%d/repository/commits/%s" % (project_id, commit_id)
        return self.__request(api)

    def get_codes(self, start_time=None, end_time=None):
        projects = self.get_projects(all=True)
        data = []
        commit_ids = []
        users = self.get_users_simple(all=True)

        def get_project(project):
            id = project['id']
            branches = [i['name'] for i in self.get_branches(id)]
            print(id, project['name'], ','.join(branches))
            for branch in branches:
                commits = self.get_commits(
                    id, branch, start_time, end_time, all=True)
                print("%d:%s,commits:%d" % (id, branch, len(commits)))
                for commit in commits:
                    commit_id = commit['id']
                    if commit_id in commit_ids:
                        continue
                    commit_data = self.get_commit(id, commit_id)
                    # print(commit_data)
                    commit_stats = commit_data['stats']
                    committer_email = commit_data['committer_email']
                    committer_name = commit_data['committer_name']
                    if committer_email in users:
                        committer_name = users[committer_email]

                    data.append({
                        'project_id': id,
                        'group': project['namespace']['full_path'],
                        'project': project['name'],
                        'desc': project['description'],
                        'branch': branch,
                        'commit_id': commit_id,
                        'created_at': commit_data['created_at'],
                        'message': commit_data['message'],
                        'author': committer_name,
                        'author_name': committer_name,
                        'author_email': committer_email,
                        'additions': commit_stats['additions'],
                        'deletions': commit_stats['deletions'],
                        'total': commit_stats['total']
                    })
                    commit_ids.append(commit_id)
                    # print(commit_id, commit_data)

        with Singer.executor(max_workers=6) as executor:
            for project in projects:
                executor.start(get_project, project)
            executor.wait_complete()
        return data


def write_excel(data, excel_path):
    workbook = xlwt.Workbook()
    # 获取第一个sheet页
    sheet = workbook.add_sheet('git')
    row0 = ['项目ID', '分组', '项目名称', '项目描述', '分支名称', '提交ID',
            '新增代码', '删除代码', '总行数',  '提交时间', '提交人', '提交人邮箱', '备注消息']
    for i in range(0, len(row0)):
        sheet.write(0, i, row0[i])
    for i in range(0, len(data)):
        row = i+1
        recode = data[i]
        sheet.write(row, 0, recode['project_id'])
        sheet.write(row, 1, recode['group'])
        sheet.write(row, 2, recode['project'])
        sheet.write(row, 3, recode['desc'])
        sheet.write(row, 4, recode['branch'])
        sheet.write(row, 5, recode['commit_id'])
        sheet.write(row, 6, recode['additions'])
        sheet.write(row, 7, recode['deletions'])
        sheet.write(row, 8, recode['total'])
        sheet.write(row, 9, recode['created_at'])
        sheet.write(row, 10, recode['author_name'])
        sheet.write(row, 11, recode['author_email'])
        sheet.write(row, 12, recode['message'])
    workbook.save(excel_path)


if __name__ == "__main__":
    gl = GitlabRest()
    # users = gl.get_users_simple(all=True)
    # print(users)
    data = gl.get_codes('2020-01-01', '2021-01-01')
    write_excel(data, 'd://gitlab_02.xlsx')
