# -*- coding: utf-8 -*-
'''Test the search interface against PLOS.

This test sources that require an api key to
be used. It also checks the author and title search.'''
import unittest
import fetch
from sources import Plos

ENABLE_REMOTE = False # This will stop queries going to PLOS.

class TestApi(unittest.TestCase):
    '''Check API keys can be used in Solr bibliographic search.'''          
    def setUp(self):
        self.NAME = 'plos_test'
        p = Plos()
        self.END = p.ENDPOINT 
        self.KEY = p.KEY
        self.URL_API_KEY = p.URL_KEY_FIELD 
        self.SEARCH = fetch.Search(self.NAME)
            
    # Test functionality where sources require an API key
    # ===============================================================
    def do_prepare_api(self, endpoint=True):
        if endpoint:
            self.SEARCH.set_endpoint(self.END)
        self.SEARCH.set_apikey(self.KEY)
        self.assertEqual(self.KEY, self.SEARCH.QUERY_AT[self.URL_API_KEY])
        
    def test10_api(self):
        self.do_prepare_api(False)
    
    def test15_api_urlkey(self):
        custom_key = 'keyinurl'
        self.SEARCH.set_apikey(self.KEY, custom_key)
        self.assertEqual(self.KEY, self.SEARCH.QUERY_AT[custom_key])
            
    def test20_api_inquery(self):
        self.do_prepare_api()
        made = self.SEARCH.make_query()
        expected = '%s=%s'%(self.URL_API_KEY, self.KEY)
        self.assertIn(expected, made)

class TestCustomQuery(unittest.TestCase):
    '''Check API keys can be used in Solr bibliographic search.'''          
    def setUp(self):
        self.NAME = 'plos_solr'
        p = Plos()
        self.END = p.ENDPOINT 
        self.KEY = p.KEY
        self.URL_API_KEY = p.URL_KEY_FIELD
        self.AUTHOR = 'Majlender'
        self.AUTHOR2 = 'Welling'
        self.AUTHOR_NONASCII = u"Björk"
        self.TITLE = 'Open Access to the Scientific Journal Literature'
        self.EID = "10.1371/journal.pone.0011273"
        self.DATEFIELD = 'publication_date'
        self.EDATE = '2010-06-23'
        self.ETIME = '00:00:00Z'
        self.EDATETIME = '%sT%s'%(self.EDATE, self.ETIME)
        self.SEARCH = fetch.Search(self.NAME)
        self.JOINER = p.AND_JOINER
        
        # These expected value might change. Correct as
        self.DOCS_EXPECTED = 8 #of 26th July 2013
        self.DATE_EXPECTED = 259
        
    def show_query(self):
        self.SEARCH.set_indent()
        made = self.SEARCH.make_query()
        print
        print made
        print
                
    def do_prepare_api(self):
        self.SEARCH.set_endpoint(self.END)
        self.SEARCH.set_apikey(self.KEY)
                
    # Test queries against PLOS to check data is as expected.
    # ===============================================================              
    def test25_title_search(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_title(self.TITLE)
            self.SEARCH.get_documents()
            self.assertEqual(1, self.SEARCH.DOCS_FOUND)

    def test30_querysimple(self):
        if ENABLE_REMOTE:
            self.do_prepare_api() 
            self.SEARCH.query_simple(self.AUTHOR, self.TITLE)
            
            # The next line fixes a test error that showed a 400 code. It was
            # caused by adding a feature that enables the AND joiner to
            # be customised per source + changing it so the default joiner
            # is that required by ORA. See also, test57_custom_andjoiner
            # below which tests the code but does not connect to the source.      
            self.SEARCH.AND_JOINER = self.JOINER
            
            self.SEARCH.get_documents()
            self.assertEqual(1, self.SEARCH.DOCS_FOUND)

    def test35_author(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_author(self.AUTHOR)
            self.SEARCH.get_documents()
            self.assertEqual(1, self.SEARCH.DOCS_FOUND)
         
    def test40_author2_notunique(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_author(self.AUTHOR2)
            self.SEARCH.get_documents()
            self.assertEqual(self.DOCS_EXPECTED, self.SEARCH.DOCS_FOUND)
        
    def do_idfetch_check(self):
        new_documents = self.SEARCH.get_documents()
        self.SEARCH.update_documents(new_documents)
        expected = '%s'%self.EID
        self.assertTrue(self.SEARCH.DOCUMENTS.has_key(expected))
        
    def test45_id_via_title_search(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_title(self.TITLE)
            self.do_idfetch_check()
    
    def test50_id_via_query(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_id(self.EID, prefix='')
            self.do_idfetch_check()
        
    def do_datetime(self):
        self.SEARCH.query_datetime(self.DATEFIELD, self.EDATE, self.ETIME)

    def check_date_expected(self):
        unused = self.SEARCH.get_documents()
        self.assertGreaterEqual(self.SEARCH.DOCS_FOUND, self.DATE_EXPECTED)
                
    def test55_date_query(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.do_datetime()
            self.check_date_expected()
    
    def prepare_authordate(self):
        self.do_prepare_api()
        self.SEARCH.AND_JOINER = self.JOINER # use custom and
        self.SEARCH.query_author(self.AUTHOR)
        self.do_datetime()
        
    def test57_custom_andjoiner(self):
        self.prepare_authordate()
        query = self.SEARCH.make_query()
        #url encoded query makes spaces become pluses
        expected = self.JOINER.replace(' ', '+')
        self.assertIn(expected, query)
        
    def test60_authordate_query(self):
        if ENABLE_REMOTE:
            self.prepare_authordate()
            self.do_idfetch_check()

    def test65_daterange(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_daterange(self.DATEFIELD,
                            self.EDATE, self.EDATE)
            self.check_date_expected()
        #self.show_query()            
        
    def test70_fieldlist(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.do_datetime()
            self.SEARCH.set_field_getlist(('id,title'))
            self.check_date_expected()

    def test75_sort_asc(self):
        self.do_prepare_api()
        self.do_datetime()
        self.SEARCH.set_sort('title')
        made = self.SEARCH.make_query()
        self.assertIn('title+asc', made)
    
    def test80_sort_desc(self):
        self.do_prepare_api()
        self.do_datetime()
        self.SEARCH.set_sort('title', True)
        made = self.SEARCH.make_query()
        self.assertIn('title+desc', made)
        
    def test85_sort_desc_remote(self):
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.do_datetime()
            self.SEARCH.set_sort('title', True)
            # add a test check returned data is sorted.
    
    def test45_author_nonascii(self):
        #NOT YET WORKING
        # Problem, plos does not like conversion for non-ascii  'ö'
        # to unicode code %C3%B6
        
        if ENABLE_REMOTE:
            self.do_prepare_api()
            self.SEARCH.query_author(self.AUTHOR_NONASCII)
            #self.show_query()
            #self.SEARCH.get_documents()
            #print self.SEARCH.DOCUMENTS
        
# ===============================================================
#  Enable use of these tests by external script.
# ===============================================================
SUITE_NAME = str(__name__)
TESTS_AVAILABLE = [TestApi, TestCustomQuery]
def suite(tests=TESTS_AVAILABLE):
    '''Return a test suite of tests so this can run run by external script.'''
    suite  = unittest.TestSuite()
    for test in tests:
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(test))
    return suite 
    
if __name__ == '__main__':
    # unittest.main(verbosity=2) # run all tests
    #   OR
    unittest.TextTestRunner(verbosity=2).run(suite()) # just those in suite
        