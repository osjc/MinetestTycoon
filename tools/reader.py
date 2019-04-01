import zlib
from cStringIO import StringIO

CompressedBlockSize=128
class TFileReader(object):
  def __init__(s,Data):
    if isinstance(Data,str):
      Data=StringIO(Data)
    s.File=Data
    Header=Data.read(6)
    s.Buffer=StringIO(Header)
    s.NextBuffer=[]
    s.Decompressor=zlib.decompressobj()
    s.NextDecompressor=[None,zlib.decompressobj()]
  def NextFile(s):
    if len(s.NextBuffer)>0:
      s.Buffer=s.NextBuffer.pop()
    elif s.Decompressor is not None:
      Compressed=s.File.read(CompressedBlockSize)
      Data=s.Decompressor.decompress(Compressed)
      s.Buffer=StringIO(Data)
      while s.Decompressor is not None and s.Decompressor.unused_data!="":
        NextData=s.Decompressor.unused_data
        s.Decompressor=s.NextDecompressor.pop()
        if s.Decompressor is None:
          s.NextBuffer.append(StringIO(NextData))
          s.NextBuffer.append(s.File)
        else:
          Data=s.Decompressor.decompress(NextData)
          s.NextBuffer.append(StringIO(Data))
      s.NextBuffer.reverse()
    else:
      s.Buffer=None
      return True
  def read(s, Size):
    if s.Buffer is None:
      return ""
    Result=[]
    while Size>0:
      Portion=s.Buffer.read(Size)
      if Portion=="":
        if s.NextFile():
          break
      Size-=len(Portion)
      Result.append(Portion)
    return "".join(Result)
  def readline(s):
    if s.Buffer is None:
      return ""
    Result=[]
    while True:
      Piece=s.Buffer.readline()
      Result.append(Piece)
      if Piece!="" and Piece[-1]=="\n":
        break
      if s.NextFile():
        break
    return "".join(Result)
