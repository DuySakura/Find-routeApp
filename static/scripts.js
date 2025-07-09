let map = L.map('map').setView([21.038235, 105.826213], 15);
let points = [];
let markers = [];
let ban_routes = [];
let polyline;


//Tạo bản đồ
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);


//Tạo đường bao
fetch('/boundary')
.then(res => res.json())
.then(coords => {
    const polygon = L.polygon(coords, {
    color: 'green',
    weight: 2,
    fillOpacity: 0.2
    }).addTo(map);
    map.fitBounds(polygon.getBounds());
})
.catch(err => {
    console.error('Lỗi khi lấy đường bao:', err);
});


//Tạo sự kiện click
map.on('click', function(e) {
    //Reset
    if (points.length >= 2) {
        points = [];
        markers.forEach(m => map.removeLayer(m));
        if (polyline) map.removeLayer(polyline);
        markers = [];
    }

    const latlng = e.latlng;
    points.push(latlng);

    //Xác định điểm xuất phát
    if (points.length == 1) {
        const marker = L.marker(latlng).addTo(map).bindPopup('Điểm xuất phát').openPopup();
        markers.push(marker);
    } 
    //Xác định điểm đến
    else {
        const marker = L.marker(latlng).addTo(map).bindPopup('Điểm đến').openPopup();
        markers.push(marker);
    }

    if (points.length === 2) {
    //Gửi dữ liệu về backend
    fetch('/find-route-by-click', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            point1: {lat: points[0].lat, lng: points[0].lng},
            point2: {lat: points[1].lat, lng: points[1].lng}
        })
    })
    //Nhận lại dữ liệu từ backend
    .then(res => res.json())
    .then(coords => {
        //Vẽ đường đi nếu tìm được, không thì báo lỗi
        if (coords.length > 0) {
            polyline = L.polyline(coords, { color: 'blue' }).addTo(map);
            map.fitBounds(polyline.getBounds());
        } else {
            alert(coords.error);
        }
    })
    .catch(err => console.error(err));
    }
});


//Hàm xử lý dữ liệu khi xảy ra sự kiện bấm nút "Tìm đường"
function findRoute() {
    //Lấy dữ liệu từ text box
    const start = document.getElementById('placeInput1').value;
    const end = document.getElementById('placeInput2').value;

    //Gửi dữ liệu về backend
    fetch('/find-route-by-text', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            place1: start,
            place2: end
    })
    })
    //Nhận lại dữ liệu từ backend
    .then(res => res.json())
    .then(coords => {
    //Vẽ đường đi và đánh dấu điểm xuất phát, điểm đích nếu tìm được, không thì báo lỗi
    if (coords.length > 0) {
        //Reset
        if (polyline) map.removeLayer(polyline);
        if (markers) {
            markers.forEach(m => map.removeLayer(m));
            markers = [];
        }
        const start_marker = L.marker(coords[0]).addTo(map).bindPopup('Điểm xuất phát').openPopup();
        const end_marker = L.marker(coords[coords.length-1]).addTo(map).bindPopup('Điểm đích').openPopup();
        markers.push(start_marker, end_marker);
        polyline = L.polyline(coords, { color: 'blue' }).addTo(map);
        map.fitBounds(polyline.getBounds());
    } else {
        alert(coords.error);
    }
    })
    .catch(err => console.error(err));
}


//Hàm xử lý dữ liệu khi xảy ra sự kiện bấm nút "Xác nhận"
function changeWeight() {
    const selected = document.querySelector('input[name="action"]:checked');
    const street = document.getElementById('streetInput').value;
    if (selected && selected.value == "change") {
        const level = document.getElementById('level').value
        fetch('/change-weight', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                street: street,
                level: level
            })
        })
        .then(res => res.json())
        .then(data => alert(data.message))
        .catch(err => console.error(err));
    } else {
        fetch('/ban-route', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({street: street})
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.routes) {
                data.routes.forEach(line => {
                    const ban_route = L.polyline(line, { color: 'red', weight: 1, dashArray: '5, 10' }).addTo(map);
                    ban_routes.push(ban_route);
                })
            }
        })
        .catch(err => console.error(err));
    }
}


//Hàm xử lý sự kiện bấm nút "Reset"
function resetGraph() {
    ban_routes.forEach(line => map.removeLayer(line));
    ban_routes = [];

    fetch('/reset', {method: 'POST'})
    .then(res => res.json())
    .then(data => alert(data.message))
    .catch(err => console.error(err));

}


//Ẩn/Hiện sidebar
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main');
    sidebar.classList.toggle('appear');
    main.classList.toggle('minimize');
}


//Hàm xử lý thay đổi của mức độ tắc
const levelSlider = document.getElementById('level');
const levelValue = document.getElementById('levelValue');

levelSlider.addEventListener('input', function () {
    levelValue.textContent = levelSlider.value;
});
