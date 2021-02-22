# -*- coding: utf-8 -*-
# /home/ipshita/workspace/odoo10/amazon_gre,/home/ipshita/workspace/odoo10/ebay_gre-im,/home/ipshita/workspace/odoo10/e-commerce_base-md
from __future__ import absolute_import
# from pyxml2dict import XML2Dict
import hashlib
import hmac
# from ZSI.generate.commands import name
from urllib.parse import urlencode
from datetime import date, timedelta
from odoo import osv, fields
import time
# import xmlrpclib
import urllib.request
import base64
from odoo.tools.translate import _
import http.client, configparser, urllib.parse

from hashlib import md5
import logging
from odoo.api import returns
logger = logging.getLogger('amazonerp_osv')
# from elementtree.ElementTree import XML, fromstring, tostring
from lxml import etree as ET
import base64
from xml.dom import minidom
import re
import sys
import hashlib
import hmac
from time import gmtime, strftime

import datetime
from requests import request
from requests.exceptions import HTTPError
from . import utils
# import xmltodict
# import python_utils as utils

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote
try:
    from xml.etree.ElementTree import ParseError as XMLError
except ImportError:
    from xml.parsers.expat import ExpatError as XMLError
from time import strftime, gmtime

from requests import request
from requests.exceptions import HTTPError
import time

from odoo.http import request as oe_request
from odoo import SUPERUSER_ID


# import sys
# reload(sys)
# sys.setdefaultencoding('latin-1')

MARKETPLACES = {
    "CA": "https://mws.amazonservices.ca",  # A2EUQ1WTGCTBG2
    "US": "https://mws.amazonservices.com",  # ATVPDKIKX0DER",
    "DE": "https://mws-eu.amazonservices.com",  # A1PA6795UKMFR9
    "ES": "https://mws-eu.amazonservices.com",  # A1RKKUPIHCS9HS
    "FR": "https://mws-eu.amazonservices.com",  # A13V1IB3VIYZZH
    "IN": "https://mws.amazonservices.in",  # A21TJRUUN4KGV
    "IT": "https://mws-eu.amazonservices.com",  # APJ6JRA9NG5V4
    "UK": "https://mws-eu.amazonservices.com",  # A1F83G8C2ARO7P
    "JP": "https://mws.amazonservices.jp",  # A1VC38T7YXB528
    "CN": "https://mws.amazonservices.com.cn",  # AAHKV2X7AFYLW
    "MX": "https://mws.amazonservices.com.mx",  # A1AM78C64UM0Y8
}
class Session:

    def Initialize(self, access_key=False, secret_key=False, merchant_id=False, marketplace_id=False, domain=False):
        self.access_key = access_key
        self.secret_key = secret_key
        self.merchant_id = merchant_id
        self.marketplace_id = marketplace_id
        self.domain = 'mws.amazonservices.' + domain
        print ("=====self.domain=====>", self.domain,self.secret_key,self.access_key)
        self.version = '2011-01-01'

        
class Call:
    RequestData = ""  # just a stub
    command = ''
    url_string = ''

    def calc_signature(self, url_params, post_data):
        """Calculate MWS signature to interface with Amazon
        '/Orders/2011-01-01"""
        keys = url_params.keys()
        keys = list(keys)
        keys.sort()
        values = map(url_params.get, keys)
        url_string = urlencode(list(zip(keys, values)))
        print('url_string>>>>>>>>>',url_string)
        string_to_sign = 'POST\n%s\n%s\n%s' % (self.Session.domain, post_data, url_string)
        signature = hmac.new(self.Session.secret_key.encode('utf-8'), string_to_sign.encode(), hashlib.sha256).digest().strip()
        signature = base64.encodestring(signature)
        return signature, url_string

    def cal_content_md5(self, request_xml):
        m = hashlib.md5()
        m.update(request_xml.encode())
        value = m.digest()
        print("=========valuevaluevalue====>>>>>>>>", value)
        hash_string = base64.b64encode(value)
        print("=========hash_string===cal_content_md5=>>>>>>>>", hash_string)
#         hash_string = hash_string.replace('\n', '')
        return hash_string

    def MakeCall(self, callName):
        logger.info('URL String ===> %s', self.url_string)
#         try:
        conn = http.client.HTTPSConnection(self.Session.domain)
        if callName.startswith('POST_'):
            content_md5 = self.cal_content_md5(self.RequestData)
            print("=========content_md5====>>>>>>>>", content_md5)
            print("=========self.RequestDataself.RequestData====>>>>>>>>", self.RequestData)
            conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders(len(self.RequestData), content_md5))
        else:
            conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders('', ''))
        response = conn.getresponse()
        while response == None:
            time.sleep(30)
            if callName.startswith('POST_'):
                content_md5 = self.cal_content_md5(self.RequestData)
                print("=========content_md5====>>>>>>>>", content_md5)
                conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders(len(self.RequestData), content_md5))
            else:
                conn.request("POST", self.url_string, self.RequestData, self.GenerateHeaders('', ''))
            response = conn.getresponse()
        data = response.read()
#         print("data ", data)
        conn.close()
        if callName == 'GetReport':
            return data
        else:
            responseDOM = minidom.parseString(data)
            responseDOM.toprettyxml()
            return responseDOM
#         except Exception as e:
#             logger.info('Error %s', e, exc_info=True)
#             return None

    def GenerateHeaders(self, length_request, contentmd5):
        headers = {}
        print("=========length_request====>>>>>>>>", length_request)
        print("=========contentmd5====>>>>>>>>", contentmd5)
        headers = {
                   "Content-type": "text/xml; charset=UTF-8"
                   }
        if length_request and contentmd5:
            headers['Content-Length'] = length_request
            headers['Content-MD5'] = contentmd5
        return headers
    
    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
                if cNode.nodeName == 'Code':
                    info['Code'] = cNode.childNodes[0].data
        return info

class MWS(object):
    """ Base Amazon API class """
    URI = "/"
    VERSION = "2009-01-01"
    NS = ''
    ACCOUNT_TYPE = "SellerId"
    def __init__( self, access_key, secret_key, account_id, region='US', domain='', uri="", version="", auth_token="", proxies={}):
        self.access_key = access_key
        self.secret_key = secret_key
        self.account_id = account_id
        self.auth_token = auth_token
        self.version = version or self.VERSION
        self.uri = uri or self.URI
        self.response = None
        self.parsed_response_error = None
        self.domain = 'mws.amazonservices.' + domain
        self.proxies=proxies
        print("domaindomaindomain????//",domain)
        if domain:
            self.domain = domain
        elif region in MARKETPLACES:
            self.domain = MARKETPLACES[region]
        else:
            error_msg = "Incorrect region supplied ('%(region)s'). Must be one of the following: %(marketplaces)s" % {
                "marketplaces": ', '.join(list(MARKETPLACES.keys())),
                "region": region,
            }
            raise MWSError(error_msg)

    def make_request(self, extra_data, method="GET", **kwargs):
        """Make request to Amazon MWS API with these parameters
        """

        # Remove all keys with an empty value because
        # Amazon's MWS does not allow such a thing.
        extra_data = remove_empty(extra_data)

        # convert all Python date/time objects to isoformat
        for key, value in extra_data.items():
            if isinstance(value, (datetime.datetime, datetime.date)):
                extra_data[key] = value.isoformat()

        params = {
            'AWSAccessKeyId': self.access_key,
            self.ACCOUNT_TYPE: self.account_id,
            'SignatureVersion': '2',
            'Timestamp': self.get_timestamp(),
            'Version': self.version,
            'SignatureMethod': 'HmacSHA256',
        }
        if self.auth_token:
            params['MWSAuthToken'] = self.auth_token
        params.update(extra_data)
        request_description = '&'.join(['%s=%s' % (k, quote(params[k], safe='-_.~')) for k in sorted(params)])
        signature = self.calc_signature(method, request_description)
        url = '%s%s?%s&Signature=%s' % (self.domain, self.uri, request_description, quote(signature))
        headers = {'User-Agent': 'python-amazon-mws/0.0.1 (Language=Python)'}
        headers.update(kwargs.get('extra_headers', {}))
        
        try:
            # Some might wonder as to why i don't pass the params dict as the params argument to request.
            # My answer is, here i have to get the url parsed string of params in order to sign it, so
            # if i pass the params dict as params to request, request will repeat that step because it will need
            # to convert the dict to a url parsed string, so why do it twice if i can just pass the full url :).
            response = request( method, url, data=kwargs.get( 'body', '' ), headers=headers,proxies=self.proxies or {})
            self.response = response
            if response.status_code!=200:
                self.parsed_response_error = DictWrapper( response.content.decode("utf-8"), "Error" )
            response.raise_for_status()
            # When retrieving data from the response object,
            # be aware that response.content returns the content in bytes while response.text calls
            # response.content and converts it to unicode.
            if response.headers.get('Content-Type')=='text/xml':
                try:
                    data=response.content.decode()
                except:
                    data=response.content
            elif response.encoding == 'Windows-31J':
                data=response.content.decode('shift_jisx0213','ignore').encode()
            else:
                data=response.content.decode(response.encoding).encode()
            # I do not check the headers to decide which content structure to server simply because sometimes
            # Amazon's MWS API returns XML error responses with "text/plain" as the Content-Type.
            rootkey = kwargs.get('rootkey', extra_data.get("Action") + "Result")
            try:
                try:
                    parsed_response = DictWrapper(data, rootkey)
                except TypeError:  # raised when using Python 3 and trying to remove_namespace()
                    # When we got CSV as result, we will got error on this
                    parsed_response = DictWrapper(response.text, rootkey)

            except XMLError:
                try:
                    parsed_response = DataWrapper(data, response.headers)
                except:
                    parsed_response = DataWrapper(data,{})
                    
        except HTTPError as e:
            error = MWSError(str(e.response.text))
            error.response = e.response
            raise error

        # Store the response object in the parsed_response for quick access
        parsed_response.response = response
        return parsed_response

    def get_service_status(self):
        """
            Returns a GREEN, GREEN_I, YELLOW or RED status.
            Depending on the status/availability of the API its being called from.
        """

        return self.make_request(extra_data=dict(Action='GetServiceStatus'))

    def calc_signature(self, method, request_description):
        """Calculate MWS signature to interface with Amazon

        Args:
            method (str)
            request_description (str)
        """
        sig_data = '\n'.join([
            method,
            self.domain.replace('https://', '').lower(),
            self.uri,
            request_description
        ])
        return base64.b64encode(hmac.new(self.secret_key.encode(), sig_data.encode(), hashlib.sha256).digest())

    def get_timestamp(self):
        """
            Returns the current timestamp in proper format.
        """
        return strftime("%Y-%m-%dT%H:%M:%SZ", gmtime())

    def enumerate_param(self, param, values):
        """
            Builds a dictionary of an enumerated parameter.
            Takes any iterable and returns a dictionary.
            ie.
            enumerate_param('MarketplaceIdList.Id', (123, 345, 4343))
            returns
            {
                MarketplaceIdList.Id.1: 123,
                MarketplaceIdList.Id.2: 345,
                MarketplaceIdList.Id.3: 4343
            }
        """
        params = {}
        print("valuesvalues>>>>>>>>>>>",values)
        if values is not None:
            if not param.endswith('.'):
                param = "%s." % param
            for num, value in enumerate(values):
                params['%s%d' % (param, (num + 1))] = value
        print("paramsparams>>>>>>>>>>>>.",params)
        return params
    

class MWSError(Exception):
    """
        Main MWS Exception class
    """
    # Allows quick access to the response object.
    # Do not rely on this attribute, always check if its not None.
    response = None


def calc_md5(string):
    """Calculates the MD5 encryption for the given string
    """
    md = hashlib.md5()
    md.update(string)
    return base64.b64encode(md.digest()).strip(b'\n')


def remove_empty(d):
    """Helper function that removes all keys from a dictionary (d), that have an empty value.

    Args:
        d (dict)

    Return:
        dict
    """
    return {k: v for k, v in d.items() if v}


def remove_namespace(xml):
    regex = re.compile(' xmlns(:ns2)?="[^"]+"|(ns2:)|(xml:)')
    return regex.sub('', xml)


class DictWrapper(object):
    def __init__(self, xml, rootkey=None):
        self.original = xml
        self._rootkey = rootkey
        self._mydict = utils.xml2dict().fromstring(remove_namespace(xml))
        print("self._mydict >>>>>>>>>>>",self._mydict)
        self._response_dict = self._mydict.get(list(self._mydict.keys())[0],
                                                self._mydict)
# class DictWrapper(object):
#     def __init__(self, xml, rootkey=None):
#         print("xmlxmlxmlxmlxml>>>>>>>>>>.",xml)
#         self.original = xml
#         self._rootkey = rootkey
#         self._mydict = dict(xmltodict.parse(remove_namespace(xml)))
#         print("self._mydictself._mydict><>>>>>>>>>>>>>",self._mydict)
#         
#         self._response_dict = self._mydict.get(list(self._mydict.keys())[0],
#                                                self._mydict)
#         print("self._response_dict",self._response_dict)
#         weeeeeeeeeeee
    @property
    def parsed(self):
        if self._rootkey:
            return self._response_dict.get(self._rootkey)
        else:
            return self._response_dict


