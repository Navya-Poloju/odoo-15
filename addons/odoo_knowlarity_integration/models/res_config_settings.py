# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    kowlarity_authorization_token = fields.Char("Knowlarity Authorization Token", help="Knowlarity Authorization Token",
                               default='ab8b7892-7645-4810-9c12-b4c7ba5547d9',
                               config_parameter='odoo_knowlarity_integration.knowlarity_authorization_token')
