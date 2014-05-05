__author__ = 'Govnocode('

import sqlite3
import subprocess
import time
import json
from socket import socket, gethostbyname, AF_INET, SOCK_STREAM


con=sqlite3.connect('test.db')
cur = con.cursor()
build_session = str(time.time())
sshparams='-i /home/alexa/works/dima/virt/builder/docker/ssh_keys/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o ConnectTimeout=10'
postgres = {'count': 3, 'mode': 'master-slave',
                       'pgpool': {'mode': 'standin', 'connaddr': '192.168.55.55', 'wathdog': 'on'},
                       'create': {'user': {'name': 'frontendprj', 'db': 'frontendprj', 'pass': 'testpasswd'}}}

postgres2 = {'count': 3, 'mode': 'master-slave',
                       'pgpool': {'mode': 'standin', 'connaddr': '192.168.55.77', 'wathdog': 'on'},
                       'create': {'user': {'name': 'frontendprj', 'db': 'frontendprj', 'pass': 'testpasswd'}}}



nginx = {'count': 1, 'connaddr': '195.168.55.66', 'config': {'pynginxconfig':
        {'backend': {'target': {'1': {'docker': {'php-fpm': 'c_host'}}}}
        }}}

nginx2 = {'count': 1, 'connaddr': '195.168.55.66', 'config': {'pynginxconfig':
        {'backend': {'target': {'2': {'docker': {'php-fpm': 'c_host'}}}}
        }}}


phpfpm = {'count': 2, 'config':
    {'data':
    {'dest': '/usr/share/nginx', 'source':
    {'git': 'https://github.com/babnikzero/backend'}},
    'editfile': {'/usr/share/nginx/app/config/database.php':
                 {"'default' =>[^>]*": "'default' => 'production',"}}},
    'exec': {'target': {'1': {'docker': {'postgres': {'create': {'user': {'name': 'frontendprj', 'db': 'frontendprj', 'pass': 'testpasswd'}}}}}}},
    'runonce': ['cd /usr/share/nginx&&php artisan migrate:install', 'cd /usr/share/nginx&&php artisan migrate', 'cd /usr/share/nginx&&php artisan db:seed' ]}

phpfpm2 = {'count': 2, 'config':
    {'data':
    {'dest': '/usr/share/nginx', 'source':
    {'git': 'https://github.com/babnikzero/frontend'}},
    'editfile': {'/usr/share/nginx/app/config/database.php':
                 {"'default' =>[^>]*": "'default' => 'production',"},
                 '/usr/share/nginx/app/config/backend.php':
                     {"localhost": {'target': {'1': {'docker': {'nginx': 'c_host'}}}}}}},
    'exec': {'target': {'2': {'docker': {'postgres': {'create': {'user': {'name': 'frontendprj', 'db': 'frontendprj', 'pass': 'testpasswd'}}}}}}},
    'runonce': ['cd /usr/share/nginx&&php artisan migrate:install', 'cd /usr/share/nginx&&php artisan migrate', 'cd /usr/share/nginx&&php artisan db:seed' ]}

target={'1': {'docker': {'postgres': postgres, 'php-fpm': phpfpm, 'nginx': nginx}, 'network': '192.168.55.0'}}

#var_dump(target)

def reg_c(c_group, c_type, c_ip_index, c_host, c_port, c_mode='NULL', c_conn_port='NULL', c_conn_addr='NULL'):
    global con
    global build_session
    cur = con.cursor()
    fields='c_group, c_type, c_ip_index, c_host, c_port, c_mode, c_conn_port, c_conn_addr, build_session'
    values= "'"+c_group+"', '"+c_type+"', '"+c_ip_index+"', '"+c_host+"', '"+c_port+"', '"+c_mode+"', '"+c_conn_port+"', '"+c_conn_addr+"', '"+build_session+"'"
    #print("INSERT INTO containers ("+fields+") VALUES ("+values+");")
    cur.execute("INSERT INTO containers ("+fields+") VALUES ("+values+");")
    con.commit()

def get_doc_var(data):
    global build_session
    global con
    if 'target' in data:
        groupid=data['target'].keys()[0]
        type=data['target'][groupid]['docker'].keys()[0]
        field=data['target'][groupid]['docker'][type]
        cur = con.cursor()
        cur.execute("SELECT "+field+" FROM containers WHERE build_session='"+build_session+"' AND \
         c_type ='"+type+"' AND c_group ='"+str(groupid)+"' ")
        res = cur.fetchall()

        return res




