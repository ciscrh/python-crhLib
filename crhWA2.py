# crhWA2.py -- wild apricot api v2 helper library for python v2.7
# essential functionality derived from the python v3 sample code by dsmirnov@wildapricot.com
# converted to python v2.7, extra functionality added 
# & updated to use application-based authentication (june-15) by crh
# no write to wa server functionality included
# Copyright (c) 2015 CR Hailey
# v0.91 crh 03-jun-15 -- development version
# v0.92 crh 21-jun-15 -- investigating the new application-based authentication

# written on a windows platform using python v2.7
# do not import crh library modules into this module

#!/usr/local/bin/python


'''
This module provides set of classes for working with WildApricot public API v2.
Public API documentation can be found here: http://help.wildapricot.com

Example:
    api = crhWA2.WaAPI2()
    api.authClientSecret("admin@youraccount.com", "your_password", "client_id", "client_secret")
    accounts = api.execRequest("/v2/accounts")
    for account in accounts:
        print(account.PrimaryDomainName)
        
Response format is JSON by default & most methods assume this unless they state otherwise
'''
import datetime
import urllib
import urllib2
import json
import base64

# handle compression to reduce bandwidth
from StringIO import StringIO
import gzip

from sys import stderr

_libName = 'crhWA2' # used by _statusErrMsg()

