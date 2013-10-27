'''Test the search interface against ORA using Solr.

This tests the core features which should
be the same for most sources.'''
import unittest
import fetch
from sources import Ora

class TestOraBasic(unittest.TestCase):
    '''Check the basic functionality of the Solr bibliographic search.'''          
    def setUp(self):
        self.NAME = 'ora_solr'
        self.END = Ora().ENDPOINT
        self.FIELD = 'author'
        # We are going to use the following thesis as our test item.
        # http://ora.ox.ac.uk/objects/uuid:83530474-369e-417b-a8db-ac06ebf42c84
        self.AUTHOR = 'cummings'
        self.TITLE = 'neural control of convergence eye movements'
        self.EID = '83530474-369e-417b-a8db-ac06ebf42c84'
        self.SEARCH = fetch.Search(self.NAME)
        self.DATEFIELD = 'timestamp'
        self.EDATE = '2013-01-21'
        self.ETIME = '11:14:22.227Z'
        self.EDATETIME = '%sT%s'%(self.EDATE, self.ETIME)
        self.JOINER = '&'
        
        # These expected value might change. Correct as of 18th July 2013
        # The total expected is due to ORA defaulting return 10 rows.
        self.TOTAL_EXPECTED = 10
        self.ROWS_EXPECTED = 2
        self.DOCS_EXPECTED = 334
        self.TITLE_NOQUOTES_EXPECTED = 112100
        self.TOTAL_DATERANGE = 250
        # Total until able to explain why it has changed. 
        self.TOTAL_DATERANGE = 248
 
    #  Basic checks the query is constructed okay, before calling source
    # ===============================================================
    def test100_default(self):
        self.assertEqual(self.NAME, self.SEARCH.NAME)
        self.assertFalse(self.SEARCH.make_query())
    
    def do_endpoint(self):
        self.SEARCH.set_endpoint(self.END)
            
    def test105_endpoint(self):
        self.do_endpoint()
        self.assertEqual(self.END, self.SEARCH.END_POINT)
    
    def check_query(self):
        '''This will check the two ways of setting queries.'''
        self.assertIn(self.FIELD, self.SEARCH.QUERYCOLON)
        self.assertEqual(self.AUTHOR, self.SEARCH.QUERYCOLON[self.FIELD])
        
    def test110_query(self):
        self.SEARCH.query(self.FIELD, self.AUTHOR)
        self.check_query()  
    
    def do_author(self):
        self.SEARCH.query_author(self.AUTHOR)
        
    def test115_query_author(self):
        self.do_author()
        self.check_query()
        
    def test120_make_colon(self):
        self.do_author()
        result = self.SEARCH.make_colon()
        self.assertEqual(result, '%s:%s'%(self.FIELD, self.AUTHOR))
        
    def test125_make_and_default(self):
        self.do_author()
        result = self.SEARCH.make_and()
        items = [self.FIELD, self.AUTHOR, 'wt', 'json']
        for item in items:
            self.assertIn(item, result)
        
    def test126_make_and_noquery(self):
        self.do_endpoint()
        result = self.SEARCH.make_and()
        # the query should be *:* but this gets url encoded so test raw values
        star = r'%2A'
        colon = r'%3A'
        self.assertTrue(result.startswith('q=%s%s%s'%(star, colon, star)))
        
    def show_query(self): 
        self.SEARCH.set_indent()
        made = self.SEARCH.make_query()
        print
        print made
        print
        
    #  Call the source with query and do a simple check of results.
    # ===============================================================
    def do_prepare_query(self):
        self.do_endpoint()
        self.do_author()
        
    def test130_fetch_data(self):
        self.do_prepare_query()
        data = self.SEARCH.fetch_data()
        #print len(data)
        self.assertLess(20000, len(data)) # len=29543 as of July 18th 2013

    def get_header_bit(self, header, bit):
        head = 'responseHeader'
        pa = 'params'
        return header[head][pa][bit]
            
    def test135_get_json_response(self):
        self.do_prepare_query()
        answer = self.SEARCH.get_json_raw()
        wt = self.get_header_bit(answer, 'wt')
        q = self.get_header_bit(answer, 'q')
        self.assertEqual(wt, 'json')
        self.assertEqual(q, '%s:%s'%(self.FIELD, self.AUTHOR))
    
    def do_get_docs(self):
        self.do_prepare_query()
        self.assertEqual(self.SEARCH.DOCS_FOUND, 0)
        return self.SEARCH.get_documents()
    
    def test140_get_documents(self):
        docs = self.do_get_docs()
        self.assertGreaterEqual(self.TOTAL_EXPECTED, len(docs))
        self.assertGreaterEqual(self.SEARCH.DOCS_FOUND, self.DOCS_EXPECTED) 
        
    def test145_update_documents(self):
        docs = self.do_get_docs()
        self.SEARCH.update_documents(docs)
        self.assertGreaterEqual(self.TOTAL_EXPECTED, len(docs))
        
    #  Test optional items in the query string
    # ===============================================================
    def do_row_limit(self):
        self.SEARCH.set_rows(self.ROWS_EXPECTED) # change default query
        
    def test150_setrows(self):
        self.do_prepare_query()
        self.do_row_limit()
        docs = self.SEARCH.get_documents()
        self.assertGreaterEqual(self.ROWS_EXPECTED, len(docs))
    
    def test155_setstart(self):
        self.do_prepare_query()
        self.SEARCH.set_start(self.ROWS_EXPECTED)
        answer = self.SEARCH.get_json_raw()
        result = self.get_header_bit(answer, 'start')
        self.assertEqual(str(self.ROWS_EXPECTED), result)

    def test160_next_start(self):
        self.do_prepare_query()
        self.assertEqual(self.SEARCH.NEXT_START, 0)
        self.do_get_docs()
        self.assertEqual(self.SEARCH.NEXT_START, 11)
    
    def test165_next_start_url(self):
        self.do_get_docs()
        self.SEARCH.set_start(self.SEARCH.NEXT_START)
        self.assertIn('start=11',self.SEARCH.make_query())
        
    #  Test title searches in the query string
    # ===============================================================
    def test170_title(self):
        self.do_endpoint()
        self.SEARCH.query_title(self.TITLE)
        expected = '"%s"'%self.TITLE
        self.assertEqual(expected, self.SEARCH.QUERYCOLON['title'])
        bits = self.TITLE.split(' ')
        made = self.SEARCH.make_query()
        for bit in bits:
            self.assertIn(bit, made) 
    
    def test175_title_getdata(self):
        self.do_endpoint()
        self.SEARCH.query_title(self.TITLE)
        self.SEARCH.get_documents()
        self.assertEqual(1, self.SEARCH.DOCS_FOUND)
        
    def test180_title_noquotes(self):
        self.do_endpoint()
        self.SEARCH.query_title(self.TITLE, False) # make it so quotes not used
        self.assertEqual(self.TITLE, self.SEARCH.QUERYCOLON['title'])
        bits = self.TITLE.split(' ')
        made = self.SEARCH.make_query()
        for bit in bits:
            self.assertIn(bit, made)
        
    def test175_title_noquotes_data(self):
        self.do_endpoint()
        self.SEARCH.query_title(self.TITLE, False)
        self.SEARCH.set_rows('2')
        self.SEARCH.get_documents()
        self.assertGreater(self.SEARCH.DOCS_FOUND, self.DOCS_EXPECTED)    
    
    #  Test other searches in query string
    # ===============================================================
    def test180_authortitle(self):
        self.do_endpoint()
        self.SEARCH.query_simple(self.AUTHOR, self.TITLE)
        self.SEARCH.get_documents()
        self.assertEqual(1, self.SEARCH.DOCS_FOUND)
    
    def do_uuid(self):
        '''This will search ORA and test the returned UUID.'''
        new_documents = self.SEARCH.get_documents()
        self.SEARCH.update_documents(new_documents)
        expected = 'uuid:%s'%self.EID
        self.assertTrue(self.SEARCH.DOCUMENTS.has_key(expected))
        
    def test185_id_via_title_search(self):
        self.do_endpoint()
        self.SEARCH.query_title(self.TITLE)
        self.do_uuid()
    
    def test190_id_via_query(self):
        self.do_endpoint()
        self.SEARCH.query_id(self.EID)        
        self.do_uuid()
        
    #  Test date queries
    # ===============================================================
    def test195_date_query(self):
        self.do_endpoint()
        self.SEARCH.query_datetime(self.DATEFIELD, self.EDATE, self.ETIME)
        self.do_uuid()
        text = self.SEARCH.DOCUMENTS['uuid:%s'%self.EID]
        expected = text[self.DATEFIELD]
        self.assertEqual(expected, self.EDATETIME)
            
    def test200_default_andjoiner(self):
        self.assertEqual(self.SEARCH.AND_JOINER, self.JOINER)
        self.do_endpoint()
        self.SEARCH.query_datetime(self.DATEFIELD, self.EDATE, self.ETIME)
        query = self.SEARCH.make_query()
        self.assertIn(str(self.JOINER).replace(' ', '+'), query)
    
    def test205_daterange(self):
        self.do_endpoint()
        self.SEARCH.query_daterange(self.DATEFIELD, self.EDATE, self.EDATE)
        self.SEARCH.get_documents()
        #self.show_query()
        
        # In theory, the number of items added on a certain day will not
        # change. Also, since we never delete stuff from ORA, if this number
        # does change it will only be to increase.
        self.assertGreaterEqual(self.SEARCH.DOCS_FOUND, self.TOTAL_DATERANGE)
        
        # But, we can test the above theory. If this test fails you would
        # need to check if bulk loading or something else is likely to
        # have caused this. If the theory is wrong then you will have to
        # disable this test or update TOTAL_DATERANGE with the latest number.
        m = 'Num of items added to ORA on the test day has changed, why?' 
        self.assertEqual(self.SEARCH.DOCS_FOUND, self.TOTAL_DATERANGE, m) 
        
    def test210_fieldlist(self):
        self.do_endpoint()
        self.do_author() 
        self.SEARCH.set_field_getlist(('id,title'))
        docs = self.SEARCH.get_documents()
        self.assertGreaterEqual(self.SEARCH.DOCS_FOUND, self.DOCS_EXPECTED)
        for item in range(len(docs)): # test each doc has both field.
            data = docs[item]
            self.assertEqual(len(data), 2)
            self.assertTrue(data.has_key('id'))
            self.assertTrue(data.has_key('title'))
            self.assertTrue(str(data['id']).startswith('uuid')),
            self.assertTrue(len(data['title']) > 5) #Check it is not empty
    
    #  Trigger printing of items, good for developing tests. 
    # ===============================================================
    def notest999_print_json(self):
        self.do_prepare_query()
        text = self.SEARCH.get_json_raw()
        print self.SEARCH.pprint_json(text)
        
    def notest999_print_documents(self):
        self.do_prepare_query()
        text = self.SEARCH.get_documents()
        print self.SEARCH.pprint_json(text)

    
