import sys
import subprocess
import os
import time
import pandas as pd
import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox


def install(package):
    """Installs missing Python packages using pip."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# Ensure all required libraries are installed
libraries = ['pandas', 'openai', 'openpyxl', 'tiktoken']
for lib in libraries:
    try:
        if lib == 'tiktoken':
            print(f"Installing {lib}...")
            install(lib)
            print(f"{lib} installed successfully.")
        __import__(lib)
    except ImportError:
        print(f"Installing {lib}...")
        install(lib)
        print(f"{lib} installed successfully.")

import openai
import tiktoken

# Pricing information for specific models
MODEL_PRICING = {
    "gpt-4o-2024-08-06": {"input": 0.00250, "output": 0.01000},
    "gpt-4o": {"input": 0.00500, "output": 0.01500},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.00060},
    "gpt-4o-mini-2024-07-18": {"input": 0.000150, "output": 0.000600},
    "gpt-4o-2024-05-13": {"input": 0.00500, "output": 0.01500},
    "gpt-4-turbo": {"input": 0.00500, "output": 0.01500}

}


def load_api_key_from_file(file_path):
    """Load the OpenAI API key from a file."""
    with open(file_path, 'r') as file:
        return file.read().strip()


def get_api_key():
    """Interactive dialog to get the API key."""
    root = tk.Tk()
    root.withdraw()

    choice = simpledialog.askstring("API Key Input",
                                    "Choose input method:\n1. Paste API key\n2. Select file with API key",
                                    initialvalue="1")

    if choice == "1":
        api_key = simpledialog.askstring("API Key Input", "Paste your OpenAI API key:", show='*')
        if api_key:
            return api_key.strip()
        else:
            print("No API key provided. Operation cancelled.")
            return None
    elif choice == "2":
        file_path = filedialog.askopenfilename(
            title="Select the file containing your OpenAI API key",
            filetypes=[("Text Files", "*.txt")],
            initialdir=os.getcwd()
        )
        if file_path:
            return load_api_key_from_file(file_path)
        else:
            print("No file selected. Operation cancelled.")
            return None
    else:
        print("Invalid choice. Operation cancelled.")
        return None


def get_available_models(client):
    """Get a list of available models from OpenAI."""
    try:
        models = client.models.list()
        return [model.id for model in models.data if model.id.startswith('gpt')]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return list(MODEL_PRICING.keys())  # Fallback to models with pricing info


def select_model(available_models):
    """Interactive dialog to select a model."""
    root = tk.Tk()
    root.withdraw()

    print("Available models:")
    for i, model in enumerate(available_models):
        print(f"{i + 1}. {model}")

    while True:
        choice = simpledialog.askstring("Model Selection",
                                        f"Enter the number of the model you want to use (1-{len(available_models)}):")
        if choice and choice.isdigit() and 1 <= int(choice) <= len(available_models):
            return available_models[int(choice) - 1]
        print("Invalid selection. Please try again.")


def generate_prompt(base_prompt: str, review: str) -> str:
    """Combine the base prompt with the review text."""
    return f"{base_prompt}\n\nReview to analyze: {review}"


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count the number of tokens in the given text using the specified model's tokenizer."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def create_openai_client(api_key):
    """Create and return an OpenAI client instance."""
    return openai.OpenAI(api_key=api_key)


def generate_content(client, prompt: str, model: str) -> str:
    """Generate content using OpenAI's API."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except openai.APIError as e:
        raise Exception(f"OpenAI API request failed: {str(e)}")


def calculate_cost(tokens: int, model: str, is_input: bool = True) -> float:
    """Calculate the cost for the given number of tokens."""
    if model in MODEL_PRICING:
        price_per_1k = MODEL_PRICING[model]["input" if is_input else "output"]
        return (tokens / 1000) * price_per_1k
    return 0  # Return 0 if pricing is not available for the model


def schedule_request(client, prompt: str, tracker: dict, model: str) -> dict:
    """Schedule and make a request to the OpenAI API, respecting rate limits."""
    current_time = time.time()

    if int(current_time) % 60 == 0 or int(current_time) % 86400 == 0:
        tracker['request_count'] = 0
        tracker['token_count'] = 0
        tracker['start_minute'] = current_time
        tracker['start_day'] = current_time

    if tracker['request_count'] >= REQUESTS_PER_MINUTE_LIMIT:
        print("Rate limit reached. Waiting...")
        time.sleep(60 - (current_time % 60))
        return schedule_request(client, prompt, tracker, model)

    if tracker['request_count'] >= REQUESTS_PER_DAY_LIMIT:
        raise Exception("Daily request limit reached.")

    input_tokens = count_tokens(prompt, model)
    if (tracker['token_count'] + input_tokens) > TOKENS_PER_MINUTE_LIMIT:
        print("Token limit reached. Waiting...")
        time.sleep(60 - (current_time % 60))
        return schedule_request(client, prompt, tracker, model)

    tracker['request_count'] += 1
    tracker['token_count'] += input_tokens
    start_time = time.time()
    ai_text = generate_content(client, prompt, model)
    end_time = time.time()

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


