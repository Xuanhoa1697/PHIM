# -*- coding: utf-8 -*-
{
    'name': "THT Cinema Management",

    'summary': """
        THT Cinema Management""",

    'description': """
        THT Cinema Management 20201215 - 20210114
    """,

    'author': "Tien, Hieu",
    'website': "",


    'category': 'Uncategorized',
    'version': 'v11',


    'depends': ['base', 'account',
                'product', 'website', 'report_xlsx', 'web_timeline', 'point_of_sale',
                ],

    'data': [
        # 'data/momo_draft.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views_menu.xml',
        'views/views_dm_diadiem.xml',
        'views/views_dm_ptthanhtoan.xml',
        'views/views_dm_phong.xml',
        'views/views_dm_loaighe.xml',
        # 'views/views_dm_ghe.xml',
        'views/views_dm_seat_arrangement.xml',
        'views/assets.xml',
        'views/dm_website_sodoghe.xml',
        'views/views_dm_product.xml',
        'views/views_dm_banggia.xml',
        'views/views_dm_loaive.xml', 
        'views/v_dm_session.xml',
        'views/views_dm_session_line.xml',

        'views/views_dm_phim.xml', 
        
        'views/views_dm_lichchieu.xml', 
        'views/views_dm_donbanve.xml', 
        'views/views_dm_donbanve_line.xml', 

        'views/dm_website_cinema_assets.xml',
        'views/dm_website_cinema_backend_assets.xml',

        'views/dm_website_cinema_menu.xml',
        'views/dm_website_cinema_menu_pos_banve.xml',

        'views/dm_website_phim.xml',
        'views/dm_website_lichchieu_detail.xml',
        'views/dm_website_lichchieu_receipt.xml',
        'views/dm_website_donbanve_view.xml',
        # 'views/dm_website_cinema_pos_template.xml',
        'views/pos_template.xml',
        'views/dm_website_cinema_vexemphim.xml',
        'views/dm_website_cinema_booking_result.xml',
        'views/dm_website_lichchieu_sudung.xml',
        'views/dm_website_cinema_datvetruoc.xml',
        'views/dm_website_cinema_datvetruoc_today.xml',
        'views/dm_website_cinema_diembanve.xml',
        'views/dm_website_cinema_pos_datvetruoc.xml',

        'views/dm_website_cinema_booking_datvetruoc.xml',
        'views/dm_website_cinema_vexemphim_datvetruoc.xml',
        'views/dm_website_cinema_datvetruoc_inve.xml',

        'views/dm_website_cinema_dangchieu.xml',
        'views/dm_website_huyve.xml',
        

        'views/donbanve_searchbar.xml',
        'views/donbanve_order.xml',
        
        'views/inlaive_menu.xml',

        'views/inlaive_searchbar.xml',
        'views/inlaive_order.xml',
        'views/inlaive_vexemphim.xml',
        'views/inlaive_line_vexemphim.xml',
        
        'views/trave_searchbar.xml',
        'views/trave_order.xml',

        'views/session_line_report.xml',

        'views/customer_display_pos_id.xml',

        # 'report/dm_report_view.xml',
        # 'report/dm_report_donbanve_pdf_view.xml',
        # 'report/dm_report_pdf_80.xml',
        #
        # 'report/dm_report_donbanve_general_matrix_print_view.xml',
        # 'report/dm_report_donbanve_general_pdf_view.xml',
        #
        # 'report/dm_report_donbanve_view.xml',
        # 'report/dm_report_kqcp_view.xml',
        # 'report/dm_report_bcnb_view.xml',
        #
        # 'report/dm_report_thanhtoan_view.xml',

        
  
    ],
    'qweb': ['static/src/xml/*.xml'],

    'demo': [
        # 'demo/demo.xml',
    ],
}
