import os
import subprocess
import binascii

def ParseAndStore(InF,BlockWriter):
  Count=InF.readline()
  try:
    Count=int(Count)
  except ValueError:
    return
  BlockWriter.SetCount(Count)
  while Count>0:
    Line=InF.readline()
    if Line=="":
      break
    Line=Line[:-1].split("|")
    Position=int(Line[0])
    Data=binascii.unhexlify(Line[1])
    del Line
    BlockWriter.WriteBlock(Position, Data)

def ExtractMap(WorldBase,BlockWriter):
  Process=subprocess.Popen(
    ["sqlite3","map.sqlite"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    cwd=WorldBase
  )
  Process.stdin.write(
    "select count(pos) from blocks;"
    "select pos,hex(data) from blocks;"
  )
  Process.stdin.close()
  ParseAndStore(Process.stdout,BlockWriter)
#  Out=open("test.out","w")
#  while True:
#    Data=Process.stdout.read(8192)
#    if Data=="":
#      break
#    Out.write(Data)
#  Out.close()
  Process.wait()
