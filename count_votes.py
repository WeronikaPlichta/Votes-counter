# -*- coding: utf-8 -*-
"""
Created on Thu May 20 18:11:01 2021

@author: weron
"""
import numpy as np
import sqlite3
from sys import argv
import pandas as pd
import csv
import matplotlib.pyplot as plt

def count(database):
    
    sqliteConnection = sqlite3.connect(database)
    cursor = sqliteConnection.cursor()
    
    sqlite_select_query = """SELECT Liczba_mandatow from Okregi """
    cursor.execute(sqlite_select_query)
    records1 = cursor.fetchall()
    
    mandaty = []
    for row in records1:
          mandaty.append(int(row[0]))
          
    sqlite_select_query = """SELECT SUM(Liczba_głosów_ważnych) from Okregi """
    cursor.execute(sqlite_select_query)
    records2 = cursor.fetchall()
    
    for row in records2:
        all_votes = int(row[0])
    #print(all_votes)
    
    sqlite_select_query = """SELECT * from Wyniki """
    cursor.execute(sqlite_select_query)
    records3 = cursor.fetchall()
    
    #sprawdzamy, które komitety się kwalifikują
    sqlite_select_query = """SELECT Sygnatura, Nazwa_komitetu, SUM(Liczba_glosow) FROM Wyniki_alt GROUP BY Nazwa_komitetu """
    cursor.execute(sqlite_select_query)
    records4 = cursor.fetchall()

    qualified = [] #1 i 0 przypisane do indeksów partii
    votes_percentage = []
    names = []
        
    for row in records4:
        dziel = int(row[2])/all_votes
        votes_percentage.append(dziel)
        names.append(row[1])
        if dziel>0.05:
            qualified.append(1)
        else:
            qualified.append(0)
    #mniejszosci narodowe nie muszą przekroczyć progu, a koalicje muszą przekroczyć 8% - sprawdzamy czy w naszej bazie są takie
    for k in range(len(names)):
        if 'KOALICJA' in names[k]:
            #print("Koalicja, idx:", k)
            if votes_percentage[k]>0.08:
                qualified[k] = 1
        if 'MNIEJSZOŚĆ' in names[k]:
            #print("Mniejszosc narodowa, idx:", k)
            qualified[k] = 1
    #print(qualified)
    #print(names)

    #liczymy podział mandatów
     
    results = np.zeros((len(records3),len(names)))
    seats = np.zeros(len(names))
    okr = 0
    for row in records3:
        number = mandaty[okr]
        dziel_przez = np.linspace(1,int(number),int(number)) 
        temporary_results = np.zeros((number,len(names)))
        for m in range(0,number):
            for n in range(0,len(names)):
                if qualified[n] == 0: #zerujemy niezakwalifikowane partie
                    temporary_results[m,n] = 0
                if row[n+2] == '':
                    temporary_results[m,n] = 0
                else:
                    temporary_results[m,n] = int(row[n+2])/dziel_przez[m]
        #print(temporary_results)
        
        #szukamy tyle największych liczb, ile jest mandatów
        num_largest = number
        indices = (-temporary_results).argpartition(num_largest, axis=None)[:num_largest]
        x, y = np.unravel_index(indices, temporary_results.shape)
            
        # print("x =", x)
        # print("y =", y)
        # print("Largest values:", temporary_results[x, y])
        # print("Sort: " ,np.sort(temporary_results, axis=None)[-num_largest:])
        
        for element in range(0,number):
            idx = y[element]
            results[okr,idx] +=1
            seats[idx] +=1
        okr +=1
    
    #print(results)
    #print(seats)
    print("Mandaty przyznane zgodnie z metodą d'Hondta obowiązującą w 2019r:")
    for i in range(len(seats)):
        print(names[i], ':    ', int(seats[i]))
            
####### algorytm z 1991r - metoda Hare'a-Niemeyera
    #brak progu wyborczego do przekroczenia - wszystkie partie, na które oddano głosy w danym okręgu są brane pod uwagę przy podziale mandatów
    
    results_hn = np.zeros((len(records3),len(names)))
    seats_hn = np.zeros(len(names))
    okr = 0
    for row in records3:
        number = mandaty[okr]
        second_digit = np.zeros(len(names))
        seats_okr = 0
        for n in range(0,len(names)):
            if row[n+2] == '':
                temporary_results[n] = 0
            else:
                q = (int(row[n+2])*number)/int(row[1])
                q_str = str(q)
                seats_hn[n] +=int(q_str[0])
                second_digit[n] = q - int(q_str[0])
                seats_okr +=int(q_str[0])
        reszta = number - seats_okr
        if reszta == 0:
            pass
        else:
            indices = (-second_digit).argpartition(reszta, axis=None)[:reszta]
            x = np.unravel_index(indices, second_digit.shape)
        for element in range(0,len(x)):
            idx = x[element]
            seats_hn[idx] +=1
        results_hn[okr,:] = seats_hn
        okr+=1
    print("\n\n\nMandaty przyznane zgodnie z metodą Hare'a-Niemeyera obowiązującą w 1991r:")
    for i in range(len(seats)):
        print(names[i], ':    ', int(seats_hn[i]))

##### algorytm z 2001r - zmodyfikowana metoda Sainte-Lague  
##### występuje prób wyborczy, na tych samych zasadach co w 2019r.

    results_sl = np.zeros((len(records3),len(names)))
    seats_sl = np.zeros(len(names))
    okr = 0
    for row in records3:
        number = mandaty[okr]
        dziel_przez = np.array([1.4,3,5,7,9,11,13,15,17,19,21,23,25]) 
        temporary_results = np.zeros((len(dziel_przez),len(names)))
        for m in range(0,len(dziel_przez)):
            for n in range(0,len(names)):
                if qualified[n] == 0: #zerujemy niezakwalifikowane partie
                    temporary_results[m,n] = 0
                if row[n+2] == '':
                    temporary_results[m,n] = 0
                else:
                    temporary_results[m,n] = int(row[n+2])/dziel_przez[m]
        #szukamy tyle największych liczb, ile jest mandatów
        num_largest = number
        indices = (-temporary_results).argpartition(num_largest, axis=None)[:num_largest]
        x, y = np.unravel_index(indices, temporary_results.shape)
            
        
        for element in range(0,number):
            idx = y[element]
            results_sl[okr,idx] +=1
            seats_sl[idx] +=1
        okr +=1
    
    #print(results)
    #print(seats)
    print("\n\n\nMandaty przyznane zgodnie ze zmodyfikowaną metodą Saint-Lague obowiązującą w 2001r:")
    for i in range(len(seats_sl)):
        print(names[i], ':    ', int(seats_sl[i]))    
                    

    x = np.arange(len(names)) 
    width = 0.2  
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, seats, width, label="Metoda d'Hondta")
    rects2 = ax.bar(x, seats_hn, width, label="Metoda Hare'a-Niemeyera")
    rects3 = ax.bar(x + width, seats_sl, width, label="Matoda Saint-Lague")
    
    ax.set_ylabel('Ilosc mandatów')
    ax.set_title('Komitety wyborcze')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation = 'vertical')
    ax.legend()

    #fig.tight_layout()

    plt.show(block=True)



    cursor.close()
    
    
    
if __name__ == "__main__":
    #database = 'Wybory_sejm.db'
    database = argv[1]
    count(database)  
    
    
    