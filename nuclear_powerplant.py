
'''
Outer reactors yield 120MW each (200% neighbor bonus).
Inner reactors yield 160MW each (300% neighbor bonus).

That results in 12 and 16 heat exchanges per reactor respectively.
Each Heat exchanger produces 103 steam/s, each turbine consumes
60 steam/s (at maximum power usage).

That means that we need 20 and 27 turbines per reactor respectively.

Each heat exchanger line needs 1236 and 1648 water/s respectively.

It's possible to provide water by one pipeline to 3 reactors using
the "pump->pipe" pipeline configuration.

As for the steam output, it's the same as the water input, so we can get away
with the "pump->4*pipe" pipeline configuration for each exchanger line
(1909 water/s throughput).

For some reason, reactors won't cool down below 504 C.
'''

tank_capacity = 25000
turbine_consumption = 60
inner_turbines = 27
outer_turbines = 20
cell_time = 200

n_tanks_before_heat_up_outer = cell_time / (tank_capacity / (outer_turbines*turbine_consumption))

print(n_tanks_before_heat_up_outer)


