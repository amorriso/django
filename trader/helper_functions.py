import string
import operator
import datetime

def sql_clean(istring):

    '''
    Remove anything from a string that is not a letter, _ or a digit.
    '''

    allowed_set = set(list(string.ascii_letters+'_'+string.digits))
    for i in istring:
        if not i in allowed_set:
            istring = istring.replace(i, ' ')

    return istring

def diff_dates_year_fraction(future_date, base_date, day_count = 365):
    #time_to_expiry = relativedelta(future_date, base_date)
    return (future_date - base_date).days / float(day_count)

def sqldate2datetime(date):
    return datetime.datetime.strptime(date[:10], "%Y-%m-%d")

def date2datetime(date):
    return datetime.datetime.combine(date, datetime.datetime.min.time())

def datetime2date(datet):
    return datetime.date(*datetime.datetime.timetuple(datet)[0:3])
    
def argsort(inputlist):

    '''
    Sort (ascending) the inputlist, return the new index order.

    Like exactly the same as scipy.argsort, but for lists see 
      online documentation for scipy.argsort. Uses built in list.sort method.

    Inputs:
        inputlist, list - containing objects that can be compared >, < etc

    Outputs:
        list - containing ints -> representing the new ordering of the inputlist
            indices, if you were to have sorted it.

    Example:
        argsort([1,2,3,9,4])
            returns [0,1,2,4,3]

    '''

    lst = [(i, l) for i, l in enumerate(inputlist)]
    lst.sort(key=operator.itemgetter(1))
    return [l[0] for l in lst]

