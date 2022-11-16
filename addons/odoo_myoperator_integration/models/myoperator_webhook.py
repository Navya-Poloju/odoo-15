from odoo import api, fields, _, models

class MyoperatorWebhook(models.Model):
    _name = 'myoperator.webhook'
    _description = 'MyOperator WebHook'

    agent_phone_number = fields.Char('Agent Phone Number')
    cust_phone_number = fields.Char('Customer Phone Number')
    call_duration = fields.Char('Call Duration')
    log_event = fields.Char('Log Event')
    log_status = fields.Char('Log Status')
    call_uid = fields.Char('Call Uid')
    unique_caller_id = fields.Char('Unique Call Id')
    call_record_url = fields.Char('Call Record URL')
    create_date = fields.Datetime("Create Date", default=lambda self: fields.Datetime.now())

    @api.model
    def create(self, vals_list):
       return super(MyoperatorWebhook, self).create(vals_list)

    def write(self, vals):
        return super(MyoperatorWebhook, self).write(vals)
