import json
from enum import Enum
from math import ceil
from typing import Optional

from colorama import Fore

from pydantic import BaseModel, field_validator

from factorio_dir import pth


def building_speed(base_speed: float, n_modules: int) -> float:
    return base_speed * (1 + n_modules * SPEED_MODULE_PERCENTS)


RESOURCE = "utility-science-pack"
ITEMS_PER_SECOND = 1
SPEED_MODULE_PERCENTS = 0.3
FORMATTING_NAME = "se-formatting-1"
BUILDING_SPEED_MAP = {
    "smelting": building_speed(base_speed=4, n_modules=5),
    "crafting": building_speed(base_speed=1.25, n_modules=4),
    "space-crafting": building_speed(base_speed=1.25, n_modules=4),
    "space-supercomputing": building_speed(base_speed=1, n_modules=2),
    "space-manufacturing": building_speed(base_speed=10, n_modules=6),
    "space-biochemical": building_speed(base_speed=4, n_modules=4),
    "space-radiation": building_speed(base_speed=1, n_modules=2),
    "space-decontamination": building_speed(base_speed=2, n_modules=4),
    "pulverising": building_speed(base_speed=2, n_modules=4),
    "oil-processing": building_speed(base_speed=1, n_modules=3),
    "chemistry": building_speed(base_speed=1, n_modules=3)
}

#####################################
#    H   H  W   W  DDDD   PPPP      #
#    H   H  W   W  D   D  P   P     #
#    HHHHH  W W W  D   D  PPPP      #
#    H   H  W W W  D   D  P         #
#    H   H   W W   DDDD   P         #
#####################################

line_length_formatting = 100

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
    "se-space-coolant-hot": "se-space-coolant",
    "se-data-storage-substrate-cleaned": "se-data-storage-substrate-cleaned-chemical"
}

alternative_products_keys = {
    "se-formatting-1": "se-empty-data"
}

RECIPES_WITH_RECYCLING_TO_SKIP = {"se-space-coolant-hot"}


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
    SPACE_ASSEMBLER = "space-crafting"
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
    main_product: Optional[Product] = None

    @field_validator("building", mode="before")
    @classmethod
    def validate_building(cls, b: str, _):
        if b == "kiln":
            return "smelting"
        elif "crafting" in b and "space" not in b:
            return "crafting"
        elif "space-supercomputing" in b:
            return "space-supercomputing"
        elif "space-observation" in b:
            return "space-observation"
        elif b == "core-fragment-processing":
            return "pulverising"
        else:
            return b


class RawResourcesResult(BaseModel):
    resources: dict[str, float]

    def __str__(self):
        lines = [format_header("Raw Resources")]
        for k, v in self.resources.items():
            lines.append(f"{k}: {round(v, 2)}")
        return "\n".join(lines)


class RecipesBuildingsResult(BaseModel):
    recipes_buildings: dict[str, dict]

    def __build_line__(self, k, v, fore):
        return f"{fore}{k}: {Fore.RESET}{v['n_buildings']} {Fore.YELLOW}{v['building']}, {Fore.RESET}items per second: {Fore.YELLOW}{round(v['items_per_second'], 2)}"

    def __str__(self):
        lines = [format_header("Buildings Per Recipe")]
        space_recipes = {}
        normal_recipes = {}
        for k, v in self.recipes_buildings.items():
            if "SPACE" in v["building"]:
                space_recipes[k] = v
            else:
                normal_recipes[k] = v
        lines.append(Fore.GREEN + "Planet/Moon:")
        for k, v in normal_recipes.items():
            lines.append(self.__build_line__(k, v, Fore.GREEN))

        lines.append(Fore.LIGHTBLUE_EX + "Space:")
        for k, v in space_recipes.items():
            lines.append(self.__build_line__(k, v, Fore.LIGHTBLUE_EX))
        return "\n".join(lines)


class BuildingsTotalResult(BaseModel):
    buildings_total: dict[str, int]

    def __str__(self):
        lines = [format_header("Buildings Total")]
        space_buildings = {}
        normal_buildings = {}
        for k, v in self.buildings_total.items():
            if "SPACE" in k:
                space_buildings[k] = v
            else:
                normal_buildings[k] = v

        lines.append(Fore.GREEN + "Planet/Moon: ============")
        for k, v in normal_buildings.items():
            lines.append(f"{Fore.GREEN}{k}: {Fore.RESET}{round(v, 2)}")
        lines.append(Fore.LIGHTBLUE_EX + "Space: ===================")
        for k, v in space_buildings.items():
            lines.append(f"{Fore.LIGHTBLUE_EX}{k}: {Fore.RESET}{round(v, 2)}")
        return "\n".join(lines)


class ByproductsResult(BaseModel):
    byproducts: dict[str, float]

    def __str__(self):
        lines = [format_header("Byproducts")]
        for k, v in self.byproducts.items():
            lines.append(Fore.RED + f"{k}: {round(v, 2)}")
        return "\n".join(lines)


