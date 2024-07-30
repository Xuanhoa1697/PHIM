# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.osv.expression import OR
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        domain, donbanve_count = [], 0
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        # dbv_obj = self.get_employeess()
        # if dbv_obj:
        #     domain += [('id', 'in', dbv_obj.ids)]
        #     donbanve_count = request.env['dm.donbanve'].sudo().search_count(domain)
        donbanve_count = request.env['dm.donbanve'].sudo().search_count(domain)
        values['donbanve_count'] = donbanve_count
        values['page_name'] = 'donbanve'
        return values

    @http.route(['/cnm/my/dbv', '/cnm/my/dbv/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_maintances(self, page=1, access_token=None, search=None, search_in='all', sortby=None, groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        donbanve_obj = request.env['dm.donbanve'].sudo()
        domain = [('user_id', '=', request.env.uid )]
        donbanve_count, donbanve_ids = 0, None
        

        searchbar_sortings = {
            'name': {'label': _('Name'), 'order': 'name asc'},
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'date_hoadon': {'label': _('Status'), 'order': 'date_hoadon desc'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'equipment_id': {'input': 'equipment_id', 'label': _('Search by Equipment')},
            'owner_user_id': {'input': 'owner_user_id', 'label': _('Search by Owner')},
            'schedule_date': {'input': 'schedule_date', 'label': _('Search by Date')},
            'name': {'input': 'name', 'label': _('Search By name')},
        }

        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'date_hoadon': {'input': 'date_hoadon', 'label': _('Status')},
        }

        if not sortby:
            sortby = 'id'
        order = searchbar_sortings[sortby]['order']

        # count for pager
        if donbanve_obj:
            donbanve_count = donbanve_obj.search_count(domain)

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('date_hoadon', 'all'):
                search_domain = OR([search_domain, [('date_hoadon', 'ilike', search)]])
            if search_in in ('user_id', 'all'):
                search_domain = OR([search_domain, [('user_id', 'ilike', search)]])
            # if search_in in ('schedule_date', 'all'):
            #     search_domain = OR([search_domain, [('schedule_date', 'like', search)]])
            
            domain += search_domain

        pager = portal_pager(
            url="/cnm/my/dbv",
            total=donbanve_count,
            page=page,
            url_args={'search_in': search_in, 'search': search},
            step=12
        )

        grouped_maintenance = []
        # content according to pager and archive selected
            
        donbanve_ids = donbanve_obj.search(domain,  order=order, limit=12, offset=pager['offset'])
        request.session['my_expense_history'] = donbanve_ids.ids[:100]
        grouped_maintenance = [donbanve_ids]
        if groupby == 'stage_id':
            grouped_maintenance = [donbanve_obj.concat(*g) for k, g in groupbyelem(donbanve_ids, itemgetter('stage_id'))]

        values = {}
        values.update({
            'donbanve_ids': donbanve_ids,
            'page_name': 'donbanve',
            'donbanve_count': donbanve_count,
            'pager': pager,
            'default_url': '/cnm/my/dbv',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'search_in': search_in,
            'groupby': groupby,
            'grouped_maintenance': grouped_maintenance,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby
        })
        return request.render("tht_cinema_website.portal_dbv", values)