class WaAPI2(object):
    '''
    Wild apricot API V2 client
    '''
    ## class attributes
    _authEndpoint = 'https://oauth.wildapricot.org/auth/token'
    _apiEndpoint = 'https://api.wildapricot.org'
    _allScopes = 'account_view contacts_view event_registrations_view events_view finances_view membership_levels_view'
    _verbose = False # extra output to stderr, for testing/debugging purposes

    ## class methods
    @classmethod
    def printContact(cls, contact, full =  True, ascii = True, tab = 4):
        '''
        print contact details
        contact -- contact record?
        full    -- print contact.FieldValues
        ascii   -- convert field values to ascii for printing
        tab     -- nr of spaces in each indent
        '''
        spacer = ' '*tab
        print('Contact details for ' + contact.DisplayName + ' (' + contact.Email + ')')
        print('Main info...')
        print(spacer + '{: <14}: '.format('ID') + str(contact.Id))
        print(spacer + '{: <14}: '.format('First Name') + contact.FirstName)
        print(spacer + '{: <14}: '.format('Last Name') + contact.LastName)
        print(spacer + '{: <14}: '.format('Email') + contact.Email)
        if full:
            print(spacer + 'Contact fields...')
            for field in contact.FieldValues:
                if isinstance(field.Value, ApiObject):   # can happen
                    print(spacer*2 + '{: <12}... '.format(field.FieldName))
                    for valueName, valueValue in field.Value.attribGen():
                        print(spacer*3 + '{: <14}: '.format(valueName) + cls._pretty(valueValue, ascii))
                elif isinstance(field.Value, list):   # can also happen
                    print(spacer*2 + '{: <12}... '.format(field.FieldName))
                    for item in field.Value:
                        if isinstance(item, ApiObject): # usually is
                            for itemName, itemValue in item.attribGen():
                                print(spacer*3 + '{: <14}: {}'.format(itemName, cls._pretty(itemValue, ascii)))
                elif field.Value is not None:
                    if ascii and isinstance(field.Value, unicode):
                        print(spacer*2 + '{: <14}: {}'.format(field.FieldName, cls._ascii(field.Value, newline = True)))
                    else:
                        print(spacer*2 + '{: <14}: '.format(field.FieldName) + repr(field.Value))

    @classmethod
    def printGrp(cls, group, full = True, ascii = True, tab = 4):
        '''
        print group details
        group -- group dictionary list?
        full  -- print all group values
        ascii -- convert field values to ascii for printing
        tab   -- nr of spaces in each indent
        '''
        if group is None:   # can be the case if invalid groupID given to getGrps()
            if cls._verbose: _statusErrMsg('warn', 'WaAPI2.printGrp()', 'group is set to None')
            return
        spacer = ' '*tab
        
        print('Group details for: ' + cls._pretty(group.Name, ascii))

        print(spacer + '{: <13}: '.format('ContactsCount') + cls._pretty(group.ContactsCount, ascii))
        print(spacer + '{: <13}: '.format('Id') + cls._pretty(group.Id, ascii))
        if not full: return
        
        try:    # ContactIds often doesn't exist so fail gracefully & continue
            print(spacer + '{: <13}: '.format('ContactIds') + cls._pretty(group.ContactIds, ascii))
        except AttributeError: pass
        print(spacer + '{: <13}: '.format('Description') + cls._pretty(group.Description, ascii))
        print(spacer + '{: <13}: '.format('Url') + cls._pretty(group.Url, ascii))
        print(spacer + '{: <13}: '.format('Name') + cls._pretty(group.Name, ascii))

    @classmethod
    def verbose(cls, verbose = None):
        '''
        set/get verbose state & return it
        '''
        if verbose is not None: cls._verbose = verbose
        return cls._verbose
        
    ## private class methods
    @classmethod
    def _pretty(cls, value, ascii = False):
        '''
        printing housekeeping returns printable version of value
        do not use to convert unicode string to ascii string
        '''
        if value is None:
            if ascii:
                return 'null'
            else:
                return u'null'
        elif ascii and isinstance(value, unicode):  # error handler substitutes a ? character
            return value.encode('ascii', 'replace').replace(r'\n', '<newline>')
        elif isinstance(value, unicode):
            pass
        return repr(value)
    
    @classmethod
    def _ascii(cls, uStr, errHandler = 'replace', newline = False):
        '''
        converts unicode string to ascii string & returns it
        uStr    -- unicode string
        handler -- encode error handler (default: 'replace', which replaces unicode characters
                   with no valid ascii equivalent with a question mark character)
                   alternative handlers include 'strict' (raises UnicodeError), 'ignore',
                   'xmlcharrefreplace' & 'backslashreplace'
        newline -- replaces newline characters with <newline> if true (default: False)
        '''
        if newline:
            return uStr.encode('ascii', errHandler).replace(r'\n', '<newline>')
        else:
            return uStr.encode('ascii', errHandler)
        
    ## instance methods
    def __init__(self):
        '''
        constructor
        '''
        self._accounts = None
        self._authHdr = None
        self._token = None

    def authClientSecret(self, username, password, clientID, clientSecret, scope=None):
        '''
        authenticate using crhWA2 application client credentials & store result for exeRequest method
        username     -- wa username
        password     -- wa password
        clientID     -- wa app client ID previously generated from wa admin account
        clientSecret -- wa app client secret previously generated from wa admin account
        scope        -- optional scope of authentication request. If None full list of API scopes will be used
        '''
        scope = self._allScopes if scope is None else scope
        data = {"grant_type": "password", "username": username, "password": password, "scope": scope}
        encodedData = urllib.urlencode(data).encode()
        request = urllib2.Request(self._authEndpoint, encodedData)
        request.add_header("ContentType", "application/x-www-form-urlencoded")
        authHeader = base64.standard_b64encode((clientID + ':' + clientSecret).encode()).decode('utf-8')
        self._authHdr = authHeader  # needed when refreshing token
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.authClientSecret()', 'data: {}'.format(data))
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.authClientSecret()', 'authHeader: {}'.format((clientID + ':' + clientSecret).encode()))
        request.add_header("Authorization", 'Basic ' + authHeader)
        response = urllib2.urlopen(request)
        self._token = WaAPI2._parseResponse(response)
        self._tokenRetrievedAt = datetime.datetime.now()
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.authClientSecret()', self._token)

    def authAppKey(self, appKey, scope=None):
        '''
        authenticate using crhWA2 application key & store result for executeRequest method
        apiKey -- wa app key previously generated from wa admin account
        scope  -- optional scope of authentication request. If None full list of API scopes will be used
        '''
        if scope is None: scope = self._allScopes
        data = {"grant_type": "client_credentials", "scope": scope}
        encodedData = urllib.urlencode(data).encode()
        request = urllib2.Request(self._authEndpoint, encodedData)
        request.add_header("ContentType", "application/x-www-form-urlencoded")
        authHeader = base64.standard_b64encode(('APIKEY:' + appKey).encode())
        self._authHdr = authHeader  # needed if refreshing token
        request.add_header("Authorization", 'Basic ' + authHeader)
        response = urllib2.urlopen(request)
        self._token = WaAPI2._parseResponse(response)
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.authAppKey()', self._token)
        self._tokenRetrievedAt = datetime.datetime.now()

    def execRequest(self, apiURL, json = True, raw = False, apiRequestObject = None, compress = False):
        '''
        perform api request and return result as an instance of ApiObject or list of ApiObjects
        apiURL           -- absolute or relative api resource url
        json             -- response format is either json (default) or xml
        raw              -- return result as raw json code or xml code instead of instance or list
        apiRequestObject -- any json serializable object to send to API
        method           -- HTTP method of api request 
                            [Default: GET if apiRequestObject is None else POST]
        compress         -- use gzip compression to reduce bandwidth (default = False)
        '''
        if (not json) and (not raw):
            raise RuntimeError('WaAPI2.execRequest() -- xml only allowable in raw mode')
        gzipData = compress # hint, updated later
        if self._token is None:
            raise RuntimeError('WaAPI2.execRequest() -- no access token available')
        elif not True:  # check if token has timed out & renew if necessary
            pass
        if not apiURL.startswith("http"):
            apiURL = self._apiEndpoint + apiURL
        request = urllib2.Request(apiURL)
        if apiRequestObject is not None:    # "GET" method used
            request.data = json.dumps(apiRequestObject, cls=_ApiObjectEncoder).encode()
            if self._verbose: _statusErrMsg('info', 'WaAPI2.execRequest()', request.data)
        request.add_header("Content-Type", "application/json")
        if compress: # save bandwidth for large responses :-)
            request.add_header("Accept-Encoding", "gzip")
        if json:    # default: most methods assume response data is in json format
            request.add_header("Accept", "application/json")
        else:   # brave decision!
            request.add_header("Accept", "application/xml")
        request.add_header("Authorization", "Bearer " + self._getToken())

        response = urllib2.urlopen(request)
        gzipData = response.info().get('Content-Encoding') == 'gzip'
        if self._verbose and gzipData: _statusErrMsg('info', 'WaAPI2.execRequest()', 'response Content-Encoding: gzip')
        if not raw: # default case
            return WaAPI2._parseResponse(response, gzipData)
        elif gzipData:  # decompress data before returning it
            compData = StringIO( response.read())
            decompData = gzip.GzipFile(fileobj=compData)
            return decompData.read().decode('utf-8')        
        else:   # not compressed
            return response.read().decode('utf-8')

    def accounts(self):
        '''
        retrieve & store accounts data from WA site
        '''
        if self._accounts is None:
            self._accounts = self.execRequest('/v2/accounts')
            if self._verbose: _statusErrMsg('info', 'WaAPI2.accounts()', self._accounts[0].PrimaryDomainName)
        return self._accounts
    
    def getContacts(self, json = True, raw = False, top = None, skip = None, filter = None, select = None, compress = True):
        '''
        retrieve contact records object
        json     -- return as json if true (default), or as xml otherwise
        raw      -- return as raw json code if false (default) or xml code otherwise
        top      -- max nr of records to retrieve [None -> all records]
        skip     -- nr of records to skip before staring retrieval [None -> start at beginning]
        filter   -- filter expression [None -> do not specify filter]
        select   -- select fields from FieldValues [None -> retrieve all fields]
        compress -- use gzip compression to reduce bandwidth (default = True)
        '''
        params = {'$async': 'false'}
        if filter is not None: params['$filter'] = str(filter)
        if select is not None: params['$select'] = str(select)
        if top is not None: params['$top'] = str(top)
        if skip is not None: params['$skip'] = str(skip)
        contactsURL = next(res for res in self._accounts[0].Resources if res.Name == 'Contacts').Url
        requestURL = contactsURL + '?' + urllib.urlencode(params)
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.getContacts()', requestURL)
        if not raw: # default case
            return self.execRequest(requestURL, json = json, raw = False, compress = compress).Contacts
        else:
            return self.execRequest(requestURL, json = json, raw = True, compress = compress)
    
    def getGrps(self, groupID = None, xml = False, raw = False, compress = True):
        '''
        retrieve group records object
        groupID -- used to get single group record (returns None if no matching record)
                   note that getting a single group gives ContactIds attribute
                   if default value of None is used then all group records retrieved
        xml     -- return as xml if true, or as json otherwise (dafault)
        raw     -- return as raw json code if false (default) or xml code otherwise
        compress -- use gzip compression to reduce bandwidth (default = True)
        '''
        params = {'$async': 'false'}
        groupsURL = next(res for res in self._accounts[0].Resources if res.Name == 'Member groups').Url
        if groupID is not None:
            groupsURL += '{}'.format(groupID)
        requestURL = groupsURL + '?' + urllib.urlencode(params)
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2.getGrps()', requestURL)
        try:
            if not raw: # default case
                return self.execRequest(requestURL, json = not xml, compress = compress)
            else:
                return self.execRequest(requestURL, json = not xml, raw = True, compress = compress)
        except urllib2.HTTPError as e:
            _statusErrMsg('error', 'WaAPI2.getGrps()', 'groupID {} is not valid'.format(groupID))
            return None
    
    ## private methods
    #### this needs revising to use new authentication protocols ####
    def _getToken(self):
        '''
        retrieve authentication token for exeRequest(), automatically refreshing token if expired
        '''
        expires_at = self._tokenRetrievedAt + datetime.timedelta(seconds=self._token.expires_in)
        if datetime.datetime.now() > expires_at:
            self._refreshToken()
        return self._token.access_token

    def _refreshToken(self):
        '''
        refresh authentication token
        '''
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2._refreshToken()', 'access token being refreshed')
        if self._authHdr is None:
            raise RuntimeError('WaAPI2._refreshToken() -- no authHeader available')
        data = {"grant_type": "refresh_token", "refresh_token": self._token.refresh_token}
        encoded_data = urllib.urlencode(data).encode()
        request = urllib2.Request(self._authEndpoint, encoded_data)
        request.add_header("ContentType", "application/x-www-form-urlencoded")
        authHeader = self._authHdr
        request.add_header("Authorization", 'Basic ' + authHeader)
        response = urllib2.urlopen(request)
        self._token = WaAPI2._parseResponse(response)
        self._tokenRetrievedAt = datetime.datetime.now()
        if self._verbose:
            _statusErrMsg('info', 'WaAPI2._refreshToken()', '{}'.format(self._token))

    ## static methods
    @staticmethod
    def _parseResponse(http_response, gzipData = False):
        '''
        '''
        if gzipData:  # decompress data as first step
            compData = StringIO( http_response.read())
            decompData = gzip.GzipFile(fileobj=compData)
            decoded = json.loads(decompData.read().decode('utf-8'))
        else:
            decoded = json.loads(http_response.read().decode('utf-8'))
        if isinstance(decoded, list):
            result = []
            for item in decoded:
                result.append(ApiObject(item))
            return result
        elif isinstance(decoded, dict):
            return ApiObject(decoded)
        else:
            return None

