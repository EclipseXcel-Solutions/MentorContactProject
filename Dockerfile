# pull official base image
FROM python:3.9-alpine

# set work directory
#WORKDIR /usr/src/project

RUN mkdir /dev-mcp
WORKDIR /dev-mcp

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2d
RUN apk update \
    && apk add python3 python3-dev gcc \
    && apk add gfortran musl-dev g++ \
    && apk add libffi-dev openssl-dev \
    && apk add libxml2 libxml2-dev \
    && apk add libxslt libxslt-dev \
    && apk add libjpeg-turbo-dev zlib-dev\
    && apk add --virtual build-deps python3-dev musl-dev \
    && apk add jpeg-dev zlib-dev  \
    && apk add --no-cache gcc libc-dev git \
    && apk add postgresql-dev autoconf automake libtool nasm\
    && apk add postgresql-client\
    && apk add redis\
    && apk del build-deps \
    && apk add  gdal-dev gdal --update-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    && apk add  geos-dev geos --update-cache --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    && rm -fr /var/cache/apk 



# install dependencies
ADD . /dev-mcp
RUN pip install --upgrade pipa
RUN pip install -r requirements.txt
# run entrypoint.sh
CMD ["python" , "manage.py" , "runserver"]
