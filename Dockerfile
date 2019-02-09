FROM ubuntu:18.10

WORKDIR /app

ADD . /app

ENV DOCKER True

RUN apt update && apt install -y \
    python3.7 python3.7-pip wget gdebi-core git
RUN  apt-get update \
&&  apt-get install -y software-properties-common \
&&  apt-add-repository ppa:ansible/ansible \
&&  apt-get update \
&&  apt-get install -y ansible

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt

RUN wget https://github.com/srh/rethinkdb/releases/download/v2.3.6.srh.1/rethinkdb_2.3.6.srh.1.0bionic_amd64.deb -O rethinkdb.deb && gdebi --option=APT::Get::force-yes=1,APT::Get::Assume-Yes=1 -n rethinkdb.deb

RUN wget  https://deb.nodesource.com/setup_8.x -O -  | bash - && \
 apt-get install -y nodejs

RUN cp /etc/rethinkdb/default.conf.sample /etc/rethinkdb/instances.d/instance1.conf

RUN ln -sf /dev/stdout nohup.out

VOLUME /root login.ini

EXPOSE 3000 8889

WORKDIR /app/new-frontend

RUN npm install && npm run build:dll

WORKDIR /app

CMD ./start.sh
