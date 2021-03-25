#############################-----------PREREQUISITES/README-------------##########################################################
##
##     FOLLOWING INSTRUCTIONS ARE FOR LINUX ENVIORNMENTS (Tested on Ubuntu-18.04)
##
##     1. Java runtime environment ("jre1.8" or above)
##     2. postgresql ("13.2, server 10.16" or above)
##     3. PostGIS ("2.4.4 r16526" or above)
##     4. Now run the following commands on your terminal
##         i.   sudo -u postgres createuser [DB_USER]
##         ii.  sudo -u postgres createdb --encoding=UTF8 --owner=[DB_USER] [DB_NAME]
##         iii. sudo -u postgres psql osm --command='CREATE EXTENSION postgis;'
##         iv.  sudo -u postgres psql osm --command='CREATE EXTENSION hstore;'
##     5. Enter/Update your DB_HOST, DB_USER, DB_NAME, DB_PASS in the 'database.config' file
##     6. The following Python Packages may have to be installed on your Machine:
##         --> 'psycopg2', 'configparser', 'heapq', 'webbrowser', 'tkinter'
##     7. Download and unzip "osm2po"
##     8. Run the command: java -jar osm2po-core-w.x.yz-signed.jar prefix=at "FILE_PATH/filename.osm"
##     9. Run the command: cd /osm2po-w-x-yz/at
##     10. Run the command: psql -U [DB_USER] -d [DB_NAME] -f at_2po_4pgr.sql
##     11. You will now have a table named 'at_2po_4gr' in your database.
##     12. For the first time execute this python code 'build.py'. After executing it once you need not run it again.
##     13. Now execute run.py for each of your routing queries
##
############################################################################################################################

import os
import src.make_graph
import psycopg2
import configparser

#make vertex_table and edge_table

config = configparser.ConfigParser()
config.read('database.config')
details = config['DB_PARAMS']

print("Caution: Pickled graph files will be deleted")
print("Are you sure you want to continue..?(Y/N)")
inp = input()
if inp.lower() != 'y':
    print("exiting")
    exit(0)
    
conn = psycopg2.connect(dbname=details['DB_NAME'], user=details['DB_USER'], password=details['DB_PASS'], host=details['DB_HOST'])
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS edge_table;')
conn.commit()
cur.execute('CREATE TABLE edge_table AS ' +
	            'SELECT id, osm_name, source, y1, x1, ST_MakePoint(x1, y1) as geom_source, ' + 
	                'target, y2, x2, ST_MakePoint(x2, y2) as geom_target, ' +
	                'ST_DistanceSphere(ST_MakePoint(x1, y1), ST_MakePoint(x2, y2)) AS dist_in_meters, ' + 
	                'cost, reverse_cost, kmh AS speed_limit_kmh ' +
	            'FROM at_2po_4pgr;'
)
conn.commit()

cur.execute('DROP TABLE IF EXISTS vertex_table;')
conn.commit()
cur.execute('CREATE TABLE vertex_table AS ' +
                'SELECT source AS ID, ST_MakePoint(x1, y1) as geom, y1 AS latitude, x1 AS longitude FROM at_2po_4pgr ' +
                'UNION ' +
                'SELECT target AS ID, ST_MakePoint(x2, y2) as geom, y2 AS latitude, x2 AS longitude FROM at_2po_4pgr;'
)
conn.commit()

cur.close()
conn.close()

print("Deleting previous .gph, .vtx, .edg files...")
test_list = os.listdir('data/')
for item in test_list:
    if item.endswith('.gph') or item.endswith('.edg') or item.endswith('.vtx'):
        os.remove('data/' + item) 
print("Deleted!")
print("ABOVE = ", os.getcwd())
src.make_graph.build_graph(details['DB_HOST'], details['DB_NAME'], details['DB_USER'], details['DB_PASS'])

##END OF BUILD##
