from math import floor, ceil

# SPACE MANA
stacks = {
    "processing_unit": {"proportion": 20, "stack_size": 200},
    "fuel": {"proportion": 20, "stack_size": 10},
    "electric_motor": {"proportion": 40, "stack_size": 50},
    "lds": {"proportion": 20, "stack_size": 50},
    "steel": {"proportion": 40, "stack_size": 100},
    "stone": {"proportion": 100, "stack_size": 50}
}

# stacks = {
#     "module": {"proportion": 1, "stack_size": 50},
#     "ingot": {"proportion": 5, "stack_size": 50}
# }

all_stacks = sum(v["proportion"] / v["stack_size"] for v in stacks.values())
print(all_stacks)

all_slots = 0
required_slots = 480
for k, v in stacks.items():
    slots = ceil(required_slots * ((v["proportion"] / v["stack_size"]) / all_stacks))
    print(f"{k}: stacks: {round(slots)}, items: {round(slots * v['stack_size'])}")
    all_slots += slots

print(all_slots)

