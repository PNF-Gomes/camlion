import mysql.connector
import time
import datetime
from utils import interpolation


class DataBase():

    def __init__(self):

        self.update = False

        self.mydb = mysql.connector.connect(
            host="2.80.0.133",
            user="PedroGomes",
            passwd="2020guarda#",
            database="camlion"
        )

        self.pm2 = 0.0
        self.physic_dist = 0.0
        self.environmental_risk = 0.0
        self.geographical_risk = 0.0
        self.risk = 0.0

        self.monitoring_update_rate = 2

        self.coordinates = []

        self.introduced_coordinates = []

        print(self.mydb)

    def update_database(self):
        while True:
            if self.update:
                mycursor = self.mydb.cursor()
                sql = "UPDATE monitoring SET pm2 = %s, fisicdist = %s, zonedanger = %s, georisk = %s, risk = %s, data = %s WHERE idmonitoring = %s"
                ts = time.time()
                time_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                val = (self.pm2, self.physic_dist, self.environmental_risk, self.geographical_risk, self.risk, time_date, 1)
                mycursor.execute(sql, val)
                self.mydb.commit()
                print(mycursor.rowcount, "was inserted.")
                # print("updating {} {} {} {} {}".format(self.pm2, self.physic_dist, self.zonedanger, self.risk, datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
                # self.insert_coordinates()
                time.sleep(self.monitoring_update_rate)
    
    def insert_coordinates(self):
        if self.coordinates:
            mycursor = self.mydb.cursor()
            sql = "INSERT INTO heat (x, y, date) VALUES (%s, %s, %s)"
            val = []
            for coordinate in self.coordinates:
                ts = time.time()
                time_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                val.append((coordinate[0], coordinate[1], time_date))

            mycursor.executemany(sql, val)
            self.mydb.commit()
            print(mycursor.rowcount, "was inserted.")
            self.introduced_coordinates.append(self.coordinates)
            print("inserting coordinates {}", self.coordinates)

    def update_information(self, pm2, physic_dist, environmental_risk, geographical_risk, risk, coordinates):
        self.pm2 = pm2
        self.physic_dist = physic_dist
        self.environmental_risk = environmental_risk
        self.geographical_risk = geographical_risk
        self.risk = risk
        self.coordinates = coordinates
            

