# -*- coding: utf-8 -*-
"""
Created on Thu May 20 18:11:00 2021

@author: weron
"""
import numpy as np
import sqlite3
from sys import argv
import csv



def create_database(plik1, plik2):
    db_name = 'Wybory_sejm.db'
    con = sqlite3.connect(db_name)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    
    with open(plik1) as lines:
        rows1,nr_okr, nazwa, liczba_wyb,wyniki,rows2 = [],[],[],[],[],[]
        #rows2 = []
        licznik = 0
        rows = csv.reader(lines, delimiter=';')
        for row in rows:
            if licznik == 0:
                pierwsza=row
                licznik+=1
            else:
                nr_okr.append(row[0])
                nazwa.append(row[1])
                liczba_wyb.append(row[23])
                wyniki.append((row[0],row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33]))
                licznik += 1
    pierwsza = pierwsza[24:]
    column_heads = ['Nr_okr', 'Liczba_glosow_waznych_lacznie']
    for i in pierwsza:
        napis = i.split(' - ')
        column_heads.append(napis[0])
        rows2.append(tuple(napis))

    rows3 = []
    okr = np.arange(1,len(nr_okr)+1)
    for j in okr:
        for i in range(2,len(wyniki[0])):
            if wyniki[j-1][i] == '':
                rows3.append((rows2[i-2][1],rows2[i-2][0], str(j), None))
            else:
                rows3.append((rows2[i-2][1],rows2[i-2][0], str(j), wyniki[j-1][i]))

    
    with open(plik2) as lines:
        mandaty = []
        licznik = 0
        rows = csv.reader(lines, delimiter=';')
        for row in rows:
            if licznik == 0:
                first = row
                licznik +=1
            else:
                mandaty.append(row[2])
                licznik +=1
    for i in range(len(nr_okr)):
        rows1.append((nr_okr[i],nazwa[i],liczba_wyb[i],mandaty[i]))
    
        
       
    cur.execute("DROP TABLE IF EXISTS Okregi;")

    cur.execute("""CREATE TABLE Okregi (
                Nr_okr INT,
                Nazwa_okr VARCHAR(100),
                Liczba_głosów_ważnych INT,
                Liczba_mandatow INT,
                PRIMARY KEY (Nr_okr))""")
    
    cur.execute("DROP TABLE IF EXISTS Komitety_wyborcze;")
    
    cur.execute("""CREATE TABLE Komitety_wyborcze (
                Nazwa_komitetu VARCHAR(100),
                Sygnatura VARCHAR(100),
                PRIMARY KEY (Sygnatura))""")

    cur.execute("DROP TABLE IF EXISTS Wyniki;")
    
    
    cur.execute("""CREATE TABLE Wyniki {}""".format(tuple(column_heads)))
    
    cur.execute("DROP TABLE IF EXISTS Wyniki_alt;")
    
    cur.execute("""CREATE TABLE Wyniki_alt (
                Sygnatura VARCHAR(100) references Komitety_wyborcze,
                Nazwa_komitetu VARCHAR(100),
                Nr_okr INT references Okregi,
                Liczba_glosow INT,
                PRIMARY KEY (Sygnatura,Nr_okr))""")
    con.commit()    
    
    con = sqlite3.connect(db_name)
    con.row_factory = sqlite3.Row
    with con:
        cur = con.cursor()
        for i in range(len(rows1)):
            cur.execute("INSERT INTO Okregi VALUES(?,?,?,?)",rows1[i])
            cur.execute("INSERT INTO Wyniki VALUES(?, ?,?, ?, ?,?,?,?,?,?,?,?)", wyniki[i])
        for j in range(len(rows2)):
            cur.execute("INSERT INTO Komitety_wyborcze VALUES(?, ?)", rows2[j])
        for k in range(len(rows3)):
            cur.execute("INSERT INTO Wyniki_alt VALUES(?,?,?,?)", rows3[k])
    
    con.commit()

    print("Baza danych została utworzona")

if __name__ == "__main__":
    plik1 = argv[1]
    plik2 = argv[2]
    create_database(plik1,plik2)
