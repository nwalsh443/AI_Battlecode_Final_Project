#Ben ShapiRobots Battlecode AI
#Created by Noah Walsh, Christopher Cruz, Andrew March and Thomas Cooper
#4/8/19
#We created a Battlecode agent AI that attempts to defeat our opponent and win the match.
# Originally inspired by the 2018 Battlecode Project Hephaestus: https://github.com/AnPelec/Battlecode-2018/blob/master/Project%20Hephaestus/run.py
# and https://www.youtube.com/watch?v=6Nd9nnPRS2E&t=3019s and https://www.youtube.com/watch?v=zM7XMLcWlJM&t=4981s
import battlecode as bc
import random
import traceback
import os
import sys

#sets gc to the battlecode GameController()
gc = bc.GameController()

#creates list of possible directions
directions = [bc.Direction.North,bc.Direction.Northeast,bc.Direction.East,bc.Direction.Southeast,bc.Direction.South,bc.Direction.Southwest,bc.Direction.West,bc.Direction.Northwest,bc.Direction.Center]

#creates list of possible rotations
tryRotate = [0,-1,2,-2,2]
my_team = gc.team()

#sets my_team to the team the game controller is controlling
my_team = gc.team()

#sets enemy_team to the opposite team of my_team
enemy_team = bc.Team.Red

if my_team == bc.Team.Red:
	enemy_team = bc.Team.Blue

#returns the location as a string
def locToStr(loc):
	return '('+str(loc.x)+','+str(loc.y)+')'

#Moves the bots
def goto(unit,dest):
	d = unit.location.map_location().direction_to(dest)
	if gc.can_move(unit.id,d):
		gc.move_robot(unit.id,d)

#Method that moves the bots
def fuzzygoto(unit,dest):
	toward = unit.location.map_location().direction_to(dest)
	for tilt in tryRotate:
		d = rotate(toward,tilt)
		if gc.can_move(unit.id, d):
			gc.move_robot(unit.id,d)
			break

#Finds the dimensions of earth, used to find locations to travel to		
def find_dimensions(current_planet):
	low = 19
	high = 49
	ansx = 19
	ansy = 19
	planet_map = gc.starting_map(current_planet)
	
	while (low <= high):
		med = (low + high)//2
		temp_location = bc.MapLocation(current_planet, med, 0)
		if planet_map.on_map(temp_location):
			if ansx < med:
				ansx = med
			low = med+1
		else:
			high = med-1
	
	low = 19
	high = 49
	while (low <= high):
		med = (low + high)//2
		temp_location = bc.MapLocation(current_planet, 0, med)
		if planet_map.on_map(temp_location):
			if ansy < med:
				ansy = med
			low = med+1
		else:
			high = med-1
	return (ansx, ansy)

#The dimensions of the map
(earthHeight, earthWidth) = find_dimensions(bc.Planet.Earth)

#find adjacent locations
def adjacentLocation(loc):
	placesOnMap = []

	newx = loc.x
	newy = loc.y
	
	North = bc.MapLocation(bc.Planet.Earth,newx, newy + 1)
	South = bc.MapLocation(bc.Planet.Earth,newx, newy - 1)
	East = bc.MapLocation(bc.Planet.Earth,newx + 1, newy)
	West = bc.MapLocation(bc.Planet.Earth,newx - 1, newy)
	
	NorthEast = bc.MapLocation(bc.Planet.Earth,newx + 1, newy + 1)
	NorthWest = bc.MapLocation(bc.Planet.Earth,newx - 1, newy + 1)
	SouthEast = bc.MapLocation(bc.Planet.Earth,newx + 1, newy - 1)
	SouthWest = bc.MapLocation(bc.Planet.Earth,newx - 1, newy - 1)
	
	placesOnMap.append(North)
	placesOnMap.append(South)
	placesOnMap.append(East)
	placesOnMap.append(West)
	placesOnMap.append(NorthEast)
	placesOnMap.append(NorthWest)
	placesOnMap.append(SouthEast)
	placesOnMap.append(SouthWest)
	return placesOnMap
	
#PASS IS LOCATION OF CURRENT UNTI CHECK ADJACENT LOCATIONS, IF ADJACENT LOCATION HAS NOT BEEN VISITED TRAVLE TO THAT LOCATION 

#Method that finds a new location. Use this to have the bots randomy move to a new location
def newLoc():
	newx = random.randint(1,earthWidth)
	newy = random.randint(1,earthHeight)
	locations.append((newx, newy))
	return bc.MapLocation(bc.Planet.Earth,newx,newy)
	
#Inverts the staring location of our team to find the location of the enemy team.
def invert(loc):
	newx = earthMap.width - loc.x
	newy = earthMap.height - loc.y
	return bc.MapLocation(bc.Planet.Earth,newx, newy)