def build_postgres(data, groupid, net='192.168.55.'):
    build_tpl('postgres')
    count = data['count']

    for i in range(count):
        name='postgres'+str(i)+'g'+str(groupid)
        subprocess.call('docker run -t -d --name '+name+' postgres', shell=True)
        ip = get_cont_net_info(name, 'IPAddress')
        #ip = addtonet(groupid, 'postgres', i, net)
        time.sleep(5)
        w8_for_host(ip)
        if(i==0):
            mode='master'
            config_master(ip)
        else:
            mode='slave'
            config_slave(ip, get_master_host(groupid))
        if data['pgpool']['mode'] == 'standin':
            reg_c(str(groupid), 'pgpool', str(i+1), ip, '5433')
        reg_c(str(groupid), 'postgres', str(i+1), ip, '5432', mode)

    connaddr=data['pgpool']['connaddr']

    if data['pgpool']['mode'] == 'standin':
        postgres=get_host(groupid, 'postgres')
        pgpool= get_host(groupid, 'pgpool')
        if data['pgpool']['wathdog'] == 'on':

            for node in pgpool:
                    config_pgpool(node[0], postgres, connaddr, get_cont_net_info(name, 'Gateway'), postgres)
        else:
            config_pgpool(pgpool[0][0], postgres, connaddr, get_cont_net_info(name, 'Gateway')) # not support
    if 'create' in data:
        for method in data['create']:
            if method == 'user':
                subprocess.call('ssh -T '+sshparams+' postgres@'+connaddr+' PGPASSWORD="qwerty" psql -h '+connaddr+' -p 5433 --command "\\"CREATE USER '+data['create']['user']['name']+' WITH PASSWORD \''+data['create']['user']['pass']+'\';\\"" ', shell=True)
                subprocess.call('ssh -T '+sshparams+' postgres@'+connaddr+' PGPASSWORD="qwerty" psql -h '+connaddr+' -p 5433 --command "\\"CREATE DATABASE '+data['create']['user']['db']+';\\""', shell=True)
                subprocess.call('ssh -T '+sshparams+' postgres@'+connaddr+' PGPASSWORD="qwerty" psql -h '+connaddr+' -p 5433 --command "\\"GRANT ALL PRIVILEGES ON DATABASE '+data['create']['user']['db']+' to '+data['create']['user']['name']+';\\""', shell=True)





def config_pgpool(ip, nodelist, vip, parrent, poollist=None):
    global sshparams
    w8_for_host(ip)
    subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "sudo /etc/init.d/pgpool2 stop " ', shell=True)
    subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "/var/lib/postgresql/9.2/main/scripts/init_pool conf '+vip+' '+parrent+' '+str(nodelist[0][2])+' "', shell=True)
    i=0
    for node in nodelist:
        subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "/var/lib/postgresql/9.2/main/scripts/init_pool nodeadd '+node[0]+' '+str(node[1])+' '+str(i)+' " ', shell=True)
        i=i+1
    if poollist:
        print('poolconfig')
        i=0
        for poolnode in poollist:
            if not (poolnode[0] == ip):
                print ('pooladd')
                subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "/var/lib/postgresql/9.2/main/scripts/init_pool pooladd '+poolnode[0]+' '+str(5433)+' '+str(i)+' "', shell=True)
                i=i+1
    subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "pgpool -n > /tmp/pgpool.log 2>&1 & #sudo /etc/init.d/pgpool2 restart #" ', shell=True)
    w8_for_host(vip)

def config_slave(ip, master_ip):
    global sshparams
    subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "/var/lib/postgresql/9.2/main/scripts/init_slave sync /var/lib/postgresql/9.2/main '+master_ip+' " ', shell=True)
    pass

def config_master(ip):
    global sshparams
    subprocess.call('ssh -T '+sshparams+' postgres@'+ip+' "/var/lib/postgresql/9.2/main/scripts/init_slave copy /var/lib/postgresql/9.2/main"', shell=True)
    pass

def get_master_host(groupid):
    global con
    global build_session
    cur = con.cursor()
    cur.execute("SELECT c_host FROM containers WHERE c_mode='master' AND build_session='"+build_session+"' AND c_type ='postgres' AND c_group ='"+str(groupid)+"' ")
    data = cur.fetchone()
    return data[0]

def get_slave_host(groupid):
    global con
    global build_session
    cur = con.cursor()
    cur.execute("SELECT c_host FROM containers WHERE c_mode='slave' AND build_session='"+build_session+"' AND c_type ='postgres' AND c_group ='"+str(groupid)+"' ")
    data = cur.fetchall()
    return data

def get_host(groupid, type):
    global con
    global build_session
    cur = con.cursor()
    cur.execute("SELECT c_host, c_port, c_group, id FROM containers WHERE build_session='"+build_session+"' AND c_type ='"+type+"' AND c_group ='"+str(groupid)+"' ")
    data = cur.fetchall()
    return data

