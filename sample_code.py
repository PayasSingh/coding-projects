import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import numpy as np
import folium
from math import sqrt

# connect database
def connect(path):
    conn = sqlite3.connect(path)
    c =conn.cursor()
    c.execute('PRAGMA foreign_keys=ON; ')
    conn.commit()
    return conn, c

def get_range_years():
    lb = None
    up = None
    # get valid years
    while True:
        try:
            lb = int(input("Enter start year (YYYY): "))
            up = int(input("Enter end year (YYYY): "))
        except:
            print("Invalid bounds. Please try again")
        else:
            if lb <= up:
                break
            print("Upper bound is less than lower bound. Please enter bounds again.")
    return lb, up

def get_crime_type(conn,c):
    df = pd.read_sql_query("SELECT distinct Crime_Type FROM crime_incidents", conn)
    # show all crimes
    print(df)

    crime_index= None
    # get valid crime type
    while True:
        crime_index = input("Enter the index of the crime: ")
        if crime_index.upper() == 'Q':
            return
        try:
            crime_index = int(crime_index)
            if crime_index in df.index and crime_index > 0:
                crime_type = df.iloc[crime_index]
                crime_type = crime_type[0]
                break
            else:
                print("Crime could not be found. Invalid crime, try again or press 'q' to quit")
        except:
            print("Invalid input. Please try again.")
    return crime_type

# show the barplot for a range of years and a type of crime
def show_barplot_range(conn,c):
    lb, up = get_range_years()
    crime_type = get_crime_type(conn,c)

    query = '''SELECT Month, sum(Incidents_Count) FROM crime_incidents WHERE Year >= ? and 
    Year <= ? and Crime_Type= ? group by Month'''
    df = pd.read_sql_query(query,conn, params=(lb,up,crime_type))
    # graph barplot
    try:
        plot = df.plot.bar(x="Month")
        plt.plot()
        plt.savefig(get_filename("Q1", ".png"))
        plt.show()
    except:

        print("There were no values to print. The graph is empty.")
    conn.commit()
    return 

# This function takes a sorted array, a function that can check equality between two array elements, and the minimum amount of array elements desired.
# The first n elements and any elements equivalent to the n^th element will be selected from the array, unless n < 0 or the n given to the function
# is greater than the length of the array, in which case the length of the array is returned.
def first_n_with_ties(arr, eq, n):
    val = None
    i = n - 1
    if i < 0:
        return 0
    if i < len(arr):
        val = arr[i]
        while n < len(arr) and eq(arr[n], val):
            n += 1
        return n
    return len(arr)

# This function takes a sorted list of lists/tuples and returns a list of lists that contain lists at index. Lists that are the same except for at
# index are combined and the elements at index are added to a list. 
def collapse_index(lst, index):
    info = []
    i = 0
    while i < len(lst):
        # While i < the length of the list, add the element at i to its own list. Then add the elements of equivalent lists at index
        # to this list at index until no more equivalent lists are found, then repeat for the next element.
        curr = list(lst[i][:index]) + [[lst[i][index]]] + list(lst[i][index + 1:])
        c1 = list(lst[i][:index]) + list(lst[i][index + 1:])
        i += 1
        while i < len(lst) and list(lst[i][:index]) + list(lst[i][index + 1:]) == c1:
            curr[index].append(lst[i][index])
            i += 1
        info.append(curr)
        #print(curr)
    return info

# This function takes a base filename to (potentially) increment and a file extension. An unused filename is returned. 
def get_filename(base, ext):
    n = 0
    mid = ''
    name = ''
    while True:
        # Try opening files until the file does not exist. Return that filename.
        try:
            name = base + mid + ext
            file = open(name, 'r')
            file.close()
            n += 1
            mid = '-' + str(n)
        except:
            break
    return name

