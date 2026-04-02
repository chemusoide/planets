import sqlite3
from pathlib import Path


PLANET_SEED_DATA = [
    {
        "id": 1,
        "position": 1,
        "category": "solar-system",
        "name": "Mercurio",
        "emoji": "☄️",
        "climate": "Extremo",
        "terrain": "Rocoso",
        "population": "0",
        "description": "Mercurio gira muy cerca del Sol y por eso vive entre mucho calor y mucho frío.",
        "kid_summary": "Es pequeño, veloz y parece una piedra brillante dando vueltas alrededor del Sol.",
        "fun_fact": "Un año en Mercurio dura solo 88 días terrestres.",
        "moons": 0,
        "day_length_hours": 1407.6,
        "distance_from_sun_million_km": 57.9,
        "wikipedia_title": "Mercurio_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 2,
        "position": 2,
        "category": "solar-system",
        "name": "Venus",
        "emoji": "🌕",
        "climate": "Muy caliente",
        "terrain": "Volcánico",
        "population": "0",
        "description": "Venus está cubierto por nubes espesas y guarda un calor enorme bajo su atmósfera.",
        "kid_summary": "Brilla mucho en el cielo, pero no sería un lugar cómodo para pasear.",
        "fun_fact": "Venus gira tan raro que el Sol parece salir por el oeste.",
        "moons": 0,
        "day_length_hours": 5832.5,
        "distance_from_sun_million_km": 108.2,
        "wikipedia_title": "Venus_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 3,
        "position": 3,
        "category": "solar-system",
        "name": "Tierra",
        "emoji": "🌍",
        "climate": "Templado",
        "terrain": "Océanos y continentes",
        "population": "8000000000",
        "description": "La Tierra combina agua, aire y temperatura adecuada para albergar mucha vida.",
        "kid_summary": "Es nuestro hogar y el único planeta que conocemos lleno de vida.",
        "fun_fact": "Más del 70 % de la superficie terrestre está cubierta por agua.",
        "moons": 1,
        "day_length_hours": 24,
        "distance_from_sun_million_km": 149.6,
        "wikipedia_title": "Tierra",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 4,
        "position": 4,
        "category": "solar-system",
        "name": "Marte",
        "emoji": "🔴",
        "climate": "Frío y seco",
        "terrain": "Desértico",
        "population": "0",
        "description": "Marte tiene un color rojizo, mucho polvo y pistas de que en el pasado pudo tener agua.",
        "kid_summary": "Es el planeta rojo y uno de los favoritos para imaginar futuras misiones humanas.",
        "fun_fact": "En Marte está el monte Olimpo, el volcán más grande conocido del sistema solar.",
        "moons": 2,
        "day_length_hours": 24.6,
        "distance_from_sun_million_km": 227.9,
        "wikipedia_title": "Marte_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 5,
        "position": 5,
        "category": "solar-system",
        "name": "Júpiter",
        "emoji": "🟠",
        "climate": "Gaseoso y tormentoso",
        "terrain": "Gigante gaseoso",
        "population": "0",
        "description": "Júpiter es el planeta más grande del sistema solar y está cubierto por nubes y grandes tormentas.",
        "kid_summary": "Es tan enorme que dentro cabrían muchísimas Tierras.",
        "fun_fact": "La Gran Mancha Roja es una tormenta gigante que lleva activa siglos.",
        "moons": 95,
        "day_length_hours": 9.9,
        "distance_from_sun_million_km": 778.5,
        "wikipedia_title": "Júpiter_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 6,
        "position": 6,
        "category": "solar-system",
        "name": "Saturno",
        "emoji": "🪐",
        "climate": "Gaseoso y ventoso",
        "terrain": "Gigante gaseoso con anillos",
        "population": "0",
        "description": "Saturno es famoso por sus anillos brillantes, formados por hielo, roca y polvo.",
        "kid_summary": "Parece llevar un aro enorme que lo hace inconfundible.",
        "fun_fact": "Saturno podría flotar en una bañera gigantesca porque su densidad es muy baja.",
        "moons": 146,
        "day_length_hours": 10.7,
        "distance_from_sun_million_km": 1432.0,
        "wikipedia_title": "Saturno_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 7,
        "position": 7,
        "category": "solar-system",
        "name": "Urano",
        "emoji": "🧊",
        "climate": "Muy frío",
        "terrain": "Gigante helado",
        "population": "0",
        "description": "Urano es un gigante helado con un color azul verdoso y una inclinación muy curiosa.",
        "kid_summary": "Rueda casi tumbado, como si girara acostado alrededor del Sol.",
        "fun_fact": "Su eje está tan inclinado que sus estaciones son extremas y larguísimas.",
        "moons": 28,
        "day_length_hours": 17.2,
        "distance_from_sun_million_km": 2867.0,
        "wikipedia_title": "Urano_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 8,
        "position": 8,
        "category": "solar-system",
        "name": "Neptuno",
        "emoji": "🔵",
        "climate": "Muy frío y ventoso",
        "terrain": "Gigante helado",
        "population": "0",
        "description": "Neptuno es un mundo azul profundo con algunos de los vientos más rápidos conocidos.",
        "kid_summary": "Está muy lejos del Sol y parece un planeta azul intenso.",
        "fun_fact": "Sus vientos pueden superar los 2000 kilómetros por hora.",
        "moons": 16,
        "day_length_hours": 16.1,
        "distance_from_sun_million_km": 4515.0,
        "wikipedia_title": "Neptuno_(planeta)",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 101,
        "position": 1,
        "category": "exoplanets",
        "name": "Próxima Centauri b",
        "emoji": "✨",
        "climate": "Desconocido",
        "terrain": "No confirmado",
        "population": "0",
        "description": "Próxima Centauri b es un exoplaneta que gira alrededor de la estrella más cercana al Sol.",
        "kid_summary": "Es uno de los mundos lejanos más famosos porque está relativamente cerca de nosotros.",
        "fun_fact": "Está fuera del sistema solar, pero en términos espaciales sigue siendo un vecino cercano.",
        "moons": 0,
        "day_length_hours": 268.0,
        "distance_from_sun_million_km": 40100000.0,
        "wikipedia_title": "Próxima_Centauri_b",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 102,
        "position": 2,
        "category": "exoplanets",
        "name": "Kepler-22b",
        "emoji": "🌌",
        "climate": "Desconocido",
        "terrain": "No confirmado",
        "population": "0",
        "description": "Kepler-22b fue uno de los primeros exoplanetas famosos encontrados en una zona donde podría existir agua líquida.",
        "kid_summary": "Se hizo conocido porque podría estar en una región amable para el agua.",
        "fun_fact": "Se descubrió gracias al telescopio espacial Kepler observando pequeñas sombras en una estrella lejana.",
        "moons": 0,
        "day_length_hours": 6960.0,
        "distance_from_sun_million_km": 600000000.0,
        "wikipedia_title": "Kepler-22b",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
    {
        "id": 103,
        "position": 3,
        "category": "exoplanets",
        "name": "TRAPPIST-1e",
        "emoji": "💫",
        "climate": "Desconocido",
        "terrain": "No confirmado",
        "population": "0",
        "description": "TRAPPIST-1e forma parte de un sistema con varios planetas rocosos y despierta mucho interés científico.",
        "kid_summary": "Pertenece a una familia espacial muy curiosa con varios planetas juntos.",
        "fun_fact": "El sistema TRAPPIST-1 tiene varios mundos de tamaño parecido al de la Tierra.",
        "moons": 0,
        "day_length_hours": 147.0,
        "distance_from_sun_million_km": 390000000.0,
        "wikipedia_title": "TRAPPIST-1e",
        "source_summary": "",
        "source_description": "",
        "source_page_url": "",
        "image_url": "",
        "last_synced_at": None,
    },
]

PLANET_OPTIONAL_COLUMNS: dict[str, str] = {
    "category": "TEXT NOT NULL DEFAULT 'solar-system'",
    "wikipedia_title": "TEXT NOT NULL DEFAULT ''",
    "source_summary": "TEXT NOT NULL DEFAULT ''",
    "source_description": "TEXT NOT NULL DEFAULT ''",
    "source_page_url": "TEXT NOT NULL DEFAULT ''",
    "image_url": "TEXT NOT NULL DEFAULT ''",
    "last_synced_at": "TEXT",
}


def get_connection(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_planets_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY,
            position INTEGER NOT NULL,
            category TEXT NOT NULL DEFAULT 'solar-system',
            name TEXT NOT NULL,
            emoji TEXT NOT NULL,
            climate TEXT NOT NULL,
            terrain TEXT NOT NULL,
            population TEXT NOT NULL,
            description TEXT NOT NULL,
            kid_summary TEXT NOT NULL,
            fun_fact TEXT NOT NULL,
            moons INTEGER NOT NULL,
            day_length_hours REAL NOT NULL,
            distance_from_sun_million_km REAL NOT NULL,
            wikipedia_title TEXT NOT NULL DEFAULT '',
            source_summary TEXT NOT NULL DEFAULT '',
            source_description TEXT NOT NULL DEFAULT '',
            source_page_url TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL DEFAULT '',
            last_synced_at TEXT
        )
        """
    )

    existing_columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(planets)").fetchall()
    }
    for column_name, column_definition in PLANET_OPTIONAL_COLUMNS.items():
        if column_name not in existing_columns:
            connection.execute(
                f"ALTER TABLE planets ADD COLUMN {column_name} {column_definition}"
            )


def _ensure_sync_status_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sync_status (
            id INTEGER PRIMARY KEY CHECK(id = 1),
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL,
            last_attempted_at TEXT,
            last_success_at TEXT,
            last_status TEXT NOT NULL DEFAULT 'never',
            last_message TEXT NOT NULL DEFAULT 'Pendiente de sincronización.',
            records_processed INTEGER NOT NULL DEFAULT 0,
            using_cached_data INTEGER NOT NULL DEFAULT 1
        )
        """
    )


