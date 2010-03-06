#!/usr/bin/python
#coding:utf-8
#Author:renlu.xu
#URL:http://www.162cm.com/
#date:2009.05.21

import MySQLdb

def escape(st):
    '''escape for security reason''' 
    return MySQLdb.escape_string(str(st))

def select(table ,columns="*",condition="",order="",limit="",group=""):
    if condition != "":
        condition = " WHERE %s" % condition
    if order != "":
        order = " ORDER BY %s" % order
    if limit != "":
        limit = " LIMIT %s" % limit
    if group != "":
        group = " GROUP BY %s" % group

    sql = "SELECT %s FROM %s %s %s %s %s" % ( columns, table, condition,group,order,limit )
    return sql

def update(table,columns,condition=None,limit=1):
    '''generate update sql 
    columns: like '*' ,'id,username,password' and so on
    condition: like ' id=1 ' or ' pid>7 ' and so on
    '''
    if isinstance(columns,dict):
        sql="UPDATE `%s` SET " % table
        comm=""
        for col in columns:
            sql = sql + comm+ "`"+col+"`='"+escape(columns[col])+"' "
            comm=","
        if condition:
            sql = sql + "WHERE " + condition
        sql = sql + " LIMIT " + limit
        return sql
    else:
        return None

def remove(table,columns,limit="1"):
    '''
        generate delete sql statement
    '''
    if isinstance(columns,dict):
        sql="DELETE FROM `%s` WHERE " % table
        comm=""
        for col in columns:
            sql = sql + comm+ "`"+col+"`='"+escape(columns[col])+"' "
            comm="AND "
        sql = sql + " LIMIT " + limit
        return sql
    else:
        return None

def create(table,columns,method="INSERT"):
    '''
    parameter method could be 'INSERT' or 'UPDATE'
    '''
    method=method.upper()
    if isinstance(columns,dict):
        sql=method + " INTO `%s` (" % table
        comm=""
        for col in columns:
            sql = sql + comm + "`"+col+"`"
            comm=","
        sql = sql + ") VALUES ("
        comm=""
        for col in columns:
            sql = sql + comm + "'"+escape(columns[col])+"'"
            comm=","
        sql = sql + ")" 
        return sql
    else:
        return None

def testfunc():
    table="mytable"
    columns={
        "id":1,
        "name":"xuren'lu"
    }
    condition="id=2"
    print update(table,columns,condition)
    print create(table,columns)
    print select(table,"id,username","id=7" ,"pid DESC",1000)
if __name__=="__main__":
    testfunc()
