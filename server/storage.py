import MySQLdb
import tinysql
import yaml

class Dbh:
    def __init__(self,**args):
        self.__dict__.update(args)
        #self.connect() 
    def load_yaml(self,filepath):
        try:
            dict=yaml.load(open(filepath))
            self.__dict__.update(dict)
            return True
        except Exception, e:
            return None
    def connect(self):
        self.conn=MySQLdb.connect(self.host,self.username,self.password,self.dbname)
        self.cursor=self.conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            #prepare_sql was generally  'set names utf8'
            self.cursor.execute(self.prepare_sql)
        except:
            pass

    def query(self,sql):
        return self.cursor.execute(sql)

    def fetchRows(self,sql):
        try:
            n=self.cursor.execute(sql)
        except Exception,e:
            #self.unlockTable()
            print "error occured while fetch rows from datbase ,error:",e
            return None

        if n==0:
            return None

        try:
            rows=self.cursor.fetchall()
        except Exception,e:
            return None
        return rows

    def close(self):
        self.cursor.close()
        self.conn.close()

class Table(object):
    """mysql table visiting"""
    def __init__(self, **args):
        self.table="unamed_table"
        self.__dict__.update(args)
         
    def find_by_id(self,id,columns="*"):
        sql=tinysql.select(self.table,columns,"`%s`='%s'" % (self.primary_key,id))
        return self.dbh.fetchRows(sql)
    
    def remove_by_id(self,id,limit=1):
        sql=tinysql.remove(self.table,{self.primary_key:id},limit)
        return self.dbh.query(sql)

    def update_by_id(self,id,row,limit=1):
        sql=tinysql.update(self.table,row,{self.primary_key:id},limit)

   
class Dblog(object):
    """log errors in the database"""
    def __init__(self, dbh):
        self.dbh=dbh

def authenticate(self,dbh,code):
        table=Table(table="secrets",primary_key="code",dbh=dbh)
        row=table.find_by_id(code)
        try:
            return row[0]
        except Exception, e:
            return None
             
def main():
    """docstring main"""
    #dbh=Dbh(host="localhost",username="root",password="",dbname="cloudface",prepare_sql="set names utf8")
    dbh=Dbh(prepare_sql="set names utf8")
    dbh.load_yaml("./etc/db.yaml")
    dbh.connect()
    table=Table(table="users",primary_key="id",dbh=dbh)
    print table.find_by_id(18)
    import yaml
    f=open("./etc/db.yaml","w+")
    data={"host":"localhost","username":"root","password":"","dbname":"cloudface"}
    yaml.dump(data,f)
    f.close()
    dict=yaml.load(open("./etc/db.yaml"))
    print dict


if __name__ == '__main__':
    main() 
