# -*- coding: utf-8 -*-
from odoo import models, fields


class DmSodoghe(models.Model):
    _name = "dm.sodoghe"
    _description = 'Sơ đồ ghế  '

    row_count = fields.Integer("Row")
    col_count = fields.Integer("Column")
    sequence = fields.Integer(string='Sequence', default=10)
    seat_arrangement_ids = fields.One2many(
        'event.seat.arrangement', 'event_ticket_id', string="Event Seat Arrangement")
    add_blank_row = fields.Boolean("Want to add blank row after each row ?")
    add_blank_col = fields.Boolean("Want to add blank Seat after each Seat ?")
    seats_max = fields.Integer("SM")

    @api.onchange('row_count', 'col_count', 'seat_arrangement_ids')
    def _onchange_max_available_seat(self):
        self.seats_max = self.row_count * self.col_count
        if self.seat_arrangement_ids:
            col = 0
            for arrangement_row in self.seat_arrangement_ids:
                col += len(arrangement_row.seat_selection_ids.ids)
            if col > 0:
                self.seats_max = col

    def clear_arrangement(self):
        self.ensure_one()
        self.seat_arrangement_ids.unlink()
        view = self.env.ref(
            'sh_event_seat_booking.sh_event_seat_arrangement_form')
        return {
            'name': _('Seat Arrangement'),
            'type': 'ir.actions.act_window',
            "res_model": "event.event.ticket",
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            "res_id": self.id,
            'view_id': view.id,
            "target": "new",
        }

    def prepare_arrangement(self):
        if self.row_count <= 0 or self.col_count <= 0:
            raise UserError(
                "Please Enter Total Row and Max seat in Single Row.")

        i = 1

        # get last row
        pervious_ticket = self.search([('event_id', '=', self.event_id.id), (
            'sequence', '<', self.sequence)], order='sequence desc', limit=1)
        if pervious_ticket:
            last_row = pervious_ticket.seat_arrangement_ids.sorted(
                lambda n: n.row, reverse=True)[:1]
            i = last_row.row + 1
        j = 1

        data_list = []
        odd_counter = 0
            
        for row in range(self.row_count):
            row_dic = {}
            col_list = []
            j = 1
            odd_counter += 1
            seat_col_counter = 0
            for col in range(self.col_count):
                seat_col_counter += 1 
                seat_avail = self.env['available.seat.selection'].sudo().search(
                    [('name', '=', j)], limit=1)
                if not seat_avail:
                    seat_avail = self.env['available.seat.selection'].sudo().create({
                        'name': j})
                if self.add_blank_col:
                    if seat_col_counter % 2 != 0:
                        col_list.append(seat_avail.id)
                else:
                    col_list.append(seat_avail.id)
                j += 1
            row_dic['row'] = i
            if self.add_blank_row and self.add_blank_col:
                if odd_counter % 2 != 0:
                    row_dic['seat_selection_ids'] = [(6, 0, col_list)]
            elif self.add_blank_row and not self.add_blank_col:
                if odd_counter % 2 != 0:
                    row_dic['seat_selection_ids'] = [(6, 0, col_list)]
            else:
                row_dic['seat_selection_ids'] = [(6, 0, col_list)]
            i += 1
            data_list.append((0, 0, row_dic))
            
       
        self.seat_arrangement_ids = data_list
        
        if self.seat_arrangement_ids:
            col = 0
            for arrangement_row in self.seat_arrangement_ids:
                col += len(arrangement_row.seat_selection_ids.ids)
            if col > 0:
                self.seats_max = col
                
                
        view = self.env.ref(
            'sh_event_seat_booking.sh_event_seat_arrangement_form')
        return {
            'name': _('Seat Arrangement'),
            'type': 'ir.actions.act_window',
            "res_model": "event.event.ticket",
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            "res_id": self.id,
            'view_id': view.id,
            "target": "new",
        }

    def sh_seat_arrangement_action(self):
        view = self.env.ref(
            'sh_event_seat_booking.sh_event_seat_arrangement_form')
        return {
            'name': _('Seat Arrangement'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'event.event.ticket',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,

        }
