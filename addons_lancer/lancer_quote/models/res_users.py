# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models
from odoo.exceptions import UserError
import datetime


class ResUsers(models.Model):
    _inherit = 'res.users'

    origin_password = fields.Char(string='原始密碼')

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        str = datetime.datetime.now()
        password = (str.strftime('%Y%m%d%H%M'))
        res.password = (str.strftime('%Y%m%d%H%M'))
        res.origin_password = password
        return res

    @api.model
    def change_password(self, old_passwd, new_passwd):
        res = super(ResUsers, self).change_password(old_passwd, new_passwd)
        self.env.user.write({'origin_password': new_passwd})
        return res


class ChangePasswordUser(models.TransientModel):
    _inherit = 'change.password.user'

    def change_password_button(self):
        for line in self:
            if not line.new_passwd:
                raise UserError(_("Before clicking on 'Change Password', you have to write a new password."))
            line.user_id.write({'password': line.new_passwd, 'origin_password': line.new_passwd})
        # don't keep temporary passwords in the database longer than necessary
        self.write({'new_passwd': False})

