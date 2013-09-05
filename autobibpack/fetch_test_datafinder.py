'''Test the search interface against datafinder using solr'''
import unittest
import fetch

class TestDataFinderBasic(unittest.TestCase):
    '''Check the basic functionality of Solr search of datafinder.'''          
    def setUp(self):
        self.NAME = 'dfinder_solr'
        self.END = 'http://datafinder-d2v.bodleian.ox.ac.uk:8081/solr/select?'
        self.FIELD = 'silo'
        # We are going to use the following thesis as our test item.
        self.SILO = 'eprints'
        self.DATEFIELD = 'timestamp'
        self.TID = 'oai:generic-eprints-org:774'
        self.EDATE = '2012-08-21'
        self.ETIME = '15:13:33.521Z'
        self.DATEEMBARG = '2082-08-21'
        
        self.SEARCH = fetch.Search(self.NAME)
        
        # These expected results are correct as of 3rd September 2013
        self.EXPECTED_TOTAL = 331
        self.EXPECTED_DATERANGE_TOTAL = 1814
        self.EXPECTED_EMBARG_TOTAL = 175
        
    def do_endpoint(self):
        self.SEARCH.set_endpoint(self.END)
            
    def test100_returns_data(self):
        self.do_endpoint()
        self.SEARCH.query(self.FIELD, self.SILO)
        self.SEARCH.get_documents()
        self.assertGreaterEqual(self.SEARCH.DOCS_FOUND, self.EXPECTED_TOTAL) 
        
    def test105_exact_datetime(self):
        self.do_endpoint()
        self.SEARCH.query_datetime(self.DATEFIELD, self.EDATE, self.ETIME)
        self.SEARCH.get_documents()
        self.assertEqual(1, self.SEARCH.DOCS_FOUND)

    def test110_byid(self):
        self.do_endpoint()
        self.SEARCH.query_id(self.TID, prefix='')
        #print self.SEARCH.get_documents()
        
        #print self.SEARCH.DOCS_FOUND # returns 19 items, so id is not unique
    
    def test150_daterange(self):
        self.do_endpoint()
        self.SEARCH.query_daterange(self.DATEFIELD, self.EDATE, self.EDATE)
        self.SEARCH.get_documents()
        self.assertGreaterEqual(self.EXPECTED_DATERANGE_TOTAL, self.SEARCH.DOCS_FOUND)
        
    def test155_dateemargoeduntil(self):
        self.do_endpoint()
        self.SEARCH.query_daterange('embargoedUntilDate', self.DATEEMBARG, self.DATEEMBARG)
        self.SEARCH.get_documents()
        self.assertGreaterEqual(self.EXPECTED_EMBARG_TOTAL, self.SEARCH.DOCS_FOUND)
        
# ===============================================================
#  Enable use of these tests by external script.
# ===============================================================
SUITE_NAME = str(__name__)
TESTS_AVAILABLE = [TestDataFinderBasic, ]
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
        