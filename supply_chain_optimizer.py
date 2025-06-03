import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans

from geopy.distance import geodesic
import io
import base64
import os
import folium
from folium.plugins import MarkerCluster

class DeliveryPoint:
    def __init__(self, id, name, lat, lon):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.assigned_warehouse = None
        
    def __repr__(self):
        return f"DeliveryPoint({self.id}, {self.name}, {self.lat:.4f}, {self.lon:.4f})"
        
    def distance_to(self, other):
        """Calcular distância para outro ponto em km"""
        return geodesic((self.lat, self.lon), (other.lat, other.lon)).kilometers

class Warehouse:
    def __init__(self, id, name, lat, lon):
        self.id = id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.assigned_deliveries = []
        
    def __repr__(self):
        return f"Warehouse({self.id}, {self.name}, {self.lat:.4f}, {self.lon:.4f})"
        
    def distance_to(self, delivery_point):
        """Calcular distância para um ponto de entrega em km"""
        return geodesic((self.lat, self.lon), (delivery_point.lat, delivery_point.lon)).kilometers
        
    def add_delivery(self, delivery_point):
        """Atribuir um ponto de entrega a este armazém"""
        self.assigned_deliveries.append(delivery_point)
        delivery_point.assigned_warehouse = self

class WarehouseOptimizer:
    def __init__(self):
        self.delivery_points = []
        self.warehouses = []
        self.total_distance = 0
        
        self.suitable_warehouse_areas = [
            {"name": "Setor de Indústria e Abastecimento", "lat": -15.8146, "lon": -47.9495},
            {"name": "Setor de Indústrias Gráficas", "lat": -15.7992, "lon": -47.9196},
            {"name": "Setor de Armazenagem e Abastecimento Norte", "lat": -15.7309, "lon": -47.9055},
            {"name": "Setor de Inflamáveis", "lat": -15.8519, "lon": -47.9621},
            {"name": "Taguatinga Industrial", "lat": -15.8345, "lon": -48.0742},
            {"name": "Setor de Materiais de Construção", "lat": -15.8471, "lon": -48.0335},
            {"name": "Polo JK", "lat": -16.0321, "lon": -47.9832},
            {"name": "Cidade do Automóvel", "lat": -15.8640, "lon": -48.0987},
            {"name": "Setor de Múltiplas Atividades Sul", "lat": -15.8411, "lon": -47.9410},
            {"name": "Setor de Clubes Esportivos Sul", "lat": -15.8221, "lon": -47.8944},
            {"name": "Sobradinho Industrial", "lat": -15.6565, "lon": -47.8100},
            {"name": "Núcleo Bandeirante", "lat": -15.8673, "lon": -47.9673},
            {"name": "Área Industrial de Ceilândia", "lat": -15.8307, "lon": -48.1273},
            {"name": "Samambaia Sul", "lat": -15.8665, "lon": -48.0893},
            {"name": "Recanto das Emas", "lat": -15.9138, "lon": -48.0668},
            {"name": "Guará Industrial", "lat": -15.8179, "lon": -47.9899},
        ]

    def load_delivery_points(self):
        """Carregar pontos de entrega em Brasília, DF"""
        print("Carregando pontos de entrega...")
        
        self.delivery_points = []
        
        static_points = [
            {"name": "Rodoviária do Plano Piloto", "lat": -15.7939, "lon": -47.8828},
            {"name": "Esplanada dos Ministérios", "lat": -15.7980, "lon": -47.8660},
            {"name": "Congresso Nacional", "lat": -15.7997, "lon": -47.8644},
            {"name": "Palácio do Planalto", "lat": -15.7986, "lon": -47.8678},
            {"name": "Supremo Tribunal Federal", "lat": -15.8022, "lon": -47.8628},
            {"name": "Teatro Nacional", "lat": -15.7906, "lon": -47.8789},
            {"name": "Catedral Metropolitana", "lat": -15.7981, "lon": -47.8754},
            {"name": "Memorial JK", "lat": -15.7847, "lon": -47.9135},
            {"name": "Parque da Cidade", "lat": -15.8016, "lon": -47.9124},
            {"name": "Torre de TV", "lat": -15.7905, "lon": -47.8932},
            
            {"name": "UnB - Universidade de Brasília", "lat": -15.7639, "lon": -47.8678},
            {"name": "Hospital Universitário", "lat": -15.7691, "lon": -47.8774},
            {"name": "Shopping Liberty Mall", "lat": -15.7861, "lon": -47.8874},
            {"name": "HRAN", "lat": -15.7808, "lon": -47.8898},
            {"name": "Setor Comercial Norte", "lat": -15.7861, "lon": -47.8874},
            
            {"name": "Hospital de Base", "lat": -15.8007, "lon": -47.8898},
            {"name": "Shopping Pátio Brasil", "lat": -15.7983, "lon": -47.8935},
            {"name": "CONIC", "lat": -15.7967, "lon": -47.8847},
            {"name": "Setor Bancário Sul", "lat": -15.8008, "lon": -47.8885},
            {"name": "Setor Hoteleiro Sul", "lat": -15.7953, "lon": -47.8897},
            
            {"name": "Pontão do Lago Sul", "lat": -15.8283, "lon": -47.8719},
            {"name": "Hospital Sarah Kubitschek", "lat": -15.8053, "lon": -47.8825},
            {"name": "Aeroporto Internacional de Brasília", "lat": -15.8698, "lon": -47.9208},
            
            {"name": "Shopping Deck Norte", "lat": -15.7433, "lon": -47.8684},
            {"name": "Parque Nacional de Brasília", "lat": -15.7382, "lon": -47.9265},
            
            {"name": "Cruzeiro Center", "lat": -15.7897, "lon": -47.9377},
            {"name": "Colégio Militar de Brasília", "lat": -15.7845, "lon": -47.9163},
            
            {"name": "Sudoeste Shopping", "lat": -15.7994, "lon": -47.9250},
            {"name": "Hospital das Forças Armadas", "lat": -15.8049, "lon": -47.9338},
            
            {"name": "Taguatinga Shopping", "lat": -15.8320, "lon": -48.0542},
            {"name": "Administração Regional de Taguatinga", "lat": -15.8309, "lon": -48.0555},
            {"name": "Hospital Regional de Taguatinga", "lat": -15.8189, "lon": -48.0652},
            {"name": "UniCEUB Taguatinga", "lat": -15.8282, "lon": -48.0621},
            {"name": "Avenida Comercial Norte", "lat": -15.8264, "lon": -48.0602},
            
            {"name": "Shopping JK Ceilândia", "lat": -15.8198, "lon": -48.1234},
            {"name": "Hospital Regional de Ceilândia", "lat": -15.8152, "lon": -48.1217},
            {"name": "Feira Central de Ceilândia", "lat": -15.8169, "lon": -48.1135},
            {"name": "Centro Administrativo Ceilândia", "lat": -15.8179, "lon": -48.1098},
            {"name": "Estação Ceilândia Centro", "lat": -15.8174, "lon": -48.1107},
            
            {"name": "Águas Claras Shopping", "lat": -15.8362, "lon": -48.0236},
            {"name": "Parque Águas Claras", "lat": -15.8382, "lon": -48.0202},
            {"name": "Estação Arniqueiras", "lat": -15.8432, "lon": -48.0245},
            {"name": "Unieuro Águas Claras", "lat": -15.8395, "lon": -48.0213},
            {"name": "Avenida das Araucárias", "lat": -15.8344, "lon": -48.0197},
            
            {"name": "ParkShopping", "lat": -15.8223, "lon": -47.9520},
            {"name": "Feira do Guará", "lat": -15.8304, "lon": -47.9754},
            {"name": "Administração Regional do Guará", "lat": -15.8298, "lon": -47.9737},
            
            {"name": "Hospital Regional de Sobradinho", "lat": -15.6500, "lon": -47.7940},
            {"name": "Administração Regional de Sobradinho", "lat": -15.6528, "lon": -47.7931},
            
            {"name": "Shopping Sul Gama", "lat": -16.0095, "lon": -48.0559},
            {"name": "Hospital Regional do Gama", "lat": -16.0067, "lon": -48.0452},
            {"name": "Administração Regional do Gama", "lat": -16.0192, "lon": -48.0650},
            
            {"name": "Hospital Regional de Planaltina", "lat": -15.6198, "lon": -47.6494},
            {"name": "Administração Regional de Planaltina", "lat": -15.6246, "lon": -47.6479},
            {"name": "Vale do Amanhecer", "lat": -15.6336, "lon": -47.6376},
        ]
        
        for i, point_data in enumerate(static_points):
            point = DeliveryPoint(
                i, 
                point_data["name"], 
                point_data["lat"], 
                point_data["lon"]
            )
            self.delivery_points.append(point)
            
        print(f"Carregados {len(self.delivery_points)} pontos de entrega")
        return self.delivery_points
        
    def place_warehouses_kmeans(self, num_warehouses=5):
        """Posicionar Korreios usando agrupamento K-means com restrições geográficas"""
        print(f"Posicionando {num_warehouses} Korreios usando agrupamento K-means...")
        
        if not self.delivery_points:
            print("Erro: Nenhum ponto de entrega carregado. Carregue os dados primeiro.")
            return
            
        coords = np.array([[dp.lat, dp.lon] for dp in self.delivery_points])
        
        kmeans = KMeans(n_clusters=num_warehouses, random_state=42)
        kmeans.fit(coords)
        
        self.warehouses = []
        
        for i, center in enumerate(kmeans.cluster_centers_):
            nearest_area = min(
                self.suitable_warehouse_areas,
                key=lambda area: geodesic((center[0], center[1]), (area["lat"], area["lon"])).kilometers
            )
            
            warehouse = Warehouse(
                i, 
                f"Armazém {i} ({nearest_area['name']})", 
                nearest_area["lat"], 
                nearest_area["lon"]
            )
            self.warehouses.append(warehouse)
            
            distance_moved = geodesic((center[0], center[1]), (nearest_area["lat"], nearest_area["lon"])).kilometers
            print(f"Armazém {i} posicionado em {nearest_area['name']} " +
                  f"({distance_moved:.2f} km da localização matemática ótima)")
            
        print(f"Posicionados {len(self.warehouses)} Korreios em áreas adequadas")
        return self.warehouses
    
    def place_warehouses_custom(self, locations):
        """Posicionar Korreios em locais personalizados selecionados da lista de áreas adequadas"""
        print(f"Posicionando 5 Korreios em locais personalizados...")
        
        if not self.delivery_points:
            print("Erro: Nenhum ponto de entrega carregado. Carregue os dados primeiro.")
            return
            
        if len(locations) != 5:
            print("Erro: Deve especificar exatamente 5 localizações de Korreios.")
            return
            
        self.warehouses = []
        
        for i, location_idx in enumerate(locations):
            if location_idx < 0 or location_idx >= len(self.suitable_warehouse_areas):
                print(f"Erro: Índice de localização inválido {location_idx}.")
                continue
                
            area = self.suitable_warehouse_areas[location_idx]
            
            warehouse = Warehouse(
                i, 
                f"Armazém {i} ({area['name']})", 
                area["lat"], 
                area["lon"]
            )
            self.warehouses.append(warehouse)
            
            print(f"Armazém {i} posicionado em {area['name']}")
            
        print(f"Posicionados {len(self.warehouses)} Korreios em áreas adequadas")
        return self.warehouses
        
    def assign_deliveries_to_warehouses(self):
        """Atribuir pontos de entrega ao armazém mais próximo"""
        print("Atribuindo pontos de entrega aos Korreios...")
        
        if not self.warehouses:
            print("Erro: Nenhum armazém posicionado. Posicione os Korreios primeiro.")
            return
            
        for warehouse in self.warehouses:
            warehouse.assigned_deliveries = []
            
        for delivery in self.delivery_points:
            nearest_warehouse = min(self.warehouses, 
                                   key=lambda w: w.distance_to(delivery))
            nearest_warehouse.add_delivery(delivery)
            
        for warehouse in self.warehouses:
            print(f"{warehouse.name}: {len(warehouse.assigned_deliveries)} entregas atribuídas")
    
    def calculate_total_distance(self):
        """Calcular distância total dos Korreios aos pontos de entrega atribuídos"""
        total_distance = 0
        
        for warehouse in self.warehouses:
            for delivery in warehouse.assigned_deliveries:
                total_distance += warehouse.distance_to(delivery)
                
        self.total_distance = total_distance
        print(f"Distância total: {total_distance:.2f} km")
        return total_distance
        
    def get_optimization_metrics(self):
        """Calcular e retornar métricas de otimização"""
        metrics = {
            'warehouses': self.warehouses,
            'num_warehouses': len(self.warehouses),
            'total_delivery_points': len(self.delivery_points),
            'total_distance': self.total_distance,
            'avg_distance': self.total_distance / len(self.delivery_points) if self.delivery_points else 0,
        }
        return metrics

