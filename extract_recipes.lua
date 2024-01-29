local dict = {}
for _, recipe in pairs(game.player.force.recipes) do
    local products = {}
    for _, p in pairs(recipe.products) do
        products[p.name] = p
    end
    dict[recipe.name] = {
        name=recipe.name,
        building=recipe.category,
        products=products,
        ingredients=recipe.ingredients,
        spid=recipe.energy
    }
end
game.write_file("recipes.json",game.table_to_json(dict))