#Run example
#based on https://github.com/AnPelec/Battlecode-2018/blob/master/Project%20Hephaestus/run.py
#Initially changed the strategy to what would Ben Shapiro do
import battlecode as bc
import random
import sys
import traceback
import json
from datetime import datetime

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)
my_team = gc.team()
enemy_team = bc.Team.Red
if my_team == bc.Team.Red:
	enemy_team = bc.Team.Blue
random.seed(datetime.now())



print("pystarted")

# write in team array about the probabilities
# TODO:
#	implement research
#   implement probabilities
#   implement reinforcement learning

'''
filename = 'strategy.json'
data = json.load(open(filename))
'''

#Everything is deterministic

data = {
#Making memers proud, but fix for our lord Ben

	"Earth": {
		"first_phase": {
			"threshold": 200
		},

		"second_phase": {
			"threshold": 300
		},

		"third_phase": {
		},

	}
}
#Strategy: Slowly focus on mining Karbonite, heavily militarize and then transport to Mars
#Queue one worker
gc.queue_research(bc.UnitType.Worker)
#Queue one rocket
gc.queue_research(bc.UnitType.Rocket)
#queue the knights first to focus on fighting, all 3
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
gc.queue_research(bc.UnitType.Knight)
#queue the rockets to focus on trip to Mars, the next two
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Rocket)
#queue the mages next to focus on fighting, all 3
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
gc.queue_research(bc.UnitType.Mage)
#queue the rangers next to focus on fighting, all 3
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
gc.queue_research(bc.UnitType.Ranger)
#Queue another worker
gc.queue_research(bc.UnitType.Worker)
#Queue another worker
gc.queue_research(bc.UnitType.Worker)
#Healthcare not a huge priority
gc.queue_research(bc.UnitType.Healer)


NUMBER_OF_GUESSES = 5
total_number_rockets = 0

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

marsMap = gc.starting_map(bc.Planet.Mars)
earthMap = gc.starting_map(bc.Planet.Earth)
(marsHeight, marsWidth) = find_dimensions(bc.Planet.Mars)
(earthHeight, earthWidth) = find_dimensions(bc.Planet.Earth)
locations = []

  ##############################################################################################################

#Chris
#This is supposed to guess the location of the enemy, by taking our first units position on the map and then inverting it
#Because most of the maps are symetric
#Knowing the locaion of where the enemy might be can help us attack and move more accurately

def invert(loc):
    newx = earthWidth-loc.x
    newy = earthHeight-loc.y
    return bc.MapLocation(bc.Planet.Earth, newx, newy)

if gc.planet() == bc.Planet.Earth:
    oneLoc = gc.my_units()[0].location.map_location()
    earthMap= gc.starting_map(bc.Planet.Earth)
    enemyStart = invert(oneLoc)
        ##############################################################################################################


def find_free_locations_in_Mars():
	for i in range(marsHeight+1):
		for j in range(marsWidth+1):
			temp_location = bc.MapLocation(bc.Planet.Mars, i, j)
			try:
				if marsMap.is_passable_terrain_at(temp_location):
					#print('found free location on mars!')
					locations.append((i, j))

			except Exception as e:
				print(i, j)
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

# I have to binary search to find the dimensions of the map?

non_worker_in_rocket = {}

