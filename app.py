from flask import Flask, render_template, request, jsonify
import osmnx as ox
import networkx as nx
import requests


app = Flask(__name__)
place_name = "Ngọc Hà, Ba Đình, Hà Nội, Vietnam"
G = ox.graph_from_place(place_name)
G_compared = ox.graph_from_place(["Ba Đình, Hà Nội, Vietnam", "Liễu Giai, Hà Nội, Vietnam", "Quán Thánh, Hà Nội, Vietnam", "Điện Biên, Hà Nội, Vietnam", "Đội Cấn, Hà Nội, Việt Nam", "Thụy Khuê, Tây Hồ, Hà Nội, Vietnam"])
G_original = G.copy()
street_speed = {'secondary': 40, 'tertiary': 30, 'residential': 20, 'service': 10, 'steps' : 5, 'path' : 5, 'footway' : 5}


#Thay đổi thuộc tính 'length' của các cạnh trong đồ thị thành thời gian di chuyển
for u, v, key, data in G.edges(keys=True, data=True):
    speed_min = 40
    if isinstance(data['highway'], list):
        for i in data['highway']:
            if street_speed[i] < speed_min:
                speed_min = street_speed[i]
    else: 
        speed_min = street_speed[data['highway']]
    data['length'] /= speed_min


def find_route(start_point, end_point):
    #Tìm 2 nodes gần nhất với tọa độ của điểm xuất phát và điểm đích
    orig = ox.nearest_nodes(G, start_point['lng'], start_point['lat'])
    dest = ox.nearest_nodes(G, end_point['lng'], end_point['lat'])

    #Kiểm tra xem điểm xuất phát và điểm đích có ở trong vùng đang tìm kiếm hay không
    #Nếu thuộc thì có đường đi giữa hai điểm hay không
    if (orig != ox.nearest_nodes(G_compared, start_point['lng'], start_point['lat']) or 
        dest != ox.nearest_nodes(G_compared, end_point['lng'], end_point['lat']) or
        not nx.has_path(G, orig, dest)):
        return {"error": "Không tìm thấy đường đi"}
    
    #Tìm đường đi ngắn nhất từ điểm xuất phát đến điểm đích
    route = nx.shortest_path(G, orig, dest, weight='length')
    route_coords = [[G.nodes[node]['y'], G.nodes[node]['x']] for node in route]
    route_coords.insert(0, [start_point['lat'], start_point['lng']])
    route_coords.append([end_point['lat'], end_point['lng']])
    return jsonify(route_coords)


#Tạo UI
@app.route('/')
def index():
    return render_template('index.html')


#Tạo đường bao
@app.route('/boundary')
def boundary():
    G_gdf = ox.geocode_to_gdf(place_name)

    polygon = G_gdf.geometry.iloc[0]
    coords = list(polygon.exterior.coords)
    latlng_coords = [[lat, lng] for lng, lat in coords]

    return jsonify(latlng_coords)


#Tìm đường theo phương pháp chọn trực tiếp trên bản đồ
@app.route('/find-route-by-click', methods=['POST'])
def find_route_by_click():
    try:
        data = request.get_json()
        start_point = data['point1']
        end_point = data['point2']

        return find_route(start_point, end_point)
    except Exception as e:
        return {"error": str(e)}


#Tìm đường bằng phương pháp nhập địa điểm
@app.route('/find-route-by-text', methods=['POST'])
def find_route_by_text():
    try:
        data = request.get_json()
        start_place = data['place1']
        end_place = data['place2']

        #Lấy dữ liệu về tọa độ của điểm xuất phát và điểm đích từ OSM
        url = 'https://nominatim.openstreetmap.org/search'
        params = {
        'q': start_place,
        'format': 'json',
        'limit': 1
        }

        response = requests.get(url, params=params, headers={'User-Agent': 'FindRouteApp'})
        results = response.json()

        if results:
            start_point = {'lat': float(results[0]['lat']), 'lng': float(results[0]['lon'])}
        else:
            return {"error": "Điểm xuất phát không hợp lệ"}
        
        params['q'] = end_place

        response = requests.get(url, params=params, headers={'User-Agent': 'FindRouteApp'})
        results = response.json()

        if results:
            end_point = {'lat': float(results[0]['lat']), 'lng': float(results[0]['lon'])}
        else:
            return {"error": "Điểm đích không hợp lệ"}

        return find_route(start_point, end_point)
    except Exception as e:
        return {"error": str(e)}


#Thay đổi trọng số của các cạnh trong đồ thị bằng phương pháp nhập tên đường
@app.route('/change-weight', methods=['POST'])
def change_weight():
    try:
        data = request.get_json()
        street_name = data['street']
        level = float(data['level'])
        speed_min = 40
        for u, v, key, data in G.edges(keys=True, data=True):
            if 'name' not in data:
                continue
            if  (isinstance(data['name'], list) and street_name in data['name']) or street_name in data['name']:
                if isinstance(data['highway'], list):
                    for i in data['highway']:
                        if street_speed[i] < speed_min:
                            speed_min = street_speed[i]
                else:
                    speed_min = street_speed[data['highway']]
        data['length'] = G_original.edges[u, v, key]['length'] / (speed_min * (1 - level * 0.25))
        return {"message": "Trọng số đã được thay đổi"}
    except Exception as e:
        return {"error": str(e)}


#Cấm đường bằng phương pháp nhập tên đường
@app.route('/ban-route', methods=['POST'])
def ban_route():
    try:
        data = request.get_json()
        street_name = data['street']
        edge_to_remove = []

        for u, v, key, data in G.edges(keys=True, data=True):
            if 'name' not in data:
                continue
            if  isinstance(data['name'], list):
                if street_name in data['name']:
                    edge_to_remove.append((u, v, key))
            else:
                if street_name == data['name']:
                    edge_to_remove.append((u, v, key))
                    
        for u, v, key in edge_to_remove:
            G.remove_edge(u, v, key=key)
        return {"message": "Đã cấm đường"}
    except Exception as e:
        return {"error": str(e)}


@app.route('/reset', methods=['POST'])
def reset():
    try:
        global G
        G = G_original.copy()
        return {"message": "Đã khôi phục lại đồ thị ban đầu"}
    except Exception as e:
        return {"error": str(e)}


if (__name__ == "__main__"):
    app.run(debug = True)
