FROM mcr.microsoft.com/playwright/python
LABEL maintainer="ronmarti18@gmail.com"

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

RUN pip3 install pydude[bs4,parsel,lxml,selenium]
RUN playwright install
