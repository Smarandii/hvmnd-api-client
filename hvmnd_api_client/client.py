import pytz
import hashlib
import logging
import datetime
import requests


class APIClient:
    def __init__(self, base_url: str):
        """
        Initialize the API client.

        Parameters:
            base_url (str): The base URL of the API (e.g., 'http://localhost:8080').
        """
        self.base_url = base_url
        self.logger = logging.getLogger("hvmnd_api_client")

    def get_nodes(
        self,
        id_: int = None,
        renter: int = None,
        status: str = None,
        any_desk_address: str = None,
        software: str = None
    ):
        """
        Retrieve nodes based on provided filters.

        Parameters:
            id_ (int): Node ID.
            renter (int): Renter ID. If 'non_null', returns nodes with a non-null renter.
            status (str): Node status.
            any_desk_address (str): AnyDesk address.
            software (str): Software name to filter nodes that have it installed.

        Returns:
            List of nodes matching the criteria.
        """
        url = f"{self.base_url}/nodes"
        params = {
            'id': id_,
            'renter': renter,
            'status': status,
            'any_desk_address': any_desk_address,
            'software': software,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        response = self._handle_response(requests.get(url, params=params))

        nodes = response['data']
        for node in nodes:
            self._parse_timestamptz_field(node, 'rent_start_time')
            self._parse_timestamptz_field(node, 'last_balance_update_timestamp')
        response['data'] = nodes

        return response

    def update_node(self, node: dict):
        """
        Update a node.

        Parameters:
            node (dict): Node data to update.

        Returns:
            Confirmation message.
        """

        url = f"{self.base_url}/nodes"

        if node['rent_start_time']:
            node['rent_start_time'] = node['rent_start_time'].isoformat().replace('+00:00', 'Z')
        if node['last_balance_update_timestamp']:
            node['last_balance_update_timestamp'] = node['last_balance_update_timestamp'].isoformat().replace('+00:00', 'Z')

        response = requests.patch(url, json=node)
        return self._handle_response(response)

    def get_payments(self, id_: int = None, user_id: int = None, status: str = None, limit: int = None):
        """
        Retrieve payments based on provided filters.

        Parameters:
            id_ (int): Payment ID.
            user_id (int): User ID.
            status (str): Payment status.
            limit (int): Limit the number of results.

        Returns:
            List of payments matching the criteria.
        """
        url = f"{self.base_url}/payments"
        params = {
            'id': id_,
            'user_id': user_id,
            'status': status,
            'limit': limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = self._handle_response(requests.get(url, params=params))

        nodes = response['data']
        for node in nodes:
            self._parse_timestamptz_field(node, 'datetime')
        response['data'] = nodes

        return response

    def create_payment_ticket(self, user_id: int, amount: float):
        """
        Create a payment ticket.

        Parameters:
            user_id (int): User ID.
            amount (float): Amount for the payment.

        Returns:
            Payment ticket ID.
        """
        url = f"{self.base_url}/payments"
        payload = {"user_id": user_id, "amount": amount}
        response = requests.post(url, json=payload)
        return self._handle_response(response)

    def complete_payment(self, id_: int):
        """
        Complete a payment.

        Parameters:
            id_ (int): Payment ID.

        Returns:
            Confirmation of payment completion.
        """
        url = f"{self.base_url}/payments/complete/{id_}"
        response = requests.patch(url)
        return self._handle_response(response)

    def cancel_payment(self, id_: int):
        """
        Cancel a payment.

        Parameters:
            id_ (int): Payment ID.

        Returns:
            Confirmation of payment cancellation.
        """
        url = f"{self.base_url}/payments/cancel/{id_}"
        response = requests.patch(url)
        return self._handle_response(response)

    def get_users(
        self,
        id_: int = None,
        telegram_id: int = None,
        username: str = None,
        limit: int = None
    ):
        """
        Retrieve users based on provided filters.

        Parameters:
            id_ (int): User ID.
            telegram_id (int): Telegram ID.
            username (str): Telegram Username.
            limit (int): Limit the number of results.

        Returns:
            List of users matching the criteria.
        """
        url = f"{self.base_url}/users"
        params = {
            'id': id_,
            'telegram_id': telegram_id,
            'username': username,
            'limit': limit
        }
        params = {k: v for k, v in params.items() if v is not None}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def create_or_update_user(self, user_input: dict):
        """
        Create or update a user.

        Parameters:
            user_input (dict): User data.

        Returns:
            User data after creation or update.
        """
        url = f"{self.base_url}/users"
        response = requests.post(url, json=user_input)
        return self._handle_response(response)

    def ping(self):
        """
        Ping the API.

        Returns:
            True if the API is reachable.
        """
        url = f"{self.base_url}/ping"
        response = requests.get(url)
        return response.status_code == 200

    def save_hash_mapping(self, question: str, answer: str):
        """
        Save a hash mapping for a question and answer.

        Parameters:
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            dict: Response data, including the hash.
        """
        url = f"{self.base_url}/quiz/save-hash"
        payload = {"question": question, "answer": answer}
        response = requests.post(url, json=payload)
        return self._handle_response(response)

    def get_question_answer_by_hash(self, answer_hash: str):
        """
        Retrieve a question and answer using the hash.

        Parameters:
            answer_hash (str): The hash value.

        Returns:
            dict: The question and answer.
        """
        url = f"{self.base_url}/quiz/get-question-answer"
        params = {"hash": answer_hash}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def save_user_answer(self, telegram_id: int, question: str, answer: str):
        """
        Save a user's answer to a question.

        Parameters:
            telegram_id (int): The Telegram ID of the user.
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            dict: Response data.
        """
        url = f"{self.base_url}/quiz/save-answer"
        payload = {
            "telegram_id": telegram_id,
            "question": question,
            "answer": answer
        }
        response = requests.post(url, json=payload)
        return self._handle_response(response)

    # --- Utility Methods ---

    def _parse_timestamptz_field(self, data: dict, field_name: str):
        """
        Convert a timestamptz field in ISO 8601 format to a datetime object with timezone support.

        Parameters:
            data (dict): The dictionary containing the field.
            field_name (str): The name of the field to convert.

        Returns:
            None: Modifies the `data` dictionary in place.
        """
        if field_name in data and data[field_name]:
            try:
                data[field_name] = datetime.datetime.fromisoformat(data[field_name])
            except Exception as e:
                self.logger.debug(f"Failed to parse field {field_name} ('{data[field_name]}'): {e}")
                data[field_name] = None

    @staticmethod
    def generate_hash(question: str, answer: str) -> str:
        """
        Generate a hash for a question and answer.

        Parameters:
            question (str): The question text.
            answer (str): The answer text.

        Returns:
            str: A 32-character hash.
        """
        data = question + answer
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()[:32]

    def _handle_response(self, response):
        """
        Handle the API response.

        Parameters:
            response (requests.Response): The response object.

        Returns:
            Parsed JSON data if successful.

        Raises:
            Exception: If the API returns an error or invalid response.
        """
        try:
            json_data = response.json()
        except ValueError:
            # Response is not JSON
            response.raise_for_status()
            raise Exception(f"Invalid response: {response.text}")

        if 200 <= response.status_code < 300:
            if not json_data.get('success', False):
                error_message = json_data.get('error', 'Unknown error')
                raise Exception(f"API Error: {error_message}")
            else:
                return json_data
        if 404 == response.status_code:
            self.logger.debug(json_data.get('error', response.reason))
            return {
                'success': False,
                'error': json_data.get('error', response.reason),
                'data': []
            }
        else:
            error_message = json_data.get('error', response.reason)
            self.logger.debug(error_message)
            raise Exception(f"API Error: {error_message}")
