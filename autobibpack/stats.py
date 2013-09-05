'''Storage and generation of statistical data over time.

This module will store totals for each day of the year. It will generate
a storage dictionary populated with zeros which you can then use to
to fetch data from a data source.

The data generated can then be output in various formats.
'''
import datetime
from calendar import monthrange # needed to work out days per year/month 
import random, time # Enables the internal testing dummy data loader
LOG_FETCH = False
SIM_DELAY = 0.0  #rough speed per search to simulate the time it takes.
FETCH_DELAY = 0.0 # the time in seconds to pause between fetches

class StatMake(object):
    def __init__(self, data_loader=None):
        '''Storage and making of time-based information from a data loader.'''
        if data_loader: # Need to setup a method that can fetch data.
            self.FETCH_DATA = data_loader
        else:
            self.FETCH_DATA = self.dummy_data_loader # Example of data loader
        self.reset()
    
    def dummy_data_loader(self, year, month, day):
        '''Create some random wild totals to simulate fetch from data source.'''
        total = random.randint(50000,60000) # would 
        time.sleep(SIM_DELAY)
        return total+year+month+day
                
    def reset(self):
        '''Reset data store to defaults.'''
        self.STORE_ACTIONS = {'reset' :'Reset the store to nothing.',
                              'rawdata': 'Returns the raw data as CSV.',
                              'pprint': 'Returns a TSV version of data.',
                              'fetch': 'Fetch the daily total.',}
        now = datetime.date.today().year
        self.YEARS = range(now-1, now+1)
        self.MONTHS = range(1,13)
        self.reset_store()
        
    def set_years(self, start, end):
        '''Set the start and end years for the data required.'''
        self.YEARS = range(start, end+1)
        self.reset_store()
    
    def set_months(self, start, end):
        '''Set the start and end months for the data required.'''
        self.MONTHS = range(start, end+1)
        self.reset_store()
    
    def reset_store(self):
        '''Reset the store to reflect changes to years and months to check.'''
        self.STORE = dict()
        self._store_action('reset')

    def _store_action(self, action=None, hide=None):
        '''Perform an action on the internal data store and hide bits if output.
        
        You can reset, fetch or return the data in different formats.''' 
        RESET = 'reset'
        FETCH = 'fetch'
        TSV = 'pprint'
        CSV = 'rawdata'
        if not action in self.STORE_ACTIONS:
            raise Exception
        
        # Prepare the header if the store is output.
        if action == CSV:
            head = 'year,month,day,total\n' 
        elif action == TSV:
            head = 'Year\tMonth\tDay\tDTotal\tMTotal\tYTotal\tTotal\n'
        else:
            head = str() # head must contain some value or loop can fail.
        
        # Customise the TSV output when needed.
        hide_valid = ('day', 'month')
        #if not hide in hide_valid:
         #   hide = 'month'
        if hide == 'day':
            head = 'Year\tMonth\tMTotal\tYTotal\tTotal\n'
            SHOW_MONTH = True
            SHOW_DAY = False
        elif hide == 'month':
            head = 'Year\tYTotal\tTotal\n'
            SHOW_MONTH = False
            SHOW_DAY = False
        else:
            head = head
            SHOW_MONTH = True
            SHOW_DAY = True
            
        header = head # Enables the head to be using in multiple places.
        lines = header # Store the textual output from data store.
        total_all = 0 # Keep a running total for all years.
        
        # Perform operations for each year.
        for year in self.YEARS:
            total_year = 0
            if action == RESET:
                self.STORE[year] = dict()
            elif action == FETCH and LOG_FETCH: # do nothing unless logging
                print year
            elif action == TSV and SHOW_MONTH:
                lines += '%s\n'%(year)
                
            # Perform operations for each month
            for month in self.MONTHS:
                total_month = 0
                if action == RESET:
                    self.STORE[year][month] = dict()
                elif action == FETCH and LOG_FETCH:  # do nothing unless logging
                    print month
                elif action == TSV and hide not in ['month','day']:
                    lines += '\t%s\n'% month
                day_range = 5
                weekday, day_range = monthrange(year, month)
                #weekday = day of the week month begins, NOT day of week for a date
                
                # Perform operations for each day
                for day in range(1,day_range):
                    if action == RESET:
                        self.STORE[year][month][day] = {'total': 1, 'query': ''}
                    elif action == FETCH:
                        if LOG_FETCH:
                            print day,
                        self.STORE[year][month][day]['total'] = self.FETCH_DATA(year, month, day)
                        time.sleep(FETCH_DELAY)
                    elif action in (TSV, CSV):
                        total = self.STORE[year][month][day]['total']
                        total_all += total
                        total_year += total
                        total_month += total                                  
                        if action == CSV:
                            lines += '%s,%s,%s,%s\n'%(year, month, day, total)
                        elif action == TSV:
                            if SHOW_DAY:
                                lines += '\t\t%s\t%s\n'%(day, total)
          
                # Output totals when needed
                # -----------------------------------------
                # For the month
                if action == FETCH and LOG_FETCH:
                    lines += ''
                if action == TSV:
                    if SHOW_DAY:
                        lines += '%s\t%s\t\t\t%s\n'%(year, month, total_month)
                    elif SHOW_MONTH:
                        lines += '%s\t%s\t%s\n'%(year, month, total_month)
                    
            # For the year
            if action == FETCH and LOG_FETCH:
                print ''
            elif action == TSV and hide not in ['month','day']:
                lines += '%s\t\t\t\t\t%s\n'%(year, total_year)
            elif action == TSV and hide == 'day':
                lines += '%s\t\t\t%s\n'%(year, total_year)
            elif action == TSV and hide == 'month':
                lines += '%s\t%s\n'%(year, total_year)           
        # For all years
        if action == TSV:
            if SHOW_MONTH and SHOW_DAY:
                lines += 'Total\t\t\t\t\t\t%s\n'%total_all
            elif SHOW_MONTH:
                lines += 'Total\t\t\t\t%s\n'%total_all
            elif not SHOW_MONTH and not SHOW_DAY:
                lines += 'Total\t\t%s\n'%total_all
        if not hide == 'month':
            lines += header
       
        return lines

    def fetch_data(self):
        '''Get the data from the source. It might make 1000s of calls.'''
        self._store_action('fetch')

    def raw_data(self):
        return self._store_action('rawdata')
                
    def show_years(self):
        return self._store_action('pprint', 'month')
    
    def show_months(self):
        return self._store_action('pprint', 'day')
        
    def show_days(self):    
        return self._store_action('pprint')
        
    def __str__(self):
        return self._store_action('pprint')

if __name__ == "__main__":
    s = StatMake()
    #s.set_years(2010, 2013)
    #s.set_months(1, 2)
    #s.reset_store()
    s.fetch_data() 
    print s.show_years()
    print s.show_months()
    print s.show_days()
    print s.raw_data()