class DataWrapper(object):
    """
        Text wrapper in charge of validating the hash sent by Amazon.
    """
    def __init__(self, data, header):
        self.original = data
        if 'content-md5' in header:
            hash_ = calc_md5(self.original)
            if header['content-md5'].encode() != hash_:
                raise MWSError("Wrong Contentlength, maybe amazon error...")

    @property
    def parsed(self):
        return self.original


class Reports(MWS):
    """ Amazon MWS Reports API """

    ACCOUNT_TYPE = "Merchant"

    # * REPORTS * #

    def get_report(self, report_id):
        data = dict(Action='GetReport', ReportId=report_id)
        return self.make_request(data)

    def get_report_count(self, report_types=(), acknowledged=None, fromdate=None, todate=None):
        data = dict(Action='GetReportCount',
                    Acknowledged=acknowledged,
                    AvailableFromDate=fromdate,
                    AvailableToDate=todate)
        data.update(self.enumerate_param('ReportTypeList.Type.', report_types))
        return self.make_request(data)

    def get_report_list(self, requestids=(), max_count=None, types=(), acknowledged=None,
                        fromdate=None, todate=None):
        print("requestidsrequestids>>>>>>>>>>>>>>>>.",requestids,types)
        data = dict(Action='GetReportList',
                    Acknowledged=acknowledged,
                    AvailableFromDate=fromdate,
                    AvailableToDate=todate,
                    MaxCount=max_count)
#         print("datadatadatadata??>???????????????????/",data)
        data.update(self.enumerate_param('ReportRequestIdList.Id.', requestids))
        print("datadatadata?>>>>>>>>>>>>>",data)
#         errr
        data.update(self.enumerate_param('ReportTypeList.Type.', types))
        print("datadatadatadat22222222222222222",data)
        return self.make_request(data)

    def get_report_list_by_next_token(self, token):
        data = dict(Action='GetReportListByNextToken', NextToken=token)
        return self.make_request(data)

    def get_report_request_count(self, report_types=(), processingstatuses=(), fromdate=None, todate=None):
        data = dict(Action='GetReportRequestCount',
                    RequestedFromDate=fromdate,
                    RequestedToDate=todate)
        data.update(self.enumerate_param('ReportTypeList.Type.', report_types))
        data.update(self.enumerate_param('ReportProcessingStatusList.Status.', processingstatuses))
        return self.make_request(data)

    def get_report_request_list(self, requestids=(), types=(), processingstatuses=(),
                                max_count=None, fromdate=None, todate=None):
        data = dict(Action='GetReportRequestList',
                    MaxCount=max_count,
                    RequestedFromDate=fromdate,
                    RequestedToDate=todate)
        data.update(self.enumerate_param('ReportRequestIdList.Id.', requestids))
        data.update(self.enumerate_param('ReportTypeList.Type.', types))
        data.update(self.enumerate_param('ReportProcessingStatusList.Status.', processingstatuses))
        return self.make_request(data)

    def get_report_request_list_by_next_token(self, token):
        data = dict(Action='GetReportRequestListByNextToken', NextToken=token)
        return self.make_request(data)

    def request_report(self, report_type, start_date=None, end_date=None, marketplaceids=()):
        data = dict(Action='RequestReport',
                    ReportType=report_type,
                    StartDate=start_date,
                    EndDate=end_date)
        data.update(self.enumerate_param('MarketplaceIdList.Id.', marketplaceids))
        return self.make_request(data)

    # * ReportSchedule * #

    def get_report_schedule_list(self, types=()):
        data = dict(Action='GetReportScheduleList')
        data.update(self.enumerate_param('ReportTypeList.Type.', types))
        return self.make_request(data)

    def get_report_schedule_count(self, types=()):
        data = dict(Action='GetReportScheduleCount')
        data.update(self.enumerate_param('ReportTypeList.Type.', types))
        return self.make_request(data)


class ListMatchingProducts:
    Session = Session()
    
    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def call_api(self, product_query, prod_query_contextid):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'ListMatchingProducts'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'Query':product_query, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        if prod_query_contextid:
            url_params['QueryContextId'] = prod_query_contextid
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('ListMatchingProducts')
        return responseDOM, api
        
    def Get(self, product_query, prod_query_contextid):
        responseDOM, api = self.call_api(product_query, prod_query_contextid)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(product_query, prod_query_contextid)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(product_query, prod_query_contextid)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDoM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        element = ET.XML(responseDOM)
        mydict = {}
        product_info = []
        flag = False
        for elt in element.getiterator():
                if (elt.tag[0] == "{") and (elt.text is not None):
                        uri, tag = elt.tag[1:].split("}")
                        if tag == 'Product':
                                flag = True  # set flag to true once we find a product tag
                                product_info.append(mydict)
                                mydict = {}
                        if flag:
                                mydict[tag] = elt.text.strip()
        product_info.append(mydict)
        product_info.pop(0)
        getsubmitfeed = {}
        return product_info


class ListOrders:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
        return info

    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
#             print ("nodenodenodenodenodenodenodenode",node.childNodes)
            for cNode in node.childNodes:
#                 print ('cNode.nodeNameaaaaaaaaaaaaaaaaaaaaa',cNode.nodeName)
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
#                            print ('-----------------',gcNode.nodeName)
                            if gcNode.nodeName == 'Name':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'LastUpdateDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'LatestShipDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ShippedByAmazonTFM':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderType':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PaymentMethod':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'EarliestShipDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PaymentExecutionDetail':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'Payment ':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
            transDetails.append(info)
#        print 'transDetails',transDetails
        return transDetails
    
    def call_api(self, timefrom, afn_order):
        api = Call()
        api.Session = self.Session
        version = '2013-09-01'
        method = 'ListOrders'
        command = '/Orders/2011-01-01?'
        if afn_order:
            url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'FulfillmentChannel.Channel.1':'AFN', 'MarketplaceId.Id.1':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        else:
            url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId.Id.1':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['CreatedAfter'] = timefrom
#        if timeto:
#            url_params['LastUpdatedBefore'] = timeto
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        print("url_paramsurl_paramsurl_paramsurl_params",url_params)
        logger.info('url_paramsurl_paramsur===> %s', url_params)
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('ListOrders')
        return responseDOM, api
        
    def Get(self, timefrom, afn_order):
        responseDOM, api = self.call_api(timefrom, afn_order)
        while responseDOM == None:
            time.sleep(30)
            responseDoM, api = self.call_api(timefrom, afn_order)
        error = responseDOM.getElementsByTagName('Error')
        logger.info("error--------- %s", error)
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(timefrom, afn_order)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                logger.info("getsubmitfeed Response--------- %s", getsubmitfeed)
                
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info("getsubmitfeed Response--------- %s", getsubmitfeed)
            return [getsubmitfeed]
        
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        if responseDOM.getElementsByTagName('NextToken'):
            getOrderdetails = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        logger.info("getOrderdetails Response--------- %s", getOrderdetails)
        return getOrderdetails


class ListOrderItems:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

###############################for getting products price###################################
    def getPrice(self, node):
        for cNode in node.childNodes:
            if cNode.nodeName == 'Amount':
                return cNode.childNodes[0].data
            
    def getItemTax(self, node):
        info = {}
        for cNode in node.childNodes:
            if cNode.nodeName == 'Amount':
                return cNode.childNodes[0].data
        return info

#############################for getting product details######################################
    def getProductdetails(self, nodelist):
        productDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'OrderItem':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'ASIN':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Title':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'SellerSKU':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'OrderItemId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'ItemPrice':
                                info['Amount'] = self.getPrice(gcNode)
                                
                            elif gcNode.nodeName == 'GiftWrapPrice':
                                info['GiftWrapPrice'] = self.getPrice(gcNode)
                            elif gcNode.nodeName == 'ShippingPrice':
                                info['ShippingPrice'] = self.getPrice(gcNode)
                            elif gcNode.nodeName == 'PromotionDiscount':
                                info['PromotionDiscount'] = self.getPrice(gcNode)
                            elif gcNode.nodeName == 'ShippingDiscount':
                                info['ShippingDiscount'] = self.getPrice(gcNode)
                                
                            elif gcNode.nodeName == 'ItemTax':
                                info['ItemTax'] = self.getItemTax(gcNode)
                            elif gcNode.nodeName == 'QuantityOrdered':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                        productDetails.append(info)
                        info = {}

        return productDetails
    
    def call_api(self, order_id):
        api = Call()
        api.Session = self.Session
        version = '2013-09-01'
        method = 'ListOrderItems'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['AmazonOrderId'] = order_id
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]

        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('ListOrderItems')
        return responseDOM, api
        
    def Get(self, order_id):
        responseDOM, api = self.call_api(order_id)
        while responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(order_id)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(order_id)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return [getsubmitfeed]
        
        getproductinfo = self.getProductdetails(responseDOM.getElementsByTagName('OrderItems'))
        if responseDOM.getElementsByTagName('NextToken'):
            getproductinfo = getproductinfo + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        return getproductinfo


class ListOrdersByNextToken:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Name':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
            transDetails.append(info)
        return transDetails
    
    def call_api(self, next_token):
        api = Call()
        api.Session = self.Session
        version = '2013-09-01'
        method = 'ListOrdersByNextToken'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['NextToken'] = next_token
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('ListOrdersByNextToken')
        return responseDOM, api
        
    def Get(self, next_token):
        responseDOM, api = self.call_api(next_token)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(next_token)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(next_token)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return [getsubmitfeed]
        
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        if responseDOM.getElementsByTagName('NextToken'):
            getOrderdetails = getOrderdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
        return getOrderdetails

    
class GetOrder:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def getOrderdetails(self, nodelist):
        transDetails = []
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ShippingAddress':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Name':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine1':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'AddressLine2':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'City':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'StateOrRegion':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'PostalCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Phone':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'CountryCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                elif cNode.nodeName == 'ShipServiceLevel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'FulfillmentChannel':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'BuyerEmail':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'AmazonOrderId':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'PurchaseDate':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'NumberOfItemsShipped':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'OrderStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
            transDetails.append(info)
        return transDetails
    
    def call_api(self, orderid):
        print ("kkkkkkkkkkkkkkkkkkkkkkkk", orderid)
        api = Call()
        api.Session = self.Session
        version = '2013-09-01'
        method = 'GetOrder'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        if isinstance(orderid, list):
            orderid = orderid
        else:
            orderid = [orderid]
        if len(orderid):
            count = 1
            for order in orderid:
                if order:
                    order_key = 'AmazonOrderId.Id.' + str(count)
                    count += 1
                    url_params[order_key] = order
#                     if count == 11:
        post_data = '/Orders/2011-01-01'
        print("======url_params====>", url_params)
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('GetOrder')
        return responseDOM, api
        
    def Get(self, orderid):
        print("======orderid======>,", orderid)
        responseDOM, api = self.call_api(orderid)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(orderid)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(orderid)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return [getsubmitfeed]
        
        getOrderdetails = self.getOrderdetails(responseDOM.getElementsByTagName('Order'))
        return getOrderdetails


class ListOrderItemsByNextToken:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def call_api(self, next_token):
        api = Call()
        api.Session = self.Session
        version = '2013-09-01'
        method = 'ListOrderItemsByNextToken'
        command = '/Orders/2011-01-01?'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId.Id.1':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['NextToken'] = next_token
        post_data = '/Orders/2011-01-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDoM = api.MakeCall('ListOrderItemsByNextToken')
        return responseDoM, api
        
    def Get(self, next_token):
        responseDOM, api = self.call_api(next_token)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(next_token)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(next_token)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDoM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        return responseDoM


class GetFeedSubmissionResult:

    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitfeedresult(self, nodelist):
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'ProcessingReport':
                        if cNode.childNodes:
                            for gcNode in cNode.childNodes:
                                if gcNode.nodeName == 'ProcessingSummary':
                                    for gccNode in gcNode.childNodes:
                                        if gccNode.nodeName == 'MessagesWithError':
                                            info[gccNode.nodeName] = gccNode.childNodes[0].data
                                        elif gccNode.nodeName == 'MessagesWithWarning':
                                            info[gccNode.nodeName] = gccNode.childNodes[0].data
                                if gcNode.nodeName == 'Result':
                                    for gccNode in gcNode.childNodes:
                                        if gccNode.nodeName == 'ResultCode':
                                            info[gccNode.nodeName] = gccNode.childNodes[0].data
                                        if gccNode.nodeName == 'ResultDescription':
                                            info[gccNode.nodeName] = gccNode.childNodes[0].data
        return info
    
    def call_api(self, FeedSubmissionId):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'GetFeedSubmissionResult'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['FeedSubmissionId'] = FeedSubmissionId
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDoM = api.MakeCall('GetFeedSubmissionResult')
        return responseDoM, api
        
    def Get(self, FeedSubmissionId):
        responseDOM, api = self.call_api(FeedSubmissionId)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(FeedSubmissionId)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(FeedSubmissionId)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        getsubmitfeedresult = self.submitfeedresult(responseDOM.getElementsByTagName('Message'))
        return getsubmitfeedresult

    def Get_all(self, FeedSubmissionId):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'GetFeedSubmissionResult'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['FeedSubmissionId'] = FeedSubmissionId
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDoM = api.MakeCall('GetFeedSubmissionResult')
        return responseDoM


