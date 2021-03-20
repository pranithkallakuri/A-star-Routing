
import psycopg2
import psycopg2.extras
import pickle
import configparser
import os

def build_graph(DB_HOST, DB_NAME, DB_USER ,DB_PASS):
    print("Connecting to database....")  
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connection successful")
    cur.execute('SELECT * FROM edge_table ORDER BY id;')
    edge_record = cur.fetchall() #list of Dictrows
    # for i  in edge_record[0].keys():
    #     print(i)
    # for dr in records:
    #     print(dr)
    #print(len(edge_record))

    cur.execute('SELECT * FROM vertex_table ORDER BY id;')
    vertex_record = cur.fetchall()
    # for dr in vertex_record:
    #     print(dr)
    #print(len(vertex_record))

    # cur.execute("SELECT ST_Equals(ST_MakePoint(78.4675334, 17.4072047), %s);", (vertex_record[0]['geom'], )) #010100000069B23511EC9D53400A4735913E683140
    # print(cur.fetchone()[0])
    

    graph = {} #v_id -> list of e_id s
    print("Building Graph....")
    
    for dr in edge_record:
        try:
            graph[dr['source']]['adj'].append([dr['id'], 0]) # [edge_id, location]
        except KeyError:
            graph[dr['source']] = {'type':0, 'cost': float('inf'), 'adj':[[dr['id'], 0]]} # [edge_id, location]
        
        if dr['reverse_cost'] != 1000000:
            try:
                graph[dr['target']]['adj'].append([dr['id'], 1])
            except KeyError:
                graph[dr['target']] = {'type':0, 'cost': float('inf'), 'adj':[[dr['id'], 1]]} # [edge_id, location]


        
    print("Graph created....")
    # lkeys = list(graph.keys())
    # for i in range(1, len(lkeys)):
    #     if lkeys[i] != 1+lkeys[i-1]:
    #         print(lkeys[i-1], lkeys[i])

    print(len(graph))
    cur.close()
    conn.close()
    print("Successfully Disconnected from database")
    print()
    curr_path = os.getcwd()
    print(curr_path)
    filename = curr_path + '/data/' + DB_NAME + "_graph.gph"
    with open(filename, 'wb') as handle:
        pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Created .gph file")

    filename = curr_path + '/data/' + DB_NAME + "_vertices.vtx"
    with open(filename, 'wb') as handle:
        pickle.dump(vertex_record, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Created .vtx file")

    filename = curr_path + '/data/' + DB_NAME + "_edges.edg"
    with open(filename, 'wb') as handle:
        pickle.dump(edge_record, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Created .edg file")
    
