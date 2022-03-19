# Intilializes/Creates the database with all tables and table contents
import sqlite3, os

def createNode(conn, line):
	nodeId = str(line.split('id="')[1].split('"')[0])
	nodeLon = str(line.split('lon="')[1].split('"')[0])
	nodeLat = str(line.split('lat="')[1].split('"')[0])
	
	cur = conn.cursor()
	cur.execute('INSERT INTO nodes(id, lon, lat) VALUES (?, ?, ?)', (nodeId, nodeLon, nodeLat))

def createWay(conn, lines):
	wayId = ""
	wayNodes = []
	wayName = ""
	isHighWay = False


	for line in lines:
		if "<way" in line:
			wayId = str(line.split('id="')[1].split('"')[0])
		elif "<nd ref=" in line:
			wayNodes.append(str(line.split('ref="')[1].split('"')[0]))
		elif '<tag k="name" ' in line:
			wayName = str(line.split('v="')[1].split('"')[0])
		elif '<tag k="highway" ' in line:
			isHighWay = True

	if isHighWay:
		cur = conn.cursor()
		cur.execute('INSERT INTO ways(id, name) VALUES (?, ?)', (wayId, wayName))

	for nodeId in wayNodes:
		createNodeWayJunction(conn, wayId, nodeId)

def createNodeWayJunction(conn, wayId, nodeId):
	cur = conn.cursor()
	cur.execute('INSERT INTO node_way(wayId, nodeId) VALUES (?, ?)', (wayId, nodeId))

def createWaySideWayJunction(conn, wayId, sideWayId):
	cur = conn.cursor()
	cur.execute('INSERT INTO way_sideway(wayId, sideWayId) VALUES (?, ?)', (wayId, sideWayId))

def parse_way_sideWay_junction(conn):
	print("Parse sideways")
	cur = conn.cursor()

	for wayRow in cur.execute('SELECT id FROM ways'):
		currentWayId = wayRow[0]
		nodesOfWay = getNodesOfWay(conn, currentWayId)

		for node in nodesOfWay:
			waysOfNode = getWaysOfNode(conn, node)
			if len(waysOfNode) > 1:
				for sideWay in waysOfNode:
					if sideWay != currentWayId:
						createCrossingpoint(conn, node, sideWay, currentWayId)
						createWaySideWayJunction(conn, currentWayId, sideWay)
	conn.commit()

def parse_osm_to_sql(conn, osm_path):
	print("Parsing nodes and ways of the OSM file into the database.")
	file = open(osm_path, "r", encoding="utf-8")
	wayLines = []

	for line in file.readlines():
		if "<node" in line:
			createNode(conn, line)
		elif "<way " in line:
			wayLines.append(line)
		elif "</way>" in line:
			createWay(conn, wayLines)
			wayLines = []
		elif len(wayLines) > 0:
			wayLines.append(line)

	conn.commit()

def createCrossingpoint(conn, node, currentWayId, sideWay):
	cur = conn.cursor()
	cur.execute('INSERT INTO crossingpoints(firstWay, secondWay, node) VALUES (?, ?, ?)', (sideWay, currentWayId, node))


def createDatabase(path):
	print("Generate database structure")
	conn = sqlite3.connect(path)
	cur = conn.cursor()
	cur.execute('''CREATE TABLE "nodes" (
					"id"	INTEGER NOT NULL UNIQUE,
					"lon"	TEXT NOT NULL,
					"lat"	TEXT NOT NULL,
					PRIMARY KEY("id")
				);''')

	cur.execute('''CREATE TABLE "ways" (
					"id"	INTEGER NOT NULL UNIQUE,
					"name"	TEXT,
					PRIMARY KEY("id")
				);''')

	cur.execute('''CREATE TABLE "node_way" (
					"id"	INTEGER NOT NULL UNIQUE,
					"wayId"	INTEGER NOT NULL,
					"nodeId"	INTEGER NOT NULL,
					PRIMARY KEY("id"),
					FOREIGN KEY("wayId") REFERENCES "ways"("id"),
					FOREIGN KEY("nodeId") REFERENCES "nodes"("id")
				);''')

	cur.execute('''CREATE TABLE "way_sideway" (
					"wayId"	INTEGER NOT NULL,
					"sideWayId"	INTEGER NOT NULL,
					FOREIGN KEY("wayId") REFERENCES "ways"("id"),
					FOREIGN KEY("sideWayId") REFERENCES "ways"("id")
				);''')

	cur.execute('''CREATE TABLE "crossingpoints" (
					"id"	INTEGER NOT NULL,
					"node" INTEGER NOT NULL,
					"firstWay"	INTEGER NOT NULL,
					"secondWay"	INTEGER NOT NULL,
					PRIMARY KEY("id"),
					FOREIGN KEY("node") REFERENCES "nodes"("id"),
					FOREIGN KEY("firstWay") REFERENCES "ways"("id"),
					FOREIGN KEY("secondWay") REFERENCES "ways"("id")
				);''')

	return conn

# Getters
def getNodesOfWay(conn, wayId):
	cur = conn.cursor()
	result = []

	for row in cur.execute('SELECT nodeId FROM nodes LEFT JOIN node_way ON nodes.id = node_way.nodeId WHERE node_way.wayId=' + str(wayId)):
		result.append(row[0])
	return result

def getWaysOfNode(conn, nodeId):
	cur = conn.cursor()
	result = []

	for row in cur.execute('SELECT wayId FROM ways LEFT JOIN node_way ON ways.id = node_way.wayId WHERE node_way.nodeId=' + str(nodeId)):
		result.append(row[0])
	return result

# INIT
def initSql(path, osmPath):
	print("Initializing database. This may take a while.")
	conn = createDatabase(path)
	parse_osm_to_sql(conn, osmPath)
	parse_way_sideWay_junction(conn)
	print("Done: Initializing database")