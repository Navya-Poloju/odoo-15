from bs4 import BeautifulSoup
from odoo import _, api, fields, models
from odoo.exceptions import UserError, RedirectWarning
from odoo.tools.json import JSON
import queue
import ast

class Lead(models.Model):
    _inherit = "crm.lead"

    product_id = fields.Many2one('product.product', string="Product")
    project_id = fields.Many2one('project.project', string="Project")
    source = fields.Char('Source')
    sub_source = fields.Char('Sub Source')
    date = fields.Datetime('Date')
    prev_user_id = fields.Many2one('res.users')
    received_on = fields.Datetime('Received On')
    # no_contact_reason = fields.Selection([('ringing_no_response', 'Ringing No Response'),
    #                                       ('phone_switched_off', 'Phone Switched off'),
    #                                       ('invalid_number', 'Invalid Number'),
    #                                       ('out_of_network_area', 'Out of Network Area'),
    #                                       ('customer_disconnecting', 'Customer Disconnecting')], string="No Contact")
    # unqualified_reason = fields.Selection([('Budget does not match', 'Budget does not match'),
    #                                        ('location_mismatch', 'Location mismatch'),
    #                                        ('looking_for_different_sizes', 'Looking for different sizes'),
    #                                        ('false_enquiry', 'False Enquiry'),
    #                                        ('possession_dates_dont_match', 'Possession dates don’t match'),
    #                                        ('wrong_contact_number', 'Wrong contact number'),
    #                                        ('already_a_customer', 'Already a customer'),
    #                                        ('lost_to_competition', 'Lost to Competition'),
    #                                        ('is_a_channel_partner', 'Is a Channel Partner'),
    #                                        ('duplicate_customer', 'Duplicate Customer'),
    #                                        ('needs_an_unavailable_plot_location', 'Needs an unavailable Plot Location'),
    #                                        ('postponed_purchase', 'Postponed Purchase')
    #                                        ], string="UnQualified Reason")
    # lost_reason = fields.Selection([('lost_to_competition','Lost to competition'),
    #                                 ('not_answering_or_responding', 'Not answering / responding'),
    #                                 ('loan_issues','Loan Issues'),
    #                                 ('budget_issues', 'Budget Issues'),
    #                                 ('customer_already_booked', 'Customer already booked'),
    #                                 ('customer_postponed_purchase', 'Customer Postponed Purchase'),
    #                                 ('needs_an_unavailable_plot_location', 'Needs an unavailable plot location')
    #                                 ],string="Lost Reason")
    ######################### CRM Data Import Fields #################################
    salutation = fields.Char(string='Salutation')
    lead_status = fields.Char(string='Lead Status')
    phone_country = fields.Char(string='Phone Country')
    secondary_phone = fields.Char(string='Secondary Phone')
    secondary_email = fields.Char('Secondary Email')
    location = fields.Char(string='Location')
    region = fields.Char(string='Region')
    nri_type = fields.Selection([('yes', 'YES'), ('no', 'NO')], string="NRI")
    last_sales_contacted_on = fields.Datetime(string='Last Sales Contacted On')
    last_sales_contact_attempted_on = fields.Datetime(string='Last Sales Contact Attempted On')
    site_visit_status = fields.Char(string='Site Visit Status')
    last_note_by_sales = fields.Char(string='Last Note By Sales')
    last_note_by_presales = fields.Text(string='Last Note By Presales')
    system_tags = fields.Text(string='System Tags')
    lead_hotness = fields.Integer('Lead Hotness')
    last_name = fields.Char('Last Name')
    first_name = fields.Char('First Name')

    def crm_lead_action(self):
        records = self.env['crm.lead'].search([('description', '!=', False)])
        crm_leads = self.env['crm.lead'].search(['|', '|',('user_id', '=', False), ('team_id', '=', False),('type', '=', 'lead')])
        for rec in records:
            if rec.description:
                soup = BeautifulSoup(rec.description, 'html.parser')
                ph_lst = []
                mail_lst = []
                name_lst = []
                for content in soup.contents:
                    lst = content.text.split('\n')
                    for li in lst:
                        if 'Phone' in li:
                            ph_lst = li.split(':')
                            if len(ph_lst) > 1 and rec.phone != ph_lst[1]:
                                rec.phone = ph_lst[1]
                        if 'Email' in li:
                            mail_lst = li.split(':')
                            if len(mail_lst) > 1 and rec.email_from != mail_lst[1]:
                                rec.email_from = mail_lst[1]
                        if 'Full name' in li:
                            name_lst = li.split(':')
                            if len(name_lst) > 1 and rec.name != name_lst[1]:
                                rec.name = name_lst[1]
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

    # @api.onchange('stage_id')
    # def _onchange_stage_id(self):
    #     stage_id = self.stage_id
    #     if stage_id.name == 'No Contact' or stage_id.name == 'Unqualified' or stage_id.name == 'Lost':
    #         selection_type = False
    #         if stage_id.name == 'No Contact' and self.no_contact_reason == False:
    #             selection_type = 'no_contact'
    #         elif stage_id.name == 'Unqualified' and self.unqualified_reason == False:
    #             selection_type = 'unqualified'
    #         elif stage_id.name == 'Lost' and self.lost_reason == False:
    #             selection_type = 'lost'
    #         if selection_type:
    #             action = self.env.ref('nhcl_crm_custom_module.crm_reason_action').read()[0]
    #             if self.ids:
    #                 action['context'] = dict(ast.literal_eval(action.get('context')), default_crm_lead_id=self.ids[0],
    #                                          default_selection_type=selection_type)
    #             msg = _('Please Select Reason for stage change.')
    #             raise RedirectWarning(msg, action, _('Select'))
