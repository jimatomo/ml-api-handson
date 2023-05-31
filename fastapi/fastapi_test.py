import time
import inspect
import requests
from locust import task
from locust import TaskSet, task, events
from locust.contrib.fasthttp import FastHttpUser
from locust import task, events, constant


def stopwatch(func):
    def wrapper(*args, **kwargs):
        previous_frame = inspect.currentframe().f_back
        _, _, task_name, task_func_name, _ = inspect.getframeinfo(previous_frame)
        task_func_name = task_func_name[0].split(".")[-1].split("(")[0]

        start = time.time()
        result = None

        try:
            result = func(*args, **kwargs)
            total = int((time.time() - start) * 1000)

        except Exception as e:
            events.request.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
                exception=e,
            )
        else:
            events.request.fire(
                request_type=task_name,
                name=task_func_name,
                response_time=total,
                response_length=len(result),
            )
        return result

    return wrapper


class ProtocolClient:
    def __init__(self, host):
        self.hosturl = host
        self.content_type = "application/json"
        self.payload = '{"data": [{"PassengerId": 892, "Pclass": 3, "Name": "Kelly, Mr. James", "Sex": "male", "Age": 34.5, "SibSp": 0, "Parch": 0, "Ticket": 330911, "Fare": 7.8292, "Cabin": "", "Embarked": "Q"}, {"PassengerId": 893, "Pclass": 3, "Name": "Wilkes, Mrs. James (Ellen Needs)", "Sex": "female", "Age": 47, "SibSp": 1, "Parch": 0, "Ticket": 363272, "Fare": 7, "Cabin": "", "Embarked": "S"}]}'

    @stopwatch
    def sagemaker_client_invoke_endpoint(self):
        response = requests.post(
            self.hosturl,
            data=self.payload
        )
        return response.json()


class ProtocolLocust(FastHttpUser):
    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = ProtocolClient(self.host)
        self.client._locust_environment = self.environment


class ProtocolTasks(TaskSet):
    @task
    def custom_protocol_boto3(self):
        self.client.sagemaker_client_invoke_endpoint()


class ProtocolUser(ProtocolLocust):
    wait_time = constant(0)
    tasks = [ProtocolTasks]