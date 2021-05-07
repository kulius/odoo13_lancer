# -*- coding: utf-8 -*-
{
    "name": "lancer Quote",
    "version": "1.0",
    "summary": "義成工廠股份有限公司 報價系統. ",
    "depends": ["base","mail"],
    "category": "Sale",
    "description": """義成工廠股份有限公司 報價系統""",
    "data": [
        'data/ir_sequence_data.xml',
        'data/lancer_base_system.xml',
        'data/lancer_base_param.xml',
        'security/ir.model.access.csv',
        'views/payment_term.xml',
        'views/lancer_incoterms.xml',
        'views/lancer_package_setting.xml',
        'views/lancer_package_expense.xml',
        'views/lancer_subcontract_category.xml',
        'views/lancer_subcontract_material.xml',
        'views/lancer_subcontract_treatment.xml',
        'views/lancer_main_category.xml',
        'views/lancer_main_item_category.xml',
        'views/lancer_routing_shape.xml',
        'views/lancer_routing_coating.xml',
        'views/lancer_routing_cutting.xml',
        'views/lancer_routing_outer.xml',
        'views/lancer_routing_handle.xml',
        'views/lancer_routing_series.xml',
        'views/lancer_routing_version.xml',
        'views/lancer_routing_wages.xml',
        'views/lancer_routing_material.xml',
        'views/lancer_product.xml',
        'views/lancer_product_category.xml',
        'views/lancer_product_series.xml',
        'views/lancer_main.xml',
        'views/lancer_main_item.xml',
        'views/lancer_quote.xml',
        'views/lancer_metal_type.xml',
        'views/lancer_metal_spec.xml',
        'views/lancer_metal_cutting_long.xml',
        'views/lancer_metal_exposed_long.xml',
        'views/lancer_handlematerial_process.xml',
        'views/lancer_handlematerial_material.xml',
        'views/lancer_cost_wire_file.xml',
        'views/lancer_cost_cal_file.xml',
        'views/lancer_cost_pro_file.xml',
        'views/lancer_cost_map_file.xml',
        'views/lancer_cost_plat_file.xml',
        'views/lancer_cost_handle_file.xml',
        'views/lancer_version_handle.xml',
        'views/lancer_version_metal.xml',
        'views/lancer_attr_records.xml',
        'views/menu.xml',
        "report/report_py3o.xml",
    ],
    "active": False,
    "installable": True,
}