class POST_PRODUCT_RELATIONSHIP_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_PRODUCT_RELATIONSHIP_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall('POST_PRODUCT_RELATIONSHIP_DATA')
        return responseDoM, api
        
    def Get(self, requestData):
        responseDOM = {}
        getsubmitfeed = False
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(requestData)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
#         error = responseDoM.getElementsByTagName('Error')
#         if error:
#             getsubmitfeed = api.getErrors(error)
#             return getsubmitfeed
#         getsubmitfeed = self.submitresult(responseDoM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed


class POST_INVENTORY_AVAILABILITY_DATA:
    Session = Session()

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:

            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_INVENTORY_AVAILABILITY_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_INVENTORY_AVAILABILITY_DATA')
        return responseDOM, api
        
    def Get(self, requestData):
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(requestData)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed


class POST_ORDER_FULFILLMENT_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        for node in nodelist:
            info = {}
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_ORDER_FULFILLMENT_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_ORDER_FULFILLMENT_DATA')
        return responseDOM, api
        
    def Get(self, requestData):
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(requestData)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed


class POST_PRODUCT_PRICING_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
        return info

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_PRODUCT_PRICING_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDOM = api.MakeCall('POST_PRODUCT_PRICING_DATA')
        return responseDOM, api
        
    def Get(self, requestData):
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed


class POST_PRODUCT_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_PRODUCT_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall('POST_PRODUCT_DATA')
        return responseDoM, api
        
    def Get(self, requestData):
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed


class POST_PRODUCT_OVERRIDES_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_PRODUCT_OVERRIDES_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall('POST_PRODUCT_OVERRIDES_DATA')
        return responseDoM, api
        
    def Get(self, requestData):
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDoM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        getsubmitfeed = self.submitresult(responseDoM.getElementsByTagName('SubmitFeedResult'))
        return getsubmitfeed

    
class RequestReport:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestId':
                    info[cNode.nodeName] = cNode.childNodes[0].data
                elif cNode.nodeName == 'ReportProcessingStatus':
                    info[cNode.nodeName] = cNode.childNodes[0].data
        return info
    
    def call_api(self, requestData, request_type, date):
        print ("dateaaaaaaaaaaaaaaa", date)
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'RequestReport'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'StartDate':date, 'MarketplaceIdList.Id.1':self.Session.marketplace_id, 'ReportType':request_type, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall('RequestReport')
        print ("responseDoM", responseDoM)
        return responseDoM, api
    
    def Get(self, requestData, request_type, date):
        responseDOM, api = self.call_api(requestData, request_type, date)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData, request_type, date)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(requestData, request_type, date)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        
        getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('ReportRequestInfo'))
        return getsubmitfeed


class GetReportRequestList:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def getErrors(self, node):
        info = {}
        for node in node:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Message':
                    info['Error'] = cNode.childNodes[0].data
                     
    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportRequestInfo':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'ReportProcessingStatus':
                            info['status'] = ccNode.childNodes[0].data
                        if ccNode.nodeName == 'GeneratedReportId':
                            if ccNode.childNodes[0].data != None:
                                info['GeneratedReportId'] = ccNode.childNodes[0].data
        return info

    def call_api(self, requestData, report_id, report_type=False):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'ReportTypeList.Type.1': report_type, 'ReportRequestIdList.Id.1':report_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall(requestData)
        logger.info('responseDom  %s', responseDoM)
        return responseDoM, api
        
    def Get(self, requestData, report_id, report_type=False):
        getsubmitfeed = {}
        responseDoM, api = self.call_api(requestData, report_id, report_type)
        while responseDoM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(requestData, report_id, report_type)
        error = responseDoM.getElementsByTagName('Error')
        logger.info('error  %s', error)
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info('getsubmitfeed  %s', getsubmitfeed)
            while responseDoM == None or getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(requestData, report_id, report_type)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDoM.getElementsByTagName('Error')
        logger.info('error  %s', error)
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info('getsubmitfeed  %s', getsubmitfeed)
            return getsubmitfeed
        else:
            getsubmitfeed = self.submitresult(responseDoM.getElementsByTagName('GetReportRequestListResult'))
            return getsubmitfeed


class GetReport:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'ReportInfo':
                    for ccNode in cNode.childNodes:
                        if ccNode.nodeName == 'ReportId':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
        
        return info
    
    def getbrowsenode_tree(self, nodelist):
        logger.info('Browse Category-----------------')
        node_tree = []
        for node in nodelist:
            for cNode in node.childNodes:
                print("========cNodecNodecNode>>>>>>>>>>", cNode)
                info = {}
                if cNode.nodeName == 'Node':
                    for ccNode in cNode.childNodes:
                        print("========ccNodeccNodeccNodeccNodeccNode>>>>>>>>>>", ccNode)
                        if ccNode.nodeName == 'browseNodeName':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                        if ccNode.nodeName == 'browseNodeId':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                        if ccNode.nodeName == 'browsePathById':
                            info[ccNode.nodeName] = ccNode.childNodes[0].data
                    node_tree.append(info)
        return node_tree
    
    def make_string_ascii(self, orig_string):
        try:
            orig_string = orig_string.encode('utf-8')
            return orig_string
        except Exception:
            new_string = ''
            for c in orig_string:
                if ord(c) > 127:
                    continue
                new_string += c
            return new_string
    
    def getproductlist(self, response):
        sku_list = []
        prod_data_list = {}
        prod_sku_asin_dict = {}
#         logger.info('Browse Category------------%s-----',response)
#         response = base64.decodestring(response)
        product_inv_data_lines = response.split('\n')
        for product_inv_data_line in product_inv_data_lines:
            vals = {}
            if product_inv_data_line != '' :
                product_inv_data_fields = product_inv_data_line.split('\t')
                if len(product_inv_data_fields) < 17:
                    continue 
                asin = product_inv_data_fields[16]
                if asin == 'asin1':
                    continue
#                 if product_inv_data_fields[16] != 'ASIN 1':
#                     if asin not in asin_list:
#                         asin_list.append(asin)
                if product_inv_data_fields[26] != 'DEFAULT':
                    vals.update({'fulfillment-channel':product_inv_data_fields[26].strip()})
                if  product_inv_data_fields[0]:
                    name_org = product_inv_data_fields[0].strip()
                    name = self.make_string_ascii(name_org)
                    vals.update({'name': name}) 
                if product_inv_data_fields[4]:             
                    vals.update({'list_price': product_inv_data_fields[4].strip()})
                if product_inv_data_fields[3]:
                    d_code = product_inv_data_fields[3].strip()
#                     print("d_coded_coded_coded_coded_code",d_code)
                    vals.update({'default_code': d_code})
                    if d_code not in sku_list:
                        sku_list.append(d_code)
                    if not prod_sku_asin_dict.get(product_inv_data_fields[16].strip()):
                        prod_sku_asin_dict.update({product_inv_data_fields[16].strip():[d_code]})
                    else:
                        if d_code not in prod_sku_asin_dict.get(product_inv_data_fields[16].strip()):
                            prod_sku_asin_dict.get(product_inv_data_fields[16].strip()).append(d_code)
#                     print("prod_sku_asin_dict>>>>", prod_sku_asin_dict)
                if product_inv_data_fields[2]:
#                     print("product_inv_data_fieldsproduct_inv_data_fields>>>>", product_inv_data_fields[2])
                    vals.update({'listing_id': product_inv_data_fields[2].strip()})
#                     print("valsvalsvalsvals>>>>", vals)
                if product_inv_data_fields[5]:
                    vals.update({'quantity': product_inv_data_fields[5].strip()})
                prod_data_list.update({ product_inv_data_fields[3].strip(): vals})
#         print("sku_listsku_listsku_list",sku_list)  
        return sku_list, prod_data_list, prod_sku_asin_dict

    def call_api(self, requestData, report_id, report_type=False):
        logger.info("Getting data..44..............................")
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = requestData
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'ReportId':report_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall(requestData)
#         print("responseDoM>>>>>>>>>>>>>>>>>>>>>>>>????????",responseDoM)
        return responseDoM, api
    
    def getfbaproductinventory(self, response):
        sku_list = []
        prod_data_list = {}
        prod_sku_asin_dict = {}
#         logger.info('Browse Category------------%s-----',response)
#         response = base64.decodestring(response)
        product_inv_data_lines = response.split('\n')
        for product_inv_data_line in product_inv_data_lines:
            vals = {}
            if product_inv_data_line != '' :
                product_inv_data_fields = product_inv_data_line.split('\t')
                asin = product_inv_data_fields[3]
                if asin == 'asin':
                    continue
                if product_inv_data_fields[1]:
                    vals.update({'fulfillment-channel-sku':product_inv_data_fields[1].strip()})
                if product_inv_data_fields[0]:
                    d_code = product_inv_data_fields[0].strip()
                    vals.update({'default_code': d_code})
                    if d_code not in sku_list:
                        sku_list.append(d_code)
#                 if product_inv_data_fields[4]:             
#                     vals.update({'list_price': product_inv_data_fields[4].strip()})
#                 if product_inv_data_fields[4]:             
#                     vals.update({'list_price': product_inv_data_fields[4].strip()})
                if product_inv_data_fields[5]:
                    vals.update({'quantity': product_inv_data_fields[5].strip()})
                prod_data_list.update({ product_inv_data_fields[0].strip(): vals})
                print("prod_data_list>?????????",prod_data_list)
                
        return sku_list, prod_data_list, prod_sku_asin_dict
    
    def Get(self, requestData, report_id, report_type=False, fulfillment_channel=False):
        responseDoM, api = self.call_api(requestData, report_id, report_type)
        while responseDoM == None:
            responseDoM, api = self.call_api(requestData, report_id, report_type)
            logger.info('responseDoM-Product get--------------------%s',responseDoM)
        responseDoM = responseDoM.decode('latin-1')
        if fulfillment_channel == 'fba':
            return self.getfbaproductlist(responseDoM)
        if report_type == '_GET_MERCHANT_LISTINGS_DATA_':
            print ("INSIDEEEEEEEEEEEEEEEE>>>>>>>>>>>>>>>>>>>>>")
            return self.getproductlist(responseDoM)
        else:
            logger.info('_GET_XML_BROWSE_TREE_DATA_---%s',report_type)
            if report_type == '_GET_XML_BROWSE_TREE_DATA_':
                category = []
                r_pos = [m.start() for m in re.finditer(r"</Node>",responseDoM)]
                print("r_posr_posr_pos",len(r_pos))
                while len(r_pos) < 0:
                    responseDoM, api = self.call_api(requestData, report_id, report_type)
                    r_pos = [m.start() for m in re.finditer(r"</Node>",responseDoM)]
                divide = 1000
                l = len(r_pos) // divide
                print("llllllllllll",l)
                end = 0
                if l> 0:
                    for c in range(l):
                        logger.info('endend_---%s',end)
                        if c == 0:
                            end = r_pos[divide-1] + 7
                            c_data = responseDoM[:end] + '</Result>'
                        else:
                            start = end
                            end = r_pos[(divide * c+1) -1] + 7
                            c_data = '<?xml version="1.0"?><Result>' + responseDoM[start: end] + '</Result>'
#                         logger.info('c_data---%s------ %s',c_data[:400],c_data[-100:])
                        c_data = minidom.parseString(c_data)
#                         logger.info('c_data---%s',c_data)
                        category.append(self.getbrowsenode_tree(c_data.getElementsByTagName('Result')))
                rm_data = len(r_pos) % divide
                if rm_data > 0:
                    c_data = '<?xml version="1.0"?><Result>' + responseDoM[end:]
#                     logger.info('c_data---%s------ %s',c_data[:400],c_data[-100:])
                    c_data = minidom.parseString(c_data)
                    category.append(self.getbrowsenode_tree(c_data.getElementsByTagName('Result')))
                return category
            else:
                responseDoM = minidom.parseString(responseDoM)
                responseDoM.toprettyxml()
                return responseDoM
    
