import sqlite3 as sqlite
import datetime
import copy
import scipy
import string
import helper_functions as hf
import time


class DataError(Exception):
    pass

class FutureError(Exception):
    pass

class Future(object):

    def __init__(self, db, name, table_name):
        self._con = sqlite.connect(db)
        self._name = name
        self._table_name = hf.sql_clean(table_name)
        self._updated_future_values = None
        self._future = None


    def _get_future_from_db(self):
        with self._con:

            # the line below enables us to reference column names by their title
            self._con.row_factory = sqlite.Row

            cur = self._con.cursor()
            cur.execute(
                    "SELECT * FROM " + self._table_name + " WHERE name=:name", {"name" : self._name}
                       )
            futures_list = cur.fetchall()
            if len(futures_list) > 1:
                message = "Multiple futures with name: " + self._name
                raise FutureError(message) 
            self._future = dict(futures_list[0])
            

    def get_value_from_source(self):

        if self._future == None:
            try:
                self._get_future_from_db()
            except:
                message = "self._future doesn't exist. Method 'get_future_from_db' " + \
                    "must be executed first but didn't work for some reason!"
                raise DataError(message)

        # here we connect with whatever data source we get the future values from
        # at the moment, all the values are set to UNITY.

        # this is a tempory implementation, we just randomise (slightly) the 
        # future value
        self._updated_future_values = {}
        current_value = self._future['value']
        change = ( scipy.random.randn(1)[0] + 100. ) / 100.
        self._updated_future_values[self._future['id']] = {
                    'name' : self._future['name'], 
                    'value' : self._future['value']*change, 
                    'value changed' : not self._future['value'] == self._future['value'] * change
                                                     }

    def add_values_to_db(self):

        future = self._future
        with self._con:
            cur = self._con.cursor()
            if self._updated_future_values[future['id']]['value changed']:
                cur.execute(
                            "UPDATE " + self._table_name + " SET value=:value WHERE id=:id", 
                            {"id" : future['id'],
                             "value" : self._updated_future_values[future['id']]['value']}
                           )
                self._con.commit()


    def get_and_add_values(self):
        self.get_value_from_source()
        self.add_values_to_db()


