import datetime

def round_time(dt=None, round_to=60):
   if dt == None:
       dt = datetime.datetime.now()
   seconds = (dt - dt.min).seconds
   rounding = (seconds+round_to/2) // round_to * round_to
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

print round_time(datetime.datetime(2012,12,31,23,44,59),round_to=60)
print round_time(datetime.datetime(2012,12,31,23,44,59),round_to=60*10)
print round_time(datetime.datetime(2012,12,31,23,44,59),round_to=60*60)
