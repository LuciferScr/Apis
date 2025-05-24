
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import pandas as pd

app = FastAPI(
    title="API de BINs",
    description="API para consultar información de BINs bancarios",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache para el DataFrame
df: Optional[pd.DataFrame] = None

def load_data() -> pd.DataFrame:
    """Carga los datos del archivo CSV"""
    global df
    if df is None:
        try:
            df = pd.read_csv("bins.csv")
            df['number'] = df['number'].astype(str)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error al cargar la base de datos: {str(e)}"
            )
    return df

@app.on_event("startup")
async def startup_event():
    """Carga los datos al iniciar la aplicación"""
    load_data()

@app.get("/", tags=["General"])
def read_root() -> Dict[str, str]:
    """Endpoint raíz que muestra información básica de la API"""
    return {
        "message": "API is running",
        "description": "API para consulta de BINs bancarios",
        "endpoints": "/ (root), /bin/{number} (consulta BIN), /bins/search (búsqueda), /stats (estadísticas)"
    }

@app.get("/bin/{number}", tags=["BINs"])
def get_bin(number: str = Path(..., min_length=6, max_length=8)) -> List[Dict]:
    """
    Obtiene la información de un BIN específico
    
    Args:
        number: Número de BIN (6-8 dígitos)
        
    Returns:
        Lista de coincidencias encontradas
    """
    data = load_data()
    result = data[data["number"].astype(str).str.strip('"') == number].iloc[0:1]
    
    if result.empty:
        raise HTTPException(
            status_code=404,
            detail="BIN no encontrado"
        )
    
    return result.to_dict(orient="records")

@app.get("/bins/search", tags=["BINs"])
def search_bins(
    country: Optional[str] = None,
    bank: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100)
) -> List[Dict]:
    """
    Búsqueda de BINs por país o banco
    
    Args:
        country: País a buscar
        bank: Banco a buscar
        limit: Límite de resultados (1-100)
        
    Returns:
        Lista de BINs que coinciden con los criterios
    """
    data = load_data()
    
    if country:
        data = data[data["country"].str.contains(country, case=False, na=False)]
    if bank:
        data = data[data["bank"].str.contains(bank, case=False, na=False)]
        
    if data.empty:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron resultados"
        )
        
    return data.head(limit).to_dict(orient="records")

@app.get("/stats", tags=["Estadísticas"])
def get_stats() -> Dict:
    """Obtiene estadísticas generales de la base de datos"""
    data = load_data()
    return {
        "total_bins": len(data),
        "countries": data["country"].nunique(),
        "banks": data["bank"].nunique(),
        "vendors": data["vendor"].nunique()
    }