def most_least_populous(conn,c):
    # the query returns a list of the population of each neighbourhood
    # in a descending order
    c.execute(''' SELECT 
                p.Neighbourhood_Name, Latitude, Longitude,
                CANADIAN_CITIZEN+NON_CANADIAN_CITIZEN+NO_RESPONSE as total_pop
                FROM population p, coordinates c
                WHERE p.Neighbourhood_Name = c.Neighbourhood_Name and total_pop > 0 and c.Latitude <> 0.0 and c.Longitude <> 0
                ORDER BY total_pop DESC''')
    areas = c.fetchall()
    areas = list(areas)

    # get the value of N from the user
    while True:
        try:
            int_N = int(input("Enter number of locations: "))
            if int_N > len(areas):
                print("Out of bounds. Please try again")
                continue
        except Exception as e:
            print("Invalid input. Please try again")
            continue
        break

    # call the first_n_with_ties function to find the N MOST
    # populated neighbourhoods considering ties
    most_populous = areas[:first_n_with_ties(areas, (lambda l1, l2:l1[3]== l2[3]), int_N)]

    # reversing the areas list stores the neighbourhoods with their 
    # populations in an ascending order
    areas_rev = areas.copy()

    # call the first_n_with_ties function to find the N LEAST
    # populated neighbourhoods considering ties
    areas_rev.reverse()
    least_populous = areas_rev[:first_n_with_ties(areas_rev, (lambda l1, l2:l1[3]== l2[3]), int_N)]
    
    # scale is to scale the populations for the circle markers
    scale = 0
    for i in range(len(most_populous)):
        scale = scale + most_populous[i][3]
    for i in range(len(least_populous)):
        scale = scale + least_populous[i][3]

    # define the area of the map to be shown
    m = folium.Map(location = [53.5444,-113.323], zoom_start=11)

    # map the most populous areas
    for index in range(len(most_populous)):
        folium.Circle(
            location = [areas[index][1], areas[index][2]],
            popup = areas[index][0] + "<br>" + str(areas[index][3]),
            radius = (areas[index][3]/scale)*5000,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
            ).add_to(m)

    # map the least populous areas
    for index in range(len(least_populous)):
        folium.Circle(
            location = [areas_rev[index][1], areas_rev[index][2]],
            popup = areas_rev[index][0] + "<br>" + str(areas_rev[index][3]),
            radius = (areas_rev[index][3]/scale)*5000,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
            ).add_to(m)

    # save the mapped areas in a .html file
    m.save(get_filename("Q2",".html"))
    conn.commit()
    return

def top_n_with_crime(conn, c):
    lb, up = get_range_years()
    crime_type = get_crime_type(conn,c,)

    # the query gets the sum of a given type of crime commited in each neighbourhood
    # within the given range of years
    param = (lb,up, crime_type)
    c.execute('''SELECT c.Neighbourhood_Name, d.Latitude, d.Longitude, sum(Incidents_Count) as g
        FROM crime_incidents c, coordinates d
        WHERE c.Year >= ? and c.Year <= ? and c.Crime_Type= ? and c.Neighbourhood_Name = d.Neighbourhood_Name and d.Latitude != 0.0 and d.Longitude != 0
        group by c.Neighbourhood_Name, d.Latitude, d.Longitude 
        order by g desc''', param)
    neigh_name= c.fetchall()
    neigh_name = list(neigh_name)

    # get the integer N from the user 
    while True:
        try:
            int_N = int(input("Enter number of locations: "))
            if int_N > len(neigh_name):
                print("Out of bounds. Please try again")
                continue
        except Exception as e:
            print("Invalid input. Please try again")
            continue
        break
    
    # list 'most_incidents' will contain the top N neighbourhoods, including ties
    most_incidents = neigh_name[:first_n_with_ties(neigh_name, (lambda l1, l2:l1[3]== l2[3]), int_N)]

    # define the area of the map to be shown
    m = folium.Map(location = [53.5444,-113.323],zoom_start=11)
	
    # map the top N neighbourhoods with most crimes of the given crime type
    for index in range(len(most_incidents)):
        folium.Circle(
            location = [neigh_name[index][1], neigh_name[index][2]],
            popup = neigh_name[index][0] + "<br>" + str(neigh_name[index][3]),
            radius = sqrt(neigh_name[index][3]) * 20,
            color = 'crimson',
            fill = True,
            fill_color = 'crimson'
            ).add_to(m)

    # save the map in a .html file
    m.save(get_filename("Q3",".html"))
    conn.commit()
    return

