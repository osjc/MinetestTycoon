inode = {}

local WorldWidth = 30927 - (-30912) + 1
local WorldWidthInChunks = WorldWidth / 80
local LayerSizeInChunks = WorldWidthInChunks * WorldWidthInChunks
local ChunkSize = 80*80*80

function inode.CalculateIndex(pos)
  local x = pos.x+30912
  local y = pos.y+30912
  local z = pos.z+30912
  local cx = math.floor(x/80)
  local cy = math.floor(y/80)
  local cz = math.floor(z/80)
  local rx = x-cx*80
  local ry = y-cy*80
  local rz = z-cz*80
  local IndexInChunk = rx + 80*rz + 6400*ry
  local IndexOfChunk = cx + WorldWidthInChunks*cz + LayerSizeInChunks*cy
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
