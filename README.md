gcloud builds submit --tag gcr.io/mantenimientopredictivo-407907/mantenimiento-ml6  --project=mantenimientopredictivo-407907

gcloud run deploy --image gcr.io/mantenimientopredictivo-407907/mantenimiento-ml6 --platform managed  --project=mantenimientopredictivo-407907       --allow-unauthenticated 


git remote add origin https://github.com/MarcoTroya22/mantenimientopredictivo-depliegue-streamlit_nube.git
"# mantenimientopredictivo-ML"  