def n_highest_crime_population_ratios(conn, c):
    lb, ub = get_range_years()

    # Input the number of locations to show from the user
    n = 0
    while True:
        try:
            n = int(input("Enter number of locations: "))
            assert(n > 0)
        except:
            print("Invalid input, please try again. ")
            continue
        break

    query = '''
    select P.n_name, (C.total_crimes*1.0) / P.total_pop as crime_ratio, M.mcc, L.Latitude, L.Longitude
    from (select Neighbourhood_Name as n_name, CANADIAN_CITIZEN + NON_CANADIAN_CITIZEN + NO_RESPONSE as total_pop
        from population
        where total_pop > 0) as P,
        (select Neighbourhood_Name as n_name, sum(Incidents_Count) as total_crimes
        from crime_incidents
        where Year >= {} and Year <= {}
        group by n_name) as C,
        (select n_name, mcc
        from (select Neighbourhood_Name as n_name, Crime_Type as mcc, sum(Incidents_Count) as cnt 
            from crime_incidents
            where Year >= {} and Year <= {}
            group by n_name, mcc) as CTS,
            (select n_name1, max(cnt) as mx
            from (select Neighbourhood_Name as n_name1, Crime_Type as mcc, sum(Incidents_Count) as cnt 
                from crime_incidents
                where Year >= {} and Year <= {}
                group by n_name1, mcc)
            group by n_name1) as MXS
        where CTS.n_name = MXS.n_name1 and CTS.cnt = MXS.mx) as M,
        (select Neighbourhood_name as n_name, Latitude, Longitude
        from coordinates
        where Latitude != 0.0 and Longitude != 0.0) as L
    where P.n_name = C.n_name and C.n_name = M.n_name and M.n_name = L.n_name
    order by crime_ratio desc, P.n_name;
    '''.format(lb, ub, lb, ub, lb, ub)

    # Execute the query, then call collapse_index to catch any ties for most common crime, then get the first n elements with ties in crime/pop ratio.
    info = collapse_index(list(c.execute(query).fetchall()), 2)
    info = info[:first_n_with_ties(info, (lambda l1, l2: l1[1] == l2[1]), n)]

    m = folium.Map(location = [53.5444, -113.323], zoom_start = 11)

    for i in info:
        folium.Circle(
            location = [i[3], i[4]],
            popup = "{} <br> {} <br> {}".format(i[0], ", ".join(i[2]), i[1]),
            radius= 1000*i[1],
            color= 'crimson',
            fill= True,
            fill_color= 'crimson'
        ).add_to(m)

    m.save(get_filename("Q4", ".html"))

def main():
    while True:
        try:
            conn, c = connect(input("Enter the name of the database: "))
        except:
            print("Incorrect input. Please try again.")
            continue
        break
    
    functions = [show_barplot_range, most_least_populous, top_n_with_crime, n_highest_crime_population_ratios]
    fn_select = "\nEnter your choice or press q to quit:"
    while True:
        print(fn_select)
        for i in range(0, len(functions)):
            print(str(i) + ': ' + functions[i].__name__)
        input_str = input("\n> ")
        if input_str == 'q':
            break
        else:
            try:
                fn = functions[int(input_str)]
            except Exception as e:
                print("\nInvalid input, please try again.")
                continue
            fn(conn, c)
    conn.commit()
    conn.close()

main()
