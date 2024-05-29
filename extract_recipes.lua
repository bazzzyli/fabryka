local dict = {}
for _, recipe in pairs(game.player.force.recipes) do
    local products = {}
    for _, p in pairs(recipe.products) do
        products[p.name] = p
    end
    dict[recipe.name] = {
        name=recipe.name,
        category=recipe.category,
        group=recipe.group.name,
        subgroup=recipe.subgroup.name,
        products=products,
        ingredients=recipe.ingredients,
        spid=recipe.energy,
        main_product=recipe.prototype.main_product,
        enabled=recipe.enabled
    }
end
game.write_file("recipes.json",game.table_to_json(dict))