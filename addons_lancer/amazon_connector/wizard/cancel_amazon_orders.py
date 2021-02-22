# -*- coding: utf-8 -*-
from operator import invert
from odoo import models, fields, api,_
from odoo.tools.translate import _
# import amazon_connector.amazonerp_osv as connection_obj
import logging
import socket
import time
from datetime import timedelta,datetime
import datetime
#import mx.DateTime as dt
from openerp import netsvc
# import cStringIO
from io import StringIO
from urllib.parse import urlencode
#import Image
import os
from base64 import b64decode
import urllib
import base64
from operator import itemgetter
from itertools import groupby

class  CancelUploadedAmazonOrders(models.TransientModel):
    _name = "cancel.uploaded.amazon.orders"
    
    reason = fields.Selection([
            ('NoInventory','No Inventory'),
            ('ShippingAddressUndeliverable','Shipping Address Undeliverable'),
            ('CustomerExchange','Customer Exchange'),
            ('BuyerCanceled','Buyer Canceled'),
            ('GeneralAdjustment','General Adjustment'),
            ('CarrierCreditDecision','Carrier Credit Decision'),
            ('RiskAssessmentInformationNotValid','Risk Assessment Information Not Valid'),
            ('CarrierCoverageFailure','Carrier Coverage Failure'),
            ('CustomerReturn','Customer Return'),
            ('MerchandiseNotReceived','Merchandise Not Received')], string='Cancel Reason',help='Reason For Cancelling the Order')

#    @api.multi
    def cancel_amazon_orders(self):
        sale_shop_obj = self.env['sale.shop']
        data = self[0]
        amazon_shop_ids = sale_shop_obj.search([('amazon_shop','=',True)])
        if not len(amazon_shop_ids):
            return True
        
        res = amazon_shop_ids[0].with_context({'order_ids': self._context.get('active_ids')}).cancel_amazon_orders(data.reason)
        return res
