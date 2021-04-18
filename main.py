from flask import Flask, render_template, request, Response
import csv
import json
import datetime
app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/soal-1', methods=['GET'])
def soal1():
  data = ""
  if request.method == 'GET':
    data = request.args.get('string', '')
  return data

@app.route('/soal-2', methods=['GET', 'POST'])
def soal2():
  if request.method == 'POST':
    dataRequest = request.get_json()
    if "sensor_id" in dataRequest:
      if "tanggal" in dataRequest:
        response = byDate(dataRequest["tanggal"], dataRequest["sensor_id"])
      elif "rangeTanggal" in dataRequest:
        response = dateRange(dataRequest["rangeTanggal"], dataRequest["sensor_id"])
      else:
        response = Response(
          json.dumps({"message": "please set tanggal or rangeTanggal parameter"}),
          status=400,
          mimetype='application/json'
        )
    else:
      response = Response(
        json.dumps({"message": "please set sensor_id parameter"}),
        status=400,
        mimetype='application/json'
      )
    return response

def byDate(tanggal, sensor_id):
  with open('202009020838.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    data = []
    groupByHour = {}
    for row in csv_reader:
      if line_count != 0:
        requestedDatei = parseTanggal(tanggal)

        date = row["timestamp"].split(' ')
        splittedDate = date[0].split('/')
        splittedTime = date[1].split(':')
        dateOnly = datetime.datetime(int(splittedDate[2]), int(splittedDate[0]), int(splittedDate[1]))

        if requestedDatei == dateOnly and sensor_id == row["sensor_id"]:
          if str(splittedTime[0]) in groupByHour:
            groupByHour[str(splittedTime[0])] += int(row["total"])
          else:
            groupByHour[str(splittedTime[0])] = int(row["total"])

      line_count += 1
    if len(groupByHour) > 0:
      response = Response(
        json.dumps({"hour": groupByHour}),
        status=200,
        mimetype='application/json'
      )
    else:
      response = Response(
        json.dumps({"message": "data not found at "+ tanggal}),
        status=200,
        mimetype='application/json'
      )

    return response

def dateRange(between, sensor_id):
  with open('202009020838.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    data = []
    groupByDate = {}
    for row in csv_reader:
      if line_count != 0:
        parseDateBetween = between.split(' s/d ')
        dateFromRaw = parseDateBetween[0]
        dateToRaw = parseDateBetween[1]

        dateFrom = parseTanggal(dateFromRaw)
        dateTo = parseTanggal(dateToRaw)
        date = row["timestamp"].split(' ')
        splittedDate = date[0].split('/')
        splittedTime = date[1].split(':')
        dateOnly = datetime.datetime(int(splittedDate[2]), int(splittedDate[0]), int(splittedDate[1]))

        if (dateFrom <= dateOnly <= dateTo) and sensor_id == row["sensor_id"]:
          if dateOnly.strftime("%d-%m-%Y") in groupByDate:
            groupByDate[dateOnly.strftime("%d-%m-%Y")] += int(row["total"])
          else:
            groupByDate[dateOnly.strftime("%d-%m-%Y")] = int(row["total"])

      line_count += 1
    
    if len(groupByDate) > 0:
      response = Response(
        json.dumps({"by_date_between": groupByDate}),
        status=200,
        mimetype='application/json'
      )
    else:
      response = Response(
        json.dumps({"message": "data not found at " + between}),
        status=200,
        mimetype='application/json'
      )
    return response

def parseTanggal(tanggal):
  day = int(tanggal.split("-")[0])
  month = int(tanggal.split("-")[1])
  year = int(tanggal.split("-")[2])
  return datetime.datetime(year, month, day)