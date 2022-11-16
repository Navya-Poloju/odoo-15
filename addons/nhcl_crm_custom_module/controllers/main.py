# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID, tools, _
import logging
import json
_logger = logging.getLogger(__name__)


class HttpIntegrateController(http.Controller):
    @http.route('/get_crm_data', type='json', auth='public', methods=['GET'], csrf=False)
    def get_data(self, **kwargs):
        params = []
        crm_id = request.env['crm.lead']
        jsonD = request.jsonrequest
        for kw in jsonD:
            params.append(jsonD[kw])
            if kw == 'crm_id':
                crm_id = request.env['crm.lead'].sudo().search([('id','=',jsonD[kw])])
            if crm_id and kw == 'subsource_ids':
                for i,rec in zip(range(len(jsonD['subsource_ids'])), jsonD['subsource_ids']):
                    vals = {
                        'crm_lead_id':crm_id.id,
                        'name':jsonD['subsource_ids'][i]['name']
                    }
                    request.env['sub.sources'].create(vals)