def run_warehouse_optimization(strategy="kmeans", custom_locations=None, num_warehouses=5):
    """Executar otimização de localização de Korreios usando a estratégia especificada"""
    print(f"\n--- Executando otimização de Korreios com estratégia {strategy} ---")
    
    optimizer = WarehouseOptimizer()
    optimizer.load_delivery_points()
    
    if strategy == "kmeans":
        optimizer.place_warehouses_kmeans(num_warehouses)
    elif strategy == "custom":
        optimizer.place_warehouses_custom(custom_locations)
    else:
        print(f"Erro: Estratégia desconhecida '{strategy}'")
        return None
    
    optimizer.assign_deliveries_to_warehouses()
    optimizer.calculate_total_distance()
    
    return optimizer.get_optimization_metrics()

def compare_warehouse_strategies():
    """Comparar diferentes estratégias de posicionamento de Korreios"""
    print("===== Comparando Estratégias de Posicionamento de Korreios =====")
    
    optimized_locations = [9, 10, 4, 6, 1]  
    optimized_metrics = run_warehouse_optimization("custom", custom_locations=optimized_locations)
    
    central_indices = [1, 9, 0, 15, 8]  
    central_metrics = run_warehouse_optimization("custom", custom_locations=central_indices)
    
    distributed_indices = [1, 4, 10, 6, 13]  
    distributed_metrics = run_warehouse_optimization("custom", custom_locations=distributed_indices)
    
    ns_corridor_indices = [10, 1, 0, 6, 15]  
    ns_corridor_metrics = run_warehouse_optimization("custom", custom_locations=ns_corridor_indices)
    
    ew_corridor_indices = [11, 15, 4, 12, 13]  
    ew_corridor_metrics = run_warehouse_optimization("custom", custom_locations=ew_corridor_indices)
    
    density_indices = [1, 9, 15, 4, 5]  
    density_metrics = run_warehouse_optimization("custom", custom_locations=density_indices)
    
    all_metrics = {
        'K-means': optimized_metrics,
        'Áreas Centrais': central_metrics,
        'Distribuídos': distributed_metrics,
        'Corredor Norte-Sul': ns_corridor_metrics,
        'Corredor Leste-Oeste': ew_corridor_metrics,
        'Densidade Populacional': density_metrics
    }
    
    create_expanded_comparison(all_metrics)

