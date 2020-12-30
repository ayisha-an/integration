# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug
import requests

from werkzeug.utils import redirect
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


class PayTabsController(http.Controller):
    _return_url = '/payment/paytabs/return/'
    _cancel_url = '/payment/paytabs/cancel/'

    @http.route([
        _return_url, _cancel_url
    ], type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def paytabs_return(self, **post):
        """ Paytabs."""
        print("test")
        _logger.info('Paytabs: entering form_feedback with post data %s', pprint.pformat(post))
        self._paytabs_validate_data(**post)
        if post:
            request.env['payment.transaction'].sudo().form_feedback(post, 'paytabs')
        return werkzeug.utils.redirect('/payment/process')

    def _paytabs_validate_data(self, **post):
        paytabs = request.env['payment.acquirer'].sudo().search([('provider', '=', 'paytabs')])
        response = requests.post(paytabs.paytabs_get_form_action_url(), paytabs.paytabs_tx_values)
        print('response', response)


