local function create_results_pane_tabs(player_index)
    local player = game.get_player(player_index)
    local results_pane = player.gui.screen.main_frame.result_frame.results_pane

    local recipes_buildings_tab = results_pane.add { type = "tab", name = "recipes_tab", caption = "buildings per recipe" }
    local recipes_buildings_flow = results_pane.add { type = "scroll-pane", name = "recipes_flow", direction = "vertical" }
    results_pane.add_tab(recipes_buildings_tab, recipes_buildings_flow)

    local raw_resources_tab = results_pane.add { type = "tab", name = "raw_resources_tab", caption = "raw resources" }
    local raw_resources_flow = results_pane.add { type = "scroll-pane", name = "raw_resources_flow" }
    results_pane.add_tab(raw_resources_tab, raw_resources_flow)

    local byproducts_tab = results_pane.add { type = "tab", name = "byproducts_tab", caption = "byproducts" }
    local byproducts_flow = results_pane.add { type = "scroll-pane", name = "byproducts_flow" }
    results_pane.add_tab(byproducts_tab, byproducts_flow)
end

function build_interface(player)
    local player_global = global.players[player.index]
    local screen_element = player.gui.screen
    local main_frame = screen_element.add { type = "frame", name = "main_frame", caption = "jebać leszczy" }
    main_frame.style.size = { 800, 1000 }

    player.opened = main_frame

    local content_frame = main_frame.add { type = "frame", name = "content_frame", direction = "vertical", style = "content_frame" }
    local controls_flow = content_frame.add { type = "flow", name = "controls_flow", direction = "vertical", style = "controls_flow" }

    -- get persisted search, if any
    local recipe_name = global.players[player.index].selected_recipe
    local recipe_ips = global.players[player.index].selected_ips or 0

    -- search components
    controls_flow.add { type = "line" }
    controls_flow.add { type = "label", caption = "Choose a recipe:" }
    controls_flow.add { type = "choose-elem-button", name = "choose_recipe", elem_type = "recipe", elem_value = recipe_name }--, elem_filters={{filter="enabled"}}}
    controls_flow.add { type = "line" }
    controls_flow.add { type = "label", caption = "Required items per second:" }
    controls_flow.add { type = "textfield", name = "ips_textfield", text = tostring(recipe_ips), numeric = true, allow_decimal = true, allow_negative = false, style = "controls_textfield", enabled = player_global.controls_active }
    controls_flow.add { type = "line" }
    controls_flow.add { type = "button", name = "run_recipes", caption = "hwdp" }
    controls_flow.add { type = "line" }

    -- results components
    local result_frame = main_frame.add { type = "frame", name = "result_frame", style = "content_frame", caption = "results:" }
    result_frame.add { type = "tabbed-pane", name = "results_pane" }
    create_results_pane_tabs(player.index)

end

function draw_results(player_index)
    local player = game.get_player(player_index)
    local recipes_buildings = global.players[player.index].recipes_buildings
    local byproducts = global.players[player.index].byproducts
    local raw_resources = global.players[player.index].raw_resources

    local results_pane = player.gui.screen.main_frame.result_frame.results_pane
    results_pane.clear()
    create_results_pane_tabs(player_index)

    local recipes_flow = results_pane.recipes_flow
    local raw_resources_flow = results_pane.raw_resources_flow
    local byproducts_flow = results_pane.byproducts_flow

    -- recipes
    if recipes_buildings ~= nil then
        for recipe_name, v in pairs(recipes_buildings) do
            local single_recipe_flow = recipes_flow.add { type = "flow", direction = "horizontal" }
            single_recipe_flow.add { type = "sprite", sprite = "recipe/" .. recipe_name }
            single_recipe_flow.add { type = "label", caption = game.recipe_prototypes[recipe_name].localised_name }
            single_recipe_flow.add { type = "label", caption = string.format("%.2f ips", tostring(v.items_per_second)) }
            single_recipe_flow.add { type = "label", caption = string.format("crafted in: %d", v.n_buildings) }
            if v.building ~= BUILDING_NOT_RESEARCHED then
                single_recipe_flow.add { type = "sprite", sprite = "item/" .. v.building }
                single_recipe_flow.add { type = "label", caption = game.recipe_prototypes[v.building].localised_name }
            else
                single_recipe_flow.add { type = "label", caption = BUILDING_NOT_RESEARCHED }
            end
            recipes_flow.add { type = "line" }
        end
    end

    -- raw resources
    if raw_resources ~= nil then
        for resource, amount in pairs(raw_resources) do
            local single_resource_flow = raw_resources_flow.add { type = "flow", direction = "horizontal" }
            local sprite_path = "item/" .. resource
            if not player.gui.is_valid_sprite_path(sprite_path) then
                sprite_path = "fluid/" .. resource
            end
            if player.gui.is_valid_sprite_path(sprite_path) then
                single_resource_flow.add { type = "sprite", sprite = sprite_path }
            end
            local prototype = game.item_prototypes[resource]
            local res_name
            if prototype then
                res_name = { "", prototype.localised_name }
            else
                res_name = resource
            end
            single_resource_flow.add { type = "label", caption = string.format(" %.2f %s per second", amount, resource) }
        end
    end

    -- byproducts
    if byproducts ~= nil then
        for prod_name, amount in pairs(byproducts) do
            local single_byproduct_flow = byproducts_flow.add { type = "flow", direction = "horizontal" }
            local sprite_path = "item/" .. prod_name
            if not player.gui.is_valid_sprite_path(sprite_path) then
                sprite_path = "fluid/" .. prod_name
            end
            if player.gui.is_valid_sprite_path(sprite_path) then
                single_byproduct_flow.add { type = "sprite", sprite = sprite_path }
            end
            local prototype = game.item_prototypes[prod_name]
            local res_name
            if prototype then
                res_name = { "", prototype.localised_name }
            else
                res_name = prod_name
            end
            single_byproduct_flow.add { type = "label", caption = string.format(" %.2f %s per second", amount, prod_name) }
        end
    end
end

function toggle_interface(player)
    local main_frame = player.gui.screen.main_frame

    if main_frame == nil then
        build_interface(player)
        draw_results(player.index)
    else
        main_frame.destroy()
    end
end