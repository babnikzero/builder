
FROM ubuntu:12.04

RUN apt-get update -q
RUN RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive apt-get install -q -y openssh-server wget rsync openssh-client git php5-fpm php5-pgsql php5-mcrypt php5-cli curl php5-curl

#Тюним ssh
RUN mkdir -p /var/run/sshd
RUN sed 's/UsePAM yes/UsePAM no/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitRootLogin yes/PermitRootLogin yes/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitEmptyPasswords no/PermitEmptyPasswords no/' -i /etc/ssh/sshd_config

#Добавляем ssh ключи и файл конфигурации
RUN mkdir -p /var/www/.ssh/
RUN mkdir -p /usr/share/nginx/
RUN chown -R www-data:www-data /usr/share/nginx/
ADD ssh_keys/id_rsa /var/www/.ssh/
ADD ssh_keys/authorized_keys /var/www/.ssh/
RUN chown -R www-data:www-data /var/www/.ssh/ 
RUN chmod -R 700 /var/www/.ssh/
ADD scripts/ /var/www/scripts/
RUN chown -R www-data:www-data /var/www/scripts/
RUN chmod +x /var/www/scripts/*
RUN mv /var/www/scripts/fpm_start_node /usr/bin/fpm_start_node
RUN chsh www-data -s /bin/bash
Run sed 's/listen = 127.0.0.1:9000/listen = 0.0.0.0:9000/' -i /etc/php5/fpm/pool.d/www.conf
RUN  echo "root:qwerty"|chpasswd

#Слушаем порты ssh и fpm, пользователь для виртуалки - root, необходимо для ssh
EXPOSE 9000
EXPOSE 22
USER root

CMD ["/usr/bin/fpm_start_node"]
