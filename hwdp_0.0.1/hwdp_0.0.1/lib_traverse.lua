function get_main_product(recipe_prototype)
    local main_product = recipe_prototype.main_product
    if main_product == nil then
        for _, p in pairs(recipe_prototype.products) do
            if recipe_prototype.name == "oil-processing-heavy" and p.name == "heavy-oil" then
                return p
            end
            if recipe_prototype.name == "advanced-oil-processing" and p.name == "light-oil" then
                return p
            end
            if p.name == recipe_prototype.name then
                return p
            end
        end
    end
    return main_product
end


function handle_alternative_keys(recipe_name)
    local alt_keys = {}
    --alt_keys["electronic-circuit"] = "electronic-circuit-stone"
    alt_keys["petroleum-gas"] = "basic-oil-processing"
    alt_keys["glass"] = "glass-from-sand"
    alt_keys["sand"] = "sand-from-stone"
    alt_keys["solid-fuel"] = "solid-fuel-from-petroleum-gas"
    alt_keys["light-oil"] = "advanced-oil-processing"
    alt_keys["heavy-oil"] = "oil-processing-heavy"
    alt_keys["se-space-coolant-warm"] = "se-radiating-space-coolant-normal"
    alt_keys["se-space-coolant-hot"] = "se-space-coolant"
    alt_keys["se-data-storage-substrate-cleaned"] = "se-data-storage-substrate-cleaned-chemical"
    alt_keys["se-holmium-plate"] = "se-holmium-ingot-to-plate"
    alt_keys["se-bio-sludge"] = "se-bio-sludge-from-wood"
    alt_keys["se-beryllium-plate"] = "se-beryllium-ingot-to-plate"
    return alt_keys[recipe_name]
end

function should_skip_recycling_recipe(recipe_name)
    local recycling_recipes_to_skip = { "se-space-coolant-hot", "se-vulcanite-enriched", "se-vitamelange-extract" }
    for _, skip in ipairs(recycling_recipes_to_skip) do
        if recipe_name == skip then
            return true
        end
    end
    return false
end

function traverse(
        recipes,
        recipe,
        amount_per_second,
        recipes_summary,
        raw_resources_per_second,
        byproducts_per_second,
        recursion_level,
        backwards_multipler
)
    local main_product = get_main_product(recipe.prototype)
    local recipe_amount = main_product.amount * main_product.probability * backwards_multipler
    local recipe_summary = recipes_summary[recipe.name]
    if recipe_summary == nil then
        recipes_summary[recipe.name] = { ips = amount_per_second, crafting_category = recipe.category }
    else
        recipes_summary[recipe.name]["ips"] = recipe_summary["ips"] + amount_per_second * backwards_multipler
    end

    -- handle byproducts
    for _, p in ipairs(recipe.products) do
        if p.name ~= main_product.name then
            local product_ps = amount_per_second * p.amount * p.probability / recipe_amount
            local byproduct_ps = byproducts_per_second[p.name]
            if byproduct_ps == nil then
                byproducts_per_second[p.name] = product_ps
            else
                byproducts_per_second[p.name] = byproduct_ps + product_ps
            end
        end
    end

    -- handle ingredients
    for _, ing in ipairs(recipe.ingredients) do
        local ingredient_amount_per_second = ing.amount * amount_per_second / recipe_amount
        local alt_name = handle_alternative_keys(ing.name)
        local ing_name = ing.name
        if alt_name then
            ing_name = alt_name
        end
        local ing_recipe = recipes[ing_name]

        if ing_recipe == nil or should_skip_recycling_recipe(ing.name) then
            local raw_ips = raw_resources_per_second[ing.name]
            if raw_ips == nil then
                raw_resources_per_second[ing.name] = ingredient_amount_per_second
            else
                raw_resources_per_second[ing.name] = raw_ips + ingredient_amount_per_second
            end
        else
            traverse(
                    recipes,
                    ing_recipe,
                    ingredient_amount_per_second,
                    recipes_summary,
                    raw_resources_per_second,
                    byproducts_per_second,
                    recursion_level + 1,
                    backwards_multipler
            )
        end
    end
end