class ApiObject(object):
    '''
    Represent any api call input or output object
    '''
    def __init__(self, state):
    
        self.__dict__ = state
        for key, value in vars(self).items():
            if isinstance(value, dict):
                self.__dict__[key] = ApiObject(value)
            elif isinstance(value, list):
                new_list = []
                for list_item in value:
                    if isinstance(list_item, dict):
                        new_list.append(ApiObject(list_item))
                    else:
                        new_list.append(list_item)
                self.__dict__[key] = new_list

    def __str__(self):
    
        try:    # sometimes fails so try to rescue the situation
            return json.dumps(self.__dict__)
        except TypeError:
            if WaAPI2._verbose: 
                _statusErrMsg('warn', 'ApiObject.__str__()', 'TypeError raised, attempting workaround...')
            attrDct = {} # convert the instance into an equivalent dictionary that can be printed
            for attribName, attribValue in self.attribGen():
                if isinstance(attribName, unicode):
                    attribName = attribName.encode('ascii', 'replace')
                if isinstance(attribValue, unicode):
                    attribValue = attribValue.encode('ascii', 'replace')
                attrDct[attribName] = attribValue
            return repr(attrDct)

    def __repr__(self):
    
        return json.dumps(self.__dict__)

    def attribGen(self):
        '''
        instance attribute generator (sorted alphabetically)
        iterates over the instance attributes
        yields (name, value) tuple
        '''
        for attrName, attrValue in sorted(vars(self).iteritems()):
            yield (attrName, attrValue)

class _ApiObjectEncoder(json.JSONEncoder):

    def default(self, obj):
    
        if isinstance(obj, ApiObject):
            return obj.__dict__
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
            

## helper functions
def _statusErrMsg(status, function, message):
    '''
    print status message in standard format to stderr
    '''
    # crh 15-jun-15 -- afaict this has stopped working overnight for (some?) ApiObject instances; 
    # has wa output changed in some way?
    # workaround put in place in ApiObject __str__ method
    
    stderr.write('{}-{}-{}--{}\n'.format(status, _libName, function, message))

    ## testing code
if __name__ == '__main__':
    # add test stuff here
    _statusErrMsg('info', 'test', 'library testing code')
    _api = WaAPI2()
    print dir(_api)
    print vars(_api)
