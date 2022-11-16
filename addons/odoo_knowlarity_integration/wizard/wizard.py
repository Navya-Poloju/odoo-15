from datetime import timedelta

import requests
from odoo import api, fields, models, _
import requests, json
from odoo.exceptions import AccessDenied, ValidationError, UserError
import html2text
import logging

_logger = logging.getLogger(__name__)


class KnowlarityCallWizard(models.TransientModel):
    _name = 'knowlarity.call.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient")
    partner_id = fields.Many2one('res.partner', string="Partner")
    mobile = fields.Char(string="Mobile", required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True, )
    crm_lead_id = fields.Many2one('crm.lead', string="Crm Lead")

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        res_id = self._context.get('active_id') or 1
        values = self.onchange_template_id(self.template_id.id, self.model, res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, model, res_id):
        if template_id:
            values = self.generate_email_for_composer(template_id, [res_id])[res_id]
        else:
            default_values = self.with_context(default_model=model, default_res_id=res_id).default_get(
                ['model', 'res_id', 'partner_ids', 'message'])
            values = dict((key, default_values[key]) for key in
                          ['body', 'partner_ids']
                          if key in default_values)
        values = self._convert_to_write(values)
        return {'value': values}

    def generate_email_for_composer(self, template_id, res_ids, fields=None):
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]
        if fields is None:
            fields = ['body_html']
        returned_fields = fields + ['partner_ids']
        values = dict.fromkeys(res_ids, False)
        template_values = self.env['mail.template'].with_context(tpl_partners_only=True).browse(
            template_id).generate_email(res_ids, fields=fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if
                                 template_values[res_id].get(field))
            res_id_values['message'] = html2text.html2text(res_id_values.pop('body_html', ''))
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]

    def make_call(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        # import requests
        # import json
        #
        # url1 = "https://kpi.knowlarity.com/Basic/v1/account/notifications"
        #
        # payload1 = ""
        # headers1 = {
        #     'channel': "Basic",
        #     'x-api-key': "rS23mv81DEog5jFd2hBi1ioVLOvuWsr3v8SZB0i8",
        #     'authorization': get_param('odoo_knowlarity_integration.knowlarity_authorization_token'),
        #     'content-type': "application/json",
        #     'cache-control': "no-cache",
        # }
        #
        # response1 = requests.request("GET", url1, data=payload1, headers=headers1)
        # json_data = response1.json()

        if self.mobile:

            url = 'https://kpi.knowlarity.com/Basic/v1/account/call/makecall'
            sale_user = self.user_id.name
            if self.crm_lead_id:
                customer = self.crm_lead_id.partner_id.name
            else:
                customer = self.partner_id.name
            sale_user_phone_no = self.user_id.phone or self.user_id.mobile
            customer_phone_no = self.mobile
            headers = {
                'x-api-key': "rS23mv81DEog5jFd2hBi1ioVLOvuWsr3v8SZB0i8",
                'authorization': get_param('odoo_knowlarity_integration.knowlarity_authorization_token'),
                'content-type': "application/json",
            }
            myobj = {
                "k_number": "+917353935357",
                "agent_number": sale_user_phone_no,
                "customer_number": customer_phone_no,
            }
            response = requests.post(url, json=myobj, headers=headers)

            time = fields.Datetime.now()
            time = (time+ timedelta(hours=5, minutes=30)).strftime('%d %B %Y %I:%M %p')
            body = _(
                "%(sale_user)s call to %(customer)s<br/>"
                "%(sale_user_phone_no)s -> %(customer_phone_no)s<br/>"
                "At Time -> %(time)s<br/>"
                , sale_user=sale_user, customer=customer, sale_user_phone_no=sale_user_phone_no,
                customer_phone_no=customer_phone_no, time=time)
            if self.crm_lead_id:
                self.crm_lead_id.message_post(body=body)
                if not self.crm_lead_id.partner_id:
                    raise UserError(_("Please select CRM Partner"))
                self.crm_lead_id.partner_id.message_post(body=body)
            else:
                self.partner_id.message_post(body=body)
            view_id = self.env.ref('odoo_knowlarity_integration.sh_message_wizard').id
            context = dict(self._context or {})
            if response.status_code != 200:
                context['message'] = "something went wrong, please contact your admin"
            else:
                context['message'] = "Please Wait we are try to connect call"
                phonecall_activity_type = self.env.ref('mail.mail_activity_data_call', raise_if_not_found=False)
                if not phonecall_activity_type:
                    phonecall_activity_type = self.env['mail.activity.type'].search([('category', '=', 'phonecall')],
                                                                                    limit=1)
                    if not phonecall_activity_type:
                        phonecall_activity_type = self.env.ref('mail.mail_activity_todo', raise_if_not_found=False) or \
                                                  self.env['mail.activity.type'].search([('category', '=', False)],
                                                                                        limit=1)
                        if phonecall_activity_type:
                            _logger.warning(
                                "No phonecall activity type found. MyOperator activities aren't guaranteed to work as expected. Fallback on %s",
                                phonecall_activity_type.name)
                        else:
                            _logger.warning(
                                "No phonecall or fallback activity type found. MyOperator activities aren't guaranteed to work as expected.")
                # VFE FIXME what if mail_activity_data_call was deleted by user?
                values_list = [{
                    'res_id': record.crm_lead_id.id,
                    'res_model_id': self.env['ir.model']._get(record.crm_lead_id._name).id,
                    'activity_type_id': phonecall_activity_type and phonecall_activity_type.id,
                    'user_id': self.env.user.id,
                    'date_deadline': fields.Date.today(self),
                } for record in self]
                activities = self.env['mail.activity'].sudo().create(values_list)
            _logger.info(response.text)
            return {
                'type': 'ir.actions.act_window',
                'name': ('Response'),
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'target': 'new',
                'views': [[view_id, 'form']],
                'context': context
            }
