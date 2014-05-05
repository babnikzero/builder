###NGINX###

FROM ubuntu

RUN RUNLEVEL=1 DEBIAN_FRONTEND=noninteractive apt-get install -q -y openssh-server sudo wget nginx openssh-client python-pip python-argparse
RUN pip install pynginxconfig

#Тюним ssh
RUN mkdir -p /var/run/sshd
RUN sed 's/UsePAM yes/UsePAM no/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitRootLogin yes/PermitRootLogin yes/' -i /etc/ssh/sshd_config
RUN sed 's/#PermitEmptyPasswords no/PermitEmptyPasswords no/' -i /etc/ssh/sshd_config

RUN mkdir -p /root/.ssh/
ADD ssh_keys/id_rsa /root/.ssh/
ADD ssh_keys/authorized_keys /root/.ssh/
RUN chmod -R 700 /root/.ssh/
ADD scripts/ /root/scripts/
RUN chmod +x /root/scripts/*
RUN cp /root/scripts/config/default /etc/nginx/sites-available/default
RUN mv /root/scripts/nginx_start_node /usr/bin/nginx_start_node
RUN  echo "root:qwerty"|chpasswd


EXPOSE 80
EXPOSE 443
EXPOSE 22
USER root

CMD ["/usr/bin/nginx_start_node"]
