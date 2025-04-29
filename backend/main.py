from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kubernetes import client, config



app = FastAPI()



class HPA_Request(BaseModel):
    namespace: str
    deployment_name: str
    min_replicas: int
    max_replicas: int
    target_cpu_utilization_percentage: int
    
    
@app.post("/create-hpa")
def create_hpa(hpa_request: HPA_Request):
  
      
