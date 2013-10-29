'''Search bibliographic sources and fetch content.'''
import urllib # for encoding the url
import urllib2 # for getting page
import StringIO # for reading results
import json # for converting json

class Search(object):
    '''A general class for searching for items.'''
    def __init__(self, name='test_search'):
        self.reset(name)
        
    def reset(self, name):
        '''Resets this search item to defaults.'''
        self.NAME = name
        self.STATUS = 'needs an end point url'
        self.QUERYCOLON = dict()  # to pass to q= with :
        self.QUERY_AT = dict()    # to pass to endpoint with &
        self.MAX_ROWS = 999 # how many records per request.
        self.RAWDATA = dict()   # the last set of data returned.
        self.DOCUMENTS = dict() # keys = document UUIDs in ORA, ID in others?
        self.DOCS_FOUND = 0 # How many document found during the first search
        self.NEXT_START = 0 # Where in the sequence are we
        self.AND_JOINERS_TESTED = ['&', ' AND '] # What to use for AND queries
        # It looks like ORA supports the first and PLoS uses the second.
        self.AND_JOINER = self.AND_JOINERS_TESTED[0]
        # The above line caused error in PLoS tests because [1] assumed. 
        self.set_json() # assume we always want JSON
        self.SEARCH_METHODS_AVAILABLE = {
            'solr': ('author', 'title', 'id', 'simple', 'datetime', 'daterange')
            }
        # key = search interface, tuple = tested methods for searching

    #  Set the attributes passed in the URL 
    # ===============================================================    
    def set_endpoint(self, url):
        '''The main URL that runs the query.'''
        self.END_POINT = url
        self.STATUS = '' # now we can run the query.

    # The rest of these are optional
    def set_apikey(self, unique, url_key='api_key'):
        '''Enable sources that require unique api keys to be passed in url.'''
        self.set_at(url_key, unique)
    
    def set_at(self, key, value):
        '''Add key and value to the dictionary used to generate URL.'''
        self.QUERY_AT[key] = value
        
    def set_json(self):
        '''Set JSON as the type of result to return.'''
        self.set_at('wt', 'json')
        
    def set_indent(self, enable=False):
        '''Enable indentation on results that get returned.'''
        if enable:
            self.set_at('indent', 'on')
    
    def set_rows(self, count):
        '''Set the number of rows to return per query.'''
        count = int(count)
        if count > self.MAX_ROWS:
            count = self.MAX_ROWS
        self.set_at('rows', count)
    
    def set_start(self, count):
        '''Set the start record to return for the query.'''
        self.set_at('start', count)
            
    def set_field_getlist(self, fields):
        '''Limit the returned results to specific fields.'''
        self.set_at('fl',fields)
         
    def set_sort(self, key, descending=False):
        '''Use key to sort returned results, with option to make decending.'''
        if descending:
            order = 'desc'
        else:
            order = 'asc'    
        self.set_at('sort', '%s %s'%(key, order))
        
    #  Methods that alter the SOLR query (q) string.
    # ===============================================================        
    def query(self, field, value):
        '''Add field and value to the query.'''
        self.QUERYCOLON[field] = value
        
    def query_author(self, author):
        self.query('author', author)
    
    def query_title(self, title, add_quotes=True):
        '''Adds a quoted title search to the query with option to not quote.'''
        if add_quotes:
            title = '"%s"'%title
        self.query('title', title)
    
    def query_simple(self, author, title):
        self.query_author(author)
        self.query_title(title)
        
    def query_id(self, itemid, idkeyname='id', prefix='uuid:'):
        self.query(idkeyname, '"%s%s"'%(prefix, itemid))
    
    def format_date(self, year, month, day): # not in unittests
        return '%s-%s-%s'%(year, month, day)
        
    def query_datetime(self, field, date=None, time='00:00:00.000Z'):
        '''Query field for date with option set a specific time.'''
        value = '"%sT%s"'%(date, time)
        self.query(field, value)
        
    def query_daterange(self, field, start=None, end=None,
                        usetime=True, digit3=True):
        '''Query field for a date range from start to end with inclusive time.'''
        if usetime:
            # Tested 2 and 3 digits seconds with both ORA and PLoS. Both worked
            # so went with three digits.
            if digit3:
                #Example from ORA    "timestamp":"2012-12-19T21:05:10.512Z"
                #So, seconds is in three digits
                value = '[%sT00:00:000Z TO %sT23:59:590Z]'%(start, end)
            else:
                # Example on: http://api.plos.org/solr/search-fields/
                # has seconds to two digits.
                value = '[%sT00:00:00Z TO %sT23:59:59Z]'%(start, end)
        else:
            #  See http://lucene.apache.org/core/2_9_4/queryparsersyntax.html#Range Searches
            value = '[%s TO %s]'%(start, end)
        self.query(field, value)

    #  Generate the URL and fetch the data
    # ===============================================================        
    def make_colon(self):
        '''Return the value for query (q) where items have colons.'''
        answer = ''
        addand = '' #use and to join query.
        for item in self.QUERYCOLON:
            answer += '%s%s:%s'%(addand, item, self.QUERYCOLON[item])
            addand = self.AND_JOINER # Not all sources support the same joiner
            # The colon will change to %3A when urlencoded.
        return answer
    
    def make_and(self):
        '''Return the encoded query string.'''
        made = self.make_colon()
        
        # All requests have an 'q' attribute but could be left empty if
        # user has not added any query items. So use wildcard.
        if not made: #Tested with test126_make_and_noquery in ORA tests
            made = '*:*'
        self.QUERY_AT['q'] = made
        # by adding 'q' above we can let urlencode deal with all options
        return urllib.urlencode(self.QUERY_AT)
        
    def make_query(self):
        '''Return the URL that should return data.'''
        if not self.STATUS:
            query = self.END_POINT
            query += self.make_and()
            return query
        else:
            return ''

    def fetch_data(self):
        '''Return the data from the course and cache it.'''
        load = urllib2.urlopen(self.make_query())
        self.RAWDATA = load.read()
        load.close()
        return self.RAWDATA

    #  Process fetched data
    # ===============================================================
    def get_json_raw(self):
        '''Return the data as JSON with response headers.'''
        self.fetch_data()
        data = StringIO.StringIO(self.RAWDATA)
        return json.load(data)
    
    def get_documents(self):
        '''Return a tuple containing items found and prepare next query.'''
        data = self.get_json_raw()
        documents = data['response']['docs']
        
        # Enable it so we can run the query again with different start point
        if not self.DOCS_FOUND:
            self.DOCS_FOUND = data['response']['numFound']
        this_start = data['response']['start']
        this_count = len(documents)
        self.NEXT_START = int(this_start)+int(this_count)+1
        
        return documents

    def get_all(self):
        '''Get all the documents, doing muliple fetches when needed.'''
        new_docs =  self.get_documents()
        self.update_documents(new_docs)
        while self.NEXT_START <= self.DOCS_FOUND:
            self.set_start(self.NEXT_START)
            new_docs = self.get_documents()
            self.update_documents(new_docs)
    
    #  Post-processing of data
    # ===============================================================        
    def update_documents(self, new_documents):
        '''Add new documents to internal list of documents found.'''
        for doc in new_documents:
            key = doc['id']
            self.DOCUMENTS[key] = doc
    
    def pprint_json(self, text):
        '''Print json text with small indents with keys sorted.'''
        return json.dumps(text, sort_keys=True,
                  indent=2, separators=(',', ': '))

    #  Combine fetching, processing and returning results
    # ===============================================================
    def auto_list_ids(self, endpoint, value, field='*', batchsize=999):
        '''Search endpoint for value in field and return list of ids.'''
        # Setup the query
        log = dict()
        self.set_endpoint(endpoint)
        self.set_rows(batchsize)
        self.set_field_getlist(('id'))
        log['2a. Value searching for'] = value
        log['2b. Field searching in'] = field
        self.query(field, value)
        log['2c. First query'] = self.make_query()
        
        # Run it and return results.
        self.get_all()
        log['2d. Number of IDs found'] = self.DOCS_FOUND
        unique = self.DOCUMENTS.keys()
        log['2e. Number of unique IDs'] = len(unique)
        return unique, log
        
if __name__ == '__main__':
    import fetch_test_ora as get
    import unittest
    unittest.TextTestRunner(verbosity=1).run(get.suite())
    