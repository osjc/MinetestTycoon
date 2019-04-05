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

LogLineNum=0
ReportedBlocks={}

minetest.register_on_generated(function(minp, maxp)
  if bedrock.Generate(minp, maxp) then
    return
  end
  local Index=PackChunkIndex(minp)
  LogLineNum=LogLineNum+1
  local PreviousLine=ReportedBlocks[Index]
  if PreviousLine then
    print("Duplicated emerge: "..Index.." first seen at line "..PreviousLine)
    PutToLog(":"..(LogLineNum-1-PreviousLine))
    return
  end
  ReportedBlocks[Index]=LogLineNum
  print("Emerge: "..Index)
  PutToLog(Index)
end)

local function LoadLog()
  util.IterateOverLines("mapgen.log", function(Line)
    LogLineNum=LogLineNum+1
    local Index=tonumber(Line)
    if Index ~= nil then
      ReportedBlocks[Index]=LogLineNum
    end
  end)
end

LoadLog()
