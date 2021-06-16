# -*- coding: utf-8 -*-
# Author: Jason Wu (jaronemo@msn.com)
from odoo import api, fields, models
from odoo.exceptions import UserError
import datetime


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_password(self):
        str = datetime.datetime.now()
        password = (str.strftime('%Y%m%d%H%M'))
        return password

    origin_password = fields.Char(string='預設密碼', default=_get_password)
    lancer_team_id = fields.Many2one('lancer.team', string='所屬義成團隊')

    @api.model
    def create(self, vals):
        res = super(ResUsers, self).create(vals)
        res.password = res.origin_password
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


class LancerTeam(models.Model):
    _name = "lancer.team"
    _description = "義成銷售團隊"
    _order = "sequence"

    name = fields.Char('名稱', required=True)
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the Sales Team without removing it.")
    user_id = fields.Many2one('res.users', string='團隊主管')
    member_ids = fields.One2many(
        'res.users', 'lancer_team_id', string='所屬義成團隊',
        domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_user').id)])
