

from django.db.models import Func


def sgn(x):
    # return 1 - (x <= 0)
    return int(x >= 0)

def positive_sgn(x):
    ### reurutn 0 or 1 for positive number ###
    return int(x > 0)

class Epoch(Func):
   function = 'EXTRACT'
   template = "%(function)s('epoch' from %(expressions)s)"