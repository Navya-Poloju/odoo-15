{
    'name': 'Odoo MyOperator API Integration',
    'version': '15.0.0.1',
    'summary': 'Odoo MyOperator API Integration',
    'author': 'NHCLIndia',
    'company': 'NHCLIndia',
    'maintainer': 'NHCLIndia',
    'sequence': 4,
    'images': ['static/description/Myoperator_logo.png'],
    'license': 'LGPL-3',
    'description': """Odoo MyOperator API Integration""",
    'category': 'Connector',
    'depends': [
        'base', 'contacts', 'sale', 'crm', 'stock', 'sale_management', 'account', 'purchase','project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/whatsapp_template.xml',
        # 'views/sale_wa.xml',
        'views/crm_wa.xml',
        'views/myoperator_webhook_view.xml',
        # 'views/stock_wa.xml',
        # 'views/invoice_wa.xml',
        'views/contact_wa.xml',
        'views/res_config_settings_views.xml',
        'wizard/wizard.xml',
        "wizard/sh_message_wizard.xml"
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
