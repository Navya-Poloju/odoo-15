from odoo import _, models,fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    myoperator_user_id = fields.Char("MyOperator User Id")

    def contacts_whatsapp(self):
        partner_id = self.env['res.users'].search([('id', '=', self.env.uid)]).partner_id
        return {'type': 'ir.actions.act_window',
                'name': _('ClickOCall'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_user_id': partner_id.id,
                    'default_partner_id': self.id,
                    'default_mobile': self.phone or self.mobile
                },
                }
