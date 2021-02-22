from openerp import models, fields, api, _
import time
from openerp import netsvc
from openerp.tools .translate import _
from openerp.exceptions import UserError


class StockMove(models.Model):   
    _inherit = "stock.move"

    def _action_done(self):
        product_obj=self.env['product.product']
        shop_obj=self.env['sale.shop']
        workflow_obj = self.env['amazon.order.workflow']
        workflow_id = workflow_obj.search([])
        res = super(StockMove, self)._action_done()
        print("self ",self,self.product_id)
        order = self.env['sale.order'].search([('name','=',self.origin)])
        print("orderorder",order,order.shop_id)
        if workflow_id.real_inventory_update==True:
            for move in self:
                shop_obj.UpdateRealInventory(self.product_id,order.shop_id,move.product_uom_qty)
                print