def addtonet(groupid, name, id, net):

    ip=net+str(id+1)
    subprocess.call('pipework/pipework br'+str(groupid)+' '+name+str(id)+'g'+str(groupid)+' '+ip+'/24', shell=True)
    return ip

def get_cont_net_info(name, param):
    p = subprocess.Popen('docker inspect '+name, stdout=subprocess.PIPE, shell=True)
    out = p.communicate()
    decoded=json.loads(out[0])
    #var_dump(decoded[0]['NetworkSettings']['IPAddress'])
    return decoded[0]['NetworkSettings'][param]

def w8_for_host(ip):
    rc=1
    while (rc > 0):
        time.sleep(4)
        s = socket(AF_INET, SOCK_STREAM)

        rc = s.connect_ex((ip, 22))

        if(rc == 0) :
            print 'Host '+ip+' ssh is online'
        else:
            print 'Host '+ip+' ssh is down, sleep 4 sec'
        s.close()

def build_nginx(data, groupid):
    build_tpl('nginx')
    count = data['count']

    for i in range(count):
        name='nginx'+str(i)+'g'+str(groupid)
        subprocess.call('docker run -t -d --name '+name+' nginx', shell=True)
        ip = get_cont_net_info(name, 'IPAddress')
        w8_for_host(ip)
        config_nginx(ip, data['config'], groupid)
        reg_c(str(groupid), 'nginx', str(i+1), ip, '9000')
    pass

def config_nginx(ip, data, groupid):
    if 'pynginxconfig' in data:
        ips=get_doc_var(data['pynginxconfig']['backend'])
        tmp=[]
        for b_ip in ips:

            tmp.append(b_ip[0]+':9000')
        cmd='python /root/scripts/nginxconfig.py --backend "'+' '.join(tmp)+'"'
        run(ip, [cmd])
        run(ip, ['/etc/init.d/nginx restart'])




    pass

def build_pgpool():
    pass

def config_phpfpm(ip, config, groupid):
    global sshparams
    if type(config['data']['source']) is dict:
        if 'git' in config['data']['source']:
            subprocess.call('ssh -T '+sshparams+' www-data@'+ip+' git clone '+config['data']['source']['git']+' '+config['data']['dest'], shell=True)
        elif 'svn' in config['data']['source']:
            subprocess.call('ssh -T '+sshparams+' www-data@'+ip+' svn co '+config['data']['source']['svn']+' '+config['data']['dest'], shell=True)
    elif type(config['data']['source']) is str:
        subprocess.call('cp '+config['data']['source']+' '+config['data']['dest']+'')
    if 'editfile' in config:
        for file in config['editfile']:
            for line in config['editfile'][file]:
                if type(config['editfile'][file][line]) is dict:
                    tmp=get_doc_var(config['editfile'][file][line])
                    config['editfile'][file][line]=tmp[0][0]
                subprocess.call('ssh -T '+sshparams+' www-data@'+ip+' sed "\\"s/'+line+'/'+config['editfile'][file][line]+'/"\\" -i '+file, shell=True)


def run(ip, cmds, user='root'):
    global sshparams
    for cmd in cmds:
        subprocess.call('ssh -T '+sshparams+' '+user+'@'+ip+' "'+cmd+'"', shell=True)


def build_phpfpm(data, groupid):
    build_tpl('php-fpm')
    count = data['count']

    for i in range(count):
        name='php-fpm'+str(i)+'g'+str(groupid)
        subprocess.call('docker run -t -d --name '+name+' php-fpm', shell=True)
        ip = get_cont_net_info(name, 'IPAddress')
        w8_for_host(ip)
        config_phpfpm(ip, data['config'], groupid)
        reg_c(str(groupid), 'php-fpm', str(i+1), ip, '9000')
        if i ==0:
            if 'runonce' in data:
                run(ip, data['runonce'], 'www-data')







def build_tpl(name):
    subprocess.call('cd docker/'+name+'/&&docker build --no-cache -t '+name+' .', shell=True)
"""
def main():
    for groupid in target:
        for type in target[groupid]['docker']:
            if type == 'postgres':
                build_postgres(target[groupid]['docker'][type], groupid)
            elif type == 'php-fpm':
                build_phpfpm(target[groupid]['docker'][type], groupid)
            elif type == 'nginx':
                build_nginx(target[groupid]['docker'][type], groupid)

main()"""
subprocess.call('brctl addbr br1&&ifconfig br1 192.168.55.254 netmask 255.255.255.0', shell=True)
build_postgres(postgres, 1)
build_phpfpm(phpfpm, 1)
build_nginx(nginx, 1)
build_postgres(postgres2, 2)
build_phpfpm(phpfpm2, 2)
build_nginx(nginx2, 2)