class GeneralActions(object):

	def move_bitch(unit, place, moveType):
		dir = random.choice(directions)
		if gc.is_move_ready(unit.id) and gc.can_move(unit.id, dir):
			gc.move_robot(unit.id, dir)
			#print('Moved successfully!')

	def attack_bitch(unit, place, attackType):
		if not gc.is_attack_ready(unit.id):
			return

		location = unit.location
		nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.attack_range(), enemy_team)
		for other in nearby:
			if gc.can_attack(unit.id, other.id):
				#print('attacked a thing!')
				gc.attack(unit.id, other.id)
				break

	def load_unit(unit):
		if gc.round() < data["Earth"]["second_phase"]["threshold"]:
			return

		# possible improvement: go into the most crowded garrison
		nearby = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Rocket)
		for other in nearby:
			if gc.can_load(other.id, unit.id):
				gc.load(other.id, unit.id)

				if unit.unit_type != bc.UnitType.Worker:
					if other.id in non_worker_in_rocket:
						non_worker_in_rocket[other.id] += 1
					else:
						non_worker_in_rocket[other.id] = 1
				break

	def move_towards_rocket(unit):
		if not gc.is_move_ready(unit.id):
			return

		location = unit.location.map_location()

		best_dir = directions[0]
		closest_distance = 100000
		nearby = gc.sense_nearby_units_by_type(location, unit.vision_range, bc.UnitType.Rocket)

		for other in nearby:
			other_location = other.location.map_location()
			current_distance = location.distance_squared_to(other_location)
			if current_distance < closest_distance:
				closest_distance = current_distance
				best_dir = location.direction_to(other_location)

		curr_idx = 8
		for i in range(8):
			if directions[i] == best_dir:
				curr_idx = i
				break

		for i in range(4):
			temp_idx = (curr_idx + i + 9)%9
			if gc.can_move(unit.id, directions[temp_idx]):
				gc.move_robot(unit.id, directions[temp_idx])
				return

			temp_idx = (curr_idx - i + 9)%9
			if gc.can_move(unit.id, directions[temp_idx]):
				gc.move_robot(unit.id, directions[temp_idx])
				return


	def move_and_expand(unit):
		# makes the robot move to the least crowded square
		# hoping that this is expanding the crowd
		moves = []

		location = unit.location
		for temp in range(9):
			dir = bc.Direction(temp)
			# center is direction 8 so it will always be last
			try:
				new_location = (location.map_location()).add(dir)
				nearby_units = gc.sense_nearby_units_by_team(new_location, 2, my_team)
				moves.append((len(nearby_units), temp))
			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

		moves.sort()
		for tup in moves:
			if gc.is_move_ready(unit.id) and gc.can_move(unit.id, bc.Direction(tup[1])):
				gc.move_robot(unit.id, bc.Direction(tup[1]))
				#print('Moved successfully!')
				continue

	def move_and_shrink(unit):
		# makes the robot move to the least crowded square
		# hoping that this is expanding the crowd
		moves = []

		location = unit.location
		for temp in range(9):
			dir = bc.Direction(temp)
			# center is direction 8 so it will always be last
			try:
				new_location = (location.map_location()).add(dir)
				nearby_units = gc.sense_nearby_units_by_team(new_location, 2, my_team)
				moves.append((-1*len(nearby_units), temp))
			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

		moves.sort()
		for tup in moves:
			if gc.is_move_ready(unit.id) and gc.can_move(unit.id, bc.Direction(tup[1])):
				gc.move_robot(unit.id, bc.Direction(tup[1]))
				#print('Moved successfully!')
				continue

class WorkerClass(object):

	def harvest_karbonite(unit):
		for dir in directions:
			if gc.can_harvest(unit.id, dir):
				#print('harvested karbonite!')
				gc.harvest(unit.id, dir)
				break

	def build_blueprint(unit, building_type):

		global total_number_rockets

		for dir in directions:
			if gc.karbonite() >= building_type.blueprint_cost():
				if gc.can_blueprint(unit.id, building_type, dir):
					gc.blueprint(unit.id, building_type, dir)
					if building_type == bc.UnitType.Rocket:
						total_number_rockets += 1

	def repair(unit):
		nearby = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Factory)
		for other in nearby:
			if gc.can_repair(unit.id, other.id):
				gc.repair(unit.id, other.id)
				return

		nearby = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, bc.UnitType.Rocket)
		for other in nearby:
			if gc.can_repair(unit.id, other.id):
				gc.repair(unit.id, other.id)
				return


	def replicate_worker(unit):
		for dir in directions:
			if gc.can_replicate(unit.id, dir):
				gc.replicate(unit.id, dir)
				break

	def complete_build(unit, building_type):
		nearby = gc.sense_nearby_units_by_type(unit.location.map_location(), 2, building_type)
		for other in nearby:
			if gc.can_build(unit.id, other.id) and not other.structure_is_built():
				gc.build(unit.id, other.id)
				break

