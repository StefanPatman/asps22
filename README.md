Build the docker images:
`make all`

Manually run the app using docker-compose:
`docker-compose up`

To check the server output, visit:
http://0.0.0.0:5001/data?id=1
http://0.0.0.0:5001/data?location=Athens

To generate a new fogified yaml for a simple case:
```
cd src/topology
python main.py simple.yml
```
