# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    secret_token = fields.Char("Secret Token", help="MyOperator Secret Token",
                               default='664d64a398853dd51b7637f9ee3890960ce1bf5468f84c96c4bc6a136e832b67',
                               config_parameter='odoo_myoperator_integration.secret_token')
