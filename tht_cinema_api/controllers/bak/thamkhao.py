@http.route(['''/cinema/lichchieu/<int:marap_id>/'''], type='http', auth="user", website=True)
    def cinema_lichchieu_marap(self, marap_id=1, **kwargs):
        dm_session = request.env['dm.session'].search([('user_id','=',request.session.uid),('state','=','opened')])
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].browse(int(marap_id))
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', marap_id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],limit=500),
                })
        
        values = {
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj
            }

        return request.render("tht_cinema.dm_website_cinema_diembanve", values)

    # end lich chieu sudung all

    # lich chieu theo pos id
    @http.route(['''/cinema/pos_id/<int:pos_id>/'''], type='http', auth="user", website=True)
    def cinema_pos_id(self, pos_id='', **kwargs):
        dm_session = request.env['dm.session'].search([('id','=',pos_id),('user_id','=',request.session.uid),('state','=','opened')])
        # dm_session = request.env['dm.session'].browse(pos_id)
        if len(dm_session) < 1 :
            return "<div> Đăng nhập trước khi bán </div>"
        event = []
        date_list = []
        dm_diadiem_obj = request.env['dm.diadiem'].browse(dm_session.dm_diadiem_id.id)
        lichchieu_obj = request.env['dm.lichchieu']
        # today = datetime.datetime.now().strftime('%Y-%m-%d')
        today = datetime.date.today()
        for i in range(0,9): 
            date_list.append(today + relativedelta(days=i))

        
        if kwargs.get('ngaychieu', '') !='':
            ngaychieu = kwargs.get('ngaychieu')
        else: 
            ngaychieu = today
        list_phim_obj = lichchieu_obj.read_group([('dm_diadiem_id', '=', dm_diadiem_obj.id),('ngaychieu','=', ngaychieu),('sudung','=', True)], fields=['id', 'dm_phim_id'],groupby=['dm_phim_id']) 
        if list_phim_obj:
            for rec in list_phim_obj:
                event.append({
                    'dm_phim': request.env['dm.phim'].browse(rec['dm_phim_id'][0]),
                    'dm_lichchieu_obj' : lichchieu_obj.search([('ngaychieu','=', ngaychieu),('sudung','=', True),('dm_phim_id','=',rec['dm_phim_id'][1] )],order='batdau',limit=500),
                })
        
        values = {
            'ngaychieu' : ngaychieu,
            'dm_session': dm_session,
            'current_session_line_id': dm_session.current_session_line_id,
            'pos_id': pos_id,
            'pos_line_id': dm_session.current_session_line_id.id,
            'dm_diadiem_obj': dm_diadiem_obj, 
            'date_list': date_list, 
            'event': event,
            'list_phim_obj': list_phim_obj
            }

        return request.render("tht_cinema.dm_website_cinema_diembanve", values)

    # end cinema/pos_id/