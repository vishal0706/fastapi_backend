import random
import string

from locust import HttpUser, events, task


def random_string(length=10):
    """Generate a random string of letters and digits"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))


class ApiUser(HttpUser):
    # wait_time = between(1, 2.5)  # Wait between 1 and 2.5 seconds between tasks
    # wait_time = constant_throughput(0.1)

    @task(1)
    def post_endpoint(self):
        headers = {'Content-Type': 'application/json'}  # Assuming the API accepts JSON
        # Generate a random email address
        random_email = f'{random_string()}@example.com'
        data = {'email': random_email, 'first_name': 'First', 'last_name': 'Last'}
        # Replace 'api/endpoint' with your API endpoint
        self.client.post('/api/v1/users/create', headers=headers, json=data)

    @task(4)
    def get_endpoint(self):
        query_params = {'page': 1, 'page_size': 10}
        # Replace 'api/endpoint' with your API endpoint for GET request
        self.client.get('/api/v1/auth/users/paginated', params=query_params)


# pylint: disable=too-many-arguments, unused-argument
# Define a failure callback
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    if exception:
        print(f'Request to {name} failed with exception {exception}')
        # sys.exit(1)
