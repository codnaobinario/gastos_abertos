# -*- coding: utf-8 -*-

''' Read a CSV with revenues and insert them in the DB.

Usage:
    ./import_revenue [FILE] [LINES_PER_INSERT]
    ./import_revenue (-h | --help)

Options:
    -h --help   Show this message.
'''
import pandas as pd
from datetime import datetime, timedelta
import calendar
from sqlalchemy.sql.expression import insert
from docopt import docopt

from gastosabertos import create_app
from gastosabertos.extensions import db

app = create_app()
db.app = app

from gastosabertos.receita.models import Revenue

def parse_money(money_string):
    if money_string[0] == '-':
        return -float(money_string[3:].replace('.', '').replace(',', '.'))
    else:
        return float(money_string[3:].replace('.', '').replace(',', '.'))

def parse_date(date_string):
    year_month = datetime.strptime(date_string, '%Y-%m')
    date = year_month + timedelta(days = calendar.monthrange(year_month.year, year_month.month)[1] - 1)
    return date

def parse_code(code_string):
    return [int(i) for i in code_string.split('.')]

def insert_rows(rows_data):
    ins = insert(Revenue.__table__, rows_data)
    db.session.execute(ins)
    db.session.commit()

def insert_all(csv_file='../data/receitas_min.csv', lines_per_insert=100):
    data = pd.read_csv(csv_file, encoding='utf8')

    to_insert = []
    for row_i, row in data.iterrows():
    #    r = Revenue()
        r = {}

        if len(to_insert) == lines_per_insert:
           insert_rows(to_insert)
           to_insert = []

        r['code'] = row['codigo']
        r['description'] = unicode(row['descricao'])
        r['date'] = parse_date(row['data'])
        r['monthly_outcome'] = parse_money(row['realizado_mensal'])
        r['monthly_predicted'] = parse_money(row['previsto_mensal'])
        code_parsed = parse_code(row['codigo'])
        r['economical_category'] = code_parsed[0]

        if len(code_parsed) >= 2:
            r['economical_subcategory'] = code_parsed[1]
        else:
            r['economical_subcategory'] = None

        if len(code_parsed) >= 3:
            r['source'] = code_parsed[2]
        else:
            r['source'] = None

        if len(code_parsed) >= 4:
            r['rubric'] = code_parsed[3]
        else:
            r['rubric'] = None

        if len(code_parsed) >= 5:
            r['paragraph'] = code_parsed[4]
        else:
            r['paragraph'] = None

        if len(code_parsed) == 6:
            r['subparagraph'] = code_parsed[5]
        else:
            r['subparagraph'] = None

        to_insert.append(r)

    if len(to_insert) > 0:
        insert_rows(to_insert)

if  __name__ == '__main__':
    arguments = docopt(__doc__)
    args = {}
    csv_file = arguments['FILE']
    if csv_file:
        args['csv_file'] = csv_file
    lines_per_insert = arguments['LINES_PER_INSERT']
    if lines_per_insert:
        args['lines_per_insert'] = int(lines_per_insert)
    insert_all(**args)
