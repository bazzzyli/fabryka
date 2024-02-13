import json
from enum import Enum
from math import ceil
from typing import Optional
from pydantic import BaseModel, field_validator
from colorama import Fore
from factorio_dir import pth

RESOURCE = "utility-science-pack"
ITEMS_PER_SECOND = 1

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
    # "petroleum-gas": "advanced-oil-processing",
    "glass": "glass-from-sand",
    "sand": "sand-from-stone",
    "solid-fuel": "solid-fuel-from-petroleum-gas",
    "light-oil": "advanced-oil-processing",
    "heavy-oil": "oil-processing-heavy",
    "se-space-coolant-warm": "se-radiating-space-coolant-normal",
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
    CRYONITE = "se-cryonite"
    STEAM = "steam"
    SE_SPACE_COOLANT_HOT = "se-space-coolant-hot"

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


building_speed_map = {Building.FURNACE: 2, Building.ASSEMBLER: 2.75}


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


def get_n_buildings(recipe: Recipe, amount_per_second: float, product_name: Optional[str] = None) -> int:
    if not product_name:
        product_name = recipe.name
    speed_modifier = building_speed_map.get(recipe.building, None) or 1
    building_items_per_second = recipe.products[product_name].amount / recipe.spid
    return ceil(amount_per_second / (speed_modifier * building_items_per_second))


def build_line(recurrence_level: int, lines: list[tuple[str, str]]) -> str:
    """
    Build the line using formatted substrings.
    First item of the tuple is formatting string, second is content.
    """
    text_only_len = sum(len(x[1]) for x in lines)
    if len(lines) > 1:
        formatted_line = f"{Fore.RESET}".join(f"{x[0]}{x[1]}" for x in lines) + Fore.RESET
    else:
        x = lines[0]
        formatted_line = f"{Fore.RESET}{x[0]}{x[1]}{Fore.RESET}"
    line_length_including_formatting = LINE_WIDTH + len(formatted_line) - text_only_len
    indent = (" " * 10 + "|") * recurrence_level
    new_line = indent + formatted_line + " " * (line_length_including_formatting)
    return new_line[:line_length_including_formatting - 1] + f'|{Fore.RESET}\n'


def traverse(
        recipe: Recipe,
        amount_per_second: float,
        result: list[str],
        recurrence_level: int = 0,
):
    product_name = None
    if recipe.name == "se-space-coolant":
        product_name = "se-space-coolant-hot"
        recipe_amount = recipe.products["se-space-coolant-hot"].amount
    else:
        product_name = None
        recipe_amount = recipe.products[recipe.name].amount
    n_buildings = get_n_buildings(recipe, amount_per_second, product_name)
    buildings_total[recipe.building.value] += n_buildings
    try:
        recipes_total[recipe.name] += amount_per_second
    except KeyError:
        recipes_total[recipe.name] = amount_per_second

    if recurrence_level > 50:
        # FIXME this is for debug only, find a solution to work with cyclical graphs
        print("#############################################")
        print(recipe.name)
        print("ingredients")
        for i in recipe.ingredients:
            print(i.name)
    # ==============PRINTS

    result.append(build_line(recurrence_level, [(Fore.LIGHTWHITE_EX, f"{recurrence_level}" * 200)]))
    result.append(build_line(recurrence_level, [(Fore.YELLOW, "Recipe: "), (Fore.LIGHTMAGENTA_EX, f"{recipe.name}")]))
    result.append(build_line(recurrence_level, [(Fore.YELLOW, f"Required amount per second: "),
                                                (Fore.GREEN, f"{round(amount_per_second, 3)}")]))
    result.append(build_line(recurrence_level,
                             [(Fore.YELLOW, f"Item crafting time: "), (Fore.RED,
                                                                       f"{round(recipe.spid / (building_speed_map.get(recipe.building, None) or 1), 3)} seconds")]))
    result.append(build_line(recurrence_level,
                             [(Fore.YELLOW, f"Crafted in: "),
                              (Fore.LIGHTCYAN_EX, f"{n_buildings} * {recipe.building}")]))
    result.append(build_line(recurrence_level, [(Fore.LIGHTWHITE_EX, "=" * 20 + "Inputs Needed" + "=" * LINE_WIDTH)]))
    # >>>>>>>>>>>>>>PRINTS

    for ing in recipe.ingredients:
        ingredient_amount_per_second = ing.amount * amount_per_second / recipe_amount
        if ing.name == "se-space-coolant-warm":
            coolant_ps[ing.name] += ingredient_amount_per_second
            # continue

        ing_recipe = recipes.get(ing.name, None)

        if ing_recipe and ing_recipe.name != recipe.name:
            traverse(
                ing_recipe,
                ingredient_amount_per_second,
                result,
                recurrence_level + 1,
            )
        else:
            try:
                raw_resources[ing.name] += ingredient_amount_per_second
            except KeyError as e:
                # DEBUG
                print("HWDP!")
                print(recipe)
                for k,v in recipe.model_dump().items():
                    print(f"{k}: {v}")
                raise e
            result.append(
                build_line(recurrence_level, [(Fore.LIGHTCYAN_EX, f"{ing.name}: {ingredient_amount_per_second:.3f}")]))

    for p in recipe.products:
        if p == "se-space-coolant-warm":
            recipe = recipes[p]
            prod_key = "se-radiating-space-coolant-normal"

# def traverse_coolant(recipes_dict: dict[str, Recipe], coolant_per_second: float):



def fix_file(raw_json: dict):
    for k, v in alternative_keys.items():
        raw_json[k] = raw_json[v]
        raw_json[k]["name"] = k
        # if v != "advanced-oil-processing":
        #     del raw_json[v]
        del raw_json[v]


if __name__ == "__main__":
    raw_resources = {k.value: 0 for k in Resource}
    buildings_total = {b.value: 0 for b in Building}
    recipes_ips_total = {}
    recipes_total = {}
    coolant_ps = {"se-space-coolant-warm": 0}
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
        print("=" * 100)
        print("RAW RESOURCES per second:")
        for k, v in raw_resources.items():
            raw_resources[k] = round(v, 3)
        print({k: v for k, v in raw_resources.items() if v > 0})

        print("=" * 100)
        print("Buildings total:")
        print({k: v for k, v in buildings_total.items() if v > 0})
        print("=" * 100)
        print("Buildings per recipe:")
        for i in recipes_total.items():
            print(i)
        print("=" * 100)
        print("Recycling Recipes: ")
        if Resource.SE_SPACE_COOLANT_HOT.value in raw_resources.keys():
            space_coolant_warm_ps = recipes_total["se-space-coolant-warm"]
            hot_coolant_shortage = raw_resources[Resource.SE_SPACE_COOLANT_HOT.value] - space_coolant_warm_ps
            result_orig.append("\n"*5)
            result_orig.append("RAW COOLANT: \n\n\n")
            traverse(recipes["se-space-coolant"], hot_coolant_shortage, result_orig, recurrence_level=1)
        print("Recipes:")
        print(''.join(result_orig))
