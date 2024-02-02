req = 100
light_to_pet = 2 / 3

ref = (30 + 70 * 2 / 3) / 5

print(req / ref)

stacks = {
    "processing_unit": {"proportion": 20, "stack_size": 200},
    "belt": {"proportion": 40, "stack_size": 100},
    "fuel": {"proportion": 20, "stack_size": 10},
    "water": {"proportion": 4, "stack_size": 10},
    "electric_motor": {"proportion": 40, "stack_size": 50},
    "lds": {"proportion": 20, "stack_size": 50},
    "steel": {"proportion": 40, "stack_size": 100},
    "lube": {"proportion": 4, "stack_size": 10},
    "red": {"proportion": 100, "stack_size": 200},
    "green": {"proportion": 100, "stack_size": 200},
    "black": {"proportion": 100, "stack_size": 200},
    "blue": {"proportion": 100, "stack_size": 200},
    "orange": {"proportion": 100, "stack_size": 200},
    "stone": {"proportion": 100, "stack_size": 50}
}

all_stacks = sum(v["proportion"] / v["stack_size"] for v in stacks.values())
print(all_stacks)

all_slots = 0
for k, v in stacks.items():
    slots = 480 * ((v["proportion"] / v["stack_size"]) / all_stacks)
    print(f"{k}: stacks: {round(slots)}, items: {round(slots * v['stack_size'])}")
    all_slots += slots

print(all_slots)