class MageClass(object): #if blink is ready, and it's a level 4 or higher
	def blink_attack_mars(unit):
		if not gc.is_blink_ready(unit.id):
			return
		if bc.ResearchInfo.get_level(bc.UnitType.Mage) < 4:
			return

		location = unit.location
		#sense nearby targets, and don't blink if there are less than 5 targets
		possible_targets = gc.sense_nearby_units_by_team(location.map_location(), 30, enemy_team)
		if len(possible_targets) > 5:
			return
		#pick random spot on board to teleport to
		for guess in range(NUMBER_OF_GUESSES):
			i = random.randint(0, marsHeight-1)
			j = random.randint(0, marsWidth-1)

			try:
				#if the mage can blink to that location, it does
				temp_location = bc.MapLocation(bc.Planet.Mars, i, j)
				if gc.can_blink(unit.id, temp_location):
					gc.blink(unit.id, temp_location)
					return

			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

	def blink_attack_earth(unit):
		if not gc.is_blink_ready(unit.id):
			return
		if bc.ResearchInfo.get_level(bc.UnitType.Mage) < 4:
			return

		location = unit.location

		possible_targets = gc.sense_nearby_units_by_team(location.map_location(), 30, enemy_team)
		if len(possible_targets) > 5:
			return
#Work on making this less random
		for guess in range(NUMBER_OF_GUESSES):
			i = random.randint(0, earthHeight-1)
			j = random.randint(0, earthWidth-1)

			try:
				temp_location = bc.MapLocation(bc.Planet.Earth, i, j)
				if gc.can_blink(unit.id, temp_location):
					gc.blink(unit.id, temp_location)
					return

			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

class HealerClass(object):

	def heal_bitch(unit):
		if not gc.is_heal_ready(unit.id):
			return

		location = unit.location
		nearby = gc.sense_nearby_units_by_team(location.map_location(), unit.attack_range(), my_team)
		for other in nearby:
			if gc.can_heal(unit.id, other.id):
				# print('healed a friend!')
				gc.heal(unit.id, other.id)
				return

	def overcharge_attack(unit):
		if not gc.is_overcharge_ready(unit.id):
			return
		if bc.ResearchInfo.get_level(bc.UnitType.Healer) < 3:
			return

		location = unit.location

		possible_targets = gc.sense_nearby_units_by_team(location.map_location(), unit.ability_range(), my_team)
		for other in possible_targets:
			if gc.can_heal(unit.id, other.id):
				gc.heal(unit.id, other.id)
				return

class RangerClass(object):

	def snipe_attack_mars(unit):
		if unit.ranger_is_sniping():
			return
		if not gc.is_begin_snipe_ready(unit.id):
			return
		if bc.ResearchInfo.get_level(bc.UnitType.Ranger) < 3:
			return
#picks a random location, and if it can snipe there, it snipes
#Work on making this smarter
		for guess in range(NUMBER_OF_GUESSES):
			i = random.randint(0, marsHeight-1)
			j = random.randint(0, marsWidth-1)

			try:
				temp_location = bc.MapLocation(bc.Planet.Mars, i, j)
				if gc.can_begin_snipe(unit.id, temp_location):
					gc.begin_snipe(unit.id, temp_location)
					return

			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

	def snipe_attack_earth(unit):
		if unit.ranger_is_sniping():
			return
		if not gc.is_begin_snipe_ready(unit.id):
			return
		if bc.ResearchInfo.get_level(bc.UnitType.Ranger) < 3:
			return

		location = unit.location
#Ben Shapiro attacks the Rockets first on Earth, and then the Factories
		possible_targets = sense_nearby_units_by_type(location.map_location(), unit.ability_range(), bc.UnitType.Rocket)
		for other in possible_targets:
			if gc.can_begin_snipe(unit.id, other.location.map_location()):
				gc.begin_snipe(unit.id, other.location.map_location())
				return

		possible_targets = sense_nearby_units_by_type(location.map_location(), unit.ability_range(), bc.UnitType.Factory)
		for other in possible_targets:
			if gc.can_begin_snipe(unit.id, other.location.map_location()):
				gc.begin_snipe(unit.id, other.location.map_location())
				return
