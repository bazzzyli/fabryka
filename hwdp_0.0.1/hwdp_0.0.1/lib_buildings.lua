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
    --player = game.player
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