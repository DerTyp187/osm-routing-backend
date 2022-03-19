from sql.handle_sql import SqlHandler
from server import osmPath, dbPath

# Global variables
sql = None
visitedWays = [] # [VisitedWay[wayId, parentWayId], [],...]
endFound = False

# VisitedWays
def pushIntoVisitedWays(way, parentWay = ""): # Appends a new VisitedWay to the visitedWay Array
    global visitedWays

    # "new" visited way should not already exists in array (no duplicates)
    if not any(way in visitedWay for visitedWay in visitedWays):
        if parentWay != "": # check if parent is given
            visitedWays.append([way, parentWay])
        else:
            visitedWays.append([way, ""])


def getOpenVisitedWays(): # Get all visited ways which have unchecked sideways.
    result = []
    openSideWays = 0 # counts how many sideways are found per vistedWay

    for vWay in visitedWays:
        openSideWays = 0
        currentSideWays = sql.getSideWaysOfWay(vWay[0]) #  
        for sideWay in currentSideWays:
            if not any(sideWay in visitedWay for visitedWay in visitedWays): # if sideway is not in visitedWays: Array
                openSideWays += 1
                
        if openSideWays > 0: # if visited way has unvistited sideways
            result.append(vWay[0])

    return result

def getVisitedWaybyWay(way): # Find a VisitedWay by it's way (visitedWay[0])
    result = ""
    
    for visitedWay in visitedWays:
        if visitedWay[0] == way:
            result = visitedWay
    return result

# Reverse and build route
def reverseRoute(endWay):
    route = []
    reversed = False

    currentVisitedWay = getVisitedWaybyWay(int(endWay)) # Get the visitedWay object of "endway: int" from the visitedWay-array
    while reversed == False:
        if currentVisitedWay[1] != "": # if visited sideway has a parent way (visitedWays: Array[[way,parentway], ...])
            route.append(currentVisitedWay)
            currentVisitedWay = getVisitedWaybyWay(currentVisitedWay[1]) # set currentVisitedWay to parentWay 
        else:
            reversed = True
    return route

def getRouteWayOfRoute(route):
    routeWays = []
    routeCrossingNodes = []
    counter = 0

    for vWay in route: # Get all crossingpoints
        crossingPoint = sql.getCrossingPointOfWays(vWay[0], vWay[1])
        prevCrossingPoint = ""
        if counter > 0:
            prevCrossingPoint = routeCrossingNodes[counter-1][0]
        else:
            prevCrossingPoint = sql.getNodesOfWay(vWay[0])[0]


        routeWays.append({'way': vWay[0], 'startNode': prevCrossingPoint, 'endNode': crossingPoint[0]})
        routeCrossingNodes.append(crossingPoint)
        counter += 1
    return routeWays

def buildRoute(endWay):
    routeNodes = []
    coordinates = []
    
    reversedRoute = reverseRoute(endWay)
    routeWays = getRouteWayOfRoute(reversedRoute)

    for routeWay in routeWays:
        nodesBetweenNodes = sql.getNodesBetweenNodes(routeWay)
        for node in nodesBetweenNodes:
            routeNodes.append(node)

    for node in routeNodes: # get all coordinates of the crossinpoints
        coordinates.append({'lon':sql.getLocOfNode(node)[0], 'lat': sql.getLocOfNode(node)[1] })

    return coordinates

# Search for destination
def checkSideWaysOfWay(way, endWay):
    global endFound
    global visitedWays

    sideWays = sql.getSideWaysOfWay(way)

    for sideWay in sideWays:
        
        if str(sideWay) == str(endWay):
            pushIntoVisitedWays(sideWay, way)
            endFound = True
            return
        else:
            pushIntoVisitedWays(sideWay, way)

def searchRoute(startWay, endWay): # Main
    global sql
    global visitedWays
    global endFound
    
    sql = SqlHandler(dbPath, osmPath)
    visitedWays = []
    endFound = False
    counter = 0

    sideWays = sql.getSideWaysOfWay(startWay)
    
    pushIntoVisitedWays(startWay)
    checkSideWaysOfWay(startWay, endWay)

    for sideWay in sideWays:
        checkSideWaysOfWay(sideWay, endWay)
    
    while endFound == False:
        if len(sideWays) and counter >= len(sideWays):
            counter = 0
            sideWays = getOpenVisitedWays()
        else:
            checkSideWaysOfWay(sideWays[counter], endWay)
            counter += 1
    
    result = buildRoute(endWay)
    sql.conn.close()
    del sql
    return result

def searchRouteByCoordinates(fromWayLat, fromWayLon, toWayLat, toWayLon): # Main
    global sql
    sql = SqlHandler(dbPath, osmPath)
    fromNode = sql.getNodeByCoordinates(fromWayLat, fromWayLon)
    toNode = sql.getNodeByCoordinates(toWayLat, toWayLon)

    fromWay = sql.getWaysOfNode(fromNode)[0]
    toWay = sql.getWaysOfNode(toNode)[0]
    del sql
    return searchRoute(fromWay, toWay)