import json
from enum import Enum
from math import ceil
from typing import Optional
from pydantic import BaseModel, field_validator
from colorama import Fore
from colorama import Style
from factorio_dir import pth

RESOURCE = "laser-turret"
ITEMS_PER_SECOND = 1 / 10

LINE_WIDTH = 100

#####################################
#    H   H  W   W  DDDD   PPPP      #
#    H   H  W   W  D   D  P   P     #
#    HHHHH  W W W  D   D  PPPP      #
#    H   H  W W W  D   D  P         #
#    H   H   W W   DDDD   P         #
#####################################

FORBIDDEN_ITEMS = [
    "equipment-gantry-insert",
    "equipment-gantry-remove",
    "fuel-processing",
    "se-energy-transmitter-emitter-fixed",
    "se-energy-transmitter-injector-fixed",
]

alternative_keys = {
    "electronic-circuit": "electronic-circuit-stone",
    "petroleum-gas": "basic-oil-processing",
    "glass": "glass-from-sand",
    "sand": "sand-from-stone",
    "solid-fuel": "solid-fuel-from-petroleum-gas",
    "light-oil": "advanced-oil-processing",
    "heavy-oil": "oil-processing-heavy"
}


class Resource(Enum):
    IRON = "iron-ore"
    COPPER = "copper-ore"
    COAL = "coal"
    OIL = "crude-oil"
    STONE = "stone"
    WATER = "water"
    URANIUM = "uranium-ore"
    VULCANITE = "se-vulcanite"
    VULCANITE_ENRICHED = "se-vulcanite-enriched"
    IRIDIUM_PLATE = "se-iridium-plate"
    BIO_SLUDGE = "se-bio-sludge"
    NUTRIENT_GET = "se-nutrient-gel"
    SATELLITE_TELEMETRY = "se-satellite-telemetry"

    def __str__(self):
        return self.value


class Building(Enum):
    ASSEMBLER = "crafting"
    FURNACE = "smelting"
    CHEMICAL_PLANT = "chemistry"
    OIL_REFINERY = "oil-processing"
    FUEL_REFINERY = "fuel-refining"
    EQUIPMENT_CHANGE = "equipment-change"
    CENTRIFUGE = "centrifuging"
    SPACE_MANUFACTURING = "space-manufacturing"
    ROCKET_BUILDING = "rocket-building"
    SPACE_COLLIDER = "space-collider"
    SPACE_MATERIALISATION = "space-materialisation"
    ARCOSPHERE = "arcosphere"
    SPACE_ASTROMETRICS = "space-astrometrics"
    SPACE_SUPERCOMPUTING = "space-supercomputing"
    SPACE_MECHANICAL = "space-mechanical"
    SPACE_THERMODYNAMICS = "space-thermodynamics"
    SPACE_BIOCHEMICAL = "space-biochemical"
    SPACE_GENETICS = "space-genetics"
    SPACE_ELECTROMAGNETICS = "space-electromagnetics"
    HARD_RECYCLING = "hard-recycling"
    SPACE_GROWTH = "space-growth"
    SPACE_GRAVIMETRICS = "space-gravimetrics"
    SPACE_DECONTAMINATION = "space-decontamination"
    DELIVERY_CANNON = "delivery-cannon"
    DELIVERY_CANNON_WEAPON = "delivery-cannon-weapon"
    NEXUS = "nexus"
    LIFE_SUPPORT = "lifesupport"
    SPACE_LASER = "space-laser"
    SPACE_ACCELERATOR = "space-accelerator"
    SPACE_OBSERVATION = "space-observation"
    SPACE_PLASMA = "space-plasma"
    PULVERISING = "pulverising"
    SPACE_RADIATION = "space-radiation"
    SPACE_ELEVATOR = "space-elevator"
    BIG_TURBINE = "big-turbine"
    SPACESHIP_ANTIMATTER_ENGINE = "spaceship-antimatter-engine"
    SPACESHIP_ION_ENGINE = "spaceship-ion-engine"
    SPACESHIP_ROCKET_ENGINE = "spaceship-rocket-engine"
    CONDENSER_TURBINE = "condenser-turbine"
    MELTING = "melting"
    CASTING = "casting"
    ELECTRIC_BOILING = "se-electric-boiling"
    SPACE_RADIATOR = "space-radiator"
    SPACE_HYPERCOOLING = "space-hypercooling"

    def __str__(self):
        return self.name


building_speed_map = {Building.FURNACE: 2, Building.ASSEMBLER: 0.75}


class Ingredient(BaseModel):
    name: str
    type: str
    amount: Optional[int] = None