def get_n_buildings(recipe: Recipe, amount_per_second: float) -> int:
    speed_modifier = BUILDING_SPEED_MAP.get(recipe.building.value, None) or 1
    building_items_per_second = recipe.products[recipe.name].amount / recipe.spid
    return ceil(amount_per_second / (speed_modifier * building_items_per_second))


def traverse(
        recipe: Recipe,
        amount_per_second: float,
        recipes_per_second: dict[str, float],
        raw_resources_per_second: dict[str, float],
        byproducts_per_second: dict[str, float],
        recipes: dict[str, Recipe]
):
    main_product = recipe.main_product
    if main_product is None:
        try:
            main_product = recipe.products[recipe.name]
        except KeyError:
            # try alternative products keys
            main_product = recipe.products[alternative_products_keys[recipe.name]]
    recipe_amount = main_product.amount * main_product.probability

    try:
        recipes_per_second[recipe.name] += amount_per_second
    except KeyError:
        recipes_per_second[recipe.name] = amount_per_second

    for p in recipe.products.values():
        if p.name != main_product.name:
            product_ps = amount_per_second * p.amount * p.probability / recipe_amount
            try:
                byproducts_per_second[p.name] += product_ps
            except KeyError:
                byproducts_per_second[p.name] = product_ps

    for ing in recipe.ingredients:
        ingredient_amount_per_second = ing.amount * amount_per_second / recipe_amount
        ing_recipe = recipes.get(ing.name, None)

        if ing_recipe and ing_recipe.name not in RECIPES_WITH_RECYCLING_TO_SKIP:
            traverse(
                ing_recipe,
                ingredient_amount_per_second,
                recipes_per_second,
                raw_resources_per_second,
                byproducts_per_second,
                recipes
            )
        else:
            raw_resources_per_second[ing.name] += ingredient_amount_per_second


def fix_file(raw_json: dict):
    for k, v in alternative_keys.items():
        raw_json[k] = raw_json[v]
        raw_json[k]["name"] = k
        del raw_json[v]


def remove_zeros_from_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v > 0}


def format_header(header_name: str) -> str:
    return Fore.LIGHTWHITE_EX + "#" * int(line_length_formatting / 2) + f"   {header_name}:   " + "#" * int(
        line_length_formatting / 2)


def run(resource: str, required_items_per_second: float):
    raw_resources = {k.value: 0 for k in Resource}
    recipes_ips_total = {}
    recipes_buildings = {}
    byproducts = {}
    with open(pth) as f:
        recipes = {}
        raw = json.load(f)
    fix_file(raw)
    for k, v in raw.items():
        if k in FORBIDDEN_ITEMS or v["building"] == "fixed-recipe":
            continue
        recipes[k] = Recipe.model_validate(v)
    r = recipes[resource]
    traverse(r, required_items_per_second, recipes_ips_total, raw_resources, byproducts, recipes)

    # TODO maybe move recycling to a separate function. Implement auto-recycling? (try to get through the products back to the ingredients)
    # Fix weird SE recycling / enrichment recipes
    # MUCHO IMPORTANTE! Fix coolant last as some recycling recipes use it!
    if "se-junk-data" in byproducts:
        junk_cards_ps = byproducts["se-junk-data"]
        formatting_recipe = recipes[FORMATTING_NAME]
        formatting_recipe.products[FORMATTING_NAME] = formatting_recipe.products["se-empty-data"]
        blank_cards_amount = junk_cards_ps * formatting_recipe.products["se-empty-data"].probability
        recipes_ips_total["se-empty-data"] -= blank_cards_amount
        recipes_ips_total[FORMATTING_NAME] = junk_cards_ps

    if Resource.SE_SPACE_COOLANT_HOT.value in raw_resources.keys():
        space_coolant_warm_ps = recipes_ips_total["se-space-coolant-warm"]
        hot_coolant_shortage = raw_resources[Resource.SE_SPACE_COOLANT_HOT.value] - space_coolant_warm_ps
        traverse(
            recipes["se-space-coolant-hot"],
            hot_coolant_shortage,
            recipes_ips_total,
            raw_resources,
            byproducts,
            recipes
        )

    # calculate buildings total
    buildings_total = {b.name: 0 for b in Building}
    for r, v in recipes_ips_total.items():
        recipe = recipes.get(r)
        n_buildings = get_n_buildings(recipe, v)
        buildings_total[recipe.building.name] += n_buildings
        recipes_buildings[recipe.name] = {"n_buildings": n_buildings, "building": recipe.building.name,
                                          "items_per_second": v}

    return (
        RawResourcesResult(resources=remove_zeros_from_dict(raw_resources)),
        RecipesBuildingsResult(recipes_buildings=recipes_buildings),
        BuildingsTotalResult(buildings_total=remove_zeros_from_dict(buildings_total)),
        ByproductsResult(byproducts=byproducts)
    )


if __name__ == "__main__":
    raw, recipes, total, byproduct = run(resource=RESOURCE, required_items_per_second=ITEMS_PER_SECOND)
    print(raw)
    print(recipes)
    print(total)
    print(byproduct)
