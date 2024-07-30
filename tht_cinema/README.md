# module này dùng cho app + web new 2022/12/16

# Tạo sản phẩm Vé xem phim
# Tạo khách hàng Khách vãng lai
# Cài đặt múi giờ cho user Asia/Ho_Chi_Minh +7 để hiện thị đúng thời gian
# You have to define a sequence for account.payment.customer.invoice in your company.
# Bạn phải quy định một account.payment.customer.invoice ở công ty của bạn.

# 2021/02/23 Realtime seat map

# 2021/03/16 Pos Session Line view , menu

# 2021/03/24 add date_hoadon

# 2021/03/24 delete module website_crm_score *** odoo.addons.website_crm_score.models.sales_team: Flanker is not compatible with Python 3, email validation has been disabled

# 2021/03/30 delete bccp excel title sum total -- server pc ip 48

# 2021/04/14 thêm chi tiết đơn bán vé + menu

# 2021/04/14 - 21:09 ẩn menu in vé đặt trước và menu trả vé

# 2021/04/18 - 23:00 lịch chiếu đặt vé trước order by batdau

# 2021/04/23 - 22:40 thu gọn suất chiếu đặt vé trước img 220 -> 240 , padding 8 -> 5px

# 2021/04/25 - thêm button in lại báo cáo kết ca trong form phiên bán vé

# 2021/04/26 - sửa lỗi in lại kết ca cho khớp với báo , lý do sai biến domain

# 2021/05/15 - fix accountant multi company for product

# 2021/06/10 - real map chuyển sang socket.io

# 2022/02/12 - thêm cột đơn giá 60, cột thành tiền hiện 16 + 1 = 17
<!-- sheet.write(y_offset, 17, thanhtien, body_center_style) -->

# 2022/02/13 - thêm những suất chiếu ko có vé vào báo cáo chiếu phim

# 2022/06/27 - bỏ payment_method , thêm dm_ptthanhtoan_id

# 2022/06/29 
    not use pip3 install jwt
    pip3 install pyjwt 
    pip3 uninstall cryptography
    pip3 install cryptography==36.0.2

    ModuleNotFoundError: No module named 'setuptools_rust'

    fix error

    pip3 install --upgrade pip

# 2022/12/16 giá vé chưa thêm vào module này

# 2023/01/03
    pip3 install pyjwt

# 2023/03/05
    bao cao chieu phim , bỏ domain ngày hoá đơn 

# khong chay dc ban enterprise

