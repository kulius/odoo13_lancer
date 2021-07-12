# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string="是否為客戶")
    is_supplier = fields.Boolean(string="是否為供應商")
