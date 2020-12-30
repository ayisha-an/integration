# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from werkzeug import urls
from odoo.addons.payment_paytabs.controllers.controllers import PayTabsController


import requests
import json
import logging

_logger = logging.getLogger(__name__)


class PayTabsPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paytabs', 'PayTabs')], ondelete={'paytabs': 'set default'})
    paytabs_merchant_email = fields.Char('Merchant Email', required_if_provider='PayTabs',
                                        groups='base.group_user')
    paytabs_secret_key = fields.Char('Secret Key', required_if_provider='PayTabs',
                                        groups='base.group_user')

    @api.model
    def _get_paytabs_urls(self, environment):
        """ PayTabs URLS """
        return {
            'pay_page_url': 'https://www.paytabs.com/apiv2/create_pay_page'
        }

    def paytabs_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_paytabs_urls(environment)['pay_page_url']

    def paytabs_form_generate_values(self, values):
        self.ensure_one()
        print('val', values['reference'])
        base_url = self.get_base_url()
        print("PayTabsController._return_url", PayTabsController._return_url)

        paytabs_tx_values = dict(values)
        paytabs_tx_values.update({
            "merchant_email": self.paytabs_merchant_email,
            "secret_key": self.paytabs_secret_key,
            "site_url": base_url,
            "return_url": urls.url_join(base_url, PayTabsController._return_url),
            "title": "Test Order",
            "cc_first_name": values.get('partner_first_name'),
            "cc_last_name": values.get('partner_last_name'),
            "cc_phone_number": "91",
            "phone_number": values.get('partner_phone'),
            "email": values.get('partner_email'),
            "products_per_title": "MobilePhone || Charger || Camera",
            "unit_price": "12.123 || 21.345 || 35.678 ",
            "quantity": "2 || 3 || 1",
            "other_charges": "12.123",
            "amount": values.get('amount'),
            "discount": "10.123",
            "currency": "BHD",
            "reference_no": values.get('reference'),
            "ip_customer": "1.1.1.0",
            "ip_merchant": "1.1.1.0",
            "billing_address": "Flat 3021 Manama Bahrain",
            "city": "Manama",
            "state": "Manama",
            "postal_code": "12345",
            "country": "BHR",
            "shipping_first_name": "John",
            "shipping_last_name": "Doe",
            "address_shipping": "Flat 3021 Manama Bahrain",
            "state_shipping": "Manama",
            "city_shipping": "Manama",
            "postal_code_shipping": "1234",
            "country_shipping": "USA",
            "msg_lang": "English",
            "cms_with_version": "Odoo 14.0.0.1"
        })
        return paytabs_tx_values

    # Authenticate merchant's account using the secret key
    @api.onchange('paytabs_merchant_email', 'paytabs_secret_key')
    def _onchange_paytabs_values(self):
        secret_key_validation_url = 'https://www.paytabs.com/apiv2/validate_secret_key'
        params = {'merchant_email': self.paytabs_merchant_email, 'secret_key': self.paytabs_secret_key}
        response = requests.post(url=secret_key_validation_url, data=params)
        # print(response.text)
        if response.json()['response_code'] == '4001':
            raise UserError('Missing secret_key or merchant_email parameter')

        elif response.json()['response_code'] == '4002':
            raise UserError('Invalid Secret Key')


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