#     def Get(self, requestData, report_id, report_type=False, fulfillment_channel=False):
#         responseDoM, api = self.call_api(requestData, report_id, report_type)
#         while responseDoM == None:
#             responseDoM, api = self.call_api(requestData, report_id, report_type)
#             logger.info('responseDoM-Product get--------------------%s',responseDoM)
#         responseDoM = responseDoM.decode('latin-1')
# #         if fulfillment_channel == 'fba':
# #             return self.getfbaproductlist(responseDoM)
#         if report_type == '_GET_AFN_INVENTORY_DATA_':
#             print ("AFN INVENTORY>>>>>>>>>>>>>>>>>>>>>")
#             return self.getfbaproductinventory(responseDoM)
#         if report_type == '_GET_MERCHANT_LISTINGS_DATA_':
#             print ("INSIDEEEEEEEEEEEEEEEE>>>>>>>>>>>>>>>>>>>>>")
#             return self.getproductlist(responseDoM)
#         else:
#             logger.info('_GET_XML_BROWSE_TREE_DATA_---%s',report_type)
#             if report_type == '_GET_XML_BROWSE_TREE_DATA_':
#                 category = []
#                 r_pos = [m.start() for m in re.finditer(r"</Node>",responseDoM)]
#                 while r_pos < 0:
#                     responseDoM, api = self.call_api(requestData, report_id, report_type)
#                     r_pos = [m.start() for m in re.finditer(r"</Node>",responseDoM)]
#                 divide = 1000
#                 l = len(r_pos) / divide
#                 end = 0
#                 if l> 0:
#                     for c in range(l):
#                         logger.info('endend_---%s',end)
#                         if c == 0:
#                             end = r_pos[divide-1] + 7
#                             c_data = responseDoM[:end] + '</Result>'
#                         else:
#                             start = end
#                             end = r_pos[(divide * c+1) -1] + 7
#                             c_data = '<?xml version="1.0"?><Result>' + responseDoM[start: end] + '</Result>'
# #                         logger.info('c_data---%s------ %s',c_data[:400],c_data[-100:])
#                         c_data = minidom.parseString(c_data)
# #                         logger.info('c_data---%s',c_data)
#                         category.append(self.getbrowsenode_tree(c_data.getElementsByTagName('Result')))
#                 rm_data = len(r_pos) % divide
#                 if rm_data > 0:
#                     c_data = '<?xml version="1.0"?><Result>' + responseDoM[end:]
# #                     logger.info('c_data---%s------ %s',c_data[:400],c_data[-100:])
#                     c_data = minidom.parseString(c_data)
#                     category.append(self.getbrowsenode_tree(c_data.getElementsByTagName('Result')))
#                 return category
#             else:
#                 responseDoM = minidom.parseString(responseDoM)
#                 responseDoM.toprettyxml()
#                 return responseDoM
    
        


 #################################################################################################################
