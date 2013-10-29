#!/usr/bin/env python
'''Do the views and downloads reports for ORA.'''
import logging
import time # used to put a gap between reports

import sources # needed for endpoint
import vidcount # needed to get views and downloads
              
class Report():
    def __init__(self):
        self.END = sources.Ora().ENDPOINT
        self.SLEEP = 10 # how long should it wait between multiple reports.
        self.LIST_FUNDERS = ('JISC', 'wellcome')
        self.LIST_CONTENT_SOURCES = ('polonsky',)
        self.LIST_CUSTOM = (('issn','1545-9993'),
                            ('author', 'comina'),
                            )
    def run(self):
        '''Run the standard reports'''
        self.do_funders()
        self.do_contentsources()
        self.do_custom_reports()
            
    def do_funders(self, funders=None):
        '''Do all the reports for funders.'''
        logging.info('Doing funders reports')
        if not funders:
            funders = self.LIST_FUNDERS 
        for funder in funders:
            logging.debug('Doing funder: %s'%funder)
            s = vidcount.ViewsAndDownloads(self.END)
            s.set_funder(funder)
            s.run()
            s.save_results()
            time.sleep(self.SLEEP)    
    
    def do_contentsources(self, sources=None):
        '''Do all the reports for content sources.'''
        logging.info('Doing content sources reports')
        if not sources:
            sources = self.LIST_CONTENT_SOURCES
        for source in sources:
            logging.debug('Doing content source: %s'%source)
            s = vidcount.ViewsAndDownloads(self.END)
            s.set_recordContentSource(source)
            s.run()
            s.save_results()
            time.sleep(self.SLEEP)    

    def do_custom_reports(self, customs=None):
        '''Do all the custom reports.'''
        logging.info('Doing custom reports.')
        if not customs:
            customs = self.LIST_CUSTOM
        for custom in customs:
            field = custom[0]
            value = custom[1]
            logging.debug('Doing custom: %s=%s'%(field, value))
            self.do_custom(value, field)
            time.sleep(self.SLEEP)

    def do_custom(self, value, field):
        '''Do a single custom report where field'''
        s = vidcount.ViewsAndDownloads(self.END)
        s.set_search(value, field)
        s.run()
        s.save_results()
        return s.report_method()
        
if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    reports = Report()
    reports.run()
