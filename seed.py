import math
import os
from typing import Dict, List, Set, Tuple

from neo4j import GraphDatabase


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


CATEGORIES = [
    "History",
    "Nature",
    "Food",
    "CityBreak",
]


LOCATIONS: List[Dict[str, object]] = [
    {"name": "Warszawa Stare Miasto", "lat": 52.2497, "lng": 21.0122, "description": "Historyczne centrum Warszawy wpisane na listę UNESCO.", "category": "History"},
    {"name": "Zamek Królewski na Wawelu", "lat": 50.0540, "lng": 19.9353, "description": "Symbol dawnej potęgi Polski w Krakowie.", "category": "History"},
    {"name": "Zamek Książ", "lat": 50.8422, "lng": 16.2936, "description": "Monumentalny zamek na Dolnym Śląsku.", "category": "History"},
    {"name": "Malbork Zamek", "lat": 54.0390, "lng": 19.0266, "description": "Największy ceglany zamek świata.", "category": "History"},
    {"name": "Kopalnia Soli Wieliczka", "lat": 49.9875, "lng": 20.0551, "description": "Podziemne komory i rzeźby z soli.", "category": "History"},
    {"name": "Muzeum Auschwitz-Birkenau", "lat": 50.0266, "lng": 19.2033, "description": "Miejsce pamięci i muzeum historyczne.", "category": "History"},
    {"name": "Zamek w Łańcucie", "lat": 50.0684, "lng": 22.2314, "description": "Rezydencja magnacka z pięknym parkiem.", "category": "History"},
    {"name": "Twierdza Srebrna Góra", "lat": 50.5684, "lng": 16.6468, "description": "Górska twierdza z XVIII wieku.", "category": "History"},
    {"name": "Zamek Czocha", "lat": 51.0300, "lng": 15.3086, "description": "Malowniczy zamek nad jeziorem Leśniańskim.", "category": "History"},
    {"name": "Biskupin Rezerwat", "lat": 52.7876, "lng": 17.7394, "description": "Archeologiczna osada obronna.", "category": "History"},
    {"name": "Jasna Góra", "lat": 50.8137, "lng": 19.1203, "description": "Sanktuarium i klasztor paulinów w Częstochowie.", "category": "History"},
    {"name": "Zamek Piastowski w Legnicy", "lat": 51.2070, "lng": 16.1609, "description": "Jedna z najstarszych warowni na Śląsku.", "category": "History"},
    {"name": "Muzeum Zamoyskich w Kozłówce", "lat": 51.7163, "lng": 22.2481, "description": "Pałac i kolekcja sztuki na Lubelszczyźnie.", "category": "History"},
    {"name": "Ratusz Głównego Miasta Gdańsk", "lat": 54.3487, "lng": 18.6529, "description": "Perła architektury hanzeatyckiej.", "category": "History"},

    {"name": "Morskie Oko", "lat": 49.1975, "lng": 20.0709, "description": "Najbardziej znane jezioro tatrzańskie.", "category": "Nature"},
    {"name": "Kasprowy Wierch", "lat": 49.2317, "lng": 19.9815, "description": "Szczyt z panoramą Tatr i Podhala.", "category": "Nature"},
    {"name": "Bieszczady Połonina Wetlińska", "lat": 49.1539, "lng": 22.5331, "description": "Widokowy grzbiet bieszczadzki.", "category": "Nature"},
    {"name": "Słowiński Park Narodowy", "lat": 54.7241, "lng": 17.2422, "description": "Ruchome wydmy nad Bałtykiem.", "category": "Nature"},
    {"name": "Białowieski Park Narodowy", "lat": 52.7031, "lng": 23.8657, "description": "Pierwotna puszcza i żubry.", "category": "Nature"},
    {"name": "Karkonosze Śnieżka", "lat": 50.7365, "lng": 15.7396, "description": "Najwyższy szczyt Sudetów.", "category": "Nature"},
    {"name": "Jezioro Czorsztyńskie", "lat": 49.4389, "lng": 20.3125, "description": "Górskie jezioro między zamkami.", "category": "Nature"},
    {"name": "Dolina Baryczy", "lat": 51.4772, "lng": 17.2929, "description": "Stawy milickie i ostoja ptaków.", "category": "Nature"},
    {"name": "Pieniny Trzy Korony", "lat": 49.4151, "lng": 20.4148, "description": "Wapienne turnie z widokiem na Dunajec.", "category": "Nature"},
    {"name": "Roztoczański Park Narodowy", "lat": 50.6003, "lng": 22.9781, "description": "Lasy, stawy i koniki polskie.", "category": "Nature"},
    {"name": "Mazury Giżycko", "lat": 54.0381, "lng": 21.7644, "description": "Kraina wielkich jezior i żagli.", "category": "Nature"},
    {"name": "Ojcowski Park Narodowy", "lat": 50.2124, "lng": 19.8237, "description": "Dolina Prądnika i wapienne ostańce.", "category": "Nature"},
    {"name": "Park Narodowy Ujście Warty", "lat": 52.5928, "lng": 14.7089, "description": "Rozlewiska i bogactwo awifauny.", "category": "Nature"},
    {"name": "Góry Stołowe Szczeliniec", "lat": 50.4842, "lng": 16.3398, "description": "Skalne labirynty Gór Stołowych.", "category": "Nature"},

    {"name": "Hala Koszyki Warszawa", "lat": 52.2222, "lng": 21.0088, "description": "Nowoczesny food hall z kuchniami świata.", "category": "Food"},
    {"name": "Stary Kleparz Kraków", "lat": 50.0675, "lng": 19.9413, "description": "Targ z lokalnymi produktami i przekąskami.", "category": "Food"},
    {"name": "Piwnica Świdnicka Wrocław", "lat": 51.1099, "lng": 17.0326, "description": "Legendarna restauracja na rynku.", "category": "Food"},
    {"name": "Targ Rybny Gdańsk", "lat": 54.3534, "lng": 18.6605, "description": "Nadmorska strefa smaków i restauracji.", "category": "Food"},
    {"name": "Manufaktura Smaku Łódź", "lat": 51.7773, "lng": 19.4486, "description": "Kulinarna przestrzeń w dawnych zakładach.", "category": "Food"},
    {"name": "Jarmark Kaszubski Kościerzyna", "lat": 54.1217, "lng": 17.9819, "description": "Regionalne smaki i tradycyjne wypieki.", "category": "Food"},
    {"name": "Browary Poznań", "lat": 52.4098, "lng": 16.9286, "description": "Strefa restauracyjna i kuchnia wielkopolska.", "category": "Food"},
    {"name": "Szczeciński Pasztecik", "lat": 53.4285, "lng": 14.5528, "description": "Kultowe miejsce street food w Szczecinie.", "category": "Food"},
    {"name": "Karczma Swojskie Jadło Zakopane", "lat": 49.2987, "lng": 19.9496, "description": "Podhalańskie dania regionalne.", "category": "Food"},
    {"name": "Cepelin Wilno Smaki Białystok", "lat": 53.1325, "lng": 23.1688, "description": "Kuchnia podlaska i kresowa.", "category": "Food"},
    {"name": "Restauracja Rynek Lublin", "lat": 51.2465, "lng": 22.5684, "description": "Nowoczesna kuchnia lubelska.", "category": "Food"},
    {"name": "Pierogarnia Toruń", "lat": 53.0138, "lng": 18.5984, "description": "Pierogi i tradycyjne wypieki.", "category": "Food"},
    {"name": "Zagroda Smaków Rzeszów", "lat": 50.0413, "lng": 21.9990, "description": "Kuchnia podkarpacka w centrum miasta.", "category": "Food"},
    {"name": "Rynek Smaków Katowice", "lat": 50.2599, "lng": 19.0216, "description": "Śląska kuchnia i nowoczesne bistro.", "category": "Food"},

    {"name": "Warszawa Centrum", "lat": 52.2298, "lng": 21.0118, "description": "Nowoczesne centrum biznesowo-kulturalne stolicy.", "category": "CityBreak"},
    {"name": "Kraków Rynek Główny", "lat": 50.0619, "lng": 19.9373, "description": "Największy średniowieczny rynek w Europie.", "category": "CityBreak"},
    {"name": "Wrocław Ostrów Tumski", "lat": 51.1147, "lng": 17.0466, "description": "Najstarsza część miasta nad Odrą.", "category": "CityBreak"},
    {"name": "Gdańsk Długie Pobrzeże", "lat": 54.3482, "lng": 18.6570, "description": "Nabrzeże Motławy i Żuraw.", "category": "CityBreak"},
    {"name": "Poznań Stary Rynek", "lat": 52.4081, "lng": 16.9342, "description": "Kolorowe kamienice i koziołki.", "category": "CityBreak"},
    {"name": "Łódź Piotrkowska", "lat": 51.7592, "lng": 19.4560, "description": "Najdłuższy handlowy deptak w Polsce.", "category": "CityBreak"},
    {"name": "Szczecin Wały Chrobrego", "lat": 53.4306, "lng": 14.5654, "description": "Tarasy widokowe nad Odrą.", "category": "CityBreak"},
    {"name": "Lublin Stare Miasto", "lat": 51.2481, "lng": 22.5715, "description": "Klimatyczna starówka i Brama Krakowska.", "category": "CityBreak"},
    {"name": "Białystok Pałac Branickich", "lat": 53.1294, "lng": 23.1595, "description": "Barokowa rezydencja i ogrody.", "category": "CityBreak"},
    {"name": "Bydgoszcz Wyspa Młyńska", "lat": 53.1235, "lng": 18.0018, "description": "Miejski azyl nad Brdą.", "category": "CityBreak"},
    {"name": "Toruń Starówka", "lat": 53.0102, "lng": 18.6044, "description": "Gotyckie zabytki i pierniki.", "category": "CityBreak"},
    {"name": "Rzeszów Rynek", "lat": 50.0379, "lng": 22.0047, "description": "Historyczny rynek i podziemia.", "category": "CityBreak"},
    {"name": "Katowice Strefa Kultury", "lat": 50.2662, "lng": 19.0258, "description": "Nowoczesna dzielnica kultury na Śląsku.", "category": "CityBreak"},
    {"name": "Olsztyn Starówka", "lat": 53.7784, "lng": 20.4801, "description": "Warmiańska starówka i zamek kapituły.", "category": "CityBreak"},
]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def build_roads(locations: List[Dict[str, object]]) -> List[Tuple[str, str, float, int]]:
    index = {loc["name"]: loc for loc in locations}
    roads_undirected: Set[Tuple[str, str]] = set()

    for loc in locations:
        from_name = str(loc["name"])
        distances = []
        for other in locations:
            to_name = str(other["name"])
            if from_name == to_name:
                continue
            distance = haversine_km(float(loc["lat"]), float(loc["lng"]), float(other["lat"]), float(other["lng"]))
            distances.append((distance, to_name))
        distances.sort(key=lambda item: item[0])

        for _, neighbor_name in distances[:3]:
            edge = tuple(sorted((from_name, neighbor_name)))
            roads_undirected.add(edge)

    roads: List[Tuple[str, str, float, int]] = []
    for start_name, end_name in sorted(roads_undirected):
        start = index[start_name]
        end = index[end_name]
        distance = round(haversine_km(float(start["lat"]), float(start["lng"]), float(end["lat"]), float(end["lng"])), 1)
        duration = int(round((distance / 70) * 60 + 12))
        roads.append((start_name, end_name, distance, duration))
    return roads


def seed_database() -> None:
    roads = build_roads(LOCATIONS)
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)) as driver:
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

            for category in CATEGORIES:
                session.run(
                    "CREATE (:Category {name: $name})",
                    name=category,
                )

            for loc in LOCATIONS:
                session.run(
                    """
                    CREATE (:Location {
                        name: $name,
                        lat: $lat,
                        lng: $lng,
                        description: $description
                    })
                    """,
                    name=loc["name"],
                    lat=loc["lat"],
                    lng=loc["lng"],
                    description=loc["description"],
                )

                session.run(
                    """
                    MATCH (location:Location {name: $location_name})
                    MATCH (category:Category {name: $category_name})
                    CREATE (location)-[:BELONGS_TO]->(category)
                    """,
                    location_name=loc["name"],
                    category_name=loc["category"],
                )

            for start_name, end_name, distance, duration in roads:
                session.run(
                    """
                    MATCH (start:Location {name: $start_name})
                    MATCH (end:Location {name: $end_name})
                    CREATE (start)-[:ROAD_TO {distance_km: $distance_km, duration_min: $duration_min}]->(end)
                    CREATE (end)-[:ROAD_TO {distance_km: $distance_km, duration_min: $duration_min}]->(start)
                    """,
                    start_name=start_name,
                    end_name=end_name,
                    distance_km=distance,
                    duration_min=duration,
                )

            location_count = session.run("MATCH (l:Location) RETURN count(l) AS count").single()["count"]
            road_count = session.run("MATCH (:Location)-[r:ROAD_TO]->(:Location) RETURN count(r) AS count").single()["count"]
            print(f"Węzły Location: {location_count}")
            print(f"Relacje ROAD_TO: {road_count}")
            if location_count < 50 or road_count <= 120:
                raise RuntimeError("Graf nie spełnia wymagań minimalnych (>=50 lokalizacji i >120 dróg).")


if __name__ == "__main__":
    seed_database()