class amazonerp_node_browse:
    RequestData = ""
    Command = ""
    xml = ""
    method = ""
    version = '2010-11-01'

    def __init__(self, access_key, secret_key, domain='ecs.amazonaws.com'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.domain = domain
        self.port = 443
        self.responseGroup = ''
        self.searchbrand = False

    def MakeCall(self):
        conn = http.client.HTTPSConnection(self.domain, self.port)
        headers = {'content-type':'application/x-www-form-urlencoded; charset=utf-8'}
        conn.request("POST", self.command, self.RequestData, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        responseDOM = parseString(data)
        tag = responseDOM.getElementsByTagName('Error')
        return responseDOM

    def calc_signature(self, url_string):
        """Calculate MWS signature to interface with Amazon
        """
        # Construct the string to sign
        string_to_sign = 'POST\n%s\n%s\n%s' % (self.domain, self.command, url_string)
#        print 'string_to_sign',string_to_sign
        return base64.b64encode(hmac.new(self.secret_key.encode('utf-8'), string_to_sign, hashlib.sha256).digest())

    def getProductRankRequest(self, cr, uid, search_key, itemPage=1):
        request = False
        self.command = '/onca/xml'
        update_params = {}
        url_params = {
                'Service':'AWSECommerceService',
                'ItemPage':itemPage,
                'Operation':self.operation,
                'ResponseGroup' : self.responseGroup,
                'AWSAccessKeyId':'AKIAJVPBJZQVYUN5PPQQ'
        }
        if self.searchbrand:
            update_params.update({'Brand' : self.searchbrand})

        if self.operation == 'ItemSearch':
            update_params .update({
                                 'SearchIndex' : self.searchIndex,
                                 'Keywords' : search_key,
                                 'Version':'2010-11-01'
                                })

        elif self.operation == 'ItemLookup':
            update_params.update({
                                 'ItemId' : search_key,
                                 'AssociateTag' : 'amazonlinks55-20',
                                 'Version' : '2011-08-01',
                                 'Condition' : 'All'
                                })

        elif self.operation == 'BrowseNodeLookup':
            update_params.update({
                                 'BrowseNodeId' : search_key,
                                 'AssociateTag' : 'amazonlinks55-20',
                                })

        url_params.update(update_params)
#        print"product parameter",update_params
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        # url_params['Timestamp'] = '2011-05-18T03:42:16Z'
        # Sort the URL parameters by key
        keys = url_params.keys()
        keys.sort()
        # Get the values in the same order of the sorted keys
        values = map(url_params.get, keys)
        # Reconstruct the URL paramters and encode them
        url_string = urlencode(zip(keys, values))
#        logger.notifyChannel('init', netsvc.LOG_WARNING, 'url_string before signing %s'  %(url_string,))
        signature = self.calc_signature(url_string)
        url_params['Signature'] = signature
        # Sort the URL parameters by key
        keys = url_params.keys()
        keys.sort()
        # Get the values in the same order of the sorted keys
        values = map(url_params.get, keys)
        # Reconstruct the URL paramters and encode them
        url_string = urlencode(zip(keys, values))
        url_string = url_string.replace('%0A', '')
        self.RequestData = url_string
#        logger.notifyChannel('init', netsvc.LOG_WARNING, 'url_string %s'  %(url_string))
        responseDOM = self.MakeCall()
#        logger.notifyChannel('init', netsvc.LOG_WARNING, 'responseDOM %s'  %(responseDOM.toprettyxml()))
        nodelist = responseDOM.getElementsByTagName('Items')
        if self.function == 'getChildNodes':
            nodelist = responseDOM.getElementsByTagName('Children')
        elif self.function == 'getItemsFromNodesIds':
            nodelist = responseDOM.getElementsByTagName('TopSellers')

        res_result = self.getChildNodes(nodelist)
        return res_result

    def getItemsFromNodesIds(self, nodelist):
        res_result = {}
        res_final = []
#        logger.notifyChannel('init', netsvc.LOG_WARNING, '------------getItemsFromNodesIds %s' % (nodelist))
        for cNode in nodelist:
#            logger.notifyChannel('init', netsvc.LOG_WARNING, 'cNode.nodeName %s'  %(cNode.nodeName))
            if cNode.nodeName == 'TopSellers':
                if cNode.childNodes[0].childNodes:
                    for gcNode in cNode.childNodes:
#                        logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gcNode.nodeName))
                        if gcNode.nodeName == 'TopSeller':
                            if gcNode.childNodes[0].childNodes:
                                for gccNode in gcNode.childNodes:
#                                    logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gccNode.nodeName))
                                    if gccNode.nodeName == 'ASIN':
#                                        logger.notifyChannel('init', netsvc.LOG_WARNING, 'gccNode.childNodes[0].data %s'  %(gccNode.childNodes[0].data))
                                        res_result[gccNode.nodeName] = gccNode.childNodes[0].data
                                res_final.append(res_result)
                                res_result = {}
        return res_final

    def getChildNodes(self, nodelist):
        res_result = {}
        res_final = []
#        logger.notifyChannel('init', netsvc.LOG_WARNING, '------------GetChildNode')
        for cNode in nodelist:
            if cNode.nodeName == 'Children':
                if cNode.childNodes[0].childNodes:
                    for gcNode in cNode.childNodes:
#                        logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gcNode.nodeName))
                        if gcNode.nodeName == 'BrowseNode':
                            if gcNode.childNodes[0].childNodes:
                                for gccNode in gcNode.childNodes:
#                                    logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gccNode.nodeName))
                                    if gccNode.nodeName == 'BrowseNodeId' or gccNode.nodeName == 'Name':
#                                        logger.notifyChannel('init', netsvc.LOG_WARNING, 'gccNode.childNodes[0].data %s'  %(gccNode.childNodes[0].data))
                                        res_result[gccNode.nodeName] = gccNode.childNodes[0].data
                                res_final.append(res_result)
                                res_result = {}
        return res_final

    def getRank(self, nodelist):
        res_result = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Item':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'SalesRank':
                                res_result['SalesRank'] = gcNode.childNodes[0].data
                            if gcNode.nodeName == 'SmallImage':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'URL':
                                        res_result['SmallImage'] = gccNode.childNodes[0].data
                            if gcNode.nodeName == 'MediumImage':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'URL':
                                        res_result['MediumImage'] = gccNode.childNodes[0].data
                            if gcNode.nodeName == 'LargeImage':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'URL':
                                        res_result['LargeImage'] = gccNode.childNodes[0].data
                            if gcNode.nodeName == 'CustomerReviews':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'IFrameURL':
                                        res_result['IFrameURL'] = gccNode.childNodes[0].data

        return res_result

    def getChildAsins(self, nodelist):
        res_result = {}
        res_final = []
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'Item':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'Variations':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'Item':
                                        for gcccNode in gccNode.childNodes:
                                            if gcccNode.nodeName == 'ASIN':
                                                res_result['ASIN'] = gcccNode.childNodes[0].data
                                            elif gcccNode.nodeName == 'ItemAttributes':
                                                for gccxcNode in gcccNode.childNodes:
                                                    if gccxcNode.nodeName == 'Color':
                                                        res_result['Color'] = gccxcNode.childNodes[0].data
                                                    elif gccxcNode.nodeName == 'Size':
                                                        res_result['Size'] = gccxcNode.childNodes[0].data
                                        res_final.append(res_result)
                                        res_result = {}
        return res_final

    def getProducts(self, nodelist):
        res_final = []
        image_set = []
        images = {}
        res_result = {}
        res_feature = []
        firstAttributes = ['SalesRank', 'ASIN', 'DetailPageURL']
        imageAttributes = ['SmallImage', 'MediumImage', 'LargeImage']
        ItemAttributes = ['Brand', 'Color', 'Department', 'EAN', 'Label', 'Manufacturer', 'Model', 'Size', 'UPC', 'Title',
        'ProductTypeName', 'SKU', 'Publisher', 'Binding', 'Studio', 'ProductGroup', 'PartNumber']

        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'TotalPages':
                    res_result['TotalPages'] = cNode.childNodes[0].data
                if cNode.nodeName == 'TotalResults':
                    res_result['TotalResults'] = cNode.childNodes[0].data
                if cNode.nodeName == 'Item':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
#                            logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gcNode.nodeName))
                            if gcNode.nodeName in firstAttributes:
                                res_result[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName in imageAttributes:
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'URL':
                                        res_result[gcNode.nodeName] = gccNode.childNodes[0].data
                            elif gcNode.nodeName == 'ImageSets':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'ImageSet' and gccNode.getAttribute('Category') == 'primary':
                                        for gccxNode in gccNode.childNodes:
                                            if gccxNode.nodeName == 'SwatchImage' or gccxNode.nodeName == 'LargeImage':
                                                for gccxxNode in gccxNode.childNodes:
                                                    if gccxxNode.nodeName == 'URL':
                                                        images[gccxNode.nodeName] = gccxxNode.childNodes[0].data
                                        image_set.append(images)
                            elif gcNode.nodeName == 'EditorialReviews':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'EditorialReview':
                                        for gcccNode in gccNode.childNodes:
                                            if gcccNode.nodeName == 'Content':
                                                res_result['Content'] = gcccNode.childNodes[0].data
                            elif gcNode.nodeName == 'ItemAttributes':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName in ItemAttributes:
                                        res_result[gccNode.nodeName] = gccNode.childNodes[0].data
                                    elif gccNode.nodeName == 'Feature':
                                        res_feature.append(gccNode.childNodes[0].data)
                                    elif gccNode.nodeName == 'ListPrice':
                                        for gcccNode in gccNode.childNodes:
                                            if gcccNode.nodeName == 'FormattedPrice':
                                                res_result['FormattedPrice'] = gcccNode.childNodes[0].data
                    if len(image_set):
                        res_result['image_set'] = image_set
                    if len(res_feature):
                        res_result['Feature'] = res_feature
                    res_final.append(res_result)
                    res_result = {}
        print ("res_final", res_final)
        return res_final


 #################################################################################################################
class amazonerp_product_osv:
    RequestData = ""
    Command = ""
    xml = ""
    method = ""
    version = '2010-11-01'

    def __init__(self, access_key, secret_key, domain='ecs.amazonaws.com'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.domain = domain
        self.port = 443
        self.searchbrand = False

    def MakeCall(self):
        try:
            conn = http.request.HTTPSConnection(self.domain, self.port)
            headers = {'content-type':'application/x-www-form-urlencoded; charset=utf-8'}
            conn.request("POST", self.command, self.RequestData, headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
            responseDOM = parseString(data)
            tag = responseDOM.getElementsByTagName('Error')
            return responseDOM
        except:
            pass

    def calc_signature(self, url_string):
        """Calculate MWS signature to interface with Amazon
        """
        # Construct the string to sign
        string_to_sign = 'POST\n%s\n%s\n%s' % (self.domain, self.command, url_string)
        return base64.b64encode(hmac.new(self.secret_key.encode('utf-8'), string_to_sign, hashlib.sha256).digest())

    def getProductRankRequest(self, cr, uid, search_key, itemPage=1, new_param=None):
        # stry:
            res_result = False
            self.command = '/onca/xml'
            update_params = {}
            url_params = {
                    'Service':'AWSECommerceService',
                    'ItemPage':itemPage,
                    'Operation':self.operation,
                    'ResponseGroup' : self.responseGroup,
                    'AWSAccessKeyId':'AKIAJVPBJZQVYUN5PPQQ'
            }
            if self.searchbrand:
                update_params.update({'Brand' : self.searchbrand})

            if self.operation == 'ItemSearch':
                update_params = {
                                 'SearchIndex' : self.searchIndex,
                                 'Keywords' : search_key,
                                 'Version':'2010-11-01'
                                }
            elif self   .operation == 'ItemLookup':
                update_params = {
                                 'ItemId' : search_key,
                                 'AssociateTag' : 'eminspac-20',
                                 'Version' : '2011-08-01',
                                 'Condition' : 'All',
                                 'IdType':'ASIN'
                                }
            elif self.operation == 'BrowseNodeLookup':
                update_params = {
                                 'BrowseNodeId' : search_key,
                                 'AssociateTag' : 'technoearh-20',
                                }

            if not new_param is None:
                update_params.update(new_param)

            url_params.update(update_params)
    #        print 'url_params',url_params
            url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
            # url_params['Timestamp'] = '2011-05-18T03:42:16Z'
            # Sort the URL parameters by key
            keys = url_params.keys()
            keys.sort()
            # Get the values in the same order of the sorted keys
            values = map(url_params.get, keys)
            # Reconstruct the URL paramters and encode them
            url_string = urlencode(zip(keys, values))

#            logger.notifyChannel('init', netsvc.LOG_WARNING, 'url_string before signing %s'  %(url_string,))
            signature = self.calc_signature(url_string)
            url_params['Signature'] = signature
            # Sort the URL parameters by key
            keys = url_params.keys()
            keys.sort()
            # Get the values in the same order of the sorted keys
            values = map(url_params.get, keys)
            # Reconstruct the URL paramters and encode them
            url_string = urlencode(zip(keys, values))
            url_string = url_string.replace('%0A', '')
            self.RequestData = url_string
            logger.error('self.RequestData %s', self.RequestData)
            responseDOM = self.MakeCall()
#            logger.notifyChannel('init', netsvc.LOG_WARNING, 'responseDOM %s'  %(responseDOM.toprettyxml()))
#             print'responseDOM', responseDOM.toprettyxml()
            logger.error('responseDOM.toprettyxml() %s', responseDOM.toprettyxml())

            if  responseDOM != None:
                nodelist = responseDOM.getElementsByTagName('Items')
                res_result = eval('self.%s(nodelist)' % (self.function))
                print ('-------------', res_result)

            return res_result
#        except:
#            pass

    def getProducts(self, nodelist):
        res_final = []
        image_set = []
        images = {}
        res_result = {}
        res_feature = []
        res_offers = []

        firstAttributes = ['SalesRank', 'ASIN', 'DetailPageURL']
        imageAttributes = ['SmallImage', 'MediumImage', 'LargeImage']
        ItemAttributes = ['Brand', 'Color', 'Department', 'EAN', 'Label', 'Manufacturer', 'Model', 'Size', 'UPC', 'Title',
        'ProductTypeName', 'SKU', 'Publisher', 'Binding', 'Studio', 'ProductGroup', 'PartNumber']
        dimensionAttributes = ['Height', 'Length', 'Weight', 'Width']
        offerAttributes = ['TotalOffers', 'TotalOfferPages', 'MerchantId', 'Name', 'GlancePage', 'AverageFeedbackRating', 'TotalFeedback', 'OfferListingId', 'Amount', 'CurrencyCode', 'FormattedPrice', 'Availability',
        'Quantity', 'IsEligibleForSuperSaverShipping', 'IsFulfilledByAmazon', 'GlancePage']

        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'TotalPages':
                    res_result['TotalPages'] = cNode.childNodes[0].data
                if cNode.nodeName == 'TotalResults':
                    res_result['TotalResults'] = cNode.childNodes[0].data
                if cNode.nodeName == 'Item':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
#                            logger.notifyChannel('init', netsvc.LOG_WARNING, 'gcNode.nodeName %s'  %(gcNode.nodeName))
                            if gcNode.nodeName in firstAttributes:
                                res_result[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName in imageAttributes:
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'URL':
                                        res_result[gcNode.nodeName] = gccNode.childNodes[0].data
                            elif gcNode.nodeName == 'ImageSets':
                                for gccNode in gcNode.childNodes:
                                    count = 1
                                    if gccNode.nodeName == 'ImageSet' and gccNode.getAttribute('Category') in ('primary', 'variant'):
                                        for gccxNode in gccNode.childNodes:
                                            if gccxNode.nodeName == 'SwatchImage' or gccxNode.nodeName == 'LargeImage':
                                                for gccxxNode in gccxNode.childNodes:
                                                    if gccxxNode.nodeName == 'URL':
                                                        if images.has_key(gccxNode.nodeName):
                                                            images['PT' + str(count)] = gccxxNode.childNodes[0].data
                                                            count += 1
                                                        else:
                                                            images[gccxNode.nodeName] = gccxxNode.childNodes[0].data
                                        image_set.append(images)
                            elif gcNode.nodeName == 'EditorialReviews':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName == 'EditorialReview':
                                        for gcccNode in gccNode.childNodes:
                                            if gcccNode.nodeName == 'Content':
                                                res_result['Content'] = gcccNode.childNodes[0].data
                            elif gcNode.nodeName == 'ItemAttributes':
                                for gccNode in gcNode.childNodes:
                                    if gccNode.nodeName in ItemAttributes:
                                        res_result[gccNode.nodeName] = gccNode.childNodes[0].data
                                    elif gccNode.nodeName == 'Feature':
                                        res_feature.append(gccNode.childNodes[0].data)
                                    elif gccNode.nodeName == 'ListPrice':
                                        for gcccNode in gccNode.childNodes:
                                            if gcccNode.nodeName == 'FormattedPrice':
                                                res_result['FormattedPrice'] = gcccNode.childNodes[0].data
                                    elif gccNode.nodeName == 'ItemDimensions':
                                        for gcccNode in gccNode.childNodes:
                                            res_result[gccNode.nodeName + gcccNode.nodeName] = gcccNode.childNodes[0].data
                                    elif gccNode.nodeName == 'PackageDimensions':
                                        for gcccNode in gccNode.childNodes:
                                            res_result[gcccNode.nodeName + 'Units'] = gcccNode.getAttribute('Units')
                                            res_result[gcccNode.nodeName] = gcccNode.childNodes[0].data
                            elif gcNode.nodeName == 'Offers':
                                for gccNode in gcNode.childNodes:
#                                    print 'gccNode.nodeName',gccNode.nodeName
                                    if gccNode.nodeName in offerAttributes:
#                                        print 'gccNode.nodeName values',gccNode.childNodes[0].data
                                        res_result[gccNode.nodeName] = gccNode.childNodes[0].data
                                    elif gccNode.nodeName == 'Offer':
                                        res_offer_result = {}
                                        for offerNode in gccNode.childNodes:
#                                            print 'offerNode.nodeName',offerNode.nodeName
                                            if offerNode.nodeName == 'Merchant':
                                                for merchantNode in offerNode.childNodes:
#                                                    print '---Merchant',merchantNode.nodeName
                                                    if merchantNode.nodeName in offerAttributes:
                                                        res_offer_result[merchantNode.nodeName] = merchantNode.childNodes[0].data
                                            elif offerNode.nodeName == 'OfferListing':
                                                for offerListNode in offerNode.childNodes:
#                                                    print '------',offerListNode.nodeName
                                                    if offerListNode.nodeName in offerAttributes:
                                                        res_offer_result[offerListNode.nodeName] = offerListNode.childNodes[0].data
                                                    elif offerListNode.nodeName == 'Price':
                                                        for priceNode in offerListNode.childNodes:
#                                                            print '------',priceNode.nodeName
                                                            if priceNode.nodeName in offerAttributes:
                                                                res_offer_result[priceNode.nodeName] = priceNode.childNodes[0].data
                                        res_offers.append(res_offer_result)

                    if len(image_set):
                        res_result['image_set'] = image_set
                    if len(res_feature):
                        res_result['Feature'] = res_feature
                    if len(res_offers):
                        res_result['Offer'] = res_offers

                    res_final.append(res_result)
                    res_result = {}

        return res_final

    
class GetMatchingProduct:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def get_products_info(self, nodelist):
        products_info_list = []
        for node in nodelist:
            for cNode in node.getElementsByTagNameNS('*', 'Product'):
                prod_info = {}
                asin_ids = cNode.getElementsByTagNameNS('*', 'ASIN')
                if asin_ids:
                    prod_info.update({'asin' : asin_ids[0].firstChild.data})
                    
                title_ids = cNode.getElementsByTagNameNS('*', 'Title')
                if title_ids:
                    prod_info.update({'Title' : title_ids[0].firstChild.data})
                
                # To get Attributes of Products 
                AttributeSets = [] 
                for attribute in cNode.getElementsByTagNameNS('*', 'AttributeSets'):
                    attrs_set = {}
                    binding_ids = attribute.getElementsByTagNameNS('*', 'Binding')
                    if binding_ids:
                        attrs_set.update({'Binding' : binding_ids[0].firstChild.data})
                        
                    productgroup_ids = attribute.getElementsByTagNameNS('*', 'ProductGroup')
                    if productgroup_ids:
                        attrs_set.update({'ProductGroup' : productgroup_ids[0].firstChild.data})
                        
                    height_ids = attribute.getElementsByTagNameNS('*', 'Height')
                    if height_ids:
                        attrs_set.update({'PackageDimensionsHeight' : height_ids[0].firstChild.data})
                        
                    width_ids = attribute.getElementsByTagNameNS('*', 'Width')
                    if width_ids:
                        attrs_set.update({'PackageDimensionsWidth' : width_ids[0].firstChild.data})
                        
                    length_ids = attribute.getElementsByTagNameNS('*', 'Length')
                    if length_ids:
                        attrs_set.update({'PackageDimensionsLength' : length_ids[0].firstChild.data})
                        
                    weight_ids = attribute.getElementsByTagNameNS('*', 'Weight')
                    if weight_ids:
                        attrs_set.update({'PackageDimensionsWeight' : weight_ids[0].firstChild.data})
                        
                    label_ids = attribute.getElementsByTagNameNS('*', 'Label')
                    if label_ids:
                        attrs_set.update({'Label' : label_ids[0].firstChild.data})
                        
                    producttypename_ids = attribute.getElementsByTagNameNS('*', 'ProductTypeName')
                    if producttypename_ids:
                        attrs_set.update({'ProductTypeName' : producttypename_ids[0].firstChild.data})
                        
                    smallimage_ids = attribute.getElementsByTagNameNS('*', 'SmallImage')
                    if smallimage_ids:
                        image_url_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'URL')
                        if image_url_ids:
                            attrs_set.update({'SmallImageURL' : image_url_ids[0].firstChild.data})
                            
                        image_height_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'Height')
                        if image_height_ids:
                            attrs_set.update({'SmallImageHeight' : image_height_ids[0].firstChild.data})
                        
                        image_width_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'Width')
                        if image_width_ids:
                            attrs_set.update({'SmallImageWidth' : image_width_ids[0].firstChild.data})
                        
                    packagequantity_ids = attribute.getElementsByTagNameNS('*', 'PackageQuantity')
                    if packagequantity_ids:
                        attrs_set.update({'PackageQuantity' : packagequantity_ids[0].firstChild.data})
                        
                    itemdimensions_ids = attribute.getElementsByTagNameNS('*', 'ItemDimensions')
                    if itemdimensions_ids:
                        idm_height_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Height')
                        if idm_height_ids:
                            attrs_set.update({'ItemDimensionsHeight' : idm_height_ids[0].firstChild.data})
                        
                        idm_length_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Length')
                        if idm_length_ids:
                            attrs_set.update({'ItemDimensionsLength' : idm_length_ids[0].firstChild.data})
                        
                        idm_width_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Width')
                        if idm_width_ids:
                            attrs_set.update({'ItemDimensionsWeight' : idm_width_ids[0].firstChild.data})
                             
                    brand_ids = attribute.getElementsByTagNameNS('*', 'Brand')
                    if brand_ids:
                        attrs_set.update({'Brand' : brand_ids[0].firstChild.data})
                        
                    studio_ids = attribute.getElementsByTagNameNS('*', 'Studio')
                    if studio_ids:
                        attrs_set.update({'Studio' : studio_ids[0].firstChild.data})
                        
                    manufacturer_ids = attribute.getElementsByTagNameNS('*', 'Manufacturer')
                    if manufacturer_ids:
                        attrs_set.update({'Manufacturer' : manufacturer_ids[0].firstChild.data})
                    
                    color_ids = attribute.getElementsByTagNameNS('*', 'Color')
                    if color_ids:
                        attrs_set.update({'Color' : color_ids[0].firstChild.data})
                    AttributeSets.append(attrs_set)
                prod_info.update({'AttributeSets': AttributeSets})
                
                # To get all variants of Products
                
                variants_list = []
                if cNode.getElementsByTagNameNS('*', 'Relationships'):
                    rel = cNode.getElementsByTagNameNS('*', 'Relationships').item(0)
                    for variant in rel.childNodes:
                        print ("======variant.nodeName=====", variant.nodeName)
                        if variant.nodeName == 'VariationParent':
                            v_asin = variant.getElementsByTagNameNS('*', 'ASIN')
                            if v_asin:
                                print(" v_asin[0].firstChild.data", v_asin[0].firstChild.data)
                                prod_info.update({'parent_asin' : v_asin[0].firstChild.data})
                        for identifier in variant.childNodes:
                            print ("======identifier.nodeName=====", identifier.nodeName)
                            if identifier.nodeName == 'Identifiers':
                                variants = {}
                                if identifier.getElementsByTagNameNS('*', 'ASIN'):
                                    asin = identifier.getElementsByTagNameNS('*', 'ASIN')
                                    variants.update({'asin': asin[0].firstChild.data})
                            else:
                                variants.update({identifier.nodeName[4:]: identifier.childNodes[0].data})
                        variants_list.append(variants)
                    attributes = {}            
                    for variant_val in variants_list:
                        for childkey in variant_val.keys():
                            if childkey != 'asin':
                                print ("===variant_val.get(k)==", variant_val.get(childkey))
                                if childkey not in attributes.keys():
                                    attributes.update({childkey: []})
                                print (attributes.get(childkey))
                                print(variant_val.get(childkey) not in attributes.get(childkey))
                                if variant_val.get(childkey) not in attributes.get(childkey):
                                    attributes.get(childkey).append(variant_val.get(childkey))
         
                    print ("====attributes====", attributes)
                    prod_info.update({'attributes':attributes})
                    prod_info.update({'variant_info':variants_list})
                    print ("====prod_info====", prod_info)
                 
                variants = {}
                for variant in cNode.getElementsByTagNameNS('*', 'VariationChild'):
                    v_attrs = {}
                    for var_attr in variant.childNodes:
                        if var_attr.nodeName != 'Identifiers':
                            v_attrs.update({var_attr.nodeName : var_attr[0].firstChild.data})
                    child_asin = variant.getElementsByTagNameNS('*', 'ASIN')
                    if child_asin:
                        variants.update({child_asin[0].firstChild.data: v_attrs})
                 
                    prod_info.update({'variants': variants})
                   
                # TO get features
                fetch_data = ''
                for fetc in cNode.getElementsByTagNameNS('*', 'Feature'):
                    fetch_data += fetc.firstChild.data + '\n'
                prod_info.update({'features': fetch_data})
                print ("prod_info", prod_info)
                products_info_list.append(prod_info)
                print ("products_info_list", products_info_list)
        return products_info_list
    
    def call_api(self, asin_list):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetMatchingProduct'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        if len(asin_list):
            count = 1
            for asin in asin_list:
                if asin:
                    asin_key = 'ASINList.ASIN.' + str(count)
                    count += 1
                    url_params[asin_key] = asin
#                     if count == 11:
#                         break

        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('GetMatchingProduct')
        return responseDOM, api
        
    def Get(self, asin_list):
        getsubmitfeed = {}
        responseDoM, api = self.call_api(asin_list)
        if responseDoM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(asin_list)
            error = responseDoM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDoM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(asin_list)
                error = responseDoM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDoM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            getsubmitfeed = self.get_products_info(responseDoM.getElementsByTagName('GetMatchingProductResponse'))
            return getsubmitfeed
        
##############################@###################################################################################################################################################


class GetMatchingProductForId:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)


    def get_products_info(self, nodelist):
        products_info_list = []
        for node in nodelist:
            for cNode in node.getElementsByTagNameNS('*', 'GetMatchingProductForIdResult'):
                print("cNode", cNode)
                prod_info = {}
                if cNode.attributes["Id"]:
                    prod_info.update({'SellerSKU': cNode.attributes["Id"].value})
                asin_ids = cNode.getElementsByTagNameNS('*', 'ASIN')
                if asin_ids:
                    prod_info.update({'asin' : asin_ids[0].firstChild.data})
                    
                title_ids = cNode.getElementsByTagNameNS('*', 'Title')
                if title_ids:
                    prod_info.update({'Title' : title_ids[0].firstChild.data})
                # To get attributes of variants product 
#                 childVariants = []
#                 if cNode.getElementsByTagNameNS('*','Relationships'):
#                     for variant in cNode.getElementsByTagNameNS('*','VariationChild'):
#                         if variant.getElementsByTagNameNS('*','Identifiers'):
#                             print"variants", variant
#                         else:
#                             variant_id = variant.getElementsByTagNameNS()
#                             prod_info.update({'attirbute_id'})
                            
                # To get Attributes of Products 
                AttributeSets = [] 
                for attribute in cNode.getElementsByTagNameNS('*', 'AttributeSets'):
                    attrs_set = {}
                    binding_ids = attribute.getElementsByTagNameNS('*', 'Binding')
                    if binding_ids:
                        attrs_set.update({'Binding' : binding_ids[0].firstChild.data})
                        
                    productgroup_ids = attribute.getElementsByTagNameNS('*', 'ProductGroup')
                    if productgroup_ids:
                        attrs_set.update({'ProductGroup' : productgroup_ids[0].firstChild.data})
                        
                    height_ids = attribute.getElementsByTagNameNS('*', 'Height')
                    if height_ids:
                        attrs_set.update({'PackageDimensionsHeight' : height_ids[0].firstChild.data})
                        
                    width_ids = attribute.getElementsByTagNameNS('*', 'Width')
                    if width_ids:
                        attrs_set.update({'PackageDimensionsWidth' : width_ids[0].firstChild.data})
                        
                    length_ids = attribute.getElementsByTagNameNS('*', 'Length')
                    if length_ids:
                        attrs_set.update({'PackageDimensionsLength' : length_ids[0].firstChild.data})
                        
                    weight_ids = attribute.getElementsByTagNameNS('*', 'Weight')
                    if weight_ids:
                        attrs_set.update({'PackageDimensionsWeight' : weight_ids[0].firstChild.data})
                        
                    label_ids = attribute.getElementsByTagNameNS('*', 'Label')
                    if label_ids:
                        attrs_set.update({'Label' : label_ids[0].firstChild.data})
                        
                    producttypename_ids = attribute.getElementsByTagNameNS('*', 'ProductTypeName')
                    if producttypename_ids:
                        attrs_set.update({'ProductTypeName' : producttypename_ids[0].firstChild.data})
                        
                    smallimage_ids = attribute.getElementsByTagNameNS('*', 'SmallImage')
                    if smallimage_ids:
                        image_url_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'URL')
                        if image_url_ids:
                            attrs_set.update({'SmallImageURL' : image_url_ids[0].firstChild.data})
                            
                        image_height_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'Height')
                        if image_height_ids:
                            attrs_set.update({'SmallImageHeight' : image_height_ids[0].firstChild.data})
                        
                        image_width_ids = smallimage_ids[0].getElementsByTagNameNS('*', 'Width')
                        if image_width_ids:
                            attrs_set.update({'SmallImageWidth' : image_width_ids[0].firstChild.data})
                        
                    packagequantity_ids = attribute.getElementsByTagNameNS('*', 'PackageQuantity')
                    if packagequantity_ids:
                        attrs_set.update({'PackageQuantity' : packagequantity_ids[0].firstChild.data})
                        
                    itemdimensions_ids = attribute.getElementsByTagNameNS('*', 'ItemDimensions')
                    if itemdimensions_ids:
                        idm_height_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Height')
                        if idm_height_ids:
                            attrs_set.update({'ItemDimensionsHeight' : idm_height_ids[0].firstChild.data})
                        
                        idm_length_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Length')
                        if idm_length_ids:
                            attrs_set.update({'ItemDimensionsLength' : idm_length_ids[0].firstChild.data})
                        
                        idm_width_ids = itemdimensions_ids[0].getElementsByTagNameNS('*', 'Width')
                        if idm_width_ids:
                            attrs_set.update({'ItemDimensionsWeight' : idm_width_ids[0].firstChild.data})
                             
                    brand_ids = attribute.getElementsByTagNameNS('*', 'Brand')
                    if brand_ids:
                        attrs_set.update({'Brand' : brand_ids[0].firstChild.data})
                    
                    size_ids = attribute.getElementsByTagNameNS('*', 'Size')
                    if size_ids:
                        attrs_set.update({'Size' : size_ids[0].firstChild.data})
                        
                    studio_ids = attribute.getElementsByTagNameNS('*', 'Studio')
                    if studio_ids:
                        attrs_set.update({'Studio' : studio_ids[0].firstChild.data})
                        
                    manufacturer_ids = attribute.getElementsByTagNameNS('*', 'Manufacturer')
                    if manufacturer_ids:
                        attrs_set.update({'Manufacturer' : manufacturer_ids[0].firstChild.data})
                    
                    color_ids = attribute.getElementsByTagNameNS('*', 'Color')
                    if color_ids:
                        attrs_set.update({'Color' : color_ids[0].firstChild.data})
                    AttributeSets.append(attrs_set)
                prod_info.update({'AttributeSets': AttributeSets})
                
                # To get all variants of Products
                variants_list = []
                if cNode.getElementsByTagNameNS('*', 'Relationships'):
                    rel = cNode.getElementsByTagNameNS('*', 'Relationships').item(0)
                    for variant in rel.childNodes:
                        print ("======variant.nodeName=====", variant.nodeName)
                        if variant.nodeName == 'VariationParent':
                            v_asin = variant.getElementsByTagNameNS('*', 'ASIN')
                            if v_asin:
                                print(" v_asin[0].firstChild.data", v_asin[0].firstChild.data)
                                prod_info.update({'parent_asin' : v_asin[0].firstChild.data})
                        for identifier in variant.childNodes:
                            print ("======identifier.nodeName=====", identifier.nodeName)
                            if identifier.nodeName == 'Identifiers':
                                variants = {}
                                if identifier.getElementsByTagNameNS('*', 'ASIN'):
                                    asin = identifier.getElementsByTagNameNS('*', 'ASIN')
                                    variants.update({'asin': asin[0].firstChild.data})
                            else:
                                variants.update({identifier.nodeName[4:]: identifier.childNodes[0].data})
                        variants_list.append(variants)
                    attributes = {}            
                    for variant_val in variants_list:
                        for childkey in variant_val.keys():
                            if childkey != 'asin':
                                print ("===variant_val.get(k)==", variant_val.get(childkey))
                                if childkey not in attributes.keys():
                                    attributes.update({childkey: []})
                                print (attributes.get(childkey))
                                print (variant_val.get(childkey) not in attributes.get(childkey))
                                if variant_val.get(childkey) not in attributes.get(childkey):
                                    attributes.get(childkey).append(variant_val.get(childkey))
         
                    print ("====attributes====", attributes)
                    prod_info.update({'attributes':attributes})
                    prod_info.update({'variant_info':variants_list})
                    print ("====prod_info====", prod_info)
                   
                # TO get features
                fetch_data = ''
                for fetc in cNode.getElementsByTagNameNS('*', 'Feature'):
                    fetch_data += fetc.firstChild.data + '\n'
                prod_info.update({'features': fetch_data})
                print ("prod_info", prod_info)
                products_info_list.append(prod_info)
                print ("products_info_list", products_info_list)
        return products_info_list

    def call_api(self, sku_list, sku_type='SellerSKU'):

        logger.info("sku_list....>>>...................%s", sku_list)
        logger.info("sku_type.>>>>>......................%s", sku_type)
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetMatchingProductForId'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'IdType': sku_type, 'Version':version}
        print("url_params", url_params)
        if len(sku_list):
            count = 1
            for sku in sku_list:
                sku = sku.encode('ascii', 'ignore')
                if sku:
                    asin_key = 'IdList.Id.' + str(count)
                    count += 1
                    url_params[asin_key] = sku
