import logging
import json

from fastapi import FastAPI
from dapr.clients import DaprClient
from dapr.clients.grpc._crypto import EncryptOptions, DecryptOptions

# Configure logging
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="ChatAgentService",
              description="DACA Step 1: Cryptography API with SDK")

# Constants for Dapr Cryptography
CRYPTO_COMPONENT_NAME = "secretstore"
CRYPTO_KEY_NAME = "encryption-key"

options = EncryptOptions(
    component_name=CRYPTO_COMPONENT_NAME,
    key_name=CRYPTO_KEY_NAME,
    key_wrap_algorithm='AES',
)

decrypt_options = DecryptOptions(
    component_name=CRYPTO_COMPONENT_NAME,
    key_name=CRYPTO_KEY_NAME
)


@app.post("/encrypt")
async def encrypt_value(data: dict):
    """Encrypt a value using DaprClient."""
    with DaprClient() as dapr_client:
        encrypt_resp = dapr_client.encrypt(json.dumps(data), options)
        return {"encrypted": encrypt_resp.read()}

# Test route that decrypts any value


@app.post("/decrypt")
async def decrypt_value(data: str):
    """Decrypt a value using DaprClient."""
    with DaprClient() as dapr_client:
        decrypt_resp = dapr_client.decrypt(data, decrypt_options)
        return {"decrypted": decrypt_resp.read()}