def _seed_planets(connection: sqlite3.Connection) -> None:
    total = connection.execute("SELECT COUNT(*) FROM planets").fetchone()[0]
    if total == 0:
        connection.executemany(
            """
            INSERT INTO planets (
                id, position, name, emoji, climate, terrain, population,
                category,
                description, kid_summary, fun_fact, moons,
                day_length_hours, distance_from_sun_million_km,
                wikipedia_title, source_summary, source_description,
                source_page_url, image_url, last_synced_at
            ) VALUES (
                :id, :position, :name, :emoji, :climate, :terrain, :population,
                :category,
                :description, :kid_summary, :fun_fact, :moons,
                :day_length_hours, :distance_from_sun_million_km,
                :wikipedia_title, :source_summary, :source_description,
                :source_page_url, :image_url, :last_synced_at
            )
            """,
            PLANET_SEED_DATA,
        )
    for planet in PLANET_SEED_DATA:
        connection.execute(
            """
            INSERT OR IGNORE INTO planets (
                id, position, name, emoji, climate, terrain, population,
                category, description, kid_summary, fun_fact, moons,
                day_length_hours, distance_from_sun_million_km,
                wikipedia_title, source_summary, source_description,
                source_page_url, image_url, last_synced_at
            ) VALUES (
                :id, :position, :name, :emoji, :climate, :terrain, :population,
                :category, :description, :kid_summary, :fun_fact, :moons,
                :day_length_hours, :distance_from_sun_million_km,
                :wikipedia_title, :source_summary, :source_description,
                :source_page_url, :image_url, :last_synced_at
            )
            """,
            planet,
        )
        connection.execute(
            """
            UPDATE planets
            SET category = ?,
                wikipedia_title = ?,
                source_summary = COALESCE(source_summary, ''),
                source_description = COALESCE(source_description, ''),
                source_page_url = COALESCE(source_page_url, ''),
                image_url = COALESCE(image_url, '')
            WHERE id = ?
            """,
            (planet["category"], planet["wikipedia_title"], planet["id"]),
        )


def initialize_database(database_path: Path, source_name: str, source_url: str) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(database_path) as connection:
        _ensure_planets_table(connection)
        _ensure_sync_status_table(connection)
        _seed_planets(connection)
        connection.execute(
            """
            INSERT INTO sync_status (id, source_name, source_url)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                source_name = excluded.source_name,
                source_url = excluded.source_url
            """,
            (source_name, source_url),
        )