class TestOraLonger(unittest.TestCase):
    '''Check the basic functionality of the Solr bibliographic search.'''          
    def setUp(self):
        self.NAME = 'ora_solr'
        self.END = Ora().ENDPOINT
        self.FIELD = 'author'
        self.AUTHOR = 'cummings'
        self.SEARCH = fetch.Search(self.NAME)
    
    def do_prepare_query(self):
        self.SEARCH.set_endpoint(self.END)
        self.SEARCH.query_author(self.AUTHOR)
        
    def notest160_all_rows(self):
        self.do_prepare_query()
        rwanted = self.SEARCH.MAX_ROWS
        self.SEARCH.set_rows(rwanted)
        text = self.SEARCH.get_documents()
        expected = 334 # as of July 23rd 2013
        self.assertGreaterEqual(len(text), expected)
        
    def notest170_get_all(self):
        self.do_prepare_query()
        self.SEARCH.get_all()
        print len(self.SEARCH.DOCUMENTS)
    
class TestOraAuto(unittest.TestCase):
    '''Check the methods that combine different parts of the system.'''          
    def setUp(self):
        self.NAME = 'ora_solr_idlist'
        self.END = Ora().ENDPOINT
        self.FIELD = 'recordContentSource'
        self.VALUE = 'polonsky'
        # Did a visual check of ORA to confirm this id is from the source above.
        self.CHECK_ID = 'uuid:278c6978-9421-46af-af61-a062a2044591'   
        self.SEARCH = fetch.Search(self.NAME)
        self.TOTAL_EXPECTED = 1242
        
    def do_get(self, end, value, field):
        return self.SEARCH.auto_list_ids(end, value, field)
    
    def test100_basic(self):
        ids, log = self.do_get(self.END, self.VALUE, self.FIELD)
        self.assertIn(self.CHECK_ID, ids)
        self.assertGreaterEqual(len(ids), self.TOTAL_EXPECTED)
        self.assertEqual(len(log), 5)
        
# ===============================================================
#  Enable use of these tests by external script.
# ===============================================================
SUITE_NAME = str(__name__)
#TESTS_AVAILABLE = [TestOraBasic, TestOraLonger, TestOraAuto]
TESTS_AVAILABLE = [TestOraBasic, TestOraAuto, ] # disable longer tests
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
        