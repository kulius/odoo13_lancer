# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Copyright (C) 2017-now  yuanchih-consult.com :chingyun@yuanchih-consult.com

{
    'name': '課程用模組安裝',
    'version': '1.0',
    'category': 'other',
    'author': ['www.yuanchih-consult.com'],

    'website': 'https://www.yuanchih-consult.com',
    'description': """

本模塊供課程過程中快速進行模組安裝用

本模組無其他相關功能

    """,
    'depends': ['crm', 
                'account', 
                'om_account_accountant',
                'stock',
                'purchase',
                'sale_management',
                'website',
                'website_sale',
                'board',
                'website_crm',
               ],
    'data': [],
}
