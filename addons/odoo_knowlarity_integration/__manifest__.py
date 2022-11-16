{
    'name': 'Odoo Knowlarity API Integration',
    'version': '15.0.0.1',
    'summary': 'Odoo Knowlarity API Integration',
    'author': 'NHCLIndia',
    'company': 'NHCLIndia',
    'maintainer': 'NHCLIndia',
    'sequence': 4,
    # 'images': ['static/description/Myoperator_logo.png'],
    'license': 'LGPL-3',
    'description': """Odoo Knowlarity API Integration""",
    'category': 'Connector',
    'depends': [
        'base', 'contacts', 'sale', 'crm', 'stock', 'sale_management', 'account', 'purchase','project'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/contact_view.xml',
        'views/res_config_settings_views.xml',
        'views/knowlarity_webhook_view.xml',
        'wizard/wizard.xml',
        "wizard/sh_message_wizard.xml"
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
