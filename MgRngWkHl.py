
import battlecode as bc
import random
import traceback
import os
import sys

gc = bc.GameController()
directions = [bc.Direction.North,bc.Direction.Northeast,bc.Direction.East,bc.Direction.Southeast,bc.Direction.South,bc.Direction.Southwest,bc.Direction.West,bc.Direction.Northwest,bc.Direction.Center]
tryRotate = [0,-1,2,-2,2]
#random.seed(6137)
my_team = gc.team()

my_team = gc.team()
enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
	enemy_team = bc.Team.Blue



def locToStr(loc):
	return '('+str(loc.x)+','+str(loc.y)+')'

def goto(unit,dest):

	d = unit.location.map_location().direction_to(dest)
	if gc.can_move(unit.id,d):
		gc.move_robot(unit.id,d)

def fuzzygoto(unit,dest):
	toward = unit.location.map_location().direction_to(dest)
	for tilt in tryRotate:
		d = rotate(toward,tilt)
		if gc.can_move(unit.id, d):
			gc.move_robot(unit.id,d)
			break
			
			
			

			
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


(marsHeight, marsWidth) = find_dimensions(bc.Planet.Mars)
(earthHeight, earthWidth) = find_dimensions(bc.Planet.Earth)

print(earthHeight)
print(earthWidth)

		
	 


def newLoc():
  
	newx = random.randint(1,earthWidth)
	newy = random.randint(1,earthHeight)
	locations.append((newx, newy))
	
	return bc.MapLocation(bc.Planet.Earth,newx,newy)

def invert(loc):
	newx = earthMap.width - loc.x
	newy = earthMap.height - loc.y
	return bc.MapLocation(bc.Planet.Earth,newx, newy)

def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind + amount) % 8 ]

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
	
	print('worker stars at' +locToStr(oneLoc))
	print('enemy location at' +locToStr(enemyStart))
#	print('another lcoation at' +locToStr(anotherLocation))

locations = []
#limit amount of factories
turnNumber = 0

while True:
	try:
	#	print(locations)
		
		visted = False
		
		numRangers = 0
		
		#turnNumber = 0
		
		numHealers = 0
		
		numMages = 0
		
		numWorkers = 0
		
		amount_of_factories = 0
		
		numRocket = 0
		
		blueprintLocation = None
		
		blueprintWaiting = False
		
		FoundEnemyLocation = False
		
		
		
		for unit in gc.my_units():
			if unit.unit_type == bc.UnitType.Factory:
				if not unit.structure_is_built():
					ml = unit.location.map_location()
					blueprintLocation = ml
					blueprintWaiting = True
			if unit.unit_type == bc.UnitType.Worker:
				numWorkers +=1

		for unit in gc.my_units():
			if unit.unit_type == bc.UnitType.Ranger:
				numRangers +=1
			if unit.unit_type == bc.UnitType.Factory:
				amount_of_factories =+1
			if unit.unit_type == bc.UnitType.Rocket:
				numRocket +=1
			if unit.unit_type == bc.UnitType.Mage:
				numMages +=1
			if unit.unit_type == bc.UnitType.Healer:
				numHealers +=1
				
			if unit.unit_type == bc.UnitType.Worker:
				d = random.choice(directions)
				if numWorkers < 5 and gc.can_replicate(unit.id,d):
					gc.replicate(unit.id,d)
					continue
		
				if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and amount_of_factories < 5:
					if gc.can_blueprint(unit.id,bc.UnitType.Factory,d):
						gc.blueprint(unit.id,bc.UnitType.Factory,d)
				elif gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
					if gc.can_blueprint(unit.id,bc.UnitType.Rocket,d):
						gc.blueprint(unit.id,bc.UnitType.Rocket,d)
						print('building rocket')
		#				continues
				adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
				for adjacent in adjacentUnits:
					if gc.can_build(unit.id,adjacent.id):
						gc.build(unit.id,adjacent.id)
						
		#				continue

				if blueprintWaiting:
					if gc.is_move_ready(unit.id):
						ml = unit.location.map_location()
						bdist = ml.distance_squared_to(blueprintLocation)
						if bdist > 2:
							fuzzygoto(unit,blueprintLocation)

			if unit.unit_type == bc.UnitType.Factory:
				garrison = unit.structure_garrison()
				if len(garrison) > 0:
					d = random.choice(directions)
					if gc.can_unload(unit.id,d):
						gc.unload(unit.id,d)
		#				continue
					
				if gc.can_produce_robot(unit.id, bc.UnitType.Ranger) and turnNumber < 3 or numRangers < numMages:
					gc.produce_robot(unit.id, bc.UnitType.Ranger)
					turnNumber += 1
					#numRangers = numRangers + 1
					print('numRangers = ', numRangers)
					print('turnNumber = ', turnNumber)
					print('Printing Ranger')
					
		#			continue
					
				if gc.can_produce_robot(unit.id, bc.UnitType.Mage) and turnNumber >= 3 and turnNumber < 6:
					gc.produce_robot(unit.id, bc.UnitType.Mage)
					turnNumber += 1
					#numMages = numMages + 1
					print('numMages = ', numMages)
					print('Printing Mage')
		#			continue
			
				if gc.can_produce_robot(unit.id, bc.UnitType.Healer) and turnNumber >= 6:
					gc.produce_robot(unit.id, bc.UnitType.Healer)
					turnNumber = 0
					#numHealers = numHealers + 1
					print('numHealers = ', numHealers)
					print('Printing  Healer')
					
					#continue

			if unit.unit_type == bc.UnitType.Ranger:
				if unit.location.is_on_map():
					temp_location = newLoc()
					
					if gc.is_move_ready(unit.id):
						if gc.round()>50 and FoundEnemyLocation == False:
							fuzzygoto(unit,enemyStart)
							if gc.can_sense_location(enemyStart):
								#print('Found enemy start')
								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id):
								fuzzygoto(unit,temp_location)					
								if temp_location == unit.location.map_location():
									print('been here')
									continue
									
			if unit.unit_type == bc.UnitType.Mage:
				if unit.location.is_on_map():
					temp_location = newLoc()
					
					if gc.is_move_ready(unit.id):
						if gc.round()>50 and FoundEnemyLocation == False:
							fuzzygoto(unit,enemyStart)
							if gc.can_sense_location(enemyStart):
								print('Found enemy start')
								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id):
								fuzzygoto(unit,temp_location)					
								if temp_location == unit.location.map_location():
									print('been here')
									continue
									
			if unit.unit_type == bc.UnitType.Healer:
				if unit.location.is_on_map():
					temp_location = newLoc()
					
					if gc.is_move_ready(unit.id):
						if gc.round() > 50 and FoundEnemyLocation == False:
							fuzzygoto(unit, enemyStart)
							if gc.can_sense_location(enemyStart):
								print('Found enemy start')
								FoundEnemyLocation = True
						else:
							if gc.is_move_ready(unit.id):
								fuzzygoto(unit, temp_location)
								if temp_location == unit.location.map_location():
									print('been here')
									continue
						
						
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
