# Test on Locust
```
pip install locust
pip install boto3
```

```
# change --host option to your endpoint name
locust -f sagemaker_test.py \
  -u 1 \
  --headless \
  --host='http://DEMO-2023-05-22-0416' \
  --stop-timeout 60 \
  -t 3m \
  --logfile=logfile.log \
  --csv=locust.csv \
  --csv-full-history \
  --reset-stats
```

```
# change --host option to your endpoint name
locust -f sagemaker_test.py
```