class Product(Ingredient):
    probability: float
    amount_min: Optional[int] = None
    amount_max: Optional[int] = None


class Recipe(BaseModel):
    name: str
    building: Building
    products: dict[str, Product]
    ingredients: list[Ingredient]
    spid: float

    @field_validator("building", mode="before")
    @classmethod
    def validate_building(cls, b: str, _):
        if b == "kiln":
            return "smelting"
        elif "crafting" in b:
            return "crafting"
        elif "space-supercomputing" in b:
            return "space-supercomputing"
        elif "space-observation" in b:
            return "space-observation"
        elif b == "core-fragment-processing":
            return "pulverising"
        else:
            return b


def get_n_buildings(recipe: Recipe, amount_per_second: float, ) -> int:
    speed_modifier = building_speed_map.get(recipe.building, None) or 1
    building_items_per_second = recipe.products[recipe.name].amount / recipe.spid
    return ceil(amount_per_second / (speed_modifier * building_items_per_second))


def build_line(recurrence_level: int, line: str) -> str:
    indent = (" " * 10 + "|") * recurrence_level
    new_line = indent + line + " " * LINE_WIDTH
    return new_line[:LINE_WIDTH - 1] + '|\n'


def traverse(
        recipe: Recipe,
        amount_per_second: float,
        result: list[str],
        recurrence_level: int = 0,
):
    recipe_amount = recipe.products[recipe.name].amount
    n_buildings = get_n_buildings(recipe, amount_per_second)
    buildings_total[recipe.building.value] += n_buildings
    if recurrence_level > 50:
        print("#############################################")
        print(recipe.name)
        print("ingredients")
        for i in recipe.ingredients:
            print(i.name)
    # ==============PRINTS

    result.append(build_line(recurrence_level, f"{Fore.LIGHTWHITE_EX}{recurrence_level}" * 200))
    # result.append(build_line(recurrence_level, f"{recurrence_level}" * 200))
    # ^tu się coś brzydko pindoli ;(
    result.append(build_line(recurrence_level,
                             f"{Fore.YELLOW}Recipe:{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}{recipe.name}{Style.RESET_ALL}"))
    result.append(build_line(recurrence_level,
                             f"{Fore.YELLOW}Required amount per second:{Style.RESET_ALL} {Fore.GREEN}{round(amount_per_second, 3)}{Style.RESET_ALL}"))
    result.append(build_line(recurrence_level,
                             f"{Fore.YELLOW}Item crafting time:{Style.RESET_ALL} {Fore.RED}{round(recipe.spid / (building_speed_map.get(recipe.building, None) or 1), 3)} seconds{Style.RESET_ALL}"))
    result.append(build_line(recurrence_level,
                             f"{Fore.YELLOW}Crafted in:{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}{n_buildings} * {recipe.building}{Style.RESET_ALL}"))
    result.append(build_line(recurrence_level, "=" * 20 + "Inputs Needed" + "=" * 200))
    # >>>>>>>>>>>>>>PRINTS

    for ing in recipe.ingredients:
        ingredient_amount_per_second = ing.amount * amount_per_second / recipe_amount
        ing_recipe = recipes.get(ing.name, None)

        if ing_recipe and ing_recipe.name != recipe.name:
            traverse(
                ing_recipe,
                ingredient_amount_per_second,
                result,
                recurrence_level + 1,
            )
        else:
            raw_resources[ing.name] += ingredient_amount_per_second
            result.append(build_line(recurrence_level, f"{ing.name}: {ingredient_amount_per_second:.3f}"))


def fix_file(raw_json: dict):
    for k, v in alternative_keys.items():
        raw_json[k] = raw_json[v]
        raw_json[k]["name"] = k
        del raw_json[v]


if __name__ == "__main__":
    raw_resources = {k.value: 0 for k in Resource}
    buildings_total = {b.value: 0 for b in Building}
    with open(pth) as f:
        recipes = {}
        raw = json.load(f)
        fix_file(raw)
        for k, v in raw.items():
            if k in FORBIDDEN_ITEMS or v["building"] == "fixed-recipe":
                continue
            recipes[k] = Recipe.model_validate(v)

        result_orig = []
        r = recipes[RESOURCE]
        traverse(r, ITEMS_PER_SECOND, result_orig)
        for k, v in raw_resources.items():
            raw_resources[k] = round(v, 3)
        print({k: v for k, v in raw_resources.items() if v > 0})
        print({k: v for k, v in buildings_total.items() if v > 0})
        print(''.join(result_orig))
