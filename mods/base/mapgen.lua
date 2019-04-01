mapgen={}

local function PackChunkIndex(pos, cy, cz)
  local cx
  if cy == nil then
    local d = inode.DissectPosition(pos)
    cx = d.cx
    cy = d.cy
    cz = d.cz
  end
  local ChunkIndex = cx*1048576+cy*1024+cz
  return ChunkIndex
end

local function PutToLog(Text)
  local file = openfile("mapgen.log","a")
  file:write(Text.."\n")
  file:close()
end

ReportedBlocks={}

minetest.register_on_generated(function(minp, maxp)
  if bedrock.Generate(minp, maxp) then
    return
  end
  local Index=PackChunkIndex(minp)
  if ReportedBlocks[Index] then
    print("Duplicated emerge: "..Index)
    return
  end
  ReportedBlocks[Index]=true
  print("Emerge: "..Index)
  PutToLog(Index)
end)

local function LoadLog()
  util.IterateOverLines("mapgen.log", function(Line)
    local Index=tonumber(Line)
    ReportedBlocks[Index]=true
  end)
end

LoadLog()
