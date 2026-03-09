# OldShop Database Setup Guide

## Tổng quan
Dự án database OldShop được chuyển đổi từ SQL Server sang PostgreSQL với cấu trúc chuyên nghiệp.

## Cấu trúc thư mục
```
database/
├── init.sql                    # File khởi tạo chính
├── 01_schema/                  # Định nghĩa bảng
├── 02_functions/               # Functions và Triggers (theo bảng)
├── 03_seeds/                   # Dữ liệu mẫu (theo bảng)
├── 04_modules/                 # CRUD operations
├── config/                     # Cấu hình setup
│   ├── database_config.sql     # Cấu hình database
│   ├── docker-compose.yml      # Docker setup
│   ├── .env.example            # Environment variables
│   └── setup.sh                # Setup script
└── README.md                   # Tài liệu này
```

## Cách setup

### 1. Sử dụng Docker (Khuyến nghị)
```bash
cd config
docker-compose up -d
```

### 2. Setup thủ công
```bash
# Cài đặt PostgreSQL
# Tạo database
createdb oldshop

# Chạy setup script
chmod +x config/setup.sh
./config/setup.sh
```

### 3. Chạy trực tiếp
```bash
psql -d oldshop -f init.sql
```

## Kết nối database
Sử dụng thông tin trong file `config/.env.example` để cấu hình kết nối.

## Lưu ý
- Triggers tự động chặn việc tự mua hàng và cập nhật tồn kho
- Sử dụng soft delete cho các bảng chính
- Dữ liệu mẫu được tách theo từng bảng để dễ quản lý