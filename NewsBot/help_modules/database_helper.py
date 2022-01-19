import json

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_costants
import azure.cosmos.documents as documents

from config import DefaultConfig
from help_modules import RegisteredUser

import hashlib


class DatabaseHelper:
    def __init__(self, default_config: DefaultConfig):
        self._default_config = default_config
        self._cosmos_client = cosmos_client.CosmosClient(
            self._default_config.COSMOS_DB_URL,
            {'masterKey': self._default_config.COSMOS_DB_KEY}
        )
        self.database_name = ""
        self.database = None
        self.container_definition = {}
        self.container = None

    def create_database(self, database_name: str):
        self.database_name = database_name
        try:
            self.database = self._cosmos_client.CreateDatabase({'id': self.database_name})
            print(f"Il database {self.database_name} è stato creato")
        except errors.HTTPFailure:
            print(f"Il database {self.database_name} esiste già")
            self.database = self._cosmos_client.ReadDatabase("dbs/" + self.database_name)

    def create_container(self, container_name: str):
        self.container_definition = {
            'id': container_name,
            'partitionKey': {
                'paths': ['/email'],
                'kind': documents.PartitionKind.Hash
            }
        }
        try:
            self.container = self._cosmos_client.CreateContainer("dbs/" + self.database_name, self.container_definition)
            print(f"Il container {self.container_definition['id']} è stato creato")
        except errors.HTTPFailure as e:
            if e.status_code == http_costants.StatusCodes.CONFLICT:
                print(f"Il container {self.container_definition['id']} esiste già")
                self.container = self._cosmos_client.ReadContainer(
                    "dbs/" + self.database_name + "/colls/" + self.container_definition['id'])
            else:
                raise e

    def insert_data(self, registered_user: RegisteredUser):
        self._cosmos_client.UpsertItem(
            "dbs/" + self.database_name + "/colls/" + self.container_definition['id'],
            {
                'id': registered_user.email,
                'email': registered_user.email,
                'preferenze': registered_user.preferenze
            }
        )

    def find_by_id(self, email: str):
        try:
            response = self._cosmos_client.ReadItem(
                f"dbs/{self.database_name}/colls/{self.container_definition['id']}/docs/{email}",
                options={'partitionKey': email}
            )
            added_user = RegisteredUser(email=response['email'], preferenze=response['preferenze'])
            return added_user
        except errors.HTTPFailure:
            print(f"L'utente con l'email {email} non esiste")
            return None

    def delete_by_id(self, email: str):
        try:
            self._cosmos_client.DeleteItem(
                f"dbs/{self.database_name}/colls/{self.container_definition['id']}/docs/{email}",
                options={'partitionKey': email}
            )
            return True
        except errors.HTTPFailure:
            print(f"L'utente con l'email {email} non esiste")
            return False
