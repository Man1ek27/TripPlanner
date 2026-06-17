import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from neo4j import GraphDatabase
from pydantic import BaseModel, Field


NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
ALLOWED_ORIGINS = [
    origin
    for origin in (value.strip() for value in os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(","))
    if origin
]

# Support opening index.html directly via file:// (browser sends Origin: null).
if "null" not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append("null")


driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


class RouteRequest(BaseModel):
    start: str = Field(..., min_length=2)
    end: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    driver.close()


app = FastAPI(title="Generator Roadtripów Tematycznych", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/locations")
def get_locations() -> List[Dict[str, Any]]:
    query = """
    MATCH (l:Location)
    RETURN l.name AS name, l.lat AS lat, l.lng AS lng, l.description AS description
    ORDER BY l.name
    """
    with driver.session() as session:
        rows = session.run(query)
        return [dict(row) for row in rows]


@app.get("/api/categories")
def get_categories() -> List[str]:
    query = """
    MATCH (c:Category)
    RETURN c.name AS name
    ORDER BY c.name
    """
    with driver.session() as session:
        rows = session.run(query)
        return [row["name"] for row in rows]


@app.post("/api/route")
def get_route(payload: RouteRequest) -> Dict[str, Any]:
    if payload.start == payload.end:
        raise HTTPException(status_code=400, detail="Punkt startowy i końcowy muszą być różne.")

    query = """
    MATCH (start:Location {name: $start})
    MATCH (destination:Location {name: $end})
    MATCH (category:Category {name: $category})
    MATCH (waypoint:Location)-[:BELONGS_TO]->(category)

    CALL {
      WITH start, waypoint
      MATCH path_to_waypoint = (start)-[:ROAD_TO*1..12]->(waypoint)
      WITH path_to_waypoint,
           reduce(distance = 0.0, road IN relationships(path_to_waypoint) | distance + road.distance_km) AS segment_distance_1
      ORDER BY segment_distance_1 ASC
      LIMIT 1
      RETURN path_to_waypoint, segment_distance_1
    }

    CALL {
      WITH waypoint, destination
      MATCH path_to_destination = (waypoint)-[:ROAD_TO*1..12]->(destination)
      WITH path_to_destination,
           reduce(distance = 0.0, road IN relationships(path_to_destination) | distance + road.distance_km) AS segment_distance_2
      ORDER BY segment_distance_2 ASC
      LIMIT 1
      RETURN path_to_destination, segment_distance_2
    }

    WITH waypoint,
         path_to_waypoint,
         path_to_destination,
         segment_distance_1 + segment_distance_2 AS total_distance
    ORDER BY total_distance ASC
    LIMIT 1

    WITH nodes(path_to_waypoint) + tail(nodes(path_to_destination)) AS route_nodes, total_distance
    RETURN [node IN route_nodes | {
      name: node.name,
      lat: node.lat,
      lng: node.lng,
      description: node.description
    }] AS route,
    total_distance
    """

    with driver.session() as session:
        record = session.run(
            query,
            start=payload.start,
            end=payload.end,
            category=payload.category,
        ).single()

    if not record:
        raise HTTPException(status_code=404, detail="Nie znaleziono trasy spełniającej kryteria.")

    return {
        "route": record["route"],
        "total_distance_km": round(record["total_distance"], 1),
    }
