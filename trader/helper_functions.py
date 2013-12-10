import string
import operator
import datetime
import scipy
import scipy.stats as stats
import scipy.optimize as opt
import scipy.interpolate as interpolate
import datetime
import pdb

def sql_clean(istring):

    '''
    Remove anything from a string that is not a letter, _ or a digit.
    '''

    allowed_set = set(list(string.ascii_letters+'_'+string.digits))
    for i in istring:
        if not i in allowed_set:
            istring = istring.replace(i, ' ')

    return istring


def diff_dates_year_fraction(date, base_date, day_count = 365):
    if type(date) == type(datetime.datetime.today()):
        date = date.date()
    return (date - base_date).days / float(day_count)


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


def black_pricer(T, S, K, v, call = True):
    
    '''
    Pricer for a European options with bond future undlying. Returns the risk neutral fair value.

    T, float, time to expiry
    S, float, underlying value
    K, float, strike
    v, float, vol
    call, Bool, if True price a call option, if false price a put option

    '''

    if not all([T, S, K, v]):
        return None

    d1 = ( scipy.log(S/K) + ((v**2)/2.0)*T ) / ( v*(T**0.5) )
    d2 = d1 - v*(T**0.5)

    if call:
        return S * stats.norm.cdf(d1) - K * stats.norm.cdf(d2)
    else:
        return K * stats.norm.cdf(-d2) - S * stats.norm.cdf(-d1)


def black_delta(T, S, K, v, call = True):

    '''
    Calc. delta for a European options with bond future undlying.

    T, float, time to expiry
    S, float, underlying value
    K, float, strike
    v, float, vol
    call, Bool, if True price a call option, if false price a put option

    '''

    if not all([T, S, K, v]):
        return None

    d1 = ( scipy.log(S/K) + ((v**2)/2.0)*T ) / ( v*(T**0.5) )
    d2 = d1 - v*(T**0.5)

    if call:
        return stats.norm.cdf(d1)
    else:
        return -1 * stats.norm.cdf(-d1)


def black_pricer_vol(T, S, K, Val, call = True, initialguess = None):

    '''
    
    Return the vol

    T, float, time to expiry
    S, float, underlying value
    K, float, strike
    Val, float, value of the option
    call, Bool, if True price a call option, if false price a put option
    initial_guess, float. If provided use as input to root finding function

    '''

    if not all([T, S, K, Val]):
        return None

    def function(vol):
        return abs(black_pricer(T, S, K, vol, call) - Val)
    
    if not initialguess:
        initialguess = 1.0

    originalguess = initialguess

    impliedvol = opt.fmin(function, initialguess, ftol = 1e-5, disp = 0)

    if impliedvol[0] == originalguess:
        message = 'Failed to find sensible implied vol! I.e. Didnt find f(minimum).'
        raise ValueError(message)
        
    return impliedvol[0]


def spline_interpolate(series, index, order = 3):

    '''
    
    Given a list with non-finite values (missing data) fill in the missing data using a 
    spline interpolation routine. Note that if the number of valid points is less than 
    the order of the interpolation you require, this routine will just hand back the 
    input series list. This is because you can't fit a spline or order n with less than
    n points.

    Inputs:
        series -> list with NaN's you'd like to replace with spline interpolated values
        index -> list index values (like the x-axis)
        order -> int, the order used to fit the spline.

    Outputs:
        list with interpolated values replacing the NaNs.

    >>> [scipy.round_(i, decimals = 9) for i in spline_interpolate([9, 4, None, None, None, 4, 9], [-3, -2, -1, 0, 1, 2, 3])]
    [9.0, 4.0, 1.0, 0.0, 1.0, 4.0, 9.0]

    '''

    if series.count(None) < order:
        #message = "You're attempting to interpolate a curve but your input curve has less VALID points "+\
        #        "than the order of the spline fitting! This is firstly impossible and secondly can't be handled by the code."
        #raise ValueError(message)
        return series

    for pos, s in enumerate(series):
        try:
            isfinite = scipy.isfinite(s)
        except:
            series[pos] = scipy.NaN

    
    xspline = [i for i, s in zip(index, series) if scipy.isfinite(s)]
    x = [i for i in index]
    yspline = [s for s in series if scipy.isfinite(s)]
    s = interpolate.InterpolatedUnivariateSpline(xspline, yspline, k = order)
    spline_series = [s(i).item() for i in x]

    return spline_series


def ATM_strike(strikes, value):
    
    '''
    >>> ATM_strike([100, 110, 120, 130, 140, 150], 115)
    110
    >>> ATM_strike([100, 110, 120, 130, 140, 150], 115.0001)
    120

    '''

    distance = [abs(s - value) for s in strikes]
    min_distance = 100000000000.0
    min_pos = -1
    for pos, d in enumerate(distance):
        if d < min_distance:
            min_distance = d
            min_pos = pos 

    return strikes[min_pos]



if __name__ == "__main__":
    import doctest
    doctest.testmod()
