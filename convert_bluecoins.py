#! /usr/bin/env python
# coding: UTF-8

import argparse
import csv
import datetime
import os
import io
import sys
from os import path
import locale
from common import *
from dotenv import load_dotenv


EXPENSES_TMPLATE = """%s * "%s" "%s"
    %s                 -%s %s
    %s
"""

EXPENSES_INCOME_TMPLATE = """%s * "%s" "%s"
    %s                 +%s %s
    %s
"""

EXPENSES_TRANS_TMPLATE = """%s * "%s"
    %s                 -%s %s
    %s
"""

COMMON_TEMPLATE = """%s * "%s" "%s"
    %s                 +%s %s
    %s
"""
COMMON_BALANCE = """%s pad %s Equity:Opening-Balances
%s balance %s      %s CNY
"""


def load_csv(filename, is_strip_head=False):
    fd = open(filename, 'r', encoding="UTF-8")
    csv_reader = csv.reader(fd, delimiter=',')
    records = []
    for row in csv_reader:
        records.append(tuple(row))
    return records[1:] if is_strip_head else records

 
def build_records(mapping, record,lastAccount):
    type,date,_,payee,amount,_,_,_,catlog,accounts,_,_,_= record


    time = datetime.datetime.strptime(date, "%Y/%m/%d %H:%M")
    preDay =time+datetime.timedelta(days=-1)
    time = time.strftime('%Y-%m-%d')
    amount = locale.atof(amount)
    if type=="支出":
        # This is a transfer between accounts record
            # dedup the same transfer in different accounts
        return EXPENSES_TMPLATE % (time, payee, catlog,mapping['accounts'][accounts], abs(amount), "CNY", mapping['expenses'][catlog]),"",time
    if type=="收入":
        # This is a transfer between accounts record
            # dedup the same transfer in different accounts
        return EXPENSES_INCOME_TMPLATE % (time, payee, catlog,mapping['accounts'][accounts], amount, "CNY", mapping['incomes'][catlog]),"",time
    if type=="新账户":
    # This is a transfer between accounts record
        # dedup the same transfer in different accounts
        return COMMON_BALANCE % (preDay.strftime('%Y-%m-%d'),mapping['accounts'][accounts] ,time, mapping['accounts'][accounts], amount),"",time
    if type=="转账":
        # This is a transfer between accounts record
            # dedup the same transfer in different accounts
        if amount < 0 :
            lastAccount =mapping['accounts'][accounts] 
            return "",lastAccount,time
        else:
            # print(lastAccount+"➡"+ mapping['accounts'][accounts])
            return EXPENSES_TRANS_TMPLATE % (time, payee, lastAccount, abs(amount), "CNY", mapping['accounts'][accounts]),"",time
    return "","",time

def print_records_to_file(msg, filename):
    with open(filename, "a", encoding="utf-8") as f:
                f.write(msg)

def print_records(mapping, records):
    lastAccount=""
    for record in records:
        beancount_record, lastAccount,time= build_records(mapping, record,lastAccount)
        if beancount_record:
            time = datetime.datetime.strptime(time, "%Y-%m-%d")
            year = time.strftime('%Y')
            dataDir = os.path.join("../data/",year)
            if  not  os.path.exists(dataDir):
                os.makedirs(dataDir)
            path =  os.path.join(dataDir,time.strftime('%Y-%m')+".bean")
            print_records_to_file(beancount_record,path)

if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    load_dotenv()
    map_path = os.getenv("MAPPATH")
    mapping = load_json(path.join(os.path.dirname(os.path.realpath(__file__)), map_path))
    bluecoins_path = os.getenv("BLUECOINS_PATH")
    records = load_csv(bluecoins_path, True)
    print_records(mapping, records)

