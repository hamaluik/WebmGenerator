import subprocess as sp
from dataclasses import dataclass

@dataclass
class VideoInfo:
  filename: str
  duration: float
  fps: float
  tbr: float
  height:int
  width:int
  hasaudio:bool

def getVideoInfo(filename,filters=None):
  state=None
  stats= dict(filename=filename,duration=0,hasaudio=False,fps=24)
  if filters is None:
    proc = sp.Popen(['ffmpeg','-i',filename],stdout=sp.PIPE,stderr=sp.PIPE)
  else:
    proc = sp.Popen(['ffmpeg','-i',filename,'-filter_complex', filters,'-frames:v','1','-f','null','-'],stdout=sp.PIPE,stderr=sp.PIPE)

  outs,errs = proc.communicate()
  for errLine in errs.split(b'\n'):
    for errElem in [x.strip() for x in errLine.split(b',')]:
      if errElem.startswith(b'Duration:'):
        try:
          timeParts = [float(x) for x in errElem.split()[-1].split(b':')]
          stats['duration'] = sum([t*m for t,m in zip(timeParts[::-1],[1,60,60*60,60*60*60])])
        except Exception as e:
          print(e)
      elif errElem.startswith(b'Stream'):
        if b'Video:' in errElem:
          state='Video'
        elif b'Audio:' in errElem:
          state = 'Audio'
          stats['hasaudio'] = True

      elif state=='Video':
        if errElem.endswith(b'fps'):
          try:
            stats['fps']=float(errElem.split(b' ')[0])
          except Exception as e:
            print(e)
        elif errElem.endswith(b'tbr'):
          try:
            stats['tbr']=float(errElem.split(b' ')[0])
          except Exception as e:
            print(e)
        if b'x' in errElem:
          try:
            w,h = errElem.split(b' ')[0].split(b'x')
            w=int(w)
            h=int(h)

            stats['height'] = h
            stats['width']  = w 
          except:
            pass

  return VideoInfo(**stats)

if __name__ == '__main__':
  import webmGenerator