#                     if count == 11:
#                         break

        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        print("url_params?????????????", url_params)
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A','')
        print("url_string?????????????", url_string)
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('GetMatchingProductForId')
        return responseDOM, api
        
    def Get(self, sku_list, sku_type='SellerSKU'):
        getsubmitfeed = {}
        responseDoM, api = self.call_api(sku_list, sku_type)
        logger.info("responseDoM.ipshitaaaaaaaaaaaaaaa...%s", responseDoM)
        while responseDoM == None:
            time.sleep(25)
            responseDoM, api = self.call_api(sku_list, sku_type)
            error = responseDoM.getElementsByTagName('Error')
            logger.info("error..abcccccc.....................%s", error)
            getsubmitfeed = api.getErrors(error)
            logger.info("getsubmitfeed.reeeeeevesre......................%s", getsubmitfeed.get('Code'))
        error = responseDoM.getElementsByTagName('Error')
        logger.info("responseDoM.getElementsByTagName('Error').......................%s", responseDoM.getElementsByTagName('Error'))
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDoM, api = self.call_api(sku_list, sku_type)
                logger.info("responseDoM.......................%s", responseDoM)
                error = responseDoM.getElementsByTagName('Error')
                logger.info("error.bbbbbbbbbbbbbbbb......................%s", error)
                getsubmitfeed = api.getErrors(error)
                logger.info("getsubmitfeedssssssssssssss.......................%s", getsubmitfeed)
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info("getsubmitfeed....ddddddddddddddddddd...................%s", getsubmitfeed)
            return getsubmitfeed
        else:
            getsubmitfeed = self.get_products_info(responseDoM.getElementsByTagName('GetMatchingProductForIdResponse'))
            logger.info("getsubmitfeed.......................%s", getsubmitfeed)
            return getsubmitfeed


################################################################################################################################
class GetProductCategoriesForASIN:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def get_category_info(self, node_list):
        info1 = {}
        for cNode in node_list:
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'GetProductCategoriesForASINResult':
                    for cNode2 in cNode1.childNodes:
                        if cNode2.nodeName == 'Self':
                            for cNode8 in cNode2.childNodes:
                                if cNode8.nodeName == 'ProductCategoryName':
                                    info1[cNode8.nodeName] = cNode8.childNodes[0].data
                                if cNode8.nodeName == 'ProductCategoryId':
                                    info1[cNode8.nodeName] = cNode8.childNodes[0].data
                                if cNode8.nodeName == 'Parent':
                                    for cNode3 in cNode8.childNodes:
                                        p_cat = {}
                                        if cNode3.nodeName == 'ProductCategoryName':
                                            p_cat[cNode3.nodeName] = cNode3.childNodes[0].data
                                        if cNode3.nodeName == 'ProductCategoryId':
                                            p_cat[cNode3.nodeName] = cNode3.childNodes[0].data
                                    if p_cat:
                                        info1[cNode8.nodeName] = p_cat
                
        return info1 
    
    def call_api(self, asin):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetProductCategoriesForASIN'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['ASIN'] = asin
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        logger.error('api.url_string %s', api.url_string)
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
        
    def Get(self, asin):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(asin)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(asin)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(asin)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            category_data = self.get_category_info(responseDOM.getElementsByTagName('GetProductCategoriesForASINResponse'))
            return category_data

        
################################################################################################################################
class GetProductCategoriesForSKU:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def get_category_info(self, node_list):
        info1 = {}
        for cNode in node_list:
            for cNode1 in cNode.childNodes:
                if cNode1.nodeName == 'GetProductCategoriesForSKUResult':
                    for cNode2 in cNode1.childNodes:
                        if cNode2.nodeName == 'Self':
                            for cNode8 in cNode2.childNodes:
                                if cNode8.nodeName == 'ProductCategoryName':
                                    info1[cNode8.nodeName] = cNode8.childNodes[0].data
                                if cNode8.nodeName == 'ProductCategoryId':
                                    info1[cNode8.nodeName] = cNode8.childNodes[0].data
                                if cNode8.nodeName == 'Parent':
                                    for cNode3 in cNode8.childNodes:
                                        p_cat = {}
                                        if cNode3.nodeName == 'ProductCategoryName':
                                            p_cat[cNode3.nodeName] = cNode3.childNodes[0].data
                                        if cNode3.nodeName == 'ProductCategoryId':
                                            p_cat[cNode3.nodeName] = cNode3.childNodes[0].data
                                    if p_cat:
                                        info1[cNode8.nodeName] = p_cat
                
        return info1 
    
    def call_api(self, sku):
        logger.info('sku category ===> %s', sku)
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetProductCategoriesForSKU'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['SellerSKU'] = sku
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        logger.error('api.url_string %s', api.url_string)
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
        
    def Get(self, sku):
        logger.info('sku get ===> %s', sku)
        getsubmitfeed = {}
        responseDOM, api = self.call_api(sku)
        while responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(sku)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(sku)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            category_data = self.get_category_info(responseDOM.getElementsByTagName('GetProductCategoriesForSKUResponse'))
            return category_data
        

class GetCompetitivePricingForSKU:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        logger.info('access_key%s', access_key)
        logger.info('rsecret_key %s', secret_key)
        logger.info('merchant_id %s', merchant_id)
        logger.info('marketplace_id %s', marketplace_id)
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
     
    def get_competitiveprice_sku_info(self, node_list):
        info = {}
        data_list = []
        cnt = 0
        scnt = 0
        for cNode in node_list:
            info['SellerSKU'] = cNode.getAttribute('SellerSKU')
            for cNode1 in cNode.childNodes:
                    if cNode1.nodeName == 'Product':
                        for cNode3 in cNode1.childNodes:
                            if cNode3.nodeName == 'Identifiers':
                                for cNode4 in cNode3.childNodes:
                                    if cNode4.nodeName == 'MarketplaceASIN':
                                            for cNode5 in cNode4.childNodes:
                                                if cNode5.nodeName == 'ASIN':
                                                    info['ASIN'] = cNode5.childNodes[0].data
                        for cNode11 in cNode1.childNodes:
                            if cNode11.nodeName == 'CompetitivePricing':
                                for cNode2 in cNode11.childNodes:
                                    if cNode2.nodeName == 'CompetitivePrices':
                                        for cNode21 in cNode2.childNodes:
                                            print ('ccNode21', cNode21.nodeName)
                                            if cNode21.nodeName == 'CompetitivePrice':
                                                if cNode21.getAttribute('belongsToRequester') == 'true':
                                                    buy_box = True
                                                    info['buy_box'] = buy_box
                                                for cNode3 in cNode21.childNodes:
                                                    print ('ccNode21===', cNode3.nodeName)
                                                    if cNode3.nodeName == 'Price':
                                                        for cNode4 in cNode3.childNodes:
                                                            if cNode4.nodeName == 'LandedPrice':
                                                                for cNode5 in cNode4.childNodes:
                                                                    if cNode5.nodeName == 'Amount':
                                                                        info[cNode5.nodeName] = cNode5.childNodes[0].data
            if info != {}:
                data_list.append(info)
                info = {}
        return data_list   
        
    def call_api(self, sku_list):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetCompetitivePricingForSKU'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        if len(sku_list):
            count = 1
            for sku in sku_list:

                    sku_key = 'SellerSKUList.SellerSKU.' + str(count)
                    count += 1
                    url_params[sku_key] = sku
                    if count == 20:
                        break
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
        
    def Get(self, sku_list):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(sku_list)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(sku_list)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(sku_list)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            data_list = self.get_competitiveprice_sku_info(responseDOM.getElementsByTagName('GetCompetitivePricingForSKUResult'))
            return data_list

    def call(self, amazon_instance, method, *arguments):
        result = False
        if method == 'GetCompetitivePricingForSKU':
            lmp = GetCompetitivePricingForSKU(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id)
            result = lmp.Get(arguments[0])
        return result


#################################################################################################################
class GetCompetitivePricingForASIN:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
      
    def get_competitiveprice_asin_info(self, node_list):
        info = {}
        data_list = []
        for cNode in node_list:
            buy_box = False
            for cNode1 in cNode.childNodes:
                    if cNode1.nodeName == 'Product':
                        for cNode3 in cNode1.childNodes:
                            if cNode3.nodeName == 'Identifiers':
                                for cNode4 in cNode3.childNodes:
                                        if cNode4.nodeName == 'MarketplaceASIN':
                                            for cNode5 in cNode4.childNodes:
                                                if cNode5.nodeName == 'ASIN':
                                                    info[cNode5.nodeName] = cNode5.childNodes[0].data
                        for cNode11 in cNode1.childNodes:
                                if cNode11.nodeName == 'CompetitivePricing':
                                    for cNode2 in cNode11.childNodes:
                                        if cNode2.nodeName == 'CompetitivePrices':
                                            for cNode21 in cNode2.childNodes:
                                                print ('ccNode21', cNode21.nodeName)
                                                if cNode21.nodeName == 'CompetitivePrice':
                                                    if cNode21.getAttribute('belongsToRequester') == 'true':
                                                        buy_box = True
                                                        info['buy_box'] = buy_box
                                                    for cNode3 in cNode21.childNodes:
                                                        if cNode3.nodeName == 'Price':
                                                            for cNode4 in cNode3.childNodes:
                                                                if cNode4.nodeName == 'LandedPrice':
                                                                    for cNode5 in cNode4.childNodes:
                                                                        if cNode5.nodeName == 'Amount':
                                                                            info[cNode5.nodeName] = cNode5.childNodes[0].data
            if info != {}       :
                data_list.append(info)
                info = {}
        return data_list
      
    def call_api(self, asin_list):
        api = Call()
        api.Session = self.Session
        buy_box = False
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetCompetitivePricingForASIN'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        if len(asin_list):
            count = 1
            for asin in asin_list:
                if asin:
                    asin_key = 'ASINList.ASIN.' + str(count)
                    count += 1
                    url_params[asin_key] = asin
                    if count == 21:
                        break

        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
        
    def Get(self, asin_list):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(asin_list)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(asin_list)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(asin_list)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            data_list = self.get_competitiveprice_asin_info(responseDOM.getElementsByTagName('GetCompetitivePricingForASINResult'))
            return data_list

    def call(self, amazon_instance, method, *arguments):
        result = False
        if method == 'GetCompetitivePricingForASIN':
            lmp = GetCompetitivePricingForASIN(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id)
            result = lmp.Get(arguments[0])
        return result
    
    
class ListInventorySupply:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
    
    def submitresult(self, nodelist):
        prod_inventory_list = [] 
        datas = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'NextToken':
                    datas[cNode.nodeName] = cNode.nodeName[0].data
                if cNode.nodeName == 'InventorySupplyList':
                    for cNode2 in cNode.childNodes:
                        if cNode2.nodeName == 'member':
                            info = {}
                            for cNode1 in cNode2.childNodes:
                                if cNode1.nodeName == 'TotalSupplyQuantity':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                                if cNode1.nodeName == 'InStockSupplyQuantity':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                                if cNode1.nodeName == 'SellerSKU':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                            prod_inventory_list.append(info)
                            logger.info('Inventory dict...........: %s', info)
        datas.update({'inventories': prod_inventory_list})
        return datas
    
    def call_api(self, sellersku):
        if isinstance(sellersku, list):
            sellersku = sellersku
        else:
            sellersku = [sellersku]
        logger.info('sellersku...........: %s', sellersku)
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'ListInventorySupply'
        command = '/FulfillmentInventory/2010-10-01?'

        url_params = {'Action':method, 'ResponseGroup':'Basic', 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        count = 1
        for sku in sellersku:
            url_params['SellerSkus.member.' + str(count)] = sku
            count += 1
        post_data = '/FulfillmentInventory/2010-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        responseDoM = api.MakeCall('ListInventorySupply')
        logger.info('responseDoM...........: %s', responseDoM)
        return responseDoM, api
     
    def Get(self, sellersku):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(sellersku)
        logger.info('responseDOM...........: %s', responseDOM)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(sellersku)
        error = responseDOM.getElementsByTagName('Error')
        logger.info('error...........: %s', error)
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info('getsubmitfeed...........: %s', getsubmitfeed)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(30)
                responseDOM, api = self.call_api(sellersku)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
                logger.info('getsubmitfeed...........: %s', getsubmitfeed)
        error = responseDOM.getElementsByTagName('Error')
        logger.info('error...........: %s', error)
        if error:
            getsubmitfeed = api.getErrors(error)
            logger.info('getsubmitfeed...........: %s', getsubmitfeed)
            return getsubmitfeed
        else:
            getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('ListInventorySupplyResult'))
            return getsubmitfeed

    