#Be smarter about this
		for guess in range(NUMBER_OF_GUESSES):
			i = random.randint(0, earthHeight-1)
			j = random.randint(0, earthWidth-1)

			try:
				temp_location = bc.MapLocation(bc.Planet.Earth, i, j)
				if gc.can_begin_snipe(unit.id, temp_location):
					gc.begin_snipe(unit.id, temp_location)
					return

			except Exception as e:
				print('Error:', e)
				# use this to show where the error was
				traceback.print_exc()

class KnightClass(object):

	def javelin_attack(unit):

		location = unit.location
#Javelin opponents if it can
		possible_targets = gc.sense_nearby_units_by_team(location.map_location(), unit.ability_range(), enemy_team)
		for other in possible_targets:
			if gc.can_javelin(unit.id, other.id):
				gc.javelin(unit.id, other.id)
				return
			else:
				return

class RocketClass(object):

	def get_free_location(unit):
		return_value = random.choice(locations)
		return_location = bc.MapLocation(bc.Planet.Mars, return_value[0], return_value[1])
		return return_location

	def launch_rocket(unit):
		global total_number_rockets

		if gc.round() < data["Earth"]["second_phase"]["threshold"]:
			return

		garrison = unit.structure_garrison()

		if unit.id not in non_worker_in_rocket:
			return

		if len(garrison) > 2 and non_worker_in_rocket[unit.id] > 1:
			#print('prepare for launch')
			free_loc = RocketClass.get_free_location(unit)

			if gc.can_launch_rocket(unit.id, free_loc):
				#print('launched rocket!')
				#update_team_array(free_loc)
				gc.launch_rocket(unit.id, free_loc)
				total_number_rockets -= 1

	def unload_rocket(unit):
		garrison = unit.structure_garrison()
		if len(garrison) > 0:
			for d in directions:
				if gc.can_unload(unit.id, d):
					#print('unloaded a poulla!')
					gc.unload(unit.id, d)
		#else:
			#gc.disintegrate_unit(unit.id)

class FactoryClass(object):

	def unload_factory(unit):
		garrison = unit.structure_garrison()
		if len(garrison) > 0:
			for d in directions:
				if gc.can_unload(unit.id, d):
					#print('unloaded a poulla!')
					gc.unload(unit.id, d)

	def produce_unit(unit, product_type):
		if gc.can_produce_robot(unit.id, product_type):
			gc.produce_robot(unit.id, product_type)
			#print('produced a poulla!')

find_free_locations_in_Mars()

myWorkFlipM = 0
myWorkFlipE = 0

