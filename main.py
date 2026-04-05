
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import json
import os


    
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

with open(os.path.join(DATA_DIR, "states.json")) as f:
    STATES: list[dict] = json.load(f)

with open(os.path.join(DATA_DIR, "full.json")) as f:
    FULL: list[dict] = json.load(f)

STATE_INDEX: dict[str, dict] = {s["state"]: s for s in FULL}
STATES_META: dict[str, dict] = {s["name"]: s for s in STATES}


class StateOut(BaseModel):
    name: str
    capital: str
    zone: str
    lga_count: int
    latitude: Optional[float]
    longitude: Optional[float]

class LGAOut(BaseModel):
    name: str
    state: str
    ward_count: int
    latitude: Optional[float]
    longitude: Optional[float]

class WardOut(BaseModel):
    name: str
    lga: str
    state: str
    latitude: Optional[float]
    longitude: Optional[float]

class DropdownOption(BaseModel):
    value: str
    label: str


app = FastAPI(
    title="Nigeria Location API",
    description="Cascading State → LGA → Ward dropdown API for Nigeria. "
                "Covers all 37 states, 780 LGAs, and 8,905 wards with coordinates.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Restrict to your domain in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dropdown_ui():
    """Serves the embeddable dropdown widget."""
    return open(os.path.join(BASE_DIR, "static", "index.html"), encoding="utf-8").read()


@app.get("/states", response_model=list[StateOut], tags=["States"])
async def list_states(zone: Optional[str] = Query(None, description="Filter by geopolitical zone")):
    """List all 37 Nigerian states (+ FCT), optionally filtered by zone."""
    result = STATES
    if zone:
        result = [s for s in result if s.get("zone", "").lower() == zone.lower()]
        if not result:
            raise HTTPException(status_code=404, detail=f"No states found for zone: {zone}")
    return [StateOut(
        name=s["name"], capital=s["capital"], zone=s["zone"],
        lga_count=s["lga_count"], latitude=s.get("latitude"), longitude=s.get("longitude")
    ) for s in result]

@app.get("/states/dropdown", response_model=list[DropdownOption], tags=["Dropdown"])
async def states_dropdown():
    """Returns states as value/label pairs — ready for <select> elements."""
    return [DropdownOption(value=s["name"], label=s["name"]) for s in STATES]

@app.get("/states/{state_name}", response_model=StateOut, tags=["States"])
async def get_state(state_name: str = Path(..., description="State name e.g. Lagos")):
    """Get metadata for a single state."""
    s = STATES_META.get(state_name)
    if not s:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    return StateOut(
        name=s["name"], capital=s["capital"], zone=s["zone"],
        lga_count=s["lga_count"], latitude=s.get("latitude"), longitude=s.get("longitude")
    )


@app.get("/states/{state_name}/lgas", response_model=list[LGAOut], tags=["LGAs"])
async def list_lgas(state_name: str = Path(..., description="State name e.g. Lagos")):
    """List all LGAs in a given state."""
    state = STATE_INDEX.get(state_name)
    if not state:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    return [LGAOut(
        name=lga["name"], state=state_name,
        ward_count=len(lga["wards"]),
        latitude=lga.get("latitude"), longitude=lga.get("longitude")
    ) for lga in state["lgas"]]

@app.get("/states/{state_name}/lgas/dropdown", response_model=list[DropdownOption], tags=["Dropdown"])
async def lgas_dropdown(state_name: str = Path(..., description="State name e.g. Lagos")):
    """Returns LGAs for a state as value/label pairs — ready for <select> elements."""
    state = STATE_INDEX.get(state_name)
    if not state:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    return [DropdownOption(value=lga["name"], label=lga["name"]) for lga in state["lgas"]]

@app.get("/states/{state_name}/lgas/{lga_name}", response_model=LGAOut, tags=["LGAs"])
async def get_lga(
    state_name: str = Path(..., description="State name"),
    lga_name: str = Path(..., description="LGA name"),
):
    """Get metadata for a single LGA."""
    state = STATE_INDEX.get(state_name)
    if not state:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    lga = next((l for l in state["lgas"] if l["name"] == lga_name), None)
    if not lga:
        raise HTTPException(status_code=404, detail=f"LGA not found: {lga_name}")
    return LGAOut(
        name=lga["name"], state=state_name,
        ward_count=len(lga["wards"]),
        latitude=lga.get("latitude"), longitude=lga.get("longitude")
    )


@app.get("/states/{state_name}/lgas/{lga_name}/wards", response_model=list[WardOut], tags=["Wards"])
async def list_wards(
    state_name: str = Path(..., description="State name"),
    lga_name: str = Path(..., description="LGA name"),
):
    """List all wards in a given LGA."""
    state = STATE_INDEX.get(state_name)
    if not state:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    lga = next((l for l in state["lgas"] if l["name"] == lga_name), None)
    if not lga:
        raise HTTPException(status_code=404, detail=f"LGA not found: {lga_name}")
    return [WardOut(
        name=w["name"], lga=lga_name, state=state_name,
        latitude=w.get("latitude"), longitude=w.get("longitude")
    ) for w in lga["wards"]]

@app.get("/states/{state_name}/lgas/{lga_name}/wards/dropdown", response_model=list[DropdownOption], tags=["Dropdown"])
async def wards_dropdown(
    state_name: str = Path(..., description="State name"),
    lga_name: str = Path(..., description="LGA name"),
):
    """Returns wards for an LGA as value/label pairs — ready for <select> elements."""
    state = STATE_INDEX.get(state_name)
    if not state:
        raise HTTPException(status_code=404, detail=f"State not found: {state_name}")
    lga = next((l for l in state["lgas"] if l["name"] == lga_name), None)
    if not lga:
        raise HTTPException(status_code=404, detail=f"LGA not found: {lga_name}")
    return [DropdownOption(value=w["name"], label=w["name"]) for w in lga["wards"]]


@app.get("/search", tags=["Search"])
async def search(
    q: str = Query(..., min_length=2, description="Search term"),
    type: Optional[str] = Query(None, description="Filter by type: state, lga, ward"),
):
    """Full-text search across states, LGAs, and wards."""
    q_lower = q.lower()
    results = []

    for state_data in FULL:
        # Match state
        if (not type or type == "state") and q_lower in state_data["state"].lower():
            results.append({"type": "state", "name": state_data["state"], "state": state_data["state"]})

        for lga in state_data["lgas"]:
            # Match LGA
            if (not type or type == "lga") and q_lower in lga["name"].lower():
                results.append({"type": "lga", "name": lga["name"], "state": state_data["state"]})

            # Match ward
            if not type or type == "ward":
                for ward in lga["wards"]:
                    if q_lower in ward["name"].lower():
                        results.append({
                            "type": "ward",
                            "name": ward["name"],
                            "lga": lga["name"],
                            "state": state_data["state"],
                            "latitude": ward.get("latitude"),
                            "longitude": ward.get("longitude"),
                        })

    return {"query": q, "count": len(results), "results": results[:50]}


@app.get("/stats", tags=["Info"])
async def stats():
    """Dataset summary statistics."""
    total_lgas = sum(len(s["lgas"]) for s in FULL)
    total_wards = sum(len(l["wards"]) for s in FULL for l in s["lgas"])
    zones = {}
    for s in STATES:
        zone = s.get("zone", "Unknown")
        zones[zone] = zones.get(zone, 0) + 1
    return {
        "states": len(STATES),
        "lgas": total_lgas,
        "wards": total_wards,
        "zones": zones,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
