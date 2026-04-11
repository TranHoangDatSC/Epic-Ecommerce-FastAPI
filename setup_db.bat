@echo off
echo --- Dang xoa DB cũ (hoac drop table) ---
:: Lệnh này chỉ chạy nếu bạn muốn xóa sạch data. 
:: Lưu ý: Hãy cẩn thận với lệnh DROP.
psql -U postgres -d oldshop -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

echo --- Chay Migration de tao cau truc mới ---
alembic upgrade head

echo --- Nạp dữ liệu mẫu (Seed Data) ---
psql -U postgres -d oldshop -f database/03_seeds/user/seed.sql
echo --- DONE: Hệ thống đã sẵn sàng ---
pause