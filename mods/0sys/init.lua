-- Module for stuff that shall be part of builtin but for
-- some strange reason it isn't.

-- This complicated piece of code is repeated over and over
-- in every module that has its code broken into submodules.
-- Many times the developer of the module refrains from
-- breaking the code into submodules, leading to "init.lua"
-- files that are 30KiB or even longer.
function import(path)
  local name = minetest.get_current_modname()
  local base = minetest.get_modpath(name)
  dofile(base.."/"..path..".lua")
end

-- Function to open a file within the world directory.
-- This shall be available in builtin so modders don't have
-- to scribble their creations with this boilerplate code.
function openfile(filename, mode)
  if not mode then
    mode="r"
  end
  local fullname = minetest.get_worldpath().."/"..filename
  return io.open(fullname, mode)
end
