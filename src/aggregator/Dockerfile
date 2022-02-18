FROM python:3-alpine

WORKDIR /usr/src/app

EXPOSE 5001

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./aggregator.py" ]
