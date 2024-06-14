function get_unlocked_productivity_modules(player)
    local unlocked_productivity_modules = {}
    for _, rec in pairs(game.get_filtered_recipe_prototypes { { filter = "subgroup", subgroup = "module-productivity" } }) do
        if player.force.recipes[rec.name].enabled == true then
            table.insert(unlocked_productivity_modules, rec.name)
        end
    end
    return unlocked_productivity_modules
end

function get_unlocked_speed_modules(player)
    local unlocked_speed_modules = {}
    for _, rec in pairs(game.get_filtered_recipe_prototypes { { filter = "subgroup", subgroup = "module-speed" } }) do
        if player.force.recipes[rec.name].enabled == true then
            table.insert(unlocked_speed_modules, rec.name)
        end
    end
    return unlocked_speed_modules
end

function get_unlocked_beacons(player)
    local unlocked_beacons = {}
    for _, rec in pairs(game.get_filtered_recipe_prototypes { { filter = "subgroup", subgroup = "module" } }) do
        if player.force.recipes[rec.name].enabled == true then
            table.insert(unlocked_beacons, rec.name)
        end
    end
    return unlocked_beacons
end

function create_crafting_category_to_buildings_map(player)
    if global.players[player.index].crafting_category_selected_building == nil then
        global.players[player.index].crafting_category_selected_building = {}
    end
    local crafting_map = {}
    for _, entity in pairs(game.get_filtered_entity_prototypes { { filter = "crafting-machine" } }) do
        if player.force.recipes[entity.name] ~= nil and player.force.recipes[entity.name].enabled == true then
            for category, _ in pairs(entity.crafting_categories) do
                if crafting_map[category] == nil then
                    crafting_map[category] = {}
                end
                table.insert(crafting_map[category], entity.name)
            end
        end
    end

    --game.write_file("cats.json", game.table_to_json(crafting_map))
    return crafting_map
end

function get_buildings_per_recipe(player, recipes_summary)
    -- get recipes for productivity module
    local productivity_recipes = {}
    for _, rec_name in pairs(game.item_prototypes["productivity-module"].limitations) do
        productivity_recipes[rec_name] = true
    end
     -- get number of buildings
    local max_productivity_module = global.players[player.index].max_productivity_module
    local max_speed_module = global.players[player.index].max_speed_module
    local max_beacon = global.players[player.index].max_beacon
    local recipes_buildings = {}
    for rec_name, recipe_summary in pairs(recipes_summary) do
        -- building can be nil if it hasn't been unlocked yet
        local building_name = global.players[player.index].crafting_category_selected_building[recipe_summary.crafting_category]
        local building = game.entity_prototypes[building_name]
        if building == nil then
            -- building not researched yet
            recipes_buildings[rec_name] = { n_buildings = 0, building = BUILDING_NOT_RESEARCHED,
                                            items_per_second = recipe_summary.ips }
        else
            -- calculate how many buildings are needed to produce that recipe at desired throughput
            local r = game.recipe_prototypes[rec_name]
            local main_product = recipe_summary.main_product
            local productivity_bonus = 1
            local speed_bonus = 1

            if productivity_recipes[rec_name] ~= nil and max_productivity_module ~= nil then
                -- possible to use productivity modules
                local module_item = game.item_prototypes[max_productivity_module]
                productivity_bonus = 1 + module_item.module_effects.productivity.bonus * building.module_inventory_size
                speed_bonus = 1 + module_item.module_effects.speed.bonus * building.module_inventory_size
                if max_beacon then
                    local module_item = game.item_prototypes[max_speed_module]
                    local beacon_slots = game.entity_prototypes[max_beacon].module_inventory_size
                    speed_bonus = speed_bonus + (module_item.module_effects.speed.bonus * beacon_slots / 2)
                end
            elseif max_speed_module ~= nil then
                local module_item = game.item_prototypes[max_speed_module]
                speed_bonus = 1 + module_item.module_effects.speed.bonus * building.module_inventory_size
                if max_beacon then
                    local beacon_slots = game.entity_prototypes[max_beacon].module_inventory_size
                    speed_bonus = speed_bonus + (module_item.module_effects.speed.bonus * beacon_slots / 2)
                end
            end
            local items_per_second_per_building = productivity_bonus * main_product.amount / r.energy
            local n_buildings = math.ceil(recipe_summary.ips / (speed_bonus * building.crafting_speed * items_per_second_per_building))
            recipes_buildings[rec_name] = { n_buildings = n_buildings, building = building.name,
                                            items_per_second = recipe_summary.ips }
        end
    end
    return recipes_buildings
end