def main():
    api_key = get_api_key()
    if not api_key:
        return

    client = create_openai_client(api_key)

    # Get available models and let user select one
    available_models = get_available_models(client)
    selected_model = select_model(available_models)
    print(f"Selected model: {selected_model}")

    file_path = filedialog.askopenfilename(
        title="Select the CSV or Excel file",
        filetypes=[("Excel Files", "*.xlsx;*.xls"), ("CSV Files", "*.csv")],
        initialdir=os.getcwd()
    )
    if not file_path:
        print("No file selected. Operation cancelled.")
        return

    try:
        data = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
    except Exception as e:
        print(f"Error loading the file: {e}")
        return

    print("Available columns:")
    for i, column in enumerate(data.columns):
        print(f"{i}: {column}")

    while True:
        review_column = input("Enter the number or name of the column containing the reviews: ")
        if review_column.isdigit() and int(review_column) < len(data.columns):
            review_column = data.columns[int(review_column)]
            break
        elif review_column in data.columns:
            break
        else:
            print(f"Invalid column selection. Please try again.")

    print(f"Selected column for analysis: {review_column}")

    analysis_range = simpledialog.askstring("Input",
                                            "Analyze all rows, specify end row, or provide a range (e.g., '1-100'):")
    if not analysis_range:
        print("No range specified. Operation cancelled.")
        return

    if analysis_range.lower() == 'all':
        start_row, end_row = 0, len(data)
    elif '-' in analysis_range:
        start_row, end_row = map(int, analysis_range.split('-'))
    else:
        start_row, end_row = 0, int(analysis_range)

    num_analyses = simpledialog.askinteger("Input", "How many analyses do you want to perform?")
    if not num_analyses or num_analyses <= 0:
        print("Invalid number of analyses. Operation cancelled.")
        return

    for i in range(num_analyses):
        column_title = simpledialog.askstring("Input", f"Enter the title for analysis {i + 1}:")
        if column_title:
            data[column_title] = ''

    prompts = []
    for i in range(num_analyses):
        base_prompt = simpledialog.askstring("Input", f"Enter the base prompt for analysis {i + 1}:")
        prompts.append(base_prompt)

    print("The following columns will be populated with the analysis results:", data.columns[-num_analyses:])
    confirm = messagebox.askyesno("Confirm", "Do you want to proceed with the analysis?")
    if not confirm:
        print("Operation cancelled.")
        return

    total_input_tokens = sum(
        count_tokens(row[review_column], selected_model) for _, row in data.iloc[start_row:end_row].iterrows())
    total_input_cost = calculate_cost(total_input_tokens, selected_model, True)
    print(f"Total input tokens: {total_input_tokens}")
    print(f"Estimated input cost: ${total_input_cost:.4f}")

    confirm = messagebox.askyesno("Confirm",
                                  f"Estimated input tokens: {total_input_tokens} (${total_input_cost:.4f}). Do you want to proceed?")
    if not confirm:
        print("Operation cancelled.")
        return

    tracker = {'request_count': 0, 'token_count': 0, 'start_minute': time.time(), 'start_day': time.time()}
    error_log = []

    save_dir = filedialog.askdirectory(title="Select directory to save results")
    if not save_dir:
        print("No directory selected. Using current directory.")
        save_dir = os.getcwd()

    # Ask for custom file name
    default_filename = "sentiment_analysis_results"
    custom_filename = simpledialog.askstring("Input", "Enter the name for the final file (without extension):",
                                             initialvalue=default_filename)
    if not custom_filename:
        custom_filename = default_filename

    total_cost = 0
    for i, row in data.iloc[start_row:end_row].iterrows():
        print(f"\nProcessing row {i + 1}")
        print(f"Row content: {row[review_column]}")

        for j, prompt in enumerate(prompts):
            full_prompt = generate_prompt(prompt, row[review_column])
            try:
                print(f"Analysis {j + 1}...")
                result = schedule_request(client, full_prompt, tracker, selected_model)
                response_text = result['ai_text']
                data.at[i, data.columns[-num_analyses + j]] = response_text
                tracker = result['tracker']

                print(f"Response for analysis {j + 1}:")
                print(response_text)
                print(f"Input tokens: {result['input_tokens']}, Output tokens: {result['output_tokens']}")
                print(f"Input cost: ${result['input_cost']:.4f}, Output cost: ${result['output_cost']:.4f}")
                print(f"Time taken: {result['time_taken']:.2f} seconds")

                total_cost += result['input_cost'] + result['output_cost']

                # Save intermediate results
                intermediate_file_path = os.path.join(save_dir, f"{custom_filename}_intermediate.csv")
                data.to_csv(intermediate_file_path, index=False)
            except Exception as e:
                error_message = f"Error during request for row {i + 1}, analysis {j + 1}: {str(e)}"
                print(error_message)
                error_log.append(error_message)
            time.sleep(1)

    # Save final results
    final_file_path = os.path.join(save_dir, f"{custom_filename}_final.xlsx")
    data.to_excel(final_file_path, index=False, engine='openpyxl')
    print(f"Analysis completed. Results saved in '{final_file_path}'")
    print(f"Total cost of analysis: ${total_cost:.4f}")

    if error_log:
        error_log_path = os.path.join(save_dir, f"{custom_filename}_error_log.txt")
        with open(error_log_path, "w") as error_file:
            for error in error_log:
                error_file.write(error + "\n")
        print(f"Errors encountered. Check '{error_log_path}' for details.")

    # Open the directory where results are saved
    os.startfile(save_dir)


if __name__ == "__main__":
    REQUESTS_PER_MINUTE_LIMIT = 60
    TOKENS_PER_MINUTE_LIMIT = 90000
    REQUESTS_PER_DAY_LIMIT = 5000
    try:
        main()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        input("Press Enter to close the terminal...")