#Allows bots to move around obstacles
def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind + amount) % 8 ]

	
#queues the order of units to level up	
if gc.planet() == bc.Planet.Earth:
	gc.queue_research(bc.UnitType.Rocket)
	gc.queue_research(bc.UnitType.Rocket)
	gc.queue_research(bc.UnitType.Rocket)
	gc.queue_research(bc.UnitType.Mage)
	gc.queue_research(bc.UnitType.Mage)
	gc.queue_research(bc.UnitType.Mage)
	gc.queue_research(bc.UnitType.Ranger)
	gc.queue_research(bc.UnitType.Ranger)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Healer)
	gc.queue_research(bc.UnitType.Healer)
	oneLoc = gc.my_units()[0].location.map_location()
	
	earthMap = gc.starting_map(bc.Planet.Earth)
	enemyStart = invert(oneLoc)
	
#list of current locations
locations = []

#a list of locations bots have already been to.
pastlocations = []

#Keeps track of the amount of robots being built
turnNumber = 0

while True:
	try:
		visited = False
		numRangers = 0					
		numHealers = 0		
		numMages = 0		
		numWorkers = 0	
		amount_of_factories = 0	
		numRocket = 0	
		blueprintLocation = None	
		blueprintWaiting = False	
		FoundEnemyLocation = False
			
		#for all possible units		
		for unit in gc.my_units():
		#if unit is factory and it is not built then choose the location and set blueprintWaiting to true
			if unit.unit_type == bc.UnitType.Factory:
				if not unit.structure_is_built():
					ml = unit.location.map_location()
					blueprintLocation = ml
					blueprintWaiting = True
					#if unit is worker add 1 to numWorkers
					
			if unit.unit_type == bc.UnitType.Worker:
				numWorkers +=1

		for unit in gc.my_units():
			#if unit is ranger add one to numRangers
			if unit.unit_type == bc.UnitType.Ranger:
				numRangers +=1
				#if the location isn't in pastlocations then append it to the list
				if unit.location.is_on_map():
					for i in pastlocations:
						if unit.location.map_location() not in pastlocations:
							pastlocations.append(unit.location.map_location())
							
			#if unit is a mage then add 1 to numMages				
			if unit.unit_type == bc.UnitType.Mage:
				numMages +=1
				#if the location isn't in pastlocations then append it to the list
				if unit.location.is_on_map():
					for i in pastlocations:
						if unit.location.map_location() not in pastlocations:
							pastlocations.append(unit.location.map_location())
							
			if unit.unit_type == bc.UnitType.Healer:
				numHealers +=1
				#if the location isn't in pastlocations then append it the list
				if unit.location.is_on_map():
					for i in pastlocations:
						if unit.location.map_location() not in pastlocations:
							pastlocations.append(unit.location.map_location())
			#if unit is factory add 1 to amount_of_factories				
			if unit.unit_type == bc.UnitType.Factory:
				amount_of_factories =+1
			#if unit is rocket then add one to numRocket
			if unit.unit_type == bc.UnitType.Rocket:
				numRocket +=1
			
			#if unit is worker then set to to a random direction	
			if unit.unit_type == bc.UnitType.Worker:
				d = random.choice(directions)
				#if there are less than 5 workers then replicate if possible
				if numWorkers < 5 and gc.can_replicate(unit.id,d):
					gc.replicate(unit.id,d)
					continue
					
				#if there are less than 5 factories and there is enough karbonite and it is possible to build one, then build a factory
				if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and amount_of_factories < 5:
					if gc.can_blueprint(unit.id,bc.UnitType.Factory,d):
						gc.blueprint(unit.id,bc.UnitType.Factory,d)
				elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
					if gc.can_blueprint(unit.id,bc.UnitType.Rocket,d):
						gc.blueprint(unit.id,bc.UnitType.Rocket,d)
				#creating list called adjacentUnits that holds nearby units
				adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
				
				#for everything in adjacentUnits, if building in adjacent unit is possible, then build
				for adjacent in adjacentUnits:
					if gc.can_build(unit.id,adjacent.id):
						gc.build(unit.id,adjacent.id)
						
				#if blueprintWaiting is true
				if blueprintWaiting:
					#if is_move_ready is true
					if gc.is_move_ready(unit.id):
						#set ml to to the current location
						ml = unit.location.map_location()
						bdist = ml.distance_squared_to(blueprintLocation)
						if bdist > 2:
							fuzzygoto(unit,blueprintLocation)
							
			#if unit is factory, it puts unit.structure_garrison in a list called garrison
			if unit.unit_type == bc.UnitType.Factory:
				garrison = unit.structure_garrison()
			#if garrison isn't empty then coose a random direction and unload if possible
				if len(garrison) > 0:
					d = random.choice(directions)
					if gc.can_unload(unit.id,d):
						gc.unload(unit.id,d)
						
				#produces rangers	
				if gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and turnNumber < 3 or numRangers < numMages and not unit.is_factory_producing():
					if unit.structure_is_built():
						gc.produce_robot(unit.id, bc.UnitType.Ranger)
						turnNumber += 1
					
				#produces mages	
				if gc.can_produce_robot(unit.id, bc.UnitType.Mage) and turnNumber >= 3 and turnNumber < 6 and not unit.is_factory_producing():
					if unit.structure_is_built():
						gc.produce_robot(unit.id, bc.UnitType.Mage)
						turnNumber += 1
				#produces healers	
				if gc.can_produce_robot(unit.id, bc.UnitType.Healer) and turnNumber >= 6 and not unit.is_factory_producing():
					if unit.structure_is_built():
						gc.produce_robot(unit.id, bc.UnitType.Healer)
						turnNumber = 0
						
			#keeps track of ranger locations
			if unit.unit_type == bc.UnitType.Ranger:
				if unit.location.is_on_map():
					temp_location = newLoc()
					v = unit.location.map_location()
					adjLoc = adjacentLocation(v)
					d = random.randint(1, len(adjLoc) - 1)
					
					#keeps track of visited locations	
					for i in pastlocations:
						for j in adjLoc:
							if(i == j):
								visited = True
								
					#if enemy is not found by round 50, it finds the enemy start and sets FoundEnemyStart to true			
					if gc.is_move_ready(unit.id):
						if gc.round()>50 and FoundEnemyLocation == False:
							fuzzygoto(unit,enemyStart)
							if gc.can_sense_location(enemyStart):
								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id) and visited == False:
								fuzzygoto(unit,adjLoc[d])
							if gc.is_move_ready(unit.id) and visited == True:
								fuzzygoto(unit,adjLoc[d])
									
			#keeps track of mage locations					
			if unit.unit_type == bc.UnitType.Mage:
				if unit.location.is_on_map():
					temp_location = newLoc()
					v = unit.location.map_location()
					adjLoc = adjacentLocation(v)
					d = random.randint(1, len(adjLoc) - 1)
					
					#keeps track of visited locations	
					for i in pastlocations:
						for j in adjLoc:
							if(i == j):
								visited = True
								
					#if enemy is not found by round 50, it finds the enemy start and sets FoundEnemyStart to true			
					if gc.is_move_ready(unit.id):
						if gc.round()>50 and FoundEnemyLocation == False:
							fuzzygoto(unit,enemyStart)
							if gc.can_sense_location(enemyStart):
								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id) and visited == False:
								fuzzygoto(unit,adjLoc[d])							
							if gc.is_move_ready(unit.id) and visited == True:
								fuzzygoto(unit,adjLoc[d])
								
			#keeps track of healer locations					
			if unit.unit_type == bc.UnitType.Healer:
				if unit.location.is_on_map():
					temp_location = newLoc()
					v = unit.location.map_location()
					adjLoc = adjacentLocation(v)
					d = random.randint(1, len(adjLoc) - 1)
					
					#keeps track of visited locations	
					for i in pastlocations:
						for j in adjLoc:
							if(i == j):
								visited = True
								
					#if enemy is not found by round 50, it finds the enemy start and sets FoundEnemyStart to true			
					if gc.is_move_ready(unit.id):
						if gc.round()>50 and FoundEnemyLocation == False:
							fuzzygoto(unit,enemyStart)
							if gc.can_sense_location(enemyStart):

								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id) and visited == False:

								fuzzygoto(unit,adjLoc[d])
								
							if gc.is_move_ready(unit.id) and visited == True:
								fuzzygoto(unit,adjLoc[d])
																			
			#allows Rangers to sense enemies and attack them			
			if unit.unit_type == bc.UnitType.Ranger:
				if not unit.location.is_in_garrison():
					attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),70,enemy_team)
					if len(attackableEnemies) > 0:
						if gc.is_attack_ready(unit.id):
							if gc.can_attack(unit.id,attackableEnemies[0].id):
								gc.attack(unit.id, attackableEnemies[0].id)
					elif gc.is_move_ready(unit.id):
						nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),70,enemy_team)
						if len(nearbyEnemies) > 0: 
							destination = nearbyEnemies[0].location.map_location()
							
			#allows mages to sense enemies and attack them				
			if unit.unit_type == bc.UnitType.Mage:
				if not unit.location.is_in_garrison():
					attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),30,enemy_team)
					if len(attackableEnemies) > 0:
						if gc.is_attack_ready(unit.id):
							if gc.can_attack(unit.id,attackableEnemies[0].id):
								gc.attack(unit.id, attackableEnemies[0].id)
					elif gc.is_move_ready(unit.id):
						nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),30,enemy_team)
						if len(nearbyEnemies) > 0: 
							destination = nearbyEnemies[0].location.map_location()
		
			#allows healers to sense teammates and heal them		
			if unit.unit_type == bc.UnitType.Healer:
				if not unit.location.is_in_garrison():
					healFriendly = gc.sense_nearby_units_by_team(unit.location.map_location(),30,my_team)
					if len(healFriendly) > 0:
						if gc.is_heal_ready(unit.id):
							if gc.can_heal(unit.id,healFriendly[0].id):
								gc.heal(unit.id,healFriendly[0].id)
					elif gc.is_move_ready(unit.id):
						nearbyFriendly = gc.sense_nearby_units_by_team(unit.location.map_location(),30,my_team)
						if len(nearbyFriendly) > 0:
							destination = nearbyFriendly[0].location.map_location()

	except Exception as e:
		print('Error:', e)
		traceback.print_exc()

	gc.next_turn()

	sys.stdout.flush()
	sys.stderr.flush()
