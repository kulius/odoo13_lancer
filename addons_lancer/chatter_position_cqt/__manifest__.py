# -*- coding: utf-8 -*-
{
    'name': "Web-Chatter Position, Switch Chatter Position",
    'version': '13.0.1.0.0',
    'sequence': 1,
    'website': "https://cronquotech.odoo.com",
    'summary': 'Switch Chatter Position. Add a button to switch chatter position',
    'description': "Using this module user able to set chatter position",
    'author': 'CRON QUOTECH',
    'category': 'Base',
    'depends': ['base', 'mail'],
    'data': [
        'views/templates.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'qweb': [
        "static/src/xml/chatter_position.xml",
    ],
    "support": "cronquotech@gmail.com",
    "license": "AGPL-3",
    'installable': True,
    'application': True,
    'auto_install': False
}
