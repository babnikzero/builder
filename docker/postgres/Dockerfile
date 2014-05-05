###PG_SLAVE_CONFIG###

FROM ubuntu:12.04

#Добавляем репозитарий и ставим необходимые пакеты
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" >> /etc/apt/sources.list
RUN apt-get update -q
RUN RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive apt-get install -q -y postgresql-9.2 postgresql-9.2-pgpool2 openssh-server sudo wget rsync openssh-client pgpool2 

#Тюним ssh
RUN mkdir -p /var/run/sshd
RUN sed 's/UsePAM yes/UsePAM no/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitRootLogin yes/PermitRootLogin yes/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitEmptyPasswords no/PermitEmptyPasswords no/' -i /etc/ssh/sshd_config

#Добавляем ssh ключи и файл конфигурации
RUN mkdir -p /var/lib/postgresql/.ssh
ADD ssh_keys/id_rsa /var/lib/postgresql/.ssh/
ADD ssh_keys/authorized_keys /var/lib/postgresql/.ssh/
RUN chown -R postgres:postgres /var/lib/postgresql/.ssh 
RUN chmod -R 700 /var/lib/postgresql/.ssh 
ADD scripts/ /var/lib/postgresql/9.2/main/scripts/
RUN chown -R postgres:postgres /var/lib/postgresql/9.2/main/scripts/
RUN chmod +x /var/lib/postgresql/9.2/main/scripts/*
RUN mv /var/lib/postgresql/9.2/main/scripts/pgpool_remote_start /var/lib/postgresql/9.2/main/pgpool_remote_start
RUN mv /var/lib/postgresql/9.2/main/scripts/basebackup /var/lib/postgresql/9.2/main/basebackup
RUN mv /var/lib/postgresql/9.2/main/scripts/pg_start_node /usr/bin/pg_start_node
RUN  echo "root:qwerty"|chpasswd
RUN echo "postgres   ALL = NOPASSWD: /etc/init.d/pgpool2, /bin/cp, /bin/chown, /bin/chmod" >>/etc/sudoers
USER postgres
RUN /etc/init.d/postgresql start&&\
psql --command "ALTER USER postgres WITH PASSWORD 'qwerty';"&&\
psql -f /usr/share/postgresql/9.2/extension/pgpool-recovery.sql template1

#RUN psql --command "ALTER USER postgres WITH PASSWORD 'qwerty'";

############################# можно удалять #################################################
#USER postgres

#RUN /etc/init.d/postgresql stop
#RUN rm -rf /var/lib/postgresql/9.2/main
#RUN pg_basebackup -h 192.168.0.2 -U postgres -xlog-method=stream -D /var/lib/postgresql/9.2/main
#RUN PGPASSWORD=qwerty psql -h 192.168.0.2 --command "SELECT pg_start_backup('label', true);"
#RUN rsync -az -e 'ssh -i /var/lib/postgresql/.ssh/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no' postgres@192.168.0.2:/var/lib/postgresql/9.2 /var/lib/postgresql --exclude postmaster.pid
#RUN PGPASSWORD=qwerty psql -h 192.168.0.2 --command "SELECT pg_stop_backup();"
#RUN echo "standby_mode = 'on'">> /var/lib/postgresql/9.2/main/recovery.conf
#RUN echo "primary_conninfo = 'host=192.168.0.2 port=5432 user=postgres'">> /var/lib/postgresql/9.2/main/recovery.conf
#RUN echo "trigger_file = 'failover'">> /var/lib/postgresql/9.2/main/recovery.conf
#RUN echo "listen_addresses = '*'" >> /etc/postgresql/9.2/main/postgresql.conf
#RUN echo "hot_standby = on" >> /etc/postgresql/9.2/main/postgresql.conf
#RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.2/main/pg_hba.conf
#RUN echo "host replication	postgres    192.168.0.0/24  trust" >> /etc/postgresql/9.2/main/pg_hba.conf
############################# можно удалять #################################################

#Слушаем порты ssh и бд, пользователь для виртуалки - root, необходимо для ssh
EXPOSE 22
EXPOSE 5432
EXPOSE 5433
EXPOSE 9694
EXPOSE 9000
EXPOSE 9898
USER root

#Подключаем тома для каталогов базы(на всякий пожарный)
VOLUME	["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

CMD ["/usr/bin/pg_start_node"]