class ListInventorySupplyByNextToken:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
    
    def submitresult(self, nodelist):
        prod_inventory_list = [] 
        datas = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'NextToken':
                    datas[cNode.nodeName] = cNode.nodeName[0].data
                if cNode.nodeName == 'InventorySupplyList':
                    for cNode2 in cNode.childNodes:
                        if cNode2.nodeName == 'member':
                            info = {}
                            for cNode1 in cNode2.childNodes:
                                if cNode1.nodeName == 'TotalSupplyQuantity':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                                if cNode1.nodeName == 'InStockSupplyQuantity':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                                if cNode1.nodeName == 'SellerSKU':
                                    info[cNode1.nodeName] = cNode1.childNodes[0].data
                                prod_inventory_list.append(info)
        datas.update({'inventories': prod_inventory_list})
        return datas
    
    def call_api(self, sellersku):
        api = Call()
        api.Session = self.Session
        version = '2010-10-01'
        method = 'ListInventorySupplyByNextToken'
        command = '/FulfillmentInventory/2010-10-01?'
        url_params = {'Action':method, 'ResponseGroup':'Basic', 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['NextToken'] = sellersku
        post_data = '/FulfillmentInventory/2010-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        responseDoM = api.MakeCall('ListInventorySupplyByNextToken')
        return responseDoM, api
     
    def Get(self, sellersku):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(sellersku)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(sellersku)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(sellersku)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('ListInventorySupplyResult'))
            return getsubmitfeed


class POST_PRODUCT_IMAGE_DATA:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def submitresult(self, nodelist):
        info = {}
        for node in nodelist:
            for cNode in node.childNodes:
                if cNode.nodeName == 'FeedSubmissionInfo':
                    if cNode.childNodes[0].childNodes:
                        for gcNode in cNode.childNodes:
                            if gcNode.nodeName == 'FeedSubmissionId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
        return info
    
    def call_api(self, requestData):
        requestData = requestData.strip()
        api = Call()
        api.Session = self.Session
        version = '2009-01-01'
        method = 'SubmitFeed'
        command = '/?'
        url_params = {'Action':method, 'Merchant':self.Session.merchant_id, 'FeedType':'_POST_PRODUCT_IMAGE_DATA_', 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        url_params['PurgeAndReplace'] = 'false'
        post_data = '/'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = requestData
        responseDoM = api.MakeCall('POST_PRODUCT_IMAGE_DATA')
        return responseDoM, api
     
    def Get(self, requestData):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(requestData)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(requestData)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(requestData)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            getsubmitfeed = self.submitresult(responseDOM.getElementsByTagName('SubmitFeedResult'))
            return getsubmitfeed


class GetLowestOfferListingsForASIN:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)

    def lowest_price_asin(self, nodelist):
        info = {}
        node_list = nodelist.getElementsByTagName('LandedPrice')
        if node_list:
            for cNode in node_list[0].childNodes:
                if cNode.nodeName == 'Amount':
                    info.update({'lowestamount' : cNode.childNodes[0].data })
        return info

    def call_api(self, asin):
        api = Call()
        api.Session = self.Session
        buy_box = False
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetLowestOfferListingsForASIN'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['ASINList.ASIN.1'] = asin
        url_params['ItemCondition'] = 'New'
        url_params['ExcludeMe'] = 'true'
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
     
    def Get(self, asin):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(asin)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(asin)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(asin)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            lowest_asin_dict = self.lowest_price_asin(responseDOM.getElementsByTagName('Error'))
            return lowest_asin_dict
    
    def call(self, amazon_instance, method, *arguments):
        result = False
        if method == 'GetLowestOfferListingsForASIN':
            lmp = GetLowestOfferListingsForASIN(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id)
            result = lmp.Get(arguments[0])
        return result

    
# For getting Current price of Asin
class GetMyPriceForASIN:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, marketplace_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, marketplace_id, domain)
        
    def myprice_asin(self, node_list1, node_list2):
        info = {}
        for cNode in node_list1[0].childNodes:
            if cNode.nodeName == 'Amount':
                info.update({'currentprice' : cNode.childNodes[0].data })
                
        # GET SHIPPING           
        for cNode in node_list2[0].childNodes:
            if cNode.nodeName == 'Amount':
                info.update({'shipping' : cNode.childNodes[0].data })
        return info    
    
    def call_api(self, asin):
        api = Call()
        api.Session = self.Session
        command = '/Products/2011-10-01?'
        version = '2011-10-01'
        method = 'GetMyPriceForASIN'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'MarketplaceId':self.Session.marketplace_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
        url_params['ASINList.ASIN.1'] = asin
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + '.000Z'
        post_data = '/Products/2011-10-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall(method)
        return responseDOM, api
     
    def Get(self, asin):
        getsubmitfeed = {}
        responseDOM, api = self.call_api(asin)
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api(asin)
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api(asin)
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            data = self.myprice_asin(responseDOM.getElementsByTagName('LandedPrice'), responseDOM.getElementsByTagName('Shipping'))
            return data
    
    def call(self, amazon_instance, method, *arguments):
        result = False
        if method == 'GetMyPriceForASIN':
            lmp = GetMyPriceForASIN(amazon_instance.aws_access_key, amazon_instance.secret_key, amazon_instance.merchant_id, amazon_instance.market_place_id)
            result = lmp.Get(arguments[0])
        return result

    
class ListMarketplaceParticipations:
    Session = Session()

    def __init__(self, access_key, secret_key, merchant_id, domain):
        self.Session.Initialize(access_key, secret_key, merchant_id, domain=domain)
        
    def getMarketplaceParticipation(self, nodelist):
        transDetails = []
        
        for node in nodelist:
            for cNode in node.childNodes:
                info = {}
#                print 'cNode.nodeName',cNode.nodeName
                if cNode.nodeName == 'Marketplace':
                    if len(cNode.childNodes):
                        for gcNode in cNode.childNodes:
#                            print '-----------------',gcNode.nodeName
                            if gcNode.nodeName == 'MarketplaceId':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'DefaultCountryCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'DomainName':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'Name':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'DefaultCurrencyCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                            elif gcNode.nodeName == 'DefaultLanguageCode':
                                info[gcNode.nodeName] = gcNode.childNodes[0].data
                        transDetails.append(info)
#        print 'transDetails',transDetails
        return transDetails
    
    def call_api(self):
        api = Call()
        api.Session = self.Session
        version = '2011-07-01'
        method = 'ListMarketplaceParticipations'
        command = '/Sellers/2011-07-01?'
        url_params = {'Action':method, 'SellerId':self.Session.merchant_id, 'AWSAccessKeyId':self.Session.access_key, 'SignatureVersion':'2', 'SignatureMethod':'HmacSHA256', 'Version':version}
#        if timeto:
#            url_params['LastUpdatedBefore'] = timeto
        url_params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + 'Z'
        post_data = '/Sellers/2011-07-01'
        url_params['Signature'] = api.calc_signature(url_params, post_data)[0]
        url_string = api.calc_signature(url_params, post_data)[1].replace('%0A', '')
        api.url_string = str(command) + url_string
        api.RequestData = ''
        responseDOM = api.MakeCall('ListMarketplaceParticipations')
        logger.info('responseDOM ===> %s', responseDOM)
        return responseDOM, api
     
    def Get(self):
        getsubmitfeed = {}
        responseDOM, api = self.call_api()
        if responseDOM == None:
            time.sleep(25)
            responseDOM, api = self.call_api()
            error = responseDOM.getElementsByTagName('Error')
            getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            while getsubmitfeed.get('Code', False) in ['SignatureDoesNotMatch', 'Request is throttled', 'RequestThrottled']:
                if getsubmitfeed.get('Code') in ['Request is throttled', 'RequestThrottled']:
                    time.sleep(120)
                else:
                    time.sleep(25)
                responseDOM, api = self.call_api()
                error = responseDOM.getElementsByTagName('Error')
                getsubmitfeed = api.getErrors(error)
        error = responseDOM.getElementsByTagName('Error')
        if error:
            getsubmitfeed = api.getErrors(error)
            return getsubmitfeed
        else:
            getMarketdetails = self.getMarketplaceParticipation(responseDOM.getElementsByTagName('ListMarketplaces'))
            if responseDOM.getElementsByTagName('NextToken'):
                getMarketdetails = getMarketdetails + [{'NextToken':responseDOM.getElementsByTagName('NextToken')[0].childNodes[0].data}]
            return getMarketdetails

    
def call(amazon_shop, method, *arguments):
        print("arguments", arguments)
        if method == 'ListOrders':
            lo = ListOrders(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lo.Get(arguments[0], arguments[1])
            return result
        elif method == 'ListOrderItems':
            lo = ListOrderItems(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lo.Get(arguments[0])
            print("resultssssssssssssss", result)
            return result
        elif method == 'ListOrdersByNextToken':
            lo = ListOrdersByNextToken(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lo.Get(arguments[0])
            return result
        elif method == 'ListOrderItemsByNextToken':
            lo = ListOrderItemsByNextToken(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lo.Get(arguments[0], arguments[1])
            return result
        elif method == 'POST_INVENTORY_AVAILABILITY_DATA':
            pi = POST_INVENTORY_AVAILABILITY_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = pi.Get(arguments[0])
            return result
        elif method == 'POST_ORDER_FULFILLMENT_DATA':
            po = POST_ORDER_FULFILLMENT_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = po.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_PRICING_DATA':
            po = POST_PRODUCT_PRICING_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = po.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_DATA':
            pp = POST_PRODUCT_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = pp.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_IMAGE_DATA':
            pi = POST_PRODUCT_IMAGE_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = pi.Get(arguments[0])
            return result
        
        elif method == '_POST_PRODUCT_OVERRIDES_DATA_':
            pi = POST_PRODUCT_OVERRIDES_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = pi.Get(arguments[0])
            return result
        elif method == 'GetFeedSubmissionResult':
            gfs = GetFeedSubmissionResult(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = gfs.Get(arguments[0])
            return result
        elif method == 'GetFeedSubmissionResultall':
            gfs = GetFeedSubmissionResult(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = gfs.Get_all(arguments[0])
            return result
        elif method == 'ListMatchingProducts':
            lmp = ListMatchingProducts(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0], arguments[1])
            return result

        elif method == 'GetMatchingProduct':
            lmp = GetMatchingProduct(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetMatchingProductForId':
            lmp = GetMatchingProductForId(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print("areguemenenene", lmp.Get(arguments[0]),len(arguments))
            if len(arguments) > 1:
                result = lmp.Get(arguments[0], arguments[1])
                print("extraaaaaaaaaaaresult>>>>>>>>>>>>>>>>>>>>", result)
            else:
                result = lmp.Get(arguments[0])
                print("resultresultresult", result)
            return result
        
        elif method == 'GetProductCategoriesForASIN':
            lmp = GetProductCategoriesForASIN(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result 
        elif method == 'GetProductCategoriesForSKU':
            lmp = GetProductCategoriesForSKU(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result 
        elif method == 'RequestReport':
            lmp = RequestReport(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print ("arguemnt", arguments)
            if len(arguments) > 1:
                result = lmp.Get(method, arguments[0], arguments[1])
            else:
                result = lmp.Get(method, arguments[0])
            return result
        elif method == 'GetReportRequestList':
            lmp = GetReportRequestList(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            if len(arguments) > 1:
                result = lmp.Get(method, arguments[0], arguments[1])
            else:
                result = lmp.Get(method, arguments[0])
            return result
        elif method == 'GetReport':
            lmp = GetReport(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            if len(arguments) > 1:
                result = lmp.Get(method, arguments[0], arguments[1])
            else:
                result = lmp.Get(method, arguments[0])
            return result
        elif method == 'ListInventorySupply':
            lmp = ListInventorySupply(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'ListInventorySupplyByNextToken':
            lmp = ListInventorySupplyByNextToken(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetCompetitivePricingForASIN':
            lmp = GetCompetitivePricingForASIN(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print(arguments[0])
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetCompetitivePricingForSKU':
            lmp = GetCompetitivePricingForSKU(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print (arguments[0])
            result = lmp.Get(arguments[0])
            return result
        elif method == 'POST_PRODUCT_RELATIONSHIP_DATA':
            pi = POST_PRODUCT_RELATIONSHIP_DATA(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = pi.Get(arguments[0])
            return result
        elif method == 'GetLowestOfferListingsForASIN':
            lmp = GetLowestOfferListingsForASIN(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print (arguments[0])
            result = lmp.Get(arguments[0])
            return result
        elif method == 'GetMyPriceForASIN':
            lmp = GetMyPriceForASIN(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            print (arguments[0])
            result = lmp.Get(arguments[0])
            return result
        
        elif method == 'ListMarketplaceParticipations':
            lmp = ListMarketplaceParticipations(amazon_shop.aws_access_key_id, amazon_shop.aws_secret_access_key, amazon_shop.aws_merchant_id, amazon_shop.domain)
            result = lmp.Get()
            return result
        
        elif method == 'GetOrder':
            lmp = GetOrder(amazon_shop.amazon_instance_id.aws_access_key_id, amazon_shop.amazon_instance_id.aws_secret_access_key, amazon_shop.amazon_instance_id.aws_merchant_id, amazon_shop.aws_market_place_id, amazon_shop.domain)
            result = lmp.Get(arguments[0])
            return result
