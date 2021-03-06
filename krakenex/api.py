# This file is part of krakenex.
#
# krakenex is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# krakenex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public LICENSE along with krakenex. If not, see
# <http://www.gnu.org/licenses/gpl-3.0.txt>.


import json
import urllib

# private query nonce
import time

# private query signing
import hashlib
import hmac
import base64

from krakenex import connection


class API(object):
    """Kraken.com cryptocurrency Exchange API.
    
    Public methods:
    load_key
    query_public
    query_private
    
    """
    def __init__(self, key = '', secret = ''):
        """Create an object with authentication information.
        
        Arguments:
        key    -- key required to make queries to the API (default: '')
        secret -- private key used to sign API messages (default: '')
        
        """
        self.key = key
        self.secret = secret
        self.uri = 'https://api.kraken.com'
        self.apiversion = '0'


    def load_key(self, path):
        """Load key and secret from file.
        
        Argument:
        path -- path to file (string, no default)
        
        """
        with open(path, "r") as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()


    def _query(self, urlpath, req = {}, conn = None, headers = {}):
        """Low-level query handling.
        
        Arguments:
        urlpath -- API URL path sans host (string, no default)
        req     -- additional API request parameters (default: {})
        conn    -- kraken.Connection object (default: None)
        headers -- HTTPS headers (default: {})
        
        """
        url = self.uri + urlpath

        if conn is None:
            conn = connection.Connection()

        ret = conn._request(url, req, headers)
        return json.loads(ret)

    
    def query_public(self, method, req = {}, conn = None):
        """API queries that do not require a valid key/secret pair.
        
        Arguments:
        method -- API method name (string, no default)
        req    -- additional API request parameters (default: {})
        conn   -- connection object to reuse (default: None)
        
        """
        urlpath = '/' + self.apiversion + '/public/' + method

        return self._query(urlpath, req, conn)

    
    def query_private(self, method, req={}, conn = None):
        """API queries that require a valid key/secret pair.
        
        Arguments:
        method -- API method name (string, no default)
        req    -- additional API request parameters (default: {})
        conn   -- connection object to reuse (default: None)
        
        """
        urlpath = '/' + self.apiversion + '/private/' + method

        req['nonce'] = int(1000*time.time())
        postdata = urllib.urlencode(req)
        message = urlpath + hashlib.sha256(str(req['nonce']) +
                                           postdata).digest()
        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        headers = {
            'API-Key': self.key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        return self._query(urlpath, req, conn, headers)
