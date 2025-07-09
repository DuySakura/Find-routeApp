# Find-route App

Ứng dụng tìm đường đi tối ưu giữa 2 địa điểm trong khu vực phường Ngọc Hà, Ba Đình, Hà Nội

## Tổng Quan Dự Án

- Ứng dụng được xây dựng bằng Flask, OSMnx (backend) và Leaflet (Frontend)
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
git clone https://github.com/DuySakura/Project-IntroAI.git
```
2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```
3. Chạy server:
```bash
cd Project-IntroAI
python -u app.py
```
