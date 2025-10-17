"""Create or refresh an OpenAI vector store with the sample FAQ file."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.error import OpenAIError


def main() -> None:
    base_dir = Path(__file__).parent
    load_dotenv(base_dir / ".env", override=False)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to your .env file before running this script."
        )

    docs_dir = base_dir / "docs"
    doc_paths = sorted(docs_dir.glob("*.txt"))
    if not doc_paths:
        raise FileNotFoundError(
            f"No .txt files found in {docs_dir}. Add at least one file before running the script."
        )

    client = OpenAI(api_key=api_key)

    vector_store_id = os.getenv("OPENAI_VECTOR_STORE_ID", "").strip()

    created_new = False
    try:
        if vector_store_id:
            vector_store = client.beta.vector_stores.retrieve(vector_store_id)
            print(f"📚 Using existing vector store: {vector_store.id}")
        else:
            print("📚 Creating a new managed vector store...")
            vector_store = client.beta.vector_stores.create(name="Panaversity FAQ Store")
            vector_store_id = vector_store.id
            created_new = True
            print(f"✅ Vector store created: {vector_store_id}")

        file_streams = [path.open("rb") for path in doc_paths]
        try:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=file_streams,
            )
        finally:
            for stream in file_streams:
                stream.close()

        print("✅ Files uploaded and indexed.")

    except OpenAIError as error:
        raise RuntimeError(f"Failed to update vector store: {error}") from error

    if created_new:
        vector_id_path = base_dir / "vector_store_id.txt"
        vector_id_path.write_text(vector_store_id + "\n", encoding="utf-8")
        print(f"📝 Saved the vector store ID in {vector_id_path.name}.")

        env_path = base_dir / ".env"
        if env_path.exists():
            env_text = env_path.read_text(encoding="utf-8").splitlines()
            replaced = False
            for index, line in enumerate(env_text):
                if line.startswith("OPENAI_VECTOR_STORE_ID="):
                    env_text[index] = f"OPENAI_VECTOR_STORE_ID={vector_store_id}"
                    replaced = True
                    break
            if not replaced:
                env_text.append(f"OPENAI_VECTOR_STORE_ID={vector_store_id}")
            env_path.write_text("\n".join(env_text) + "\n", encoding="utf-8")
            print("✅ Updated .env with OPENAI_VECTOR_STORE_ID.")
        else:
            print("⚠️ .env file not found. Add OPENAI_VECTOR_STORE_ID manually when you create it.")

    print("All set! Your Chainlit app can now read from the managed vector store.")


if __name__ == "__main__":
    main()
