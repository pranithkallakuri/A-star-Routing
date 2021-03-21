import webbrowser
import psycopg2
import psycopg2.extras
import configparser

def overlay_map(start, goal, parent, vertex, edge, x):
    config = configparser.ConfigParser()
    config.read('database.config')
    details = config['DB_PARAMS']
    conn = psycopg2.connect(dbname=details['DB_NAME'], user=details['DB_USER'], password=details['DB_PASS'], host=details['DB_HOST'])
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Connection in make_map successful....")
    dist = 0
    p = goal
    v_list = []
    p_list = []
    street_names = []
    while p != -1:
        cur.execute('SELECT path[1], ST_X(geom) as longitude, ST_Y(geom) as latitude ' +
                    'FROM (SELECT (ST_DumpPoints(geom_way)).* as pts ' +
                          'FROM at_2po_4pgr WHERE id = %s) as foo;', (parent[p]['prev_e_id'],)
        )
        points = cur.fetchall()
        # print(list(parent[p].keys()))

        # This issue because we are travelling in wrong way
        # Remove wrong way travel and we can remove below code(IDTS)
        if parent[p]['parent_loc'] == 1: 
            points.reverse()

        for coord in points:
            v_list.append([coord['longitude'], coord['latitude']])
            #print([coord['longitude'], coord['latitude']])
        #print("e_id = ", parent[p]['prev_e_id'])
        # print("v_id = ", p)
        p_list.append([vertex[p-1]['longitude'], vertex[p-1]['latitude']])
        street_names.append(edge[parent[p]['prev_e_id']-1]['osm_name'])
        dist += edge[parent[p]['prev_e_id']-1]['dist_in_meters']
        p = parent[p]['parent_v_id']

    cur.close()
    conn.close()
    print('connection closed...')

    v_list.reverse()
    street_names.reverse()
    # print()
    # print()
    # # print("start = ", [vertex[start-1]['longitude'], vertex[start-1]['latitude']])
    # # print("goal = ", [vertex[goal-1]['longitude'], vertex[goal-1]['latitude']])
    # for v in v_list:
    #     print(v)

    str1 = """
    <!doctype html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/css/ol.css" type="text/css">
        <style>
        .map {{
            height: 90vh;
            width: 100%;
        }}
        </style>
        <script src="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.5.0/build/ol.js"></script>
        <title>OpenLayers Map Overlay</title>
    </head>
    <body>
        <h2>Route - Time = {timeh}:{timem}hrs ; Dist = {dist}km</h2>
        <div id="map" class="map"></div>
        <script type="text/javascript">
        var map = new ol.Map({{
            target: 'map',
            layers: [
                new ol.layer.Tile({{
                    source: new ol.source.OSM()
                }})       
            ]
        }});

        var ls_feature = new ol.Feature({{
            geometry: new ol.geom.LineString({v_list}),        
        }});
        ls_feature.setStyle(new ol.style.Style({{
                stroke: new ol.style.Stroke({{
                    color: 'rgba(0, 20, 255, 0.4)',
                    width: 6
            }})
        }}));

        var p_feature = new ol.Feature({{
            geometry: new ol.geom.MultiPoint({p_list})
        }});

        var source = new ol.Feature({{
            geometry: new ol.geom.Point({src}),
        }});

        var target = new ol.Feature({{
            geometry: new ol.geom.Point({dest}),
        }});

        source.setStyle(
            new ol.style.Style({{
                image: new ol.style.Icon({{
                    anchor: [0.5, 0.85],
                    src: 'data/start-marker.png',
                    scale: 0.13,
                }}),
            }})
        );

        target.setStyle(
            new ol.style.Style({{
                image: new ol.style.Icon({{
                    anchor: [0.5, 0.95],
                    src: 'data/finish-marker.png',
                    scale: 0.1,
                }}),
            }})
        );

        ls_feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
        p_feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
        source.getGeometry().transform('EPSG:4326', 'EPSG:3857');
        target.getGeometry().transform('EPSG:4326', 'EPSG:3857');
        var vectorSource= new ol.source.Vector({{
            features: [ls_feature, p_feature, source, target]
        }});
        var vectorLayer = new ol.layer.Vector({{
            source: vectorSource,
        }});
        map.addLayer(vectorLayer);
        map.getView().fit(
        vectorSource.getExtent(),
        {{
            padding: [100, 100, 100, 100]
        }}
    );

        </script>
    </body>
    </html>
    """.format(timeh=int(x[0]), 
               timem=int((x[0]*60)%60),
               dist=round(dist/1000, 2), 
               v_list=v_list, 
               p_list=p_list, 
               src=v_list[0], 
               dest=v_list[-1])

    with open('map.html', 'w') as file:
        file.write(str1)

    # for street in street_names:
    #     print(street)

    print("Opening webbrowser...")
    webbrowser.open('map.html', new=2)