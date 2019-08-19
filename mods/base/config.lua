local function LoadConfigFile(FileSpec)
  local f = loadfile(FileSpec)
  if f then
    setfenv(f, config)
    f()
  end
end

-- Set defaults
config = {
  DebugClock=false,
  RecordMapgen=false,
}

-- Load world specific config file
LoadConfigFile(minetest.get_worldpath().."/settings.lua")
