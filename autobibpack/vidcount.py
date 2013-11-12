'''Count the views and downloads for a set of items.

The aim of this module it is to automate reporting for groups
of items. It is intended for importing into other modules.

It has been tested using a SOLR endpoint to obtain lists
of items. With views and downloads data coming from a system
that does an offline collation of data that was
collected by Piwik Web Analytics.'''
import time, datetime
import urllib2, socket
import os

import fetch # Needed to discover which set of items we want data for.

ENABLE_STATIC_REMOTE = True # Fetch data from remote version

class ViewsAndDownloads(object):
    '''Calculate views and downloads for a set of item.
    
    This will search the endpoint to get a list of items
    and then total the views and downloads for those found. 
    '''
    def __init__(self, endpoint):
        '''Setup process, where list of items comes from endpoint.'''
        self.ENDPOINT = endpoint
        self.reset()
        
    # Setup the process
    # ===================================================    
    def reset(self):
        '''Reset report to starting point.'''
        self.FIELD = '' # the field to search
        self.VALUE = '' # the value to search for
        self.RAW_IDS = list() # a list of unique ids found
        self.REPORT_METHOD = dict() # a log of the methods used
        self.REPORT_ITEMS = list() # a log of data for items
        self.VIEWS = 0 # total number of views
        self.DOWNLOADS = 0 # total number of downloads
        self.READY = False # disable the process until search is setup.
    
    def set_search(self, value, field):
        '''Configure the value and field to search for.'''
        self.FIELD = field
        self.VALUE = value.lower()
        self.READY = True

    #  Fields where results have been checked.
    # ===================================================           
    def set_recordContentSource(self, value):
        '''Use to get views and downloads for a particular record source.'''
        self.set_search(value, 'recordContentSource')

    def set_funder(self, value):
        '''Use to get views downloads for a particular funder.'''
        self.set_search(value, 'funder')
        
    #  Get the item IDs and totals
    # ===================================================        
    def _fetch_ids(self):
        '''Obtain the IDs for the items we want to get totals for.'''
        start = time.time()
        search = fetch.Search('IDs fetching')
        ids, log = search.auto_list_ids(self.ENDPOINT, self.VALUE, self.FIELD)
        self.REPORT_METHOD.update(log)
        self.RAW_IDS = ids
        self.REPORT_METHOD['3a. Seconds taken to find IDs'] = time.time()-start 
        
    def url_source(self, item):
        '''Return the URL pattern for fetching data.'''
        d1 = item[5:7] # skip 'uuid:' and get first 2 chars 
        d2 = item[7:9] # directory level 2 is the next 2 chars
        fname = item[9:] # the filename is the rest of the uuid
        sub = '/results/dv/%s/%s/%s'%(d1,d2,fname)
        staturl = 'http://orastats.bodleian.ox.ac.uk%s'%sub
        return staturl, sub
    
    def static_remote(self, address):
        '''Get the data from a static remote file in location address.'''
        try:
            indata = urllib2.urlopen(address, timeout=5.0)
            stats = indata.read()
            indata.close()
            error_open = False
            clean = 1
        except (urllib2.URLError, urllib2.HTTPError, socket.error):
            error_open = True
            clean = 0
            stats = '0;0'
        return stats, clean, error_open
    
    def static_local(self, filepath, root='/var/www/'):
        '''Get data from a static local file.'''
        indata = '%s%s'%(root,filepath)
        try:
            infile = file(indata)
            stats = infile.read()
            infile.close()
            error_open = False
            clean = 1
        except IOError:
            error_open = True
            clean = 0
            stats = '0;0'
        return stats, clean, error_open
                                    
    def get_stat(self, item):
        '''Get the views and downloads for a single item.'''
        address, subpath = self.url_source(item)
        
        # Try and get from local file or remote source.
        stats, clean, error_open = self.static_local(subpath)
        if error_open and ENABLE_STATIC_REMOTE:
            stats, clean, error_open = self.static_remote(address)
        
        # Extract the downloads and views.
        error_index = False
        bits = stats.split(';')
        try:
            d = bits[0].strip()
            downs = int(d)
        except IndexError:
            error_index = True
            clean = 0
            downs = 0
        try:
            v = bits[1].strip()
            views = int(v)
        except IndexError:
            error_index = True
            clean = 0
            views = 0
        return views , downs, address, clean, error_open, error_index
            
    def _get_stats(self):
        '''Get the views and downloads for all items.'''
        start = time.time()
        self.REPORT_ITEMS.append('views\tdownloads\titem\tsource\n')
        count = 0
        errors_opening = 0
        errors_index = 0
        clean_count = 0
        
        # Process all the found ids.
        for item in self.RAW_IDS:
            count += 1 
            views, downs, source, clean, eopen, eindex = self.get_stat(item)
            clean_count += clean
            errors_opening += eopen
            errors_index += eindex
            result = '%s\t%s\t%s\t%s\n'%(views, downs, item, source)
            self.REPORT_ITEMS.append(result)
            self.VIEWS += views
            self.DOWNLOADS += downs
            #if count == 10:
            #    break
            #time.sleep(0.1)
        
        # Store results
        self.REPORT_METHOD['4a. Result IDs checked.'] = count
        self.REPORT_METHOD['4b. Number with results'] = clean_count
        self.REPORT_METHOD['4b. Timeout issues'] = errors_opening
        self.REPORT_METHOD['4c. Decode issues'] = errors_index
        self.REPORT_METHOD['4d. Seconds taken get results'] = time.time()-start
        v = self.VIEWS
        d = self.DOWNLOADS
        self.REPORT_ITEMS.append('%s\t%s\tTotals for all items.\n'%(v,d))
        self.REPORT_METHOD['4e. Total number of views'] = v
        self.REPORT_METHOD['4f. Total number of downloads'] = d
            
    def run(self):
        '''Run the report to get views and downloads.'''
        if not self.READY:
            raise AttributeError
        when = str(datetime.datetime.now())
        self.REPORT_METHOD['1. Process start time'] = when
        self._fetch_ids()
        self._get_stats()
        when = str(datetime.datetime.now())
        self.REPORT_METHOD['9. Process end time'] = when
        
    #  Output the results
    # ===================================================        
    def output_dir(self, root=None):
        '''Return the location the report should be output to.'''
        if not root:
            root = os.path.join(os.getcwd(),'vidcount_export')
        outdir = os.path.join(root, self.FIELD, self.VALUE)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        return outdir
            
    def report_method(self):
        '''Return a summary of the method.'''
        lines = list()
        keys = self.REPORT_METHOD.keys()
        keys.sort()
        lines.append('Report code\tResult')
        for key in keys:
            lines.append('%s\t%s'%(key,self.REPORT_METHOD[key]))
        return '\n'.join(lines)
    
    def header(self, w=None):
        '''Return the header for the report.'''
        if not w:
            w = time.strftime('%y-%m-%d at %H:%M:%S', time.gmtime())
        answer = 'Report for - %s - %s on %s\t\n'%(self.FIELD, self.VALUE, w)
        answer += '%s\tViews\n'%self.VIEWS
        answer += '%s\tDownloads\n'%self.DOWNLOADS
        answer += '\n'
        return answer

    def save_summary(self, path, when):
        '''Save the current views and downloads to a running summary.'''
        allfile = os.path.join(path, 'summary_%s.tsv'%self.VALUE)
        if not os.path.exists(allfile):
            outfile = file(allfile, 'w')
            outfile.write('Date\tTime\tViews\tDownloads\n')
            outfile.close()
        d, t = when.split(' at ') # Want date and time in columns
        line = '%s\t%s\t%s\t%s\n'%(d, t, self.VIEWS, self.DOWNLOADS)
        outfile = file(allfile, 'a')
        outfile.write(line)        
        outfile.close()
                    
    def save_results(self, root=None, summary=True, items=True, ext='txt'):
        '''Save a report of the views and downloads.'''
        outdir = self.output_dir(root)    
        when = time.strftime('%y-%m-%d at %H:%M:%S', time.gmtime())
        self.save_summary(outdir, when)
        outpath = os.path.join(outdir, '%s.%s'%(when, ext))                      
        outfile = file(outpath, 'w')
        outfile.write(self.header(when))
        if summary:
            pro = 'Processing summary =====================\n'
            pro += self.report_method()
            outfile.write(pro)
        if items:
            outfile.write('\n\nResults for each item.===================\n')
            outfile.writelines(self.REPORT_ITEMS)
        else:
            outfile.write('\n')

        outfile.close()    
        
if __name__ == '__main__':
    import sources
    end = sources.Ora().ENDPOINT
    s = ViewsAndDownloads(end) # set the location we will get discover IDs
    s.set_funder('jisc') # set the IDs we want to get
    s.run() # fetch the ids and calculate the views and downloads
    #print s.report_method() # see the method summary
    s.save_results() # save the results to file system
