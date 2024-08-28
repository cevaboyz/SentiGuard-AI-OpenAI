#  🛡️ SentiGuard-AI OpenAI Edition

Un potente strumento di analisi del sentiment che utilizza l'API di OpenAI con supporto per la selezione del modello e il calcolo dei costi.

[English](#english) | [Italiano](#italiano)

---

## English

### 📝 Description
SentiGuard-AI OpenAI Edition is a Python script that performs sentiment analysis on text data using OpenAI's language models. It features model selection, cost estimation, and detailed logging of token usage and costs. This tool is suitable for large-scale sentiment analysis tasks, allowing users to choose the most appropriate model for their needs while keeping track of API usage and costs.

### 🌟 Features
- 🧠 Utilizes OpenAI's advanced language models for accurate sentiment analysis
- 🔢 Supports multiple OpenAI models with interactive selection
- 💰 Provides cost estimation and tracking for API usage
- 🔄 Handles multiple analyses with custom prompts
- ⏱️ Respects API rate limits to ensure uninterrupted operation
- 📊 Provides real-time console output for monitoring
- 💾 Saves results progressively in CSV and final output in XLSX format

### 🛠️ Requirements
- Python 3.7+
- Required Python libraries (automatically installed by the script):
  ```
  pandas
  openai
  tiktoken
  openpyxl
  ```

### 🔑 API Key Required
- OpenAI API Key
  - 🔗 Obtain from [OpenAI API Keys](https://platform.openai.com/api-keys)
  - 📋 Instructions:
    1. Log in to your OpenAI account
    2. Navigate to the API keys section
    3. Create a new secret key

> ⚠️ **Important:** Keep your API key secure. Never share it publicly or include it in version-controlled code.

### 🚀 How to Use
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SentiGuard-AI-OpenAI.git
   ```
2. Navigate to the project directory:
   ```bash
   cd SentiGuard-AI-OpenAI
   ```
3. Run the script:
   ```bash
   python sentiguard_ai_openai.py
   ```
4. Follow the on-screen prompts to:
   - Enter your OpenAI API key
   - Select the OpenAI model to use
   - Choose your input file (CSV or Excel)
   - Select the column containing the text to analyze
   - Define the analysis range
   - Specify the number of analyses and their respective prompts

### 📤 Output
- Interim results are saved as `{custom_filename}_intermediate.csv`
- Final results are saved as `{custom_filename}_final.xlsx`
- Error logs, if any, are saved as `{custom_filename}_error_log.txt`

### 💻 Code Snippet
Here's a key part of the script:

```python
def schedule_request(client, prompt: str, tracker: dict, model: str) -> dict:
    # ... [rate limiting logic] ...

    input_tokens = count_tokens(prompt, model)
    ai_text = generate_content(client, prompt, model)
    output_tokens = count_tokens(ai_text, model)

    input_cost = calculate_cost(input_tokens, model, True)
    output_cost = calculate_cost(output_tokens, model, False)

    return {
        'ai_text': ai_text,
        'tracker': tracker,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'time_taken': end_time - start_time
    }
```

This function manages API requests, token counting, and cost calculation for each analysis.

---

## Italiano

### 📝 Descrizione
SentiGuard-AI OpenAI Edition è uno script Python che esegue l'analisi del sentiment su dati testuali utilizzando i modelli linguistici di OpenAI. Presenta la selezione del modello, la stima dei costi e il logging dettagliato dell'utilizzo dei token e dei costi. Questo strumento è adatto per attività di analisi del sentiment su larga scala, permettendo agli utenti di scegliere il modello più appropriato per le loro esigenze tenendo traccia dell'utilizzo dell'API e dei costi.

### 🌟 Caratteristiche
- 🧠 Utilizza i modelli linguistici avanzati di OpenAI per un'analisi accurata del sentiment
- 🔢 Supporta molteplici modelli OpenAI con selezione interattiva
- 💰 Fornisce stima dei costi e monitoraggio per l'utilizzo dell'API
- 🔄 Gestisce analisi multiple con prompt personalizzati
- ⏱️ Rispetta i limiti di velocità delle API per garantire un funzionamento ininterrotto
- 📊 Fornisce output in console in tempo reale per il monitoraggio
- 💾 Salva i risultati progressivamente in formato CSV e l'output finale in formato XLSX

### 🛠️ Requisiti
- Python 3.7+
- Librerie Python richieste (installate automaticamente dallo script):
  ```
  pandas
  openai
  tiktoken
  openpyxl
  ```

### 🔑 Chiave API Richiesta
- Chiave API OpenAI
  - 🔗 Ottenibile da [OpenAI API Keys](https://platform.openai.com/api-keys)
  - 📋 Istruzioni:
    1. Accedi al tuo account OpenAI
    2. Naviga nella sezione delle chiavi API
    3. Crea una nuova chiave segreta

> ⚠️ **Importante:** Mantieni la tua chiave API sicura. Non condividerla mai pubblicamente o includerla in codice versionato.

### 🚀 Come Utilizzare
1. Clona il repository:
   ```bash
   git clone https://github.com/tuousername/SentiGuard-AI-OpenAI.git
   ```
2. Naviga nella directory del progetto:
   ```bash
   cd SentiGuard-AI-OpenAI
   ```
3. Esegui lo script:
   ```bash
   python sentiguard_ai_openai.py
   ```
4. Segui le istruzioni sullo schermo per:
   - Inserire la tua chiave API OpenAI
   - Selezionare il modello OpenAI da utilizzare
   - Scegliere il file di input (CSV o Excel)
   - Selezionare la colonna contenente il testo da analizzare
   - Definire l'intervallo di analisi
   - Specificare il numero di analisi e i rispettivi prompt

### 📤 Output
- I risultati intermedi vengono salvati come `{nome_file_personalizzato}_intermediate.csv`
- I risultati finali vengono salvati come `{nome_file_personalizzato}_final.xlsx`
- I log degli errori, se presenti, vengono salvati come `{nome_file_personalizzato}_error_log.txt`

### 💻 Snippet di Codice
Ecco una parte chiave dello script:

```python
def schedule_request(client, prompt: str, tracker: dict, model: str) -> dict:
    # ... [logica di limitazione della velocità] ...

    input_tokens = count_tokens(prompt, model)
    ai_text = generate_content(client, prompt, model)
    output_tokens = count_tokens(ai_text, model)

    input_cost = calculate_cost(input_tokens, model, True)
    output_cost = calculate_cost(output_tokens, model, False)

    return {
        'ai_text': ai_text,
        'tracker': tracker,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'time_taken': end_time - start_time
    }
```

Questa funzione gestisce le richieste API, il conteggio dei token e il calcolo dei costi per ogni analisi.
