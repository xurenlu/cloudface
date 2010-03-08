#coding:utf-8
import MySQLdb
import tinysql
import yaml
import time
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
    def find_row(self,columns="*",condition=None,limit=1):
        if condition == None:
            condition=""

        sql=tinysql.select(self.table,columns,condition,"",limit)
        ret=self.dbh.query(sql)
        return ret

    def remove_by_id(self,id,limit=1):
        sql=tinysql.remove(self.table,{self.primary_key:id},limit)
        return self.dbh.query(sql)

    def update_by_id(self,id,row,limit=1):
        sql=tinysql.update(self.table,row,{self.primary_key:id},limit)

    def create(self,row):
        sql=tinysql.create(self.table,row)
        return self.dbh.query(sql)

class Dblog(object):
    """log errors in the database"""
    def __init__(self, dbh):
        self.dbh=dbh

def authenticate(dbh,code):
    table=Table(table="secrets",primary_key="code",dbh=dbh)
    row=table.find_by_id(code)
    try:
        return row[0]
    except Exception, e:
        return None

def log(dbh,code,user_id,dbpath,func_name,return_code,return_msg,uuid):
    row={"code":code,"user_id":user_id,"dbpath":dbpath,"func_name":func_name,"return_code":return_code,"return_msg":return_msg,"uuid":uuid}
    table=Table(table="logs",primary_key="id",dbh=dbh)
    return table.create(row)

def increment(dbh,user_id,dbpath,func_name):
    """increment the count of the stats"""
    tm=time.localtime(time.time())
    table=Table(table="stats",primary_key="id",dbh=dbh)
    row=table.find_row("id","user_id=%d AND dbpath='%s' AND func_name='%s' AND year=%d AND month=%d AND day=%d" % (user_id,dbpath,func_name,tm.tm_year,tm.tm_mon,tm.tm_mday))
    if row == 0:
        row=None

    if row == None :
        #之前没这条,很简单,加上;
        new_row={"user_id":user_id,"dbpath":dbpath,"count":1,"year":tm.tm_year,"month":tm.tm_mon,"day":tm.tm_mday,"func_name":func_name}
        table.create(new_row)
    else:
        sql="update stats set count=count+1 WHERE user_id=%d AND dbpath='%s' AND func_name='%s' AND year=%d AND month=%d AND day=%d" % (user_id,dbpath,func_name,tm.tm_year,tm.tm_mon,tm.tm_mday)
        table.dbh.query(sql)
        #加1
   
    
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


#if __name__ == '__main__':
#    main() 
