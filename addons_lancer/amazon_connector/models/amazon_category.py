from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
import logging
logger = logging.getLogger('amazon')


class AmazonCategory(models.Model):
    
    _name = 'amazon.category'
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'name'
    _order = 'parent_left'
    
    
    name = fields.Char(string="Name",index=True, required=True, translate=True)
    amazon_category = fields.Boolean(string='Amazon Category')
    amazon_cat_id = fields.Char(string="Amazon Category ID")
    shop_ids = fields.Many2many('sale.shop', 'amazon_categ_shop_rel', 'amazon_categ_id', 'shop_id', string="Shops")
    parent_id = fields.Many2one('product.category',string="Parent Category")
#     parent_id = fields.Many2one('product.category', 'Parent Category', index=True, ondelete='cascade')
    child_id = fields.One2many('product.category', 'parent_id', 'Child Categories')
#     type = fields.Selection([
#         ('view', 'View'),
#         ('normal', 'Normal')], 'Category Type', default='normal',
#         help="A category of the view type is a virtual category that can be used as the parent of another category to create a hierarchical structure.")
    parent_left = fields.Integer('Left Parent', index=1)
    parent_right = fields.Integer('Right Parent', index=1)
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this category (Does not consider the children categories)")
    
    
    def _compute_product_count(self):
        for rec in self:
            product_ids = self.env['product.template'].search([('amazon_categ_id','=',rec.id)])
            rec.product_count = len(product_ids)
#     def _compute_product_count(self):
#         read_group_res = self.env['product.template'].read_group([('categ_id', 'in', self.ids)], ['categ_id'], ['categ_id'])
#         group_data = dict((data['categ_id'][0], data['categ_id_count']) for data in read_group_res)
#         for categ in self:
#             categ.product_count = group_data.get(categ.id, 0)

#     @api.constrains('parent_id')
#     def _check_category_recursion(self):
#         if not self._check_recursion():
#             raise ValidationError(_('Error ! You cannot create recursive categories.'))
#         return True

    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                res.append(cat.name)
                cat = cat.parent_id
            return res
            
        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]
    
    
    
    def create_amazon_category(self, shops, categ_list):
        logger.info("Create Category From List ---> %s",  categ_list)
        # create category from list of category dict
        # categ_list : List of category_info list
        for categ in categ_list:
            parents = categ.get('browsePathById', False)
            p_id = False
            if parents:
                p_datas = parents.split(',')
                if len(p_datas) >= 2:
                    parent_values = p_datas[:-1]
                    if parent_values:
                        parent_id = parent_values[len(parent_values)-1]
                        p_ids = self.search([('amazon_cat_id', '=', parent_id)])
                        if p_ids:
                            p_id = p_ids[0].id
            
            
            cat_vals = {
                'amazon_category' : True,
                'amazon_cat_id' : categ.get('browseNodeId', False),
                'name' : categ.get('browseNodeName', False),
                'parent_id' : p_id
            }
            
            try:
                c_ids = self.search([('amazon_cat_id', '=', categ.get('browseNodeId', False))])    
                if c_ids:
                    c_id = c_ids[0]
                    c_ids.write(cat_vals)
                    logger.info("Update Category : %s with ID %s"%(c_id.name, c_id.id,))
                else:
                    c_id = self.create(cat_vals)
                    logger.info("Created Category : %s with ID %s"%(c_id.name, c_id.id,))
                self.env.cr.commit()
                self.env.cr.execute("select amazon_categ_id from amazon_categ_shop_rel where amazon_categ_id = %s and shop_id = %s"%(c_id.id, shops.id))
                if not self.env.cr.fetchone():
                    self.env.cr.execute("insert into amazon_categ_shop_rel values(%s, %s)"%(c_id.id, shops.id,))
            except Exception as e:
                logger.info('Error %s', e, exc_info=True)
                pass

    def name_search(self, name, args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            # Be sure name_search is symetric to name_get
            category_names = name.split(' / ')
            print("========category_names===>",category_names)
            parents = list(category_names)
            print("========parents===>",parents)
            child = parents.pop()
            domain = [('name', operator, child)]
            if parents:
                names_ids = self.name_search(' / '.join(parents), args=args, operator='ilike', limit=limit)
                category_ids = [name_id[0] for name_id in names_ids]
                if operator in expression.NEGATIVE_TERM_OPERATORS:
                    categories = self.search([('id', 'not in', category_ids)])
                    domain = expression.OR([[('parent_id', 'in', categories.ids)], domain])
                else:
                    domain = expression.AND([[('parent_id', 'in', category_ids)], domain])
                for i in range(1, len(category_names)):
                    domain = [[('name', operator, ' / '.join(category_names[-1 - i:]))], domain]
                    if operator in expression.NEGATIVE_TERM_OPERATORS:
                        domain = expression.AND(domain)
                    else:
                        domain = expression.OR(domain)
            categories = self.search(expression.AND([domain, args]), limit=limit)
        else:
            categories = self.search(args, limit=limit)
        return categories.name_get()
