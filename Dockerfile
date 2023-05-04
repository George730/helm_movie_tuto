FROM python:3.10
COPY . /
WORKDIR /
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5001
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]

