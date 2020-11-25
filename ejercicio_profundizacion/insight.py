'''
API InSight Mars
---------------------------
Autor: Torres Molina Emmanuel O.
Version: 1.1
Descripción:
Programa que toma los datos de una URL
otorgada por la siguiente página correspondiente
a la NASA.

InSight: Mars Weather Service API -->
https://mars.nasa.gov/insight/weather/

Documentación acerca de la API -->
https://api.nasa.gov/assets/insight/InSight%20Weather%20API%20Documentation.pdf

'''

__author__ = "Emmanuel Oscar Torres Molina"
__email__ = "emmaotm@gmail.com"
__version__ = "1.1"


import requests
import sqlite3
import json
import os
from config import config


script_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(script_path, 'config.ini')

db = config('db', config_path)


def create_schema():
    schema_path_name = os.path.join(script_path, db['schema'])

    conn = sqlite3.connect(db['database'])
    c = conn.cursor()
    c.executescript(open(schema_path_name, 'r').read())
    conn.commit()
    conn.close()


def insert_group_atm_temp(group):
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    c.executemany("""
                INSERT INTO atm_temperat (sol, av, mn, mx)
                VALUES ?; """, group)

    conn.commit()
    conn.close()


def insert_group_atm_pressure(group):
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    c.executemany("""
                    INSERT INTO atm_pressure (sol, av, mn, mx)
                    VALUES ?; """, group)        

    conn.commit()
    conn.close()


def fetch():
    '''
    Función que toma los datos provenientes
    de la URL y los devuelve en formato
    JSON.
    '''
    dataset = config('dataset', config_path)
    
    api_key = dataset['api_key']
    url = dataset['url']

    json_data = {}
    
    response = requests.get(url.format(api_key))

    if response.status_code == 200:
        json_data = response.json()

    return json_data


def transform(json_data, chart='off'):
    '''
    Función que recibe los datos en
    formato JSON y filtra la información
    necesaria.
    Devuelve los datos para graficar si
    chart == 'on'
    '''
    
    # Obtengo los días solares.
    sol_keys = json_data.get('sol_keys')

    data = [json_data.get(sol) for sol in sol_keys]

    if chart == 'on':
        data_filter = [row.get('AT') for row in data]
        data_filter_at =[[sol, 0, 0, 0] if row is None else [sol, row.get('av'), row.get('mn'),
                        row.get('mx')] for (sol, row) in zip (sol_keys, data_filter)]

        data_filter = [row.get('PRE') for row in data]
        data_filter_pre = [[sol, 0, 0, 0] if row is None else [sol, row.get('av'), row.get('mn'),
                        row.get('mx')] for (sol, row) in zip (sol_keys, data_filter)]

    elif chart == 'off':
        data_filter = [row.get('AT') for row in data]
        data_filter_at =[(sol, None, None, None) if row is None else (sol, row.get('av'), row.get('mn'),
                        row.get('mx')) for (sol, row) in zip (sol_keys, data_filter)]

        data_filter = [row.get('PRE') for row in data]
        data_filter_pre = [(sol, None, None, None) if row is None else (sol, row.get('av'), row.get('mn'),
                        row.get('mx')) for (sol, row) in zip (sol_keys, data_filter)]

    return data_filter_at, data_filter_pre


def fill (table='temperature'):
    json_data = fetch()
    at, pre = transform(json_data, chart='off')

    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    if table == 'temperature':
        group = at
        c.executemany("""INSERT INTO atm_temperat (sol, av, mn, mx)
                    VALUES (?, ?, ?, ?); """, group)

    elif table == 'pressure':
        group = pre
        c.executemany(""" INSERT INTO atm_pressure (sol, av, mn, mx)
                        VALUES (?, ?, ?, ?); """, group) 

    conn.commit()
    conn.close() 


def report(graph=False, name_table='atm_temperat'):
    conn = sqlite3.connect(db['database'])
    c = conn.cursor()

    if graph is False:

        if name_table == 'atm_temperat':
            query = """
                SELECT *
                FROM atm_temperat; """

        elif name_table == 'atm_pressure':
            query = """
                SELECT *
                FROM atm_pressure; """

    else:
        if name_table == 'atm_temperat':
            query = """
                SELECT sol, av
                FROM atm_temperat; """

        elif name_table == 'atm_pressure':
            query = """
                SELECT sol, av
                FROM atm_pressure; """

    c.execute(query)

    # Realizo un fetchall porque son pocos datos.
    query_results = c.fetchall()

    conn.close()

    return query_results      