# -*- coding: utf-8 -*-

from odoo import models,fields

class BookedSeat(models.Model):
    _name = 'event.booked.seat'

    name = fields.Char("Booked Seat")
    seat_no = fields.Char("Booked Seat No", compute='get_seat_no')
    event_ticket_id = fields.Many2one(
        'event.event.ticket', string="Ticket Type")
    event_id = fields.Many2one('event.event', string="Event")

    @api.depends('name')
    def get_seat_no(self):
        for rec in self:
            rec.seat_no = ''
            if rec.name:
                rec.seat_no = 'R' + \
                    rec.name.split('_')[0]+' S'+rec.name.split('_')[1]

