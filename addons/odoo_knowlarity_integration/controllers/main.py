# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID, tools, _
import logging

_logger = logging.getLogger(__name__)


class HttpIntegrateController(http.Controller):
    @http.route('/voip/get_call_data', type='http', auth='public', methods=['GET'], csrf=False)
    def read_call_data(self, **kwargs):
        ctx = 'voip_webhook'
        agent_number = ''
        customer_number = ''
        call_duration = ''
        Call_Type = ''
        business_call_type = ''
        uuid = ''
        caller_id = ''
        resource_url = ''
        _logger.info("get_call_data reading kwargs ... START")
        params = []
        for kw in kwargs:
            params.append(kwargs[kw])
        _logger.info("get-token reading kwargs into variables... END")
        for i in range(len(params)):
            if i == 0:
                agent_number = params[i]
            if i == 1:
                customer_number = params[i]
            if i == 2:
                call_duration = params[i]
            if i == 3:
                Call_Type = params[i]
            if i == 4:
                business_call_type = params[i]
            if i == 5:
                uuid = params[i]
            if i == 6:
                caller_id = params[i]
            if i == 7:
                resource_url = params[i]
        vals = {
            'agent_phone_number': agent_number,
            'cust_phone_number': customer_number,
            'call_duration': call_duration,
            'log_event': Call_Type,
            'log_status': business_call_type,
            'call_uid': uuid,
            'caller_id': caller_id,
            'call_record_url': resource_url
        }
        request.env['knowlarity.webhook'].sudo().create(vals)
        _logger.info(
            "Logging PARAMS:agent_number,customer_number,call_duration,Call_Type,business_call_type,uuid,unique_id,resource_url")
        _logger.info(agent_number)
        _logger.info(customer_number)
        _logger.info(call_duration)
        _logger.info(Call_Type)
        _logger.info(business_call_type)
        _logger.info(uuid)
        _logger.info(caller_id)
        _logger.info(resource_url)
        body = _(
            "User Ph No -> %(agent_phone_no)s<br/>"
            "Customer Ph No-> %(cust_ph_num)s<br/>"
            "Duration -> %(call_time)s<br/>"
            "Event Type -> %(log_event)s<br/>"
            "Call Status -> %(log_status)s<br/>"
            "Call UID -> %(call_uid)s<br/>"
            "Caller ID -> %(caller_id)s<br/>"
            "Call record URL -> %(call_rec_url)s<br/>",
            agent_phone_no=agent_number, cust_ph_num=customer_number,
            call_time=call_duration, log_event=Call_Type, log_status=business_call_type, call_uid=uuid, caller_id=caller_id,
            call_rec_url=resource_url
        )
        odoobot_id = request.env['ir.model.data']._xmlid_to_res_id('base.partner_root')
        author = request.env['res.users'].sudo().browse(odoobot_id).partner_id
        author_id = author.id
        mail_channel = request.env['mail.channel'].sudo().search([('name', '=', ctx),
                                                                  ('channel_partner_ids', 'in',
                                                                   [request.env.user.partner_id.id])], limit=1, )

        if not mail_channel:
            mail_channel = request.env['mail.channel'].with_context(mail_create_nosubscribe=True).sudo().create({
                'channel_partner_ids': [(4, request.env.user.partner_id.id), (4, author_id)],
                'public': 'private',
                'channel_type': 'chat',
                'name': ctx,
                'display_name': ctx,
            })
        message = mail_channel.message_post(
            author_id=author_id,
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_comment'
        )
        return '{Webhook: get_call_data method triggered,Voip call params set successfully}'
