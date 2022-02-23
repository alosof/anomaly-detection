FROM grafana/grafana:8.4.1

USER root

RUN apk update --no-cache && apk upgrade --no-cache && apk add --no-cache git nodejs yarn make musl-dev go

ENV GOROOT /usr/lib/go
ENV GOPATH /go
ENV PATH /go/bin:$PATH

RUN mkdir -p ${GOPATH}/src ${GOPATH}/bin

RUN git clone https://github.com/magefile/mage && cd mage && go run bootstrap.go

RUN sed -i "s/;allow_loading_unsigned_plugins =/allow_loading_unsigned_plugins = grafana-mqtt-datasource/g" /etc/grafana/grafana.ini

WORKDIR /var/lib/grafana/plugins/

RUN git clone https://github.com/grafana/mqtt-datasource.git && cd mqtt-datasource && yarn install && yarn build

WORKDIR /var/lib/grafana/plugins/mqtt-datasource

RUN mage reloadPlugin
