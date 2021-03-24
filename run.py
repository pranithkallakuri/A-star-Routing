import psycopg2
import os
import configparser
import pickle
import src.make_map
import src.find_route
import tkinter
import tkinter.messagebox

start_coord = tuple()
goal_coord = tuple()

#BASIC GUI
#----------------------------------------------------------------------------------#
def buttonClicked(root, svar, dvar, lat1, lon1, lat2, lon2):
    global start_coord, goal_coord
    minlat=float("17.1913000")
    minlon=float("78.2185000") 
    maxlat=float("17.6139000") 
    maxlon=float("78.6916000")

    if svar.get() == 'N':
        slat = float(sl1.get())
        slon = float(sl2.get())
        slat = minlat if slat < minlat else slat
        slat = maxlat if slat > maxlat else slat
        slon = minlon if slon < minlon else slon
        slon = maxlon if slon > maxlon else slon
        start_coord = float(slat), float(slon)
    if svar.get() == 'BPHC':
        start_coord = 17.5416, 78.5752
    if svar.get() == 'RGIA':
        start_coord = 17.23645, 78.42952

    if dvar.get() == 'N':
        dlat = float(dl1.get())
        dlon = float(dl2.get())
        print(dlat, dlon)
        print(dlat < minlat)
        dlat = minlat if dlat < minlat else dlat
        dlat = maxlat if dlat > maxlat else dlat
        dlon = minlon if dlon < minlon else dlon
        dlon = maxlon if dlon > maxlon else dlon
        goal_coord = float(dlat), float(dlon)

    if dvar.get() == 'BPHC':
        goal_coord = 17.5416, 78.5752
    if dvar.get() == 'RGIA':
        goal_coord = 17.23645, 78.42952
    print(start_coord, goal_coord)
    if start_coord == goal_coord:
        str1 = "Source and Destination are same \nPlease provide distinct Source and Destinations"
        tkinter.messagebox.showerror("Error", str1)
        exit(0)
    root.destroy()
    


root = tkinter.Tk()
root.geometry('1000x250')
root.title("Enter Source/Destination")
svar = tkinter.StringVar(None, 'N')
dvar = tkinter.StringVar(None, 'N')
ls = tkinter.Label(root, text = "Source")
ld = tkinter.Label(root, text = "\nDestination") 
slat = tkinter.Label(root, text='lat: ') 
slon = tkinter.Label(root, text='    lon: ')
dlat = tkinter.Label(root, text='lat: ') 
dlon = tkinter.Label(root, text='    lon: ')
snoop = tkinter.Radiobutton(root, text="lat/lon", value='N', variable=svar)
sbphc = tkinter.Radiobutton(root, text="BPHC", value='BPHC', variable=svar)
srgia = tkinter.Radiobutton(root, text="RGIA", value='RGIA', variable=svar)
dnoop = tkinter.Radiobutton(root, text="lat/lon", value='N', variable=dvar)
dbphc = tkinter.Radiobutton(root, text="BPHC", value='BPHC', variable=dvar)
drgia = tkinter.Radiobutton(root, text="RGIA", value='RGIA', variable=dvar)
but = tkinter.Button(root, text ="Calculate!", command =lambda: buttonClicked(root, svar, dvar, sl1, sl2, dl1, dl2))

sl1 = tkinter.Entry(root) 
sl2 = tkinter.Entry(root)
dl1 = tkinter.Entry(root) 
dl2 = tkinter.Entry(root)

ls.grid(row=0)
slat.grid(row=1, column=0)
sl1.grid(row=1, column=1)
slon.grid(row=1, column=2)
sl2.grid(row=1, column=3)
snoop.grid(row=1, column=5)
tkinter.Label(root, text="\t(OR)\t").grid(row=1, column=6)
sbphc.grid(row=1, column=7)
srgia.grid(row=1, column=8)
tkinter.Label(root, text="").grid(row=3)
ld.grid(row=4)
dlat.grid(row=5, column=0)
dl1.grid(row=5, column=1)
dlon.grid(row=5, column=2)
dl2.grid(row=5, column=3)
dnoop.grid(row=5, column=5)
tkinter.Label(root, text="\t(OR)\t").grid(row=5, column=6)
dbphc.grid(row=5, column=7)
drgia.grid(row=5, column=8)
tkinter.Label(root, text="").grid(row=6)
tkinter.Label(root, text="").grid(row=7)
but.grid(row=8, column=3) 

tkinter.mainloop()
#-------------------------------------------------------------------------------------------#
#Actual running from below  

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

cur.execute('SELECT max(speed_limit_kmh) FROM edge_table;')
maxspeedlimit = cur.fetchone()[0]
#print(maxspeedlimit)
cur.close()
conn.close()

############## PREPROCESSING ##############
config = configparser.ConfigParser()
config.read('database.config')
details = config['DB_PARAMS']
curr_path = os.getcwd()
curr_path += '/data/'
print('Loading graph....')
with open(curr_path + details['DB_NAME'] + "_graph.gph", 'rb') as handle:
    graph = pickle.load(handle)

with open(curr_path + details['DB_NAME'] + "_vertices.vtx", 'rb') as handle:
    vertex = pickle.load(handle)

with open(curr_path + details['DB_NAME'] + "_edges.edg", 'rb') as handle:
    edge = pickle.load(handle)
print('Graph Successfully loaded...')
print('ASTAR START...')
x, parent = src.find_route.ASTAR(start, goal, graph, vertex, edge, maxspeedlimit)
print(x)
# print(parent)
print('ASTAR DONE...')
src.make_map.overlay_map(start, goal, parent, vertex, edge, x)