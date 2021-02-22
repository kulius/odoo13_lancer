# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class QuoteOrder(models.Model):
    _name = "quote.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Quote Order"
    _order = 'date_order desc, id desc'

    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'))
    origin = fields.Char(string='Source Document', help="Reference of the document that generated this sales order request.")


class SaleOrderLine(models.Model):
    _name = 'quote.order.line'
    _description = 'Sales Order Line'
    _order = 'order_id, sequence, id'
    _check_company_auto = True

    order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

