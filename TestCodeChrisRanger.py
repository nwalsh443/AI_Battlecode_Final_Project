
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

if my_team == bc.Team.Red:enemy_team = bc.Team.Blue()
else: enemy_team = bc.Team.Red




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

def invert(loc):
	newx = earthMap.width - loc.x
	newy = earthMap.height - loc.y
	return bc.MapLocation(bc.Planet.Earth,newx, newy)

def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind + amount) % 8 ]

if gc.planet() == bc.Planet.Earth:
	oneLoc = gc.my_units()[0].location.map_location()
	earthMap = gc.starting_map(bc.Planet.Earth)
	enemyStart = invert(oneLoc)
	print('worker stars at' +locToStr(oneLoc))
	print('enemy location at' +locToStr(enemyStart))


#limit amount of factories

while True:
	try:
		numWorkers = 0
		amount_of_factories = 0
		blueprintLocation = None
		blueprintWaiting = False
		
		
		
		for unit in gc.my_units():
			if unit.unit_type == bc.UnitType.Factory:
				if not unit.structure_is_built():
					ml = unit.location.map_location()
					blueprintLocation = ml
					blueprintWaiting = True
			if unit.unit_type == bc.UnitType.Worker:
				numWorkers +=1

		for unit in gc.my_units():
			if unit.unit_type == bc.UnitType.Worker:
				d = random.choice(directions)
				if numWorkers < 5 and gc.can_replicate(unit.id,d):
					gc.replicate(unit.id,d)
					continue
		
				if gc.karbonite() > bc.UnitType.Factory.blueprint_cost():
					if gc.can_blueprint(unit.id,bc.UnitType.Factory,d) and amount_of_factories < 5:
						gc.blueprint(unit.id,bc.UnitType.Factory,d)
						amount_of_factories += 1
						continue
				adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
				for adjacent in adjacentUnits:
					if gc.can_build(unit.id,adjacent.id):
						gc.build(unit.id,adjacent.id)
						continue

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
						continue
				elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):
					gc.produce_robot(unit.id, bc.UnitType.Ranger)
					continue

			if unit.unit_type == bc.UnitType.Ranger:
				if unit.location.is_on_map():
					if gc.is_move_ready(unit.id):
						if gc.round()>50:
							fuzzygoto(unit,enemyStart)
						if gc.round()>200:
							goto(unit,random.choice(directions))
						
						
			if unit.unit_type == bc.UnitType.Ranger:
				if not unit.location.is_in_garrison():
					attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),50,enemy_team)
					if len(attackableEnemies) > 0:
						if gc.is_attack_ready(unit.id):
							gc.attack(unit.id, attackableEnemies[0].id)
					elif gc.is_move_ready(unit.id):
						nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),50,enemy_team)
						if len(nearbyEnemies) > 0:
							destination = nearbyEnemies[0].location.map_location()
						else:
							destination = enemyStart
						fuzzygoto(unit, destination)

	except Exception as e:
		print('Error:', e)
		traceback.print_exc()

	gc.next_turn()

	sys.stdout.flush()
	sys.stderr.flush()
