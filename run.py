import psycopg2
import os
import configparser
import pickle
import src.make_map
import src.find_route

# start_coord = 17.54730, 78.57258 #BITS HYD
# goal_coord = 17.2407, 78.4291    #RGIA

start_coord = 17.54078, 78.57655 #BITS HYD ISOLATED
goal_coord = 17.2302, 78.4295    #RGIA ISOLATED

# start_coord = 17.40379, 78.46795 #IMP-DONT LOSE
# goal_coord = 17.40724, 78.46794  #IMP-DONT DELETE

######## MAIN EXECUTION PART ############
config = configparser.ConfigParser()
config.read('database.config')
details = config['DB_PARAMS']

conn = psycopg2.connect(dbname=details['DB_NAME'], user=details['DB_USER'], password=details['DB_PASS'], host=details['DB_HOST'])
cur = conn.cursor()

cur.execute('SELECT id FROM vertex_table ' + 
            'WHERE ST_DWithin(geom , ST_MakePoint(%s, %s) , 100) ' + 
            'ORDER BY ST_Distance(geom, ST_MakePoint(%s, %s)), id ASC ' + 
            'LIMIT 1;', (start_coord[1], start_coord[0], start_coord[1], start_coord[0])
)

start = cur.fetchone()[0]
print("start = ", start)

cur.execute('SELECT id FROM vertex_table ' + 
            'WHERE ST_DWithin(geom , ST_MakePoint(%s, %s) , 100) ' + 
            'ORDER BY ST_Distance(geom, ST_MakePoint(%s, %s)), id ASC ' + 
            'LIMIT 1;', (goal_coord[1], goal_coord[0], goal_coord[1], goal_coord[0])
)

goal = cur.fetchone()[0]
print("goal = ", goal)
cur.close()
conn.close()

############## PREPROCESSING ##############
config = configparser.ConfigParser()
config.read('database.config')
details = config['DB_PARAMS']
curr_path = os.getcwd()
curr_path += '/data/'
with open(curr_path + details['DB_NAME'] + "_graph.gph", 'rb') as handle:
    graph = pickle.load(handle)

with open(curr_path + details['DB_NAME'] + "_vertices.vtx", 'rb') as handle:
    vertex = pickle.load(handle)

with open(curr_path + details['DB_NAME'] + "_edges.edg", 'rb') as handle:
    edge = pickle.load(handle)

x, parent = src.find_route.ASTAR(start, goal, graph, vertex, edge)
print(x)
# print(parent)

src.make_map.overlay_map(start, goal, parent, vertex, edge, x)