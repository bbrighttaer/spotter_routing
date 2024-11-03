from config.env import env

# Maximum range the vehicle can travel (500 miles)
MAXIMUM_RANGE_IN_METERS = env.int("MAXIMUM_RANGE_IN_METERS")

METERS_PER_GALLON = env.float("METERS_PER_GALLON")

DEFAULT_PRICE_PER_LITER = env.float("DEFAULT_PRICE_PER_LITER")
