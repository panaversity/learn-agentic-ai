[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/12r5H6r4jlhlVQuNY-DnaCx2FoMLcn90U?usp=sharing)

# PIAIC Agent with Guardrails (Jupyter Notebook)

This project implements a PIAIC (Presidential Initiative for Artificial Intelligence and Computing) agent using the OpenAI Agents SDK within a Jupyter Notebook (`piaic-guardrails-example.ipynb`). The agent is restricted to handling PIAIC-related queries (e.g., AI, Cloud Computing, Blockchain, IoT) through custom input and output guardrails.

## Overview

- **Purpose**: Ensure the agent processes and responds only to PIAIC-related topics.
- **Guardrails**:
  - **Input Guardrail**: Verifies that user input is relevant to PIAIC topics.
  - **Output Guardrail**: Confirms the agent's response is PIAIC-relevant.
- **Implementation**: Uses dedicated guardrail agents to assess input/output relevance, with tripwires to stop off-topic content.
- **Format**: Jupyter Notebook for interactive development and testing.

## Key Components

- **PIAIC Agent**: Core agent for answering PIAIC-related questions.
- **Input Guardrail Agent**: Checks input relevance to PIAIC.
- **Output Guardrail Agent**: Ensures response relevance to PIAIC.
- **Notebook Structure**: Combines markdown explanations with executable code cells.

## Usage

1. **Access the Notebook**:
   - Run the notebook directly in Google Colab: [PIAIC Guardrails Example](https://colab.research.google.com/drive/12r5H6r4jlhlVQuNY-DnaCx2FoMLcn90U?usp=sharing).
   - Alternatively, download `piaic-guardrails-example.ipynb` and open it in Jupyter Notebook or JupyterLab.

2. **Prerequisites**:
   - For local execution, install Jupyter Notebook/JupyterLab and required packages:
     ```bash
     pip install notebook agents pydantic
     ```

3. **Run the Notebook**:
   - In Colab or Jupyter, execute cells sequentially to:
     - Import libraries
     - Define the guardrail output model
     - Create guardrail agents and functions
     - Configure the main PIAIC agent
     - Test with sample inputs

4. **Example Inputs**:
   - PIAIC-relevant: "What is the curriculum for PIAIC's AI course?"
   - Non-PIAIC: "How do I bake a chocolate cake?"

## Output

- PIAIC-relevant inputs produce responses if both guardrails pass.
- Non-PIAIC inputs or outputs trigger a tripwire, showing an error (e.g., "Input Guardrail tripped: Input is not PIAIC-related.").

## File Structure

- `piaic-guardrails-example.ipynb`: Jupyter Notebook with the agent and guardrail implementation.

## Notes

- Utilizes OpenAI Agents SDK's `InputGuardrail` and `OutputGuardrail` classes.
- The `PIAICRelevanceOutput` model structures guardrail outputs (boolean and reasoning).
- Notebook cells include markdown for clarity and are designed for sequential execution.
- Google Colab automatically manages the `asyncio` event loop for seamless execution.