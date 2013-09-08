
class Ora(object):
    def __init__(self):
        self.ENDPOINT = 'http://ora.ox.ac.uk:8080/solr/core_metadata/select/?'

class Plos(object):
    def __init__(self):
        self.ENDPOINT = 'http://api.plos.org/search?'
        self.KEY = 'EMAILEDbyPLOS' # You need a key to enable this.
        self.URL_KEY_FIELD = 'api_key'
        self.AND_JOINER = ' AND '
        
class Datafinder8081(object):
    def __init__(self):
        self.ENDPOINT = 'http://datafinder-d2v.bodleian.ox.ac.uk:8081/solr/select?'
        
class Datafinder8000(object):
    def __init__(self):
        self.ENDPOINT = 'http://datafinder-d2v.bodleian.ox.ac.uk:8000/solr/select?'

        
