FROM hdgigante/python-opencv:4.7.0-debian
WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt --break-system-packages && pip3 cache purge
RUN python3 /app/utils/downloadModel.py

EXPOSE 9001
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9001", "--reload" ]