while True:
    # We only support Python 3, which means brackets around print()
	print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

	try:
		for current_unit in gc.my_units():

			if current_unit.location.is_in_space() or current_unit.location.is_in_garrison():
				continue

	############  MARS  ###########

			elif current_unit.location.is_on_planet(bc.Planet.Mars):
				if current_unit.unit_type == bc.UnitType.Worker:
					if myWorkFlip == 0: #Alternates between harvesting and replicating
						WorkerClass.harvest_karbonite(current_unit)

					elif myWorkFlip == 1:
						WorkerClass.replicate_worker(current_unit)

					myWorkFlip = (myWorkFlip + 1)%4

					GeneralActions.attack_bitch(current_unit, "Mars", "worker_attack")
					GeneralActions.move_bitch(current_unit, "Mars", "worker_move")

				if current_unit.unit_type == bc.UnitType.Rocket:
					RocketClass.unload_rocket(current_unit)

				if current_unit.unit_type == bc.UnitType.Knight:
					KnightClass.javelin_attack(current_unit)

					GeneralActions.attack_bitch(current_unit, "Mars", "knight_attack")
					GeneralActions.move_bitch(current_unit, "Mars", "knight_move")

				if current_unit.unit_type == bc.UnitType.Mage:
					MageClass.blink_attack_mars(current_unit)

					GeneralActions.attack_bitch(current_unit, "Mars", "mage_attack")
					GeneralActions.move_bitch(current_unit, "Mars", "mage_move")

				if current_unit.unit_type == bc.UnitType.Ranger:
					RangerClass.snipe_attack_mars(current_unit)

					GeneralActions.attack_bitch(current_unit, "Mars", "ranger_attack")
					GeneralActions.move_bitch(current_unit, "Mars", "ranger_move")

				if current_unit.unit_type == bc.UnitType.Healer:
					HealerClass.overcharge_attack(current_unit)

					HealerClass.heal_bitch(current_unit)
					GeneralActions.move_bitch(current_unit, "Mars", "healer_move")



	############  EARTH  ###########

			elif current_unit.location.is_on_planet(bc.Planet.Earth):

				phase_number = "third_phase"
				if gc.round() <= data["Earth"]["first_phase"]["threshold"]:
					phase_number = "first_phase"
				elif gc.round() <= data["Earth"]["second_phase"]["threshold"]:
					phase_number = "second_phase"

				if current_unit.unit_type == bc.UnitType.Worker:
					WorkerClass.complete_build(current_unit, bc.UnitType.Rocket)
					WorkerClass.complete_build(current_unit, bc.UnitType.Factory)

					GeneralActions.load_unit(current_unit)

					if myWorkFlipE == 0: #Alternates between harvesting, replicating, and building rockets and factories
						WorkerClass.harvest_karbonite(current_unit)

					elif myWorkFlipE == 1:
						WorkerClass.replicate_worker(current_unit)

					elif myWorkFlipE == 2:
						WorkerClass.build_blueprint(current_unit, bc.UnitType.Rocket)

					elif myWorkFlipE == 3:
						WorkerClass.build_blueprint(current_unit, bc.UnitType.Factory)

					elif myWorkFlipE == 4:
						WorkerClass.repair(current_unit)

					myWorkFlipE = (myWorkFlipE + 1)%7

					GeneralActions.attack_bitch(current_unit, "Earth", "worker_attack")
					GeneralActions.move_bitch(current_unit, "Earth", "worker_move")

				if current_unit.unit_type == bc.UnitType.Rocket:

					RocketClass.launch_rocket(current_unit)

				if current_unit.unit_type == bc.UnitType.Knight:
					GeneralActions.load_unit(current_unit)
					GeneralActions.move_towards_rocket(current_unit)

					KnightClass.javelin_attack(current_unit)

					GeneralActions.attack_bitch(current_unit, "Earth", "knight_attack")
					GeneralActions.move_bitch(current_unit, "Earth", "knight_move")

				if current_unit.unit_type == bc.UnitType.Mage:
					GeneralActions.load_unit(current_unit)
					GeneralActions.move_towards_rocket(current_unit)

					MageClass.blink_attack_earth(current_unit)

					GeneralActions.attack_bitch(current_unit, "Earth", "mage_attack")
					GeneralActions.move_bitch(current_unit, "Earth", "mage_move")

				if current_unit.unit_type == bc.UnitType.Ranger:
					GeneralActions.load_unit(current_unit)
					GeneralActions.move_towards_rocket(current_unit)

					RangerClass.snipe_attack_earth(current_unit)

					GeneralActions.attack_bitch(current_unit,"Earth", "ranger_attack")
					GeneralActions.move_bitch(current_unit, "Earth", "ranger_move")


				if current_unit.unit_type == bc.UnitType.Factory:
					FactoryClass.unload_factory(current_unit)
					if current_unit.is_factory_producing():
						continue

					FactoryClass.produce_unit(current_unit, bc.UnitType.Worker)

					FactoryClass.produce_unit(current_unit, bc.UnitType.Knight)

					FactoryClass.produce_unit(current_unit, bc.UnitType.Mage)

					FactoryClass.produce_unit(current_unit, bc.UnitType.Ranger)

					FactoryClass.produce_unit(current_unit, bc.UnitType.Healer)

				if current_unit.unit_type == bc.UnitType.Healer:
					GeneralActions.load_unit(current_unit)
					GeneralActions.move_towards_rocket(current_unit)

					HealerClass.overcharge_attack(current_unit)

					HealerClass.heal_bitch(current_unit)
					GeneralActions.move_bitch(current_unit, "Earth", "healer_move")


				if phase_number == "third_phase":
					if total_number_rockets == 0:
						total_number_rockets = -1
						#Set a new default to please the memer establishment


	except Exception as e:
		print('Error:', e)
		# use this to show where the error was
		traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
	gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
	sys.stdout.flush()
sys.stderr.flush()
