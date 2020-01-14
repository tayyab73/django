from cx_Oracle import DatabaseError,connect
import pdb
import json
class DataBase:
    def getData(self):

        try:
            with open("static/record/nosql.json", "r") as jsonFile:
                data = json.load(jsonFile)
                return data
        except Exception,e:
            return {}

    def get_connection(self):
        flag=False
        try:
            database=self.getData()
            if len(database)!=0:
                flag=True
                return flag,connect(database['username'],database['password'],database['host'])
            else:
                return flag,"Error"
        except DatabaseError,e:
            return flag,str(e)