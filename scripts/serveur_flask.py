from flask import Flask, jsonify
from influxdb_client_3 import InfluxDBClient3
import os

app = Flask(__name__)

@app.route('/api/historique')
def historique():
    host = "https://us-east-1-1.aws.cloud2.influxdata.com"
    token = os.getenv('INFLUX_TOKEN')
    database = os.getenv('INFLUX_DATABASE')

    client = InfluxDBClient3(host, token=token, database=database)

    table = client.query(
        '''SELECT
            room,
            DATE_BIN(INTERVAL '1 day', time) AS _time,
            AVG(temp) AS temp,
            AVG(hum) AS hum,
            AVG(co) AS co
        FROM home
        WHERE time >= now() - INTERVAL '30 days'
        GROUP BY room, _time
        ORDER BY _time'''
    )

    df = table.to_pandas()
    client.close()

    return jsonify(df.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
