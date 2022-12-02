import requests
from odoo import api, fields, models,_
import requests, json
import html2text
from odoo.exceptions import UserError
from odoo.tools import html_escape
import logging
_logger = logging.getLogger(__name__)

class WhatsappSendMessage(models.TransientModel):
    _name = 'whatsapp.message.wizard'

    user_id = fields.Many2one('res.partner', string="Recipient")
    partner_id = fields.Many2one('res.partner', string="Partner")
    mobile = fields.Char(string="Mobile" ,required=True)
    message = fields.Text(string="Message")
    model = fields.Char('mail.template.model_id')
    template_id = fields.Many2one('mail.template', 'Use template', index=True, )
    crm_lead_id = fields.Many2one('crm.lead',string="Crm Lead")

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

    def send_message(self):
        if self.mobile:
            headers = {"Content-type": "application/json",
                       'x-api-key': "oomfKA3I2K6TCJYistHyb7sDf0l0F6c8AZro5DJh",
                       }
            url = 'https://obd-api.myoperator.co/obd-api-v1'
            get_param = self.env['ir.config_parameter'].sudo().get_param
            myobj = {
                "company_id": "63036af247aa9906",
                "secret_token": get_param('odoo_myoperator_integration.secret_token'),
                "type": "1",
		        "user_id": self.user_id.myoperator_user_id,
                "number": self.user_id.phone or self.user_id.mobile,  # call agent first
                "public_ivr_id": "6307261c5d66f481",
                "reference_id": "1245",
                "region": "test",
                "caller_id": "test",
                "group": "test"
            }
            response = requests.post(url, json=myobj, headers=headers)
            sale_user = self.user_id.name
            if self.crm_lead_id:
                customer = self.crm_lead_id.partner_id.name
            else:
                customer = self.partner_id.name
            sale_user_phone_no = self.user_id.phone or self.user_id.mobile
            customer_phone_no = self.mobile
            time = fields.Datetime.now()
            body = _(
                "%(sale_user)s call to %(customer)s<br/>"
                "%(sale_user_phone_no)s -> %(customer_phone_no)s<br/>"
                "At Time -> %(time)s<br/>"
                , sale_user=sale_user, customer=customer, sale_user_phone_no=sale_user_phone_no,
                customer_phone_no=customer_phone_no, time=time)
            if self.crm_lead_id:
                self.crm_lead_id.message_post(body=body)
                if not self.crm_lead_id.partner_id:
                    raise UserError(_("Please Select CRM Partner"))
                self.crm_lead_id.partner_id.message_post(body=body)
            else:
                self.partner_id.message_post(body=body)
            view_id = self.env.ref('odoo_myoperator_integration.sh_message_wizard').id
            context = dict(self._context or {})
            if response.status_code != 200:
                context['message'] = "VoIP call provider returned an error. Please contact your system Adminstrator"
                _logger.info("VoIP error code and response = ",response.status_code,response.content)
            else:
                context['message'] = "Please Wait while we try to connect your VoIP call"
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
                                "Phonecall activity type found. MyOperator activities aren't guaranteed to work as expected. Fallback on %s",
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
            _logger.info("%s" %  context['message'])
            return {
                'type': 'ir.actions.act_window',
                'name': ('VoIP provider'),
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'target': 'new',
                'views': [[view_id, 'form']],
                'context' : context
            }


