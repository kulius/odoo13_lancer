# -*- coding: utf-8 -*-
##############################################################################
#
#    Globalteckz Pvt Ltd
#    Copyright (C) 2013-Today(www.globalteckz.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Amazon Odoo Connector",
    "version" : "1.1",
    "summary":"Amazon odoo connector will help to handle amazon operations within odoo. ",
    'website': 'https://www.globalteckz.com',
	"license" : "Other proprietary",
    'images': ['static/description/banner.gif'],
    "price": "199.00",
    "currency": "EUR",
    "depends" : ["base",'product','sale','sale_stock','stock', 'sale_shop','delivery','purchase',],
    "author" : "Globalteckz",
    "category" : "E-Commerce",
    "description": """Amazon E-commerce management
amazon
Amazon
amazon connector
amazon integration
amazon fba
amazon FBA
amazon mfn
amazon MFN
amazon FBM
amazon fbm
amazon settlement
amazon settlement report
amazon 12
amazon12
amazon12 connector
amazon12 integration
amazon 13
amazon13
amazon13 connector
amazon13 integration
amazon stock adjustment
amazon orders
amazon inventory
amazon export
amazon reports
amazon reporting
amazon all in one
amazon allinone
amazon removal
amazon seller
amazon seller central
amazon helpdesk
amazon fba integration
amazon fba connector""",
    "data" : [
                'security/amazon_security.xml',
                 'security/ir.model.access.csv',
                'data/amazon_schedular_data.xml',
                'data/product_data.xml',
                # 'views/log_sequence_view.xml',
                
                'wizard/create_amazon_shop.xml',
                'wizard/amazon_product_lookup.xml',
                'wizard/upload_amazon_products.xml',
                'wizard/amazon_connector_wizard.xml',
                'wizard/cancel_amazon_order.xml',
                'wizard/update_price.xml',
                'wizard/add_listing_products_view.xml',
                'wizard/update_order_status_on_amazon.xml',
                'views/log_sequence_view.xml',
                'views/amazon_view.xml',
                'views/account_view.xml',
                'views/sale_view.xml',
#                 'views/product_template_view.xml',
                'views/product_view.xml',
                'views/amazon_inventory_view.xml',
                'views/partner_view.xml',
                'views/manage_amazon_listing_view.xml',
                'views/sale_shop.xml',
                'views/product_images_view.xml',
                'views/import_order_workflow.xml',
                'views/amazon_log_view.xml',
                'views/amazon_dashboard.xml',
#                  'views/sale_analysis_view.xml',
                
                'views/amazon_menu.xml',
                'wizard/amazon_report_wizard.xml',
                'views/amazon_transaction.xml',
                'views/report_request_history.xml',
                'views/settlement_report.xml',
                
                
                
    ],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

