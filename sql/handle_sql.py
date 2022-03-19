# Handles the communication to the SQL-Database
FORCE_NEW_DB = False # Forces to always regenerate the .db file
import sqlite3, os, math
from sql.init_sql import initSql

class SqlHandler:
	def __init__(self, _path, _osmPath):
		self.path = _path
		self.osmPath = _osmPath

		if FORCE_NEW_DB and os.path.isfile(self.path):
			os.remove(self.path)

		if not os.path.isfile(self.path):
			initSql(self.path, self.osmPath)

		self.connectToDatabase()
	
	def connectToDatabase(self):        
		self.conn = sqlite3.connect(self.path)
		self.cur = self.conn.cursor()

	def getNodesOfWay(self, wayId):
		result = []

		for row in self.cur.execute('SELECT nodeId FROM nodes LEFT JOIN node_way ON nodes.id = node_way.nodeId WHERE node_way.wayId=' + str(wayId)):
			result.append(row[0])
		return result

	def getWaysOfNode(self, nodeId):
		result = []

		for row in self.cur.execute('SELECT wayId FROM ways LEFT JOIN node_way ON ways.id = node_way.wayId WHERE node_way.nodeId=' + str(nodeId)):
			result.append(row[0])
		return result

	def getSideWaysOfWay(self, wayId):
		result = []

		for row in self.cur.execute('SELECT sideWayId FROM way_sideway LEFT JOIN ways ON ways.id=way_sideway.wayId WHERE ways.id=' + str(wayId)):
			if not row[0] in result:
				result.append(row[0])
		return result

	def getCrossingPointOfWays(self, firstWay, secondWay):
		result = []

		for row in self.cur.execute('SELECT node FROM crossingpoints WHERE firstWay=? AND secondWay=?', (str(firstWay), str(secondWay))):
			if not row[0] in result:
				result.append(row[0])
		return result

	def getLocOfNode(self, node):
		for row in self.cur.execute('SELECT lon, lat FROM nodes WHERE nodes.id="' + str(node) + '"'):
			return [row[0], row[1]]

	def getNodeByCoordinates(self, lat, lon):
		for row in self.cur.execute('SELECT id FROM nodes WHERE nodes.lon=? AND nodes.lat=?', (lon, lat)):
			return row[0]
		return

	def getNameOfWay(self, wayId):
		for row in self.cur.execute('SELECT name FROM ways WHERE id="' + str(wayId) + '"'):
			return row[0]

	def getWaysByNameWildcard(self, name):
		result = []
		for row in self.cur.execute('SELECT id, name FROM ways WHERE name LIKE "' + name + '%"'):
			result.append(row[0])	
		return result

	def getNodesBetweenNodes(self, routeWay):
		nodes = []
		
		startNodeIndex = ""
		endNodeIndex = ""

		for row in self.cur.execute('SELECT id FROM node_way WHERE wayId=? AND nodeId=?', (routeWay['way'], routeWay['startNode'])):
			startNodeIndex = int(row[0])
		
		for row in self.cur.execute('SELECT id FROM node_way WHERE wayId=? AND nodeId=?', (routeWay['way'], routeWay['endNode'])):
			endNodeIndex = int(row[0])
		
		if startNodeIndex > endNodeIndex:
			tempNodes = []
			for row in self.cur.execute('SELECT nodeId FROM node_way WHERE id <=? AND id >=?', (startNodeIndex, endNodeIndex)):
				tempNodes.append(row[0])
			nodes = tempNodes[::-1]
		else:
			for row in self.cur.execute('SELECT nodeId FROM node_way WHERE id >=? AND id <=?', (startNodeIndex, endNodeIndex)):
				nodes.append(row[0])
				
		return nodes

	def __del__(self):
		self.conn.close()