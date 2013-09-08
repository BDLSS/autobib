import datetime
import time
import stats
import fetch
from sources import Ora, Datafinder8081, Datafinder8000

#From schema
#http://ora.ox.ac.uk:8080/solr/core_metadata/admin/file/?contentType=text/xml;charset=utf-8&file=schema.xml
AVAILABLE_DATE_FIELDS = ['timestamp', 'creationDate', 'modifiedDate']

class DateLoader(object):
    def __init__(self, name=None, endpoint=None,
                 field='timestamp', enable_get=False,
                 start_year=None, end_year=None):
        '''From endpoint use field to get data from start to end year, if enabled.'
        
        Configuring the DateLoader
        ==========================
        This class will extract data from the endpoint. It defaults to
        ORA core_metadata.
        
        The field can be any date field. If is probably the most important
        attribute since data is collated on this field.
        
        You MUST enable the getting of data otherwise it just simulates
        the process when the fetching process starts. This fetching process
        can hit the endpoint with 355/356 requests for each year required.
        
        Years required
        --------------
        The start year is the first year of data you wish to collect. It
        defaults to the current year minus 1.
        
        The end year is the last year of data to collect. It defaults to
        the current year.
        
        All years between the start and end will be included. To get data
        for a single year just make them the same number.
        
        Using the DateLoader
        ====================
        dmod = 'date_modified'
        # We want collate the date modified for the last two years.
        d1 = DateLoader('test1', field=dmod, enable_get=True)
        d1.fetch_stats(True)
        print d1 > gives summary of all years
        
        # We want collate 2011 to now for the timestamp.
        d2 = DateLoader('test2', enable_get=True, start_year=2011)
        d2.fetch_stats(True)
        d2.print_months() gives summary of all months for all years
        
        # We want to collate a decades worth of date modified. But want
        # to simulate this first and look at test data for every single day.
        d3 = DateLoader('test3', field=dmob, start_year=2000, end_year=2009)
        d3.fetch_stats(True)
        d3.STATS.show_days()
        
        # Checked the output is okay so now repeat but get data as string
        # in CSV format where each row is a day, with no totals calculated so
        # it is good for importing into spreadsheet.
        d4 = DateLoader('test3', enable_get=True, field=dmob,
                                    start_year=2000, end_year=2009)
        d4.fetch_stats(True)
        dataascsvstring = d4.STATS.raw_data()        
        '''
        self.NAME = name # A name used to keep track of this loader.
        self.FIELD = field # The date field to search
        # The following years are inclusive
        self.YEAR_START = start_year
        self.YEAR_END = end_year
        if not endpoint:
            self.END = Ora().ENDPOINT
        if endpoint == 'datafinder':
            self.END = Datafinder8081().ENDPOINT
            self.END = Datafinder8000().ENDPOINT
        self.ENABLE_GET_DOCUMENTS = enable_get # Force users to enable get.
                        
        self.reset()
    
    def reset(self):
        '''Reset the class that generates the queries.'''
        now = datetime.date.today().year
        if not self.YEAR_START: self.YEAR_START = now-1
        if not self.YEAR_END: self.YEAR_END = now
        self.STATS = stats.StatMake(self.data_loader)            
        self.STATS.set_years(self.YEAR_START, self.YEAR_END)
        self.STATS.set_months(1, 12)
            
    def data_loader(self, year, month, day):
        '''Return the total of items with the same year, month and day.'''
        self.SEARCH = fetch.Search(self.NAME)
        self.SEARCH.set_endpoint(self.END)
        # We might as well reduce the amount of data returned
        self.SEARCH.set_rows(2) # only two items
        self.SEARCH.set_field_getlist(('id',self.FIELD)) # and two fields
        # This data loader requires us to restrict the search by date       
        wanted = self.SEARCH.format_date(year, month, day)
        self.SEARCH.query_daterange(self.FIELD, wanted, wanted)
        
        # Now can get the data.
        if self.ENABLE_GET_DOCUMENTS:
            unused = self.SEARCH.get_documents() # execute the query 
            return self.SEARCH.DOCS_FOUND
        else: # simulate with obviously wrong numbers
            return year+month+day+10000
    
    def fetch_stats(self, confirm=False):
        if confirm:
            self.STATS.fetch_data()
        else:
            print 'You need to actively confirm you want to fetch data.'
    
    def months(self):
        return self.STATS.show_months()
        
    def years(self):
        return self.STATS.show_years()
    
    def __str__(self):
        return self.STATS.show_years()

def wiki_stat_make():
    out = 'Generating ORA stats\n\n'
    start_total_time = time.time()
    time_log = list()
    
    for fieldname in AVAILABLE_DATE_FIELDS:
        start_time = time.time()
        print 'Doing %s' %fieldname
        out += '===================================\n'
        out += 'Field: %s\n'%str(fieldname).upper()
        out += '===================================\n'
        ost = DateLoader(enable_get=True, field=fieldname, start_year=2007)
        ost.fetch_stats(True)
        out += '-----------------------------------\n'
        out += 'Summary by year\n'
        out += '-----------------------------------\n'
        out += ost.years()
        out += '-----------------------------------\n'
        out += '\nSummary by month\n'
        out += '-----------------------------------\n'
        out += ost.months()
        out += '\n'
        end_time = time.time()
        entry = '%s = time taken for field: %s'%(end_time-start_time, fieldname)
        time_log.append(entry)
    print out
    for log in time_log:
        print log
    end_total_time = time.time()
    print 'Total time: %s\n'%(end_total_time-start_total_time)

def single_field():
    start = 2007 # Data started going into ORA in 2007.    
    ost = DateLoader(enable_get=True, start_year=start),
    ost.fetch_stats(True)
    print ost.years()
    print ost.months()

def datafindersingleembago():
    dfield = 'embargoedUntilDate'    
    ost = DateLoader(enable_get=True, start_year=2082, end_year=2082,
                     endpoint='datafinder', field=dfield)
    ost.fetch_stats(True)
    print ost.years()
    print ost.months()
    

if __name__ == '__main__':
    #wiki_stat_make()
    #single_field()
    datafindersingleembago()
    