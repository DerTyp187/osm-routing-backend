from sql.handle_sql import SqlHandler
from server import osmPath, dbPath

# Initalize global variables
sql = ""

def search(wayName, limit):
    global sql
    formattedWays = []
    limit = int(limit)
    sql = SqlHandler(dbPath, osmPath)
    ways = sql.getWaysByNameWildcard(wayName)
    
    for way in ways:
        formattedWays.append({'id': way, 'name': sql.getNameOfWay(way) + " (" + str(way) + ")"})

    

    del sql

    if len(formattedWays) >= limit:
        return formattedWays[:limit]
    else:
        return formattedWays