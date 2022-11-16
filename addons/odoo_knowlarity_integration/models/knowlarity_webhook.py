from odoo import api, fields, _, models

class KnowlarityWebhook(models.Model):
    _name = 'knowlarity.webhook'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Knowlarity WebHook'

    agent_phone_number = fields.Char('Agent Phone Number')
    cust_phone_number = fields.Char('Customer Phone Number')
    call_duration = fields.Char('Call Duration')
    log_event = fields.Char('Log Event')
    log_status = fields.Char('Log Status')
    call_uid = fields.Char('Call Uid')
    caller_id = fields.Char('Caller Id')
    call_record_url = fields.Char('Call Record URL')
    create_date = fields.Datetime("Create Date", default=lambda self: fields.Datetime.now())

    @api.model
    def create(self, vals_list):
        return super(KnowlarityWebhook, self).create(vals_list)

    def write(self, vals):
        return super(KnowlarityWebhook, self).write(vals)

    def name_get(self):
        ret_list = []
        for record in self:
            if record:
                name = 'KWF - %s' % (record.id)
                ret_list.append((record.id, name))
        return ret_list
