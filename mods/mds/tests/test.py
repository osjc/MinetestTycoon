# World is from -30912, -30752, -30912 to 30927, 30927, 30927
import math

class Pos:
  def __init__(s,x,y,z):
    s.x=x
    s.y=y
    s.z=z
  def __str__(s):
    return "(x="+str(s.x)+",y="+str(s.y)+",z="+str(s.z)+")"

world_width = 30927 - (-30912) + 1
world_width_chunks = world_width / 80
layer_size_chunks = world_width_chunks * world_width_chunks
chunk_size = 80*80*80

def CalculateIndex(pos):
  x = pos.x+30912.0
  y = pos.y+30912.0
  z = pos.z+30912.0
  cx = math.floor(x/80)
  cy = math.floor(y/80)
  cz = math.floor(z/80)
  rx = x-cx*80
  ry = y-cy*80
  rz = z-cz*80
  index_in_chunk = rx + 80*rz + 6400*ry
  index_of_chunk = cx + world_width_chunks*cz + layer_size_chunks*cy
  result = index_in_chunk + chunk_size*index_of_chunk
  return int(result)

def PositionFromIndex(index):
  index = index+0.0
  index_of_chunk = math.floor(index/chunk_size)
  index_in_chunk = index - index_of_chunk * chunk_size
  ry = math.floor(index_in_chunk/6400)
  index_in_chunk = index_in_chunk - ry*6400
  rz = math.floor(index_in_chunk/80)
  rx = index_in_chunk - rz*80
  cy = math.floor(index_of_chunk/layer_size_chunks)
  index_of_chunk = index_of_chunk - cy*layer_size_chunks
  cz = math.floor(index_of_chunk/world_width_chunks)
  cx = index_of_chunk - cz*world_width_chunks
  x = cx*80+rx-30912
  y = cy*80+ry-30912
  z = cz*80+rz-30912
  return Pos(int(x), int(y), int(z))

def TestPos(x, y, z):
  pos = Pos(x, y, z)
  print pos, "=",
  index = CalculateIndex(pos)
  print index,
  new = PositionFromIndex(index)
  if new.x!=x or new.y!=y or new.z!=z:
    print "->", new,
  print

print PositionFromIndex(611869696000-1)

#################################

TestPos(-30912,-30912,-30912)
TestPos(-30911,-30912,-30912)
TestPos(-30912,-30911,-30912)
TestPos(-30912,-30912,-30911)

TestPos(-30912+79,-30912+79,-30912+79)
TestPos(-30912+80,-30912,-30912)
TestPos(-30912+81,-30912,-30912)

TestPos(30927,-30912+79,-30912+79)
TestPos(-30912,-30912,-30912+80)
TestPos(-30912+1,-30912,-30912+80)

TestPos(30927,-30912+79,30927)
TestPos(-30912,-30912+80,-30912)
TestPos(-30912+1,-30912+80,-30912)

TestPos(-30912+79,-30912+80+79,-30912+79)
TestPos(-30912+80,-30912+80,-30912)
TestPos(-30912+81,-30912+80,-30912)

TestPos(30927,-30912+80+79,30927)
TestPos(-30912,-30912+80+80,-30912)
TestPos(-30912+1,-30912+80+80,-30912)

TestPos(30927,-30912+80*3-1,30927)
TestPos(-30912,-30912+80*3,-30912)
TestPos(-30912+1,-30912+80*3,-30912)
