local dct = {}
for _, rec in pairs(game.get_filtered_recipe_prototypes {{ filter = "subgroup", subgroup = "module" }}) do
    log("#################")
    log("module name: " .. rec.name)
    if rec.name == "beacon" then
        local prot = game.entity_prototypes[rec.name]
        log("prot name: " .. prot.name)
        local mod_size = prot.module_inventory_size
        dct[rec.name] = { prot_name=prot.name, module_inventory_size=mod_size, enabled=rec.enabled }
    else
        dct[rec.name] = {rec_name=rec.name, enabled=rec.enabled}
    end
end

game.write_file("test.json",game.table_to_json(dct))