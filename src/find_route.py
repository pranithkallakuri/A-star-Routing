#A* implementation

import math
import heapq

def heuristic(lat1, lon1, lat2, lon2, msl):
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return (d/msl)


#start and goal are v_ids
#edge and vertex are zero-indexed list
#graph is a dictionary
#0 -> neither
#1 -> open
#2 -> closed
def ASTAR(start, goal, graph, vertex, edge, msl):
    parent = {}
    open_list = []
    lat, lon = vertex[start-1]['latitude'], vertex[start-1]['longitude']
    glat, glon = vertex[goal-1]['latitude'], vertex[goal-1]['longitude']
    h = heuristic(lat, lon, glat, glon, msl)
    heapq.heappush(open_list, (h, start)) #tuple (heuristic, v_id)
    parent[start] = {'parent_v_id': -1, 'prev_e_id': -1, 'parent_loc': -1}
    graph[start]['type'] = 1
    graph[start]['dist_to_start'] = 0

    while len(open_list) != 0:
        x = heapq.heappop(open_list)
        if graph[x[1]]['type'] == 2:
            continue

        if(x[1] == goal):
            print("FOUND GOAL")
            return x, parent
        for child in graph[x[1]]['adj']:
            loc = child[1]
            e_id = child[0]
            n_vtx = edge[e_id-1]['source'] if loc == 1 else edge[e_id-1]['target']
            try:
                t = graph[n_vtx]['type']
            except KeyError:
                continue
            if t == 0:
                lat, lon = vertex[n_vtx-1]['latitude'], vertex[n_vtx-1]['longitude']
                h = heuristic(lat, lon, glat, glon, msl)
                graph[n_vtx]['type'] = 1
                g = edge[e_id-1]['cost'] + graph[x[1]]['dist_to_start']  #Adding previous g value to current g 
                graph[n_vtx]['dist_to_start'] = g
                heapq.heappush(open_list, (g+h, n_vtx))
                parent[n_vtx] = {'parent_v_id': x[1], 'prev_e_id': e_id, 'parent_loc': 0 if loc == 1 else 1}

            elif t == 1:
                old_g = graph[n_vtx]['dist_to_start']
                new_g = edge[e_id-1]['cost'] + graph[x[1]]['dist_to_start']
                if new_g < old_g:
                    lat, lon = vertex[n_vtx-1]['latitude'], vertex[n_vtx-1]['longitude']
                    h = heuristic(lat, lon, glat, glon, msl)
                    graph[n_vtx]['dist_to_start'] = new_g 
                    heapq.heappush(open_list, (new_g+h, n_vtx))
                    parent[n_vtx] = {'parent_v_id': x[1], 'prev_e_id': e_id, 'parent_loc': 0 if loc == 1 else 1}

            elif t == 2:
                old_g = graph[n_vtx]['dist_to_start']
                new_g = edge[e_id-1]['cost'] + graph[x[1]]['dist_to_start']
                if new_g < old_g:
                    graph[n_vtx]['type'] = 1
                    lat, lon = vertex[n_vtx-1]['latitude'], vertex[n_vtx-1]['longitude']
                    h = heuristic(lat, lon, glat, glon, msl) 
                    graph[n_vtx]['dist_to_start'] = new_g
                    heapq.heappush(open_list, (new_g+h, n_vtx))
                    parent[n_vtx] = {'parent_v_id': x[1], 'prev_e_id': e_id, 'parent_loc': 0 if loc == 1 else 1}
            
        graph[x[1]]['type'] = 2

    return None, None