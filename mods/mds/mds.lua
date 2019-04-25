mds={}

local function IsBlockAbsent(pos)
  local manip = minetest.get_voxel_manip()
  manip:read_from_map(pos, pos)
  local node = minetest.get_node(pos)
  return node.name == "ignore"
end

local function WaitForTheEmerge(Info)
  local pos, meta = unpack(Info)
  local absent = IsBlockAbsent(pos)
  if absent then
    return true
  end
  clock.UnregisterPeriodicProc("Wait")
  for name,value in pairs(meta.data) do
    if meta.types[name]=="int" then
      meta.meta:set_int(name, value)
    else
      meta.meta:set_string(name, value)
    end
  end
  meta.data = nil
  meta.types = nil
end

local function FakeGetInt(meta, name)
  if meta.data == nil then
    return meta.meta:get_int(meta)
  else
    return meta.data[name] or 0
  end
end

local function FakeGetString(meta, name)
  if meta.data == nil then
    return meta.meta:get_string(meta)
  else
    return meta.data[name]
  end
end

local function FakeSetInt(meta, name, value)
  if meta.data == nil then
    meta.meta:set_int(name, value)
  else
    meta.types[name] = "int"
    meta.data[name] = value
  end
end

local function FakeSetString(meta, name, value)
  if meta.data == nil then
    meta.meta:set_string(name, value)
  else
    meta.types[name] = "string"
    meta.data[name] = value
  end
end

local function GetInode(index)
  local pos = inode.PositionFromIndex(index)
  local dict = {
    get_int = FakeGetInt,
    set_int = FakeSetInt,
    get_string = FakeGetString,
    set_string = FakeSetString,
    meta=minetest.get_meta(pos),
    types={},
    data={},
  }
  local Info = {pos, dict}
  local absent = WaitForTheEmerge(Info)
  if absent then
    minetest.emerge_area(pos, pos)
    clock.RegisterPeriodicProc("Wait", WaitForTheEmerge, Info)
    return dict, true
  else
    return dict.meta
  end
end

local Superblock = nil
local Loading = nil

function mds.GetSuperblock()
  if Superblock == nil then
    Loading = true
    Superblock, Loading = GetInode(0)
  elseif Loading then
    if Superblock.data == nil then
      Superblock = Superblock.meta
      Loading = nil
    end
  end
  return Superblock,Loading
end
