from config.env import env

# Maximum range the vehicle can travel (500 miles)
MAXIMUM_RANGE_IN_METERS = env.int("MAXIMUM_RANGE_IN_METERS")

# The distance after which refueling is desired
REFUELING_RANGE_IN_METERS = env.int("REFUELING_RANGE_IN_METERS")
