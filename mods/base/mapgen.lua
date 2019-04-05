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

local function PosToString(pos)
  return("["..pos.x..","..pos.y..","..pos.z.."]")
end

minetest.register_on_generated(function(minp, maxp)
  if bedrock.Generate(minp, maxp) then
    return
  end
  local Index=PackChunkIndex(minp)
  LogLineNum=LogLineNum+1
  local MinpStr = PosToString(minp)
  local MaxpStr = PosToString(maxp)
  local PosReport = " "..MinpStr.." "..MaxpStr
  local Previous=ReportedBlocks[Index]
  if Previous then
    local Msg="Duplicated emerge: "..Index
    print(Msg.." first seen at line "..Previous.Line)
    local Report=":"..(LogLineNum-1-Previous.Line)
    if Previous.Report~=PosReport then
      Report=Report..PosReport
    end
    PutToLog(Report)
    return
  end
  ReportedBlocks[Index]={Line=LogLineNum,Report=PosReport}
  print("Emerge: "..Index)
  PutToLog(Index..PosReport)
end)

local function LoadLog()
  util.IterateOverLines("mapgen.log", function(Line)
    LogLineNum=LogLineNum+1
    local FirstPos=string.find(Line," ")
    if FirstPos ~= nil then
      local IndexStr=string.sub(Line, 1, FirstPos-1)
      local Index=tonumber(IndexStr)
      local PosReport=string.sub(Line,FirstPos,-1)
    end
  end)
end

LoadLog()
