# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AvialbleSeatSelection(models.Model):
    _name = 'dm.available.seat.selection'
    _description = 'dm.available.seat.selection'

    name = fields.Char("Seat Column")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Seat Already exist !')
    ]



class DMSeatingArrangement(models.Model):
    _name = 'dm.seat.arrangement'
    _description = 'So do ghe trong phong'

    # event_ticket_id = fields.Many2one(
    #     'event.event.ticket', string="Ticket Type")
    dm_phong_line_id = fields.Many2one(
        'dm.phong.line', string="Loai ghe")
    row = fields.Integer("Row No")
    
    sequence = fields.Integer(string='Sequence', default=1)
    seat_selection_ids = fields.Many2many(
        'dm.available.seat.selection', string="Column Selection")
    
    
    def clear_row(self):
        self.write({'seat_selection_ids':[(6,0,[])]})
        # view = self.env.ref(
        #     'sh_event_seat_booking.sh_event_seat_arrangement_form')
        view = self.env.ref(
            'tht_cinema.dm_seat_arrangement_form')
            
        return {
            # 'name': _('Seat Arrangement'),
            'name': _('Sắp sếp sơ đồ ghế '),
            'type': 'ir.actions.act_window',
            "res_model": "event.event.ticket",
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            "res_id": self.dm_phong_line_id.id,
            'view_id': view.id,
            "target": "target",
        }


class DmPhongTicket(models.Model):
    # _inherit = 'event.event.ticket'
    _inherit = 'dm.phong.line'

    row_count = fields.Integer("Row")
    col_count = fields.Integer("Column")
    sequence = fields.Integer(string='Sequence', default=10)
    # seat_arrangement_ids = fields.One2many(
    #     'event.seat.arrangement', 'event_ticket_id', string="Event Seat Arrangement")
    seat_arrangement_ids = fields.One2many(
        'dm.seat.arrangement', 'dm_phong_line_id', string="Event Seat Arrangement")
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
            'tht_cinema.dm_phong_line_form')
        return {
            'name': _('Seat Arrangement'),
            'type': 'ir.actions.act_window',
            "res_model": "dm.phong.line",
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
        pervious_ticket = self.search([('dm_phong_id', '=', self.dm_phong_id.id), (
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
                seat_avail = self.env['dm.available.seat.selection'].sudo().search(
                    [('name', '=', j)], limit=1)
                if not seat_avail:
                    seat_avail = self.env['dm.available.seat.selection'].sudo().create({
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
            'tht_cinema.dm_phong_line_form')
        return {
            'name': _('Seat Arrangement'),
            'type': 'ir.actions.act_window',
            "res_model": "dm.phong.line",
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            "res_id": self.id,
            'view_id': view.id,
            "target": "target",
        }

    def room_seat_arrangement_action(self):
        view = self.env.ref(
            'tht_cinema.dm_phong_line_form')
        return {
            'name': _('Sắp sếp sơ đồ ghế '),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dm.phong.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'target',
            'res_id': self.id,

        }
