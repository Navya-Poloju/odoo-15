from bs4 import BeautifulSoup
from odoo import _, api, fields, models
from odoo.tools.json import JSON
import queue


class Lead(models.Model):
    _inherit = "crm.lead"

    product_id = fields.Many2one('product.product', string="Product")
    project_id = fields.Many2one('project.project', string="Project")
    source = fields.Char('Source')
    sub_source = fields.Char('Sub Source')
    received_on = fields.Datetime('Received On')
    sub_source_ids = fields.One2many('sub.sources', 'crm_lead_id')

    def crm_lead_action(self):
        records = self.env['crm.lead'].search([('description', '!=', False)])
        crm_leads = self.env['crm.lead'].search(['|', ('user_id', '=', False), ('team_id', '=', False)])
        for rec in records:
            if rec.description:
                soup = BeautifulSoup(rec.description, 'html.parser')
                ph_lst = []
                mail_lst = []
                for content in soup.contents:
                    lst = content.text.split('\n')
                    for li in lst:
                        if 'Phone Number' in li:
                            ph_lst = li.split(':')
                            if len(ph_lst) > 1:
                                rec.phone = ph_lst[1]
                        if 'Email' in li:
                            mail_lst = li.split(':')
                            if len(mail_lst) > 1:
                                rec.email_from = mail_lst[1]
        leads = queue.Queue()
        for lead in crm_leads:
            leads.put(lead)
        sale_user_ids = self.env['crm.team.member'].search([]).user_id
        users_size = len(sale_user_ids)
        while leads.queue:
            for j in range(users_size):
                if j <= leads.qsize():
                    convert = self.env['crm.lead2opportunity.partner'].with_context({
                        'default_lead_id': leads.queue[0].id,
                        'active_model': 'crm.lead',
                        'active_id': leads.queue[0].id,
                        'active_ids': leads.queue[0].ids
                    }).create({'name': 'convert', 'action': 'create'})
                    convert.action_apply()
                    leads.queue[0].write({'user_id': sale_user_ids[j]})
                    leads.get()


class SubSource(models.Model):
    _name = 'sub.sources'

    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead", copy=False)
    name = fields.Char('Sub Source')