def create_expanded_comparison(all_metrics):
    """Criar gráficos e HTML para comparar múltiplas estratégias de posicionamento de Korreios"""
    output_file = "resultado_localizacao_korreios.html"
    
    import matplotlib
    matplotlib.use('Agg')  
    
    plt.figure(figsize=(14, 8))
    
    sorted_strategies = sorted(all_metrics.items(), key=lambda x: x[1]['total_distance'])
    strategy_names = [s[0] for s in sorted_strategies]
    distances = [s[1]['total_distance'] for s in sorted_strategies]
    
    plt.bar(strategy_names, distances, color='skyblue')
    plt.title('Comparação de Distância Total Entre Estratégias')
    plt.ylabel('Distância Total (km)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    distance_chart_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()
    
    plt.figure(figsize=(14, 8))
    strategy_names = [s[0] for s in sorted_strategies]
    num_warehouses = [s[1]['num_warehouses'] for s in sorted_strategies]
    warehouses_with_deliveries = []
    
    for strategy in sorted_strategies:
        count = sum(1 for w in strategy[1]['warehouses'] if len(w.assigned_deliveries) > 0)
        warehouses_with_deliveries.append(count)
    
    x = np.arange(len(strategy_names))
    width = 0.35
    
    plt.bar(x - width/2, num_warehouses, width, label='Total de Korreios', color='skyblue')
    plt.bar(x + width/2, warehouses_with_deliveries, width, label='Korreios Com Entregas', color='orange')
    
    plt.xlabel('Estratégia')
    plt.ylabel('Número de Korreios')
    plt.title('Utilização de Korreios por Estratégia')
    plt.xticks(x, strategy_names, rotation=45, ha='right')
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    warehouse_chart_str = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()
    
    best_strategy = sorted_strategies[0][0]
    worst_strategy = sorted_strategies[-1][0]
    improvement = (sorted_strategies[-1][1]['total_distance'] - sorted_strategies[0][1]['total_distance']) / sorted_strategies[-1][1]['total_distance'] * 100
    
    brasilia_center = [-15.7801, -47.9292]
    
    map_strategies = {}
    for strategy_name, metrics in all_metrics.items():
        map_strategies[strategy_name] = metrics
    
    folium_map = create_multi_strategy_map(map_strategies, brasilia_center)
    
    map_html = folium_map._repr_html_()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Otimização de Localização de Korreios</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            .comparison-container {{ display: flex; flex-wrap: wrap; }}
            .strategy-box {{ 
                flex: 1; 
                min-width: 300px; 
                margin: 10px; 
                padding: 15px; 
                border: 1px solid #ddd; 
                border-radius: 5px;
                background-color: #f9f9f9; 
            }}
            .best {{ background-color: #e6ffe6; }}
            .worst {{ background-color: #ffebeb; }}
            .metric {{ margin-bottom: 10px; }}
            .metric-name {{ font-weight: bold; }}
            .better {{ color: green; }}
            .worse {{ color: red; }}
            .charts {{ text-align: center; margin: 20px 0; }}
            .map-container {{ 
                height: 450px; 
                width: 100%; 
                margin: 20px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
                overflow: hidden;
            }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .improvement {{ 
                font-weight: bold; 
                color: green;
                font-size: 18px;
                text-align: center;
                margin: 20px 0;
            }}
            .tab-container {{
                width: 100%;
                margin-top: 20px;
            }}
            .tab {{
                overflow: hidden;
                border: 1px solid #ccc;
                background-color: #f1f1f1;
            }}
            .tab button {{
                background-color: inherit;
                float: left;
                border: none;
                outline: none;
                cursor: pointer;
                padding: 14px 16px;
                transition: 0.3s;
                font-size: 16px;
            }}
            .tab button:hover {{
                background-color: #ddd;
            }}
            .tab button.active {{
                background-color: #ccc;
            }}
            .tabcontent {{
                display: none;
                padding: 6px 12px;
                border: 1px solid #ccc;
                border-top: none;
            }}
            .summary-table {{
                width: 100%;
                margin-top: 20px;
                border-collapse: collapse;
            }}
            .summary-table th, .summary-table td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            .summary-table th {{
                background-color: #f2f2f2;
                position: sticky;
                top: 0;
            }}
            .summary-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .summary-table tr:hover {{
                background-color: #f1f1f1;
            }}
            .summary-table tr.best {{
                background-color: #e6ffe6;
            }}
            .summary-table tr.worst {{
                background-color: #ffebeb;
            }}
        </style>
        <script>
            function openTab(evt, tabName) {{
                var i, tabcontent, tablinks;
                tabcontent = document.getElementsByClassName("tabcontent");
                for (i = 0; i < tabcontent.length; i++) {{
                    tabcontent[i].style.display = "none";
                }}
                tablinks = document.getElementsByClassName("tablinks");
                for (i = 0; i < tablinks.length; i++) {{
                    tablinks[i].className = tablinks[i].className.replace(" active", "");
                }}
                document.getElementById(tabName).style.display = "block";
                evt.currentTarget.className += " active";
            }}
            
            window.onload = function() {{
                document.getElementById("defaultOpen").click();
            }};
        </script>
    </head>
    <body>
        <h1>Otimização de Localização de Korreios</h1>
        
        <div class="improvement">
            A estratégia {best_strategy} fornece a melhor localização de Korreios, reduzindo a distância total de viagem em {improvement:.1f}% comparada à pior estratégia!
        </div>
        
        <div class="tab-container">
            <div class="tab">
                <button class="tablinks" onclick="openTab(event, 'Map')" id="defaultOpen">Mapa Interativo</button>
                <button class="tablinks" onclick="openTab(event, 'Details')">Detalhes das Estratégias</button>
            </div>
            
            <div id="Map" class="tabcontent">
                <h2>Mapa Interativo de Localização de Korreios</h2>
                <p>Este mapa mostra todas as estratégias de localização de Korreios. Você pode alternar a visibilidade dos diferentes elementos usando o controle de camadas no canto superior direito.</p>
                <div class="map-container">
                    {map_html}
                </div>
            </div>
            
            <div id="Details" class="tabcontent">
                <h2>Detalhes das Estratégias</h2>
                <div class="comparison-container">
    """
    
    best_metrics = sorted_strategies[0][1]
    worst_metrics = sorted_strategies[-1][1]
    
    html_content += f"""
                    <div class="strategy-box best">
                        <h2>Melhor Estratégia: {best_strategy}</h2>
                        <div class="metric">
                            <span class="metric-name">Número de Korreios:</span> {best_metrics['num_warehouses']}
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Total:</span> {best_metrics['total_distance']:.2f} km
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Média por Entrega:</span> {best_metrics['avg_distance']:.2f} km
                        </div>
                        <h3>Localizações dos Korreios</h3>
                        <table>
                            <tr>
                                <th>Armazém</th>
                                <th>Localização</th>
                                <th>Entregas</th>
                            </tr>
    """
    
    for w in best_metrics['warehouses']:
        html_content += f"""
                            <tr>
                                <td>Armazém {w.id}</td>
                                <td>{w.name.split('(')[1].split(')')[0]}</td>
                                <td>{len(w.assigned_deliveries)}</td>
                            </tr>
        """
    
    html_content += f"""
                        </table>
                    </div>
                    
                    <div class="strategy-box worst">
                        <h2>Pior Estratégia: {worst_strategy}</h2>
                        <div class="metric">
                            <span class="metric-name">Número de Korreios:</span> {worst_metrics['num_warehouses']}
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Total:</span> {worst_metrics['total_distance']:.2f} km
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Média por Entrega:</span> {worst_metrics['avg_distance']:.2f} km
                        </div>
                        <h3>Localizações dos Korreios</h3>
                        <table>
                            <tr>
                                <th>Armazém</th>
                                <th>Localização</th>
                                <th>Entregas</th>
                            </tr>
    """
    
    for w in worst_metrics['warehouses']:
        html_content += f"""
                            <tr>
                                <td>Armazém {w.id}</td>
                                <td>{w.name.split('(')[1].split(')')[0]}</td>
                                <td>{len(w.assigned_deliveries)}</td>
                            </tr>
        """
    
    html_content += f"""
                        </table>
                    </div>
    """
    
    # Adicionar as estratégias restantes (excluindo a melhor e a pior)
    for strategy_name, metrics in sorted_strategies:
        if strategy_name != best_strategy and strategy_name != worst_strategy:
            html_content += f"""
                    <div class="strategy-box">
                        <h2>Estratégia: {strategy_name}</h2>
                        <div class="metric">
                            <span class="metric-name">Número de Korreios:</span> {metrics['num_warehouses']}
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Total:</span> {metrics['total_distance']:.2f} km
                        </div>
                        <div class="metric">
                            <span class="metric-name">Distância Média por Entrega:</span> {metrics['avg_distance']:.2f} km
                        </div>
                        <h3>Localizações dos Korreios</h3>
                        <table>
                            <tr>
                                <th>Armazém</th>
                                <th>Localização</th>
                                <th>Entregas</th>
                            </tr>
            """
            
            for w in metrics['warehouses']:
                html_content += f"""
                            <tr>
                                <td>Armazém {w.id}</td>
                                <td>{w.name.split('(')[1].split(')')[0]}</td>
                                <td>{len(w.assigned_deliveries)}</td>
                            </tr>
                """
            
            html_content += f"""
                        </table>
                    </div>
            """
    
    html_content += f"""
                </div>
            </div>
        </div>
        
    </body>
    </html>
    """
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Comparação salva em {output_file}")
    print(f"A estratégia {best_strategy} fornece o melhor posicionamento de Korreios, reduzindo a distância de viagem em {improvement:.1f}%")

def create_multi_strategy_map(strategies, center):
    """Criar um mapa comparando múltiplas estratégias de posicionamento de Korreios"""
    m = folium.Map(location=center, zoom_start=10, tiles='OpenStreetMap')
    
    delivery_points = folium.FeatureGroup(name="Todos os Pontos de Entrega").add_to(m)
    
    first_strategy = list(strategies.values())[0]
    for delivery in first_strategy['warehouses'][0].assigned_deliveries:
        folium.CircleMarker(
            location=[delivery.lat, delivery.lon],
            radius=4,
            popup=f"<b>{delivery.name}</b>",
            color='gray',
            fill=True,
            fill_opacity=0.7,
            tooltip=delivery.name
        ).add_to(delivery_points)
    
    colors = {
        'Melhor Estratégia': 'green',
        'Pior Estratégia': 'red',
        'K-means': 'blue',
        'Áreas Centrais': 'orange',
        'Distribuídos': 'darkpurple',
        'Corredor Norte-Sul': 'darkblue',
        'Corredor Leste-Oeste': 'darkgreen',
        'Densidade Populacional': 'darkred'
    }
    
    for strategy_name, metrics in strategies.items():
        color = colors.get(strategy_name, 'blue')
        strategy_group = folium.FeatureGroup(name=f"{strategy_name}").add_to(m)
        
        warehouse_locations = {}
        
        for warehouse in metrics['warehouses']:
            location_key = f"{warehouse.lat:.6f}_{warehouse.lon:.6f}"
            offset = [0, 0]
            
            if location_key in warehouse_locations:
                offset = [0.002, 0.002]  
                
            warehouse_locations[location_key] = True
            
            icon_color = color if len(warehouse.assigned_deliveries) > 0 else 'lightgray'
            
            folium.Marker(
                location=[warehouse.lat + offset[0], warehouse.lon + offset[1]],
                popup=f"<b>{warehouse.name}</b><br>{strategy_name}<br>Entregas: {len(warehouse.assigned_deliveries)}",
                icon=folium.Icon(color=icon_color, icon='industry', prefix='fa')
            ).add_to(strategy_group)
            
            folium.Circle(
                location=[warehouse.lat, warehouse.lon],
                radius=5000,  
                color=color,
                fill=True,
                fill_opacity=0.1,
                popup=f"Área de cobertura para {warehouse.name}"
            ).add_to(strategy_group)
            
            for delivery in warehouse.assigned_deliveries:
                folium.PolyLine(
                    locations=[[warehouse.lat, warehouse.lon], [delivery.lat, delivery.lon]],
                    color=color,
                    weight=1.5,
                    opacity=0.5,
                    dash_array='5,5'
                ).add_to(strategy_group)
    
    folium.LayerControl(collapsed=False).add_to(m)
    
    return m

if __name__ == "__main__":
    compare_warehouse_strategies() 