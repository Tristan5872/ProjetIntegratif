from influxdb_client_3 import InfluxDBClient3
import pandas
import os

#Pour lire les bdd influx db

database = os.getenv('INFLUX_DATABASE')
token = os.getenv('INFLUX_TOKEN')
host="https://us-east-1-1.aws.cloud2.influxdata.com"

def querySQL():
  client = InfluxDBClient3(host, database=database, token=token)
  table = client.query(
    '''SELECT
        room,
        DATE_BIN(INTERVAL '1 day', time) AS _time,
        AVG(temp) AS temp,
        AVG(hum) AS hum,
        AVG(co) AS co
      FROM home
      WHERE time >= now() - INTERVAL '90 days'
      GROUP BY room, _time
      ORDER BY _time'''
  )

  print(table.to_pandas().to_markdown())

  client.close()
  
querySQL()

#pour écrire dans inlux db
database = os.getenv('INFLUX_DATABASE')
token = os.getenv('INFLUX_TOKEN')
host="https://us-east-1-1.aws.cloud2.influxdata.com"

def write_line_protocol():
  client = InfluxDBClient3(host, database=database, token=token)
  
  record = "home,room=Living\\ Room temp=22.2,hum=36.4,co=17i"
  
  print("Writing record:", record )
  client.write(record)
  
  client.close()

write_line_protocol()
