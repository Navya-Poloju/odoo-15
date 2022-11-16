# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID, tools, _
import logging

_logger = logging.getLogger(__name__)

class HttpIntegrateController(http.Controller):
    @http.route('/voip/webhook-api', type='http', auth='public', methods=['POST'], csrf=False)
    def post_api(self, **kwargs):
        _logger.info("post-api reading kwargs ... START")
        return '{Post-api: triggered, not supported}'

    @http.route('/voip/get-token', type='http', auth='none', methods=['GET'], csrf=False)
    def get_api(self, **kwargs):
        _logger.info("get-token reading kwargs ... START")
        return '{get_api: triggered,Not supported}'

    @http.route('/voip/get_call_data', type='http', auth='public', methods=['GET'], csrf=False)
    def read_call_data(self, **kwargs):
        ctx = 'voip_webhook'
        agent_phone_no = ''
        cust_ph_num = ''
        call_time = ''
        log_event = ''
        log_status = ''
        call_uid = ''
        caller_id = ''
        call_rec_url = ''
        _logger.info("get_call_data reading kwargs ... START")
        params = []
        for kw in kwargs:
            params.append(kwargs[kw])
        _logger.info("get-token reading kwargs into variables... END")
        for i in range(len(params)):
            if i == 0:
                agent_phone_no = params[i]
            if i == 1:
                cust_ph_num = params[i]
            if i == 2:
                call_time = params[i]
            if i == 3:
                log_event = params[i]
            if i == 4:
                log_status = params[i]
            if i == 5:
                call_uid = params[i]
            if i == 6:
                caller_id = params[i]
            if i == 7:
                call_rec_url = params[i]
        vals = {
            'agent_phone_number': agent_phone_no,
            'cust_phone_number': cust_ph_num,
            'call_duration': call_time,
            'log_event': log_event,
            'log_status': log_status,
            'call_uid': call_uid,
            'unique_caller_id': caller_id,
            'call_record_url': call_rec_url
        }
        request.env['myoperator.webhook'].sudo().create(vals)
        _logger.info(
            "Logging PARAMS:agent_phone_no,cust_ph_num,call_time,log_event,log_status,call_uid,caller_id,call_rec_url")
        _logger.info(agent_phone_no)
        _logger.info(cust_ph_num)
        _logger.info(call_time)
        _logger.info(log_event)
        _logger.info(log_status)
        _logger.info(call_uid)
        _logger.info(caller_id)
        _logger.info(call_rec_url)
        body = _(
            "User Ph No -> %(agent_phone_no)s<br/>"
            "Customer Ph No-> %(cust_ph_num)s<br/>"
            "Duration -> %(call_time)s<br/>"
            "Event Type -> %(log_event)s<br/>"
            "Call Status -> %(log_status)s<br/>"
            "Call UID -> %(call_uid)s<br/>"
            "Caller ID -> %(caller_id)s<br/>"
            "Call record URL -> %(call_rec_url)s<br/>",
            agent_phone_no=agent_phone_no, cust_ph_num=cust_ph_num,
            call_time=call_time, log_event=log_event, log_status=log_status, call_uid=call_uid, caller_id=caller_id,
            call_rec_url=call_rec_url
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
