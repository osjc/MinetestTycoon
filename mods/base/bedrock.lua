-- The bottom of the world is covered with a bedrock layer which cannot be
-- destroyed by any means.

local layer = -30593

minetest.register_node("base:bedrock", {
  tiles = {"base_bedrock.png"},
  groups = {immortal=1, not_in_creative_inventory=1, },
  sounds = { footstep = { name = "bedrock_step", gain = 1 } },
  is_ground_content = false,
  on_blast = function() end,
  on_destruct = function () end,
  can_dig = function() return false end,
  diggable = false,
})

local function GetLobbyCoords()
  return {x=30923, y=30921.5, z=30923}
end

minetest.register_on_generated(function(minp, maxp)
  local genbedrock = false
  if minp.y <= layer then
    genbedrock = true
  end
  if (minp.x>=30608 and minp.y>=30608 and minp.z>=30608) then
    genbedrock = true
  end
  if genbedrock then
    local vm, emin, emax = minetest.get_mapgen_object("voxelmanip")
    local data = vm:get_data()
    local area = VoxelArea:new({MinEdge=emin, MaxEdge=emax})
    local c_bedrock = minetest.get_content_id("base:bedrock")
    local c_air = minetest.get_content_id("air")

    for x = minp.x, maxp.x do
      for y = minp.y, maxp.y do
        for z = minp.z, maxp.z do
          local p_pos = area:index(x, y, z)
          data[p_pos] = c_bedrock
        end
      end
    end

    if minp.x == 30848 and minp.y == 30848 and minp.z == 30848 then
      for x = maxp.x-6, maxp.x-2 do
        for y = maxp.y-5, maxp.y-2 do
          for z = maxp.z-6, maxp.z-2 do
            local p_pos = area:index(x, y, z)
            data[p_pos] = c_air
          end
        end
      end
    end

    vm:set_data(data)
    vm:calc_lighting()
    vm:update_liquids()
    vm:write_to_map()
  end
end)

function base.TeleportToLobby(player)
  local coords = GetLobbyCoords()
  player:set_pos(coords)
end