class Option(object):

    def __init__(self, 
            db, 
            futuredefinition_table, 
            optiondefinition_table, 
            optioncontract_table, 
            name, 
            num_contracts,
            base_date = None):

        if num_contracts % 2 == 0:
            num_contracts += 1

        self._con = sqlite.connect(db)
        self._optiondefinition_table = hf.sql_clean(optiondefinition_table)
        self._futuredefinition_table = hf.sql_clean(futuredefinition_table)
        self._optioncontract_table = hf.sql_clean(optioncontract_table)
        self._optioncontract_dict = {}
        self._num_contracts = num_contracts
        self._optiondefinition = {'name' : hf.sql_clean(name)}

        if base_date == None:
            self.base_date = datetime.date.today()
        else:
            self.base_date = base_date

        # get information about the options we're going to need to price.
        with self._con:
            # the line below enables us to reference column names by their title
            self._con.row_factory = sqlite.Row

            cur = self._con.cursor()

            # get info from optiondefinition_table
            cur.execute(
                    "SELECT * FROM " + self._optiondefinition_table + " WHERE name=:name",
                    {"name" : self._optiondefinition['name']}
                       )
            option_def = cur.fetchall()
            

        if len(option_def) > 1:
            message = "Multiple option definitions with the same name. " + \
                    "This isn't allowed."
            raise DataError(message)
        
        option_def = option_def[0]

        self._optiondefinition.update(dict(option_def))

        # get information about the future the option is based on.
        with self._con:
            self._con.row_factory = sqlite.Row
            cur = self._con.cursor()

            # get info from optiondefinition_table
            cur.execute(
                    "SELECT * FROM " + self._futuredefinition_table + " WHERE id=:id",
                    {"id" : self._optiondefinition['future_id']}
                       )
            future_def = cur.fetchall()
            

        if len(future_def) > 1:
            message = "Multiple futures returned. Something has gone bung!"
            raise DataError(message)
        future_def = future_def[0]

        self._future = dict(future_def)
        self._update_optioncontract_dict()

    
    def _update_optioncontract_dict(self):

        '''
        Get information about the option contracts and store this in 
        self._optioncontracts_dict -> This is essentailly a dictionary
        that contains the same information as the optioncontract_table
        we just store in a dict to minimise calls to db.
        '''

        with self._con:
            self._con.row_factory = sqlite.Row
            cur = self._con.cursor()

            # get info from optiondefinition_table
            cur.execute(
                    "SELECT * FROM " + self._optioncontract_table + \
                            " WHERE optiondefinition_id=:id", {'id' : self._optiondefinition['id']}
                       )
            option_contracts = cur.fetchall()

        if len(option_contracts) > 0:
            for row in option_contracts:
                dict_row = dict(row)
                self._optioncontract_dict.update({dict_row['strike'] : dict_row})


    def _update_Future_value(self):

        # get information about the future the option is based on.
        with self._con:
            self._con.row_factory = sqlite.Row
            cur = self._con.cursor()

            # get info from optiondefinition_table
            cur.execute(
                    "SELECT value FROM " + self._futuredefinition_table + " WHERE id=:id",
                    {"id" : self._optiondefinition['future_id']}
                       )
            future_price = cur.fetchall()

        if len(future_price) > 1:
            message = "Multiple futures returned. Something has gone bung!"
            raise DataError(message)
        future_price = future_price[0]

        self._future.update(dict(future_price))


    def _return_ATM_strike(self):
        
        future_value = self._future['value']
        strike_interval = self._optiondefinition['strike_interval']
        strike_range = (int(future_value) - strike_interval*2, int(future_value) + strike_interval*2)
        spacing = 1 + ((strike_range[1] - strike_range[0]) / strike_interval)
        poss_strikes = scipy.linspace(strike_range[0], strike_range[1], spacing)
        distance = abs(poss_strikes - future_value)
        min_distance = min(distance)
        # if the future value is equal distance from 2 stikes then we return the lower one.
        return poss_strikes[scipy.where(distance == min_distance)[0][0]]


    def _create_required_strike_list(self):

        atm_strike = self._return_ATM_strike();
        calls = [atm_strike + i*self._optiondefinition['strike_interval'] 
                            for i in xrange(0, ((self._num_contracts - 1) / 2) + 1)]
        puts  = [atm_strike - i*self._optiondefinition['strike_interval'] 
                            for i in xrange(0, ((self._num_contracts - 1) / 2) + 1)]
        
        return sorted(list(set(calls + puts)))
    

    def _get_db_optioncontracts(self):

        with self._con:
            # the line below enables us to reference column names by their title
            self._con.row_factory = sqlite.Row

            cur = self._con.cursor()

            # get info from optiondefinition_table
            cur.execute(
                    "SELECT * FROM " + self._optioncontract_table + " WHERE optiondefinition_id=:id",
                    {"id" : self._optiondefinition['id']}
                       )
            return [dict(i) for i in cur.fetchall()]


    def _update_optioncontract_strikes(self):

        ''' 
        This method makes sure that the db only contains data that we 
        want to see. It works out what stikes are within the range 
        (around the ATM) that interest us, removes strikes which we
        don't need and adds strikes that we do. Hopefully, most of the 
        time method won't fully execute. If the Future price doesn't move
        around much then most of the time the db will contain the correct 
        srikes and so won't need to be updated.

        '''

        # first of all we grab an updated future value from the db. It is the
        # role of the Future class to keep this value updated from the source.
        # The option class and the Future class should update separately.
        self._update_Future_value()

        # the strikes we need to get from the data source.
        required_strike_set = set(self._create_required_strike_list())
        
        # the strikes we have in the db
        db_option_strikes = [i['strike'] for i in self._get_db_optioncontracts()]

        # remove unnecessary strikes
        removed_strikes = False
        refined_db_option_strikes = copy.copy(db_option_strikes)
        with self._con:
            self._con.row_factory = sqlite.Row
            cur = self._con.cursor()

            for db_strike in db_option_strikes:
                if not db_strike in required_strike_set:
                    cur.execute("DELETE FROM " + self._optioncontract_table + \
                            " where strike=:strike", {'strike' : db_strike})

                    refined_db_option_strikes.remove(db_strike)
                    removed_strikes = True

        # so refined_db_option_strikes contains the strikes we have in the db
        # that we actually want. If this equals the required_strike_set, we
        # don't need to do anything.
        added_strikes = False
        if required_strike_set != set(refined_db_option_strikes):
            added_strikes = True
            expiry_date = hf.datetime2date(hf.sqldate2datetime(self._optiondefinition['expiry_date']))
            time_to_expiry = \
                    hf.diff_dates_year_fraction(expiry_date, self.base_date)
            #add strikes and populate with defaults
            with self._con:
                self._con.row_factory = sqlite.Row
                cur = self._con.cursor()
    
                # Here we've hard coded what we expect the table schema to be for 
                # the optioncontract_table. If you update the table schema and 
                # forget to update the code we should raise an error below.
                cur.execute('PRAGMA table_info(' + self._optioncontract_table  + ')')
                column_names = set([dict(i)['name'] for i in cur.fetchall()])
                if column_names != set(['id', 'optiondefinition_id', 'strike', 'bid',
                    'ask', 'value', 'vol', 'expiry_date', 'time_to_expiry', 'last_updated']):
                    message = "Database schema appears to have been updated. " +\
                            "This code needs to be updated also. Problem table: " +\
                            self._optioncontract_table
                    raise DataBaseError(message)
    
                for strike in required_strike_set:
                    if not strike in refined_db_option_strikes:
                        parameters = {  'o' : self._optiondefinition['id'],
                                        's' : strike,
                                        'b' : -99,
                                        'a' : -99,
                                        'v' : -99,
                                        'vol' : -99,
                                        'e' : expiry_date,
                                        't' : time_to_expiry,
                                        'u' : datetime.datetime(1900,1,1,0,0,0)
                                     }
                        cur.execute(
                            "INSERT INTO " + self._optioncontract_table + \
                            " (optiondefinition_id, strike, bid, ask, value, " + \
                            "vol, expiry_date, time_to_expiry, last_updated) VALUES " + \
                            "(:o, :s, :b, :a, :v, :vol, :e, :t, :u)",
                            parameters
                            )
        else:
            # the db contains all the strikes we're interested in. And no strikes we're
            # not interest in
            #
            # Note, here added_strikes = False
            pass

        # we only need to update the _optioncontract_dict if we've modified the db.
        if added_strikes or removed_strikes:
            self._update_optioncontract_dict()


    def get_values_from_source(self):

        '''
        In this public method we update the future value. This should be kept updated 
        in the db by whatever process is managing the Future class. Then we update the
        db strike table "_optioncontract_table" with self._update_optioncontract_strikes.
        Then, if we've modified the table this will automatically update the 
        _optioncontract_dict.
        '''

        self._update_Future_value()
        self._update_optioncontract_strikes()

        atm_strike = self._return_ATM_strike()

        strike_info = sorted(self._optioncontract_dict.items(), key=lambda x:x[0])

        for strike, info in strike_info:

            dateandtimenow = datetime.datetime.now()

            info['bid'] = (strike - atm_strike)**2 - 5 + scipy.random.randn(1)[0] * 2
            info['ask'] = (strike - atm_strike)**2 + 5 + scipy.random.randn(1)[0] * 2
            info['value'] = (info['bid'] + info['ask'] ) / 2
            info['vol'] = (strike - atm_strike)**2
            info['last_updated'] = dateandtimenow
            info['time_to_expiry'] = hf.diff_dates_year_fraction(
                    hf.sqldate2datetime(info['expiry_date']), dateandtimenow
                                                                ) 


    def add_values_to_db(self):

        with self._con:
            self._con.row_factory = sqlite.Row
            cur = self._con.cursor()
    
            for strike, info in self._optioncontract_dict.items():
                cur.execute(
                            "UPDATE " + self._optioncontract_table + " " +\
                                    "SET bid = :bid, ask = :ask, value = :value, " + \
                                    "vol = :vol, last_updated = :last_updated, " + \
                                    "time_to_expiry = :time_to_expiry WHERE " + \
                                    "id = :id",
                            info
                            )
                

    def get_and_add_values(self):
        self.get_values_from_source()
        self.add_values_to_db()
            
        

    
        


db = 'trader/db/marketdata.db'

future_obj = Future(db, "BUNDMAR14", 'marketdata_future')
future_obj._get_future_from_db()
future_obj.get_and_add_values()

option_obj = Option(db, 'marketdata_future', 'marketdata_optiondefinition', 'marketdata_optioncontract', 'BUND_OPT_JAN', 20)
option_obj2 = Option(db, 'marketdata_future', 'marketdata_optiondefinition', 'marketdata_optioncontract', 'BUND_OPT_FEB', 20)
option_obj3 = Option(db, 'marketdata_future', 'marketdata_optiondefinition', 'marketdata_optioncontract', 'BUND_OPT_MAR', 20)
option_obj.get_and_add_values()
option_obj2.get_and_add_values()
option_obj3.get_and_add_values()

while True:
    time.sleep(1)
    print 'get and add ...'
    future_obj.get_and_add_values()
    option_obj.get_and_add_values()
    option_obj2.get_and_add_values()
    option_obj3.get_and_add_values()

