# -*- coding: utf-8 -*-
{
    "name": "lancer Quote",
    "version": "1.0",
    "summary": "義成工廠股份有限公司 報價系統. ",
    "depends": ["base"],
    "category": "Sale",
    "description": """義成工廠股份有限公司 報價系統""",
    "data": [
        'data/lancer_base_system.xml',
        'security/ir.model.access.csv',
        'views/payment_term.xml',
        'views/lancer_incoterms.xml',
        'views/lancer_package_setting.xml',
        'views/lancer_package_expense.xml',
        'views/lancer_subcontract_category.xml',
        'views/lancer_subcontract_material.xml',
        'views/lancer_subcontract_treatment.xml',
        'views/menu.xml',
    ],
    "active": False,
    "installable": True,
}

