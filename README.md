# Route-finding App

Ứng dụng tìm đường đi tối ưu giữa 2 địa điểm trong khu vực phường Ngọc Hà, Ba Đình, Hà Nội

## Tổng Quan Dự Án

- Ứng dụng được xây dựng bằng Flask (backend) và Leaflet (frontend)
- Hỗ trợ tìm kiếm bằng cách click 2 địa điểm trên bản đồ hoặc nhập địa chỉ của 2 địa điểm
- Đường đi tối ưu được tìm kiếm bằng thuật toán Dijkstra

## Cấu Trúc Thư Mục

```
.
├── static/               
│   ├── scripts.js
│   └── style.css
├── templates/
│   └── index.html
└── app.py
```

## Cài đặt và Chạy

1. Clone repository:
```bash
git clone https://github.com/DuySakura/Route-findingApp.git
```
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
3. Chạy server:
```bash
cd Route-findingApp
python -u app.py
```
