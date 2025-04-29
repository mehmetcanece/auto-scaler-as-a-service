from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kubernetes import client, config



app = FastAPI()


#basemodel yaptık yani apiye post edecegimiz json semasi bu.
class HPA_Request(BaseModel):
    namespace: str
    deployment_name: str
    min_replicas: int #pod sayısı asla bunun altına dusemez
    max_replicas: int #pod sayısı asla bunun ustune cikamaz!!
    target_cpu_utilization_percentage: int
    
    
@app.post("/create-hpa")
def create_hpa(hpa_request: HPA_Request):
    try:
      # kubernetese config yukluyoruz.
      config.load_kube_config()
      
      #clientı olusturduk autoscale icin.
      api = client.AutoscalingV2Api()
      
      #hpa yı yani horizontal pod autoscalerını tanımlıyoruz
      hpa = client.V2HorizontalPodAutoscaler(
        metadata=client.V1ObjectMeta( #hpaya isim verdik
          name=f"{hpa_request.deployment_name}-hpa"
        ),
        spec=client.V2HorizontalPodAutoscalerSpec( #burası hangi podu olcekleyecegini ve esik degeri ne olacak vs. onları tanımlıyor.
          scale_target_ref= client.V2CrossVersionObjectReference(
            api_version="apps/v1",
            kind="Deployment",
            name=hpa_request.deployment_name
          ),
          min_replicas= hpa_request.min_replicas, 
          max_replicas=hpa_request.max_replicas,
          metrics=[
            client.V2ResourceMetricSource(
              name="cpu",
              target=client.V2MetricTarget(
                type="Utilization",
                average_utilization= hpa_request.target_cpu_utilization_percentage
              )
            )
          ]
        )
      )
      
      #kubernetese hpa objesi olusturucaz.
      
      api.create_namespaced_horizontal_pod_autoscaler(
        namespace= hpa_request.namespace,
        body= hpa
      )
      
      return {"message": "HPA created successfully!"}
    
    except Exception as e:
      raise HTTPException(status_code= 500)
  
    
      
