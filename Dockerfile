FROM debian:buster


RUN apt update && \
  apt upgrade -y && \
  apt install -y python3-scipy python3 curl unzip python3-pip git

ADD bin /src/bin
ADD dataviz /src/dataviz
ADD setup.py /src

RUN pip3 install "git+https://github.com/javadba/mpld3@display_fix" && \
  cd /src && python3 ./setup.py install && cd / && rm -Rf /src