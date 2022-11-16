from odoo import _, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def contacts_form_view(self):
        partner_id = self.env['res.users'].search([('id', '=', self.env.uid)]).partner_id
        return {'type': 'ir.actions.act_window',
                'name': _('ClickOCall'),
                'res_model': 'knowlarity.call.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_user_id': partner_id.id,
                    'default_partner_id': self.id,
                    'default_mobile': self.phone or self.mobile
                },
                }
