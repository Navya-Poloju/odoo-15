# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "NHCL Custom CRM Module",
    'summary': """CRM Leads""",
    'description': """Custom Crm Leads""",
    'depends': ['base', 'crm', 'project', 'product', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_view.xml',
        'views/crm_schedule_action_view.xml',
        'report/crm_report_view.xml',
        'report/crm_template_view.xml'
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
