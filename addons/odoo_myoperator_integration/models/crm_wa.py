from odoo import fields, _, models


class WhatsappCrm(models.Model):
    _inherit = 'crm.lead'

    date_deadline = fields.Date('Due Date')
    call_date = fields.Datetime('Call Date')
    mail_message_id = fields.Many2one('mail.message', 'Linked Chatter Message', index=True)
    note = fields.Html('Note')

    def crm_whatsapp(self):
        partner_id = self.env['res.users'].search([('id', '=', self.env.uid)]).partner_id
        return {
            'type': 'ir.actions.act_window',
            'name': _('ClickOCall'),
            'res_model': 'whatsapp.message.wizard',
            'target': 'new',
            'view_mode': 'form',
            'view_type': 'form',
            'context': {
                'default_user_id': partner_id.id,
                'default_crm_lead_id': self.id,
                'default_mobile': self.phone
            },
        }
