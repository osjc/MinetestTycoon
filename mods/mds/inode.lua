inode = {}

local WorldWidth = 30927 - (-30912) + 1
local WorldWidthInChunks = WorldWidth / 80
local LayerSizeInChunks = WorldWidthInChunks * WorldWidthInChunks
local ChunkSize = 80*80*80

function inode.DissectPosition(pos)
  local result = {}
  local x = pos.x+30912
  local y = pos.y+30912
  local z = pos.z+30912
  result.cx = math.floor(x/80)
  result.cy = math.floor(y/80)
  result.cz = math.floor(z/80)
  result.rx = x-result.cx*80
  result.ry = y-result.cy*80
  result.rz = z-result.cz*80
  return result
end

function inode.CalculateIndex(pos)
  local d = inode.DissectPosition(pos)
  local IndexInChunk = d.rx + 80*d.rz + 6400*d.ry
  local IndexOfChunk = d.cx + WorldWidthInChunks*d.cz + LayerSizeInChunks*d.cy
  local Result = IndexInChunk + ChunkSize*IndexOfChunk
  return Result
end

function inode.PositionFromIndex(Index)
  local IndexOfChunk = math.floor(Index/ChunkSize)
  local IndexInChunk = Index - IndexOfChunk * ChunkSize
  local ry = math.floor(IndexInChunk/6400)
  local IndexInChunk = IndexInChunk - ry*6400
  local rz = math.floor(IndexInChunk/80)
  local rx = IndexInChunk - rz*80
  local cy = math.floor(IndexOfChunk/LayerSizeInChunks)
  local IndexOfChunk = IndexOfChunk - cy*LayerSizeInChunks
  local cz = math.floor(IndexOfChunk/WorldWidthInChunks)
  local cx = IndexOfChunk - cz*WorldWidthInChunks
  local x = cx*80+rx-30912
  local y = cy*80+ry-30912
  local z = cz*80+rz-30912
  return {x=x, y=y, z=z}
end
