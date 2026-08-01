from internal.vector2 import Vector2


# World Configs
TARGET_FRAMERATE = 1/60
CANVAS_SIZE = Vector2(1200, 800)
SECTOR_SIZE = Vector2(50) # Size of each sector, used for physics and nutrients, one value makes both axes equal, lower values may be laggy
TEXT_COLOR = "white" # Color of the monitoring and alert text
ALERT_LIFETIME = 5 # How long the alerts in the top right last, in seconds

STARTING_PLANTS = 25
SECTOR_BLUR_LEVEL = 5 # How smoothed the base nutrient levels of the sectors are
SECTOR_REGEN_RATE = 0.1 # How fast each sector raises back to its base nutrient level
SECTOR_DECAY_RATE = 0.01 # How fast each sector lowers back to its base nutrient level
# Max and min precision for the area overlap estimation
MIN_AREA_CALC_PRECISION = 4
MAX_AREA_CALC_PRECISION = 8


# Plant Configs
OPTIMAL_PLANT_COLOR = (0, 200, 0) # Optimal color for plants to be, plants with higher values than this will get less nutrients, plants with lower values will get more but take constant damage
PLANT_NUTRIENT_EFFICIENCY = 2 # Multiplier on how many nutrients plants extract from the ground
SEED_DRAG = 0.25
SEED_DENSITY = 1.0
SEED_SIZE_FACTOR = 0.1
SEED_COST_FACTOR = 0.1
MUTATION_CHANCE = 0.25
MUTATION_FACTOR = 0.25 # Max change a single mutation can cause, multiplied by the max range of the trait being mutated
MUTATION_CENTER_WEIGHTING = 5 # Higher values = less extreme mutations


# Plant Genome Configs
MIN_PLANT_RADIUS = 5.0
MAX_PLANT_RADIUS = 50.0
MAX_GROWTH_SPEED = 5.0
MAX_SEED_SPEED = 100.0
MIN_LIFESPAN = 30.0
MAX_LIFESPAN = 300.0