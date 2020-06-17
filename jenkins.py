import requests
import sys
import getopt
import time

requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
HOST = 'http://jenkins.local'
CRUMB = 'a0854aedfb3062b192f80d648b9d2b45'
COOKIE = 'jenkins-timestamper-offset=-28800000; ACEGI_SECURITY_HASHED_REMEMBER_ME_COOKIE=c2hheToxNTkyMzg0MjU0NTE2OmNmZTk0YmRjMDg1NWFmNWQ1ZjQ1MzY2ODI5ZDU5Njc0NDc0ZGY2N2U0Yjk1NzMwOTMyNWMzNGMwMDUwNmQ3ZmI=; JSESSIONID.a1aac16c=node010x97xouwg9kmkhsh6pvqrf64176.node0; screenResolution=1920x1080"'


def build(name, branch, delay='0sec'):
    url = '%s/job/%s/job/%s/build?delay=%s' % (HOST, name, branch, delay)
    # print(url)
    s = requests.session()
    s.keep_alive = False
    headers = {
        "Jenkins-Crumb": CRUMB,
        "Cookie": COOKIE
    }
    response = s.request("POST", url, headers=headers)
    code = response.status_code
    if code in [200, 201]:
        print('\033[32mexec %s:%s delay:%s ->\033[0m %s' %
              (name, branch, delay, '执行成功'))
    else:
        print('\033[31mexec %s:%s delay:%s ->\033[0m %s' %
              (name, branch, delay, code))


def release_build(names=[], delay='0sec'):
    # Relase
    list = [
        {"name": 'micro-main', "branch": 'release'},
        {"name": 'micro-user', "branch": 'release'},
        {"name": 'micro-market', "branch": 'release'},
        {"name": 'micro-vehicle', "branch": 'release'},
        {"name": 'micro-story', "branch": 'release'},
        {"name": 'micro-sword', "branch": 'release'},
        {"name": 'micro-gap', "branch": 'release'},
        {"name": 'micro-shield', "branch": 'release'},
        {"name": 'micro-guard', "branch": 'release'},
        {"name": 'gateway-app', "branch": 'release'},
        {"name": 'gateway-appm', "branch": 'release'},
        {"name": 'gateway-delaer', "branch": 'release'},
        {"name": 'gateway-shield', "branch": 'release'},
        {"name": 'gateway-maker', "branch": 'release'},
    ]
    names_len = len(names)

    for item in list:
        name = item['name']
        if names_len > 0 and name not in names:
            continue
        item['delay'] = delay
        print(item)

        name = 'release_%s' % name
        build(name, item['branch'], item['delay'])
        time.sleep(2)


def test_build(names=[], delay='0sec'):
    # Test
    list = [
        {"name": 'micro-main', "branch": 'v3'},
        {"name": 'micro-user', "branch": 'v3'},
        {"name": 'micro-market', "branch": 'v3'},
        {"name": 'micro-vehicle', "branch": 'master'},
        {"name": 'micro-story', "branch": 'v3'},
        {"name": 'micro-sword', "branch": 'v3'},
        {"name": 'micro-gap', "branch": 'master'},
        {"name": 'micro-shield', "branch": 'v3'},
        {"name": 'micro-guard', "branch": 'master'},
        {"name": 'gateway-app', "branch": 'v3'},
        {"name": 'gateway-appm', "branch": 'v3'},
        {"name": 'gateway-delaer', "branch": 'v3'},
        {"name": 'gateway-shield', "branch": 'v3'},
        {"name": 'gateway-maker', "branch": 'v3'}
    ]
    names_len = len(names)
    for item in list:
        name = item['name']
        if names_len > 0 and name not in names:
            continue
        item['delay'] = delay
        print(item)
        build(name, item['branch'], item['delay'])
        time.sleep(2)


def show_helper(code=0):
    print('jenkins.py -m <mode> -n <names> -d <delay> -c <cookie>')
    if code == 0:
        sys.exit()
    else:
        sys.exit(code)


if __name__ == "__main__":
    argv = sys.argv[1:]
    mode = 'test'
    names = []
    delay = '0sec'
    try:
        opts, args = getopt.getopt(
            argv, "hm:n:d:c:", ["mode=", "names=", 'delay=', 'cookie='])
    except getopt.GetoptError:
        show_helper(2)
    for opt, arg in opts:
        if opt == '-h':
            show_helper()
        elif opt in ('-m', '--mode'):
            if arg in ('test', 'prod'):
                mode = arg
        elif opt in ('-n', '--name', '--names'):
            names = arg.split(',')
        elif opt in ('-d', '--delay'):
            delay = arg
        elif opt in ('-c', '--cookie'):
            COOKIE = arg

    # print('mode: %s' % mode)
    # print('names: %s' % names)
    # print('delay: %s' % delay)
    if mode == 'test':
        test_build(names, delay)
    elif mode == 'prod':
        release_build(names, delay)
