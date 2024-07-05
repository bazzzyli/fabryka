panel_output = 60
accumulator_capacity = 5000
cycle_duration_seconds = 7.12 * 60
solar_efficiency = 112

ratio = 0.168 * (panel_output / accumulator_capacity) * cycle_duration_seconds * (solar_efficiency / 100)
print(ratio)