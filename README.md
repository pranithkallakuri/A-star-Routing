# A-star-Routing

###(Tested on Ubuntu-18.04)

##Requirements
1. Java runtime environment ("jre1.8" or above)
2. postgresql ("13.2, server 10.16" or above)
3. PostGIS ("2.4.4 r16526" or above)
4. Now run the following commands on your terminal
  1. `sudo -u postgres createuser [DB_USER]`
  1. `sudo -u postgres createdb --encoding=UTF8 --owner=[DB_USER] [DB_NAME]`
  1. `sudo -u postgres psql osm --command='CREATE EXTENSION postgis;'`
  1. `sudo -u postgres psql osm --command='CREATE EXTENSION hstore;'`
5. Enter/Update your DB_HOST, DB_USER, DB_NAME, DB_PASS in the 'database.config' file
6. The following Python Packages may have to be installed on your Machine: `psycopg2`, `configparser`, `heapq`, `webbrowser`
8. Download and unzip "osm2po", cd into the unzipped directory
9. Run the command: `java -jar osm2po-core-w.x.yz-signed.jar prefix=at "FILE_PATH/filename.osm"`
10. Run the command: `cd /osm2po-w-x-yz/at`
11. Run the command: `psql -U [DB_USER] -d [DB_NAME] -f filename.osm`
12. You will now have a table named `at_2po_4gr` in your database.
13. For the first time execute this python code 'build.py'. After executing it once you need not run it again.
14. Now execute run.py for each of your routing queries
