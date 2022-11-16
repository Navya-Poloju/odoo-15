from odoo import _, models


class WhatsappSale(models.Model):
    _inherit = 'sale.order'

    def sale_whatsapp(self):
        return {'type': 'ir.actions.act_window',
                'name': _('ClickOCall'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_template_id': self.env.ref('odoo_myoperator_integration.sales_whatsapp_template').id},
                }
