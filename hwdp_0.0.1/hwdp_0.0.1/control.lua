---
--- Generated by EmmyLua(https://github.com/EmmyLua)
--- Created by obygi.
--- DateTime: 24.05.2024 00:39
---
---
---
require("lib_traverse")
require("lib_gui")
require("lib_buildings")

BUILDING_NOT_RESEARCHED = "building not researched, you fag!"

local function check_if_entity_prototype_maps_to_recipe(name)
    return not string.find(name, "-grounded") and not string.find(name, "-spaced")
end

local function initialize_global(player)
    global.players[player.index] = {}
    global.players[player.index].controls_active = true
    global.players[player.index].selected_ips = nil
    global.players[player.index].selected_recipe = nil
    global.players[player.index].recipes_buildings = nil
    global.players[player.index].byproducts = nil
    global.players[player.index].raw_resources = nil
    global.players[player.index].unlocked_productivity_modules = {}
    global.players[player.index].unlocked_speed_modules = {}
    global.players[player.index].unlocked_beacons = {}
    global.players[player.index].max_productivity_module = nil
    global.players[player.index].max_speed_module = nil
    global.players[player.index].max_beacon = nil
    global.players[player.index].crafting_category_building_map = {}
    global.players[player.index].crafting_category_selected_building = {}
    global.players[player.index].recipes_to_skip = {}
end

local function run_recipes(player)
    local controls_flow = player.gui.screen.main_frame.content_frame.controls_flow
    local recipe_name = controls_flow.choose_recipe.elem_value
    if recipe_name == nil then
        recipe_name = global.players[player.index].selected_recipe
    end

    local recipe_ips = controls_flow.ips_textfield.text

    -- persist search in global table and clear results
    global.players[player.index].selected_recipe = recipe_name
    global.players[player.index].selected_ips = recipe_ips
    global.players[player.index].recipes_buildings = nil
    global.players[player.index].byproducts = nil
    global.players[player.index].raw_resources = nil


    local raw_resources_per_second = {}
    local recipes_summary = {}
    local recipes_buildings = {}
    local byproducts = {}

    -- now retrieve recipe
    local recipe = player.force.recipes[recipe_name]
    traverse(
            player,
            recipe,
            recipe_ips,
            recipes_summary,
            raw_resources_per_second,
            byproducts,
            0,
            1
    )

    recipes_buildings = get_buildings_per_recipe(player, recipes_summary)
    -- persist results in global table
    global.players[player.index].recipes_buildings = recipes_buildings
    global.players[player.index].byproducts = byproducts
    global.players[player.index].raw_resources = raw_resources_per_second
    -- draw results
    draw_results(player.index)
end

script.on_init(function()
    global.players = {}
    for _, player in pairs(game.players) do
        initialize_global(player)
    end
end)

script.on_event(defines.events.on_player_created, function(event)
    local player = game.get_player(event.player_index)
    initialize_global(player)
end)

script.on_event(defines.events.on_player_removed, function(event)
    global.players[event.player_index] = nil
end)

script.on_event(defines.events.on_gui_selection_state_changed, function(event)
    local player = game.get_player(event.player_index)
    local selected_index = event.element.selected_index
    local item = event.element.items[selected_index]
    if event.element.name == "productivity_modules" then
        global.players[player.index].max_productivity_module = item
    elseif event.element.name == "speed_modules" then
        global.players[player.index].max_speed_module = item
    elseif event.element.name == "beacons" then
        global.players[player.index].max_beacon = item
    else
        -- buildings
        global.players[player.index].crafting_category_selected_building[event.element.name] = item
    end
end)

script.on_event("toggle_interface", function(event)
    -- Basically an entrypoint to the calculator. Consider moving setup to a separate function.
    local player = game.get_player(event.player_index)
    local prod = get_unlocked_productivity_modules(player)
    local speed = get_unlocked_speed_modules(player)
    local beacons = get_unlocked_beacons(player)
    local crafting_to_buildings_map = create_crafting_category_to_buildings_map(player)

    for category, buildings in pairs(crafting_to_buildings_map) do
        if global.players[player.index].crafting_category_selected_building[category] == nil then
            global.players[player.index].crafting_category_selected_building[category] = buildings[#buildings]
        end
    end

    global.players[player.index].unlocked_productivity_modules = prod
    global.players[player.index].unlocked_speed_modules = speed
    global.players[player.index].unlocked_beacons = beacons
    global.players[player.index].crafting_category_building_map = crafting_to_buildings_map
    toggle_interface(player)
end)

script.on_event(defines.events.on_gui_closed, function(event)
    if event.element and event.element.name == "main_frame" then
        local player = game.get_player(event.player_index)
        toggle_interface(player)
    end
end)

script.on_event(defines.events.on_gui_click, function(event)
    if event.element.name == "run_recipes" then
        local player = game.get_player(event.player_index)
        global.players[player.index].recipes_to_skip = {}
        run_recipes(player)
    end
end)


script.on_event(defines.events.on_gui_checked_state_changed, function(event)
    local player = game.get_player(event.player_index)
    local recipe_name = event.element.name
    if global.players[player.index].recipes_to_skip == nil then
        global.players[player.index].recipes_to_skip = {}
    end
    global.players[player.index].recipes_to_skip[recipe_name] = true
    run_recipes(player)
end)