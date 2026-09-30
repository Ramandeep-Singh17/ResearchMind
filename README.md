# 🔬 ResearchMind — Multi-Agent AI Research System

ResearchMind is a **Multi-Agent AI Research System** that automates the process of researching a topic, collecting information from the web, extracting useful content, generating a structured research report, and critically reviewing the generated output.

The system uses specialized AI agents/chains for different stages of the research workflow, making the process more modular, structured, and easier to extend.

---

## 🚀 Key Features

- 🔎 **Web Search Agent** — searches the web for recent and relevant information.
- 📄 **Reader Agent** — scrapes selected web pages and extracts readable content.
- ✍️ **Writer Agent** — converts collected research into a structured report.
- 🧐 **Critic Agent** — reviews the generated report and provides feedback.
- 🤖 **Groq GPT-OSS-120B** — powers the AI reasoning and generation.
- 🌐 **Tavily Search** — provides web search capabilities.
- 🧹 **BeautifulSoup** — extracts clean text from web pages.
- 🖥️ **Streamlit UI** — provides an interactive research interface.
- 🔐 **Environment-based API keys** — keeps credentials outside the source code.
- 📥 **Markdown report download** — allows users to download the generated report.

---

# 🧠 How ResearchMind Works

The complete workflow is:

```text
                    ┌─────────────────┐
                    │      User       │
                    │ Research Topic  │
                    └────────┬────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Search Agent     │
                  │                     │
                  │  Tavily Web Search  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Reader Agent     │
                  │                     │
                  │ BeautifulSoup +     │
                  │ Requests Scraping   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Writer Agent     │
                  │                     │
                  │ Structured Research│
                  │       Report        │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Critic Agent     │
                  │                     │
                  │ Review + Feedback   │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │    Final Output     │
                  │                     │
                  │ Research Report +   │
                  │ Critic Feedback     │
                  └─────────────────────┘
```

---

# 🏗️ Project Architecture

ResearchMind follows a modular multi-agent architecture.

### 1. Search Agent

The Search Agent is responsible for finding relevant information from the web.

It uses **Tavily Search** to retrieve:

- Search result titles
- URLs
- Relevant snippets
- Recent web information

The search results are then passed to the Reader Agent.

---

### 2. Reader Agent

The Reader Agent performs deeper reading of the sources returned by the Search Agent.

It uses:

- `requests`
- `BeautifulSoup`

to retrieve and clean web page content.

The Reader Agent removes unnecessary HTML elements such as:

- Scripts
- Styles
- Navigation
- Footer elements

and extracts readable text from the page.

This provides the Writer Agent with more useful information than search snippets alone.

---

### 3. Writer Agent

The Writer Agent takes the collected research and generates a structured research report.

The generated report can contain sections such as:

- Introduction
- Key Findings
- Detailed Discussion
- Sources
- Conclusion

The goal is to transform raw web information into an organized and readable report.

---

### 4. Critic Agent

The Critic Agent receives the generated report and reviews it.

It focuses on identifying:

- Missing information
- Weak points
- Quality issues
- Possible improvements
- Overall report quality

The feedback helps evaluate the quality of the generated research.

---

# 🔄 End-to-End Execution Flow

When a user enters a topic into the Streamlit application, the following process takes place:

### Step 1 — User Input

The user enters a research topic through the Streamlit interface.

Example:

```text
Impact of Generative AI on Software Development
```

---

### Step 2 — Search Agent

The Search Agent sends the topic to Tavily.

```text
User Topic
    ↓
Tavily Search
    ↓
Multiple Relevant Sources
```

The system collects URLs and snippets from the search results.

---

### Step 3 — Reader Agent

The selected URLs are passed to the Reader Agent.

```text
URLs
 ↓
HTTP Request
 ↓
HTML Page
 ↓
BeautifulSoup
 ↓
Clean Text
```

The extracted content becomes the deeper research material.

---

### Step 4 — Writer Agent

The collected research is passed to the Writer Chain.

```text
Topic + Research
       ↓
     LLM
       ↓
Structured Report
```

The Writer Agent generates the final research draft.

---

### Step 5 — Critic Agent

The generated report is then passed to the Critic Chain.

```text
Research Report
      ↓
 Critic LLM
      ↓
Feedback / Review
```

The critic identifies weaknesses and provides suggestions for improvement.

---

### Step 6 — Final Streamlit Output

The application displays:

- Research results
- Reader output
- Generated report
- Critic feedback

The generated report can also be downloaded as a Markdown file.

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| LangChain | LLM application framework |
| LangGraph | Agent/workflow orchestration |
| Groq | LLM inference |
| GPT-OSS-120B | Primary language model |
| Tavily | Web search |
| Requests | HTTP requests |
| BeautifulSoup | Web scraping and text extraction |
| Streamlit | Frontend/UI |
| python-dotenv | Environment variable management |
| Git | Version control |
| GitHub | Source code hosting |

---

# 🤖 LLM Configuration

ResearchMind uses Groq for LLM inference.

The configured model is:

```python
ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    reasoning_effort="low",
    api_key=os.getenv("GROQ_API_KEY")
)
```

Although the model identifier contains `openai/`, the application is using the **Groq API/provider** through `ChatGroq`.

The temperature is set to `0` to make the generated output more deterministic.

---

# 🌐 Web Search

ResearchMind uses Tavily for web search.

The Search Agent calls the Tavily API and retrieves relevant search results.

A simplified representation of the process is:

```python
results = tavily.search(
    query=query,
    max_results=5
)
```

The system extracts information such as:

```text
Title
URL
Snippet
```

These results are then used by the Reader Agent.

---

# 📄 Web Content Extraction

The Reader Agent uses Requests and BeautifulSoup.

The basic process is:

```text
URL
 ↓
requests.get()
 ↓
HTML Response
 ↓
BeautifulSoup
 ↓
Remove unwanted HTML
 ↓
Extract readable text
```

Unnecessary elements such as:

```text
<script>
<style>
<nav>
<footer>
```

are removed before extracting the page text.

The extracted content is limited before being passed further into the pipeline to prevent unnecessarily large inputs.

---

# 📁 Project Structure

```text
ResearchMind/
│
├── agents.py
│
├── app.py
│
├── pipeline.py
│
├── tools.py
│
├── requirements.txt
│
├── .gitignore
│
└── README.md
```

### `app.py`

Main Streamlit application.

Responsibilities include:

- Creating the user interface
- Accepting the research topic
- Running the research pipeline
- Displaying progress
- Displaying search results
- Displaying reader output
- Displaying the generated report
- Displaying critic feedback
- Providing report download functionality

---

### `agents.py`

Contains the AI agent and chain configuration.

This file handles the AI-side components such as:

- Groq LLM configuration
- Search Agent
- Reader Agent
- Writer Chain
- Critic Chain

---

### `tools.py`

Contains the external tools used by the agents.

Currently the main tools include:

```text
web_search()
scrape_url()
```

`web_search()` connects to Tavily.

`scrape_url()` retrieves and cleans web page content.

---

### `pipeline.py`

Contains pipeline/workflow-related logic used for executing the research process.

The overall conceptual pipeline is:

```text
Search
  ↓
Read
  ↓
Write
  ↓
Critique
```

---

### `requirements.txt`

Contains the Python dependencies required to run the application.

---

### `.gitignore`

Prevents sensitive and unnecessary files from being uploaded to GitHub.

Important ignored files include:

```text
.venv/
.env
__pycache__/
*.pyc
.streamlit/secrets.toml
```

---

# 🔐 Environment Variables

API credentials are stored using environment variables rather than directly inside the source code.

Create a `.env` file locally:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### ⚠️ Important

The `.env` file must **never be uploaded to GitHub**.

It is included in `.gitignore`:

```gitignore
.env
```

This protects API credentials from accidentally becoming public.

---

# 💻 Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Ramandeep-Singh17/ResearchMind.git
```

Move into the project directory:

```bash
cd ResearchMind
```

---

## 2. Create Virtual Environment

Using Python:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install Dependencies

Using pip:

```bash
pip install -r requirements.txt
```

Or, if using `uv`:

```bash
uv pip install -r requirements.txt
```

---

## 4. Configure API Keys

Create:

```text
.env
```

and add:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

## 5. Run the Application

```bash
streamlit run app.py
```

If the `streamlit` command is not recognized:

```bash
python -m streamlit run app.py
```

The application will open in the browser.

---

# 🖥️ User Interface

The Streamlit application provides a research-focused interface containing:

### Research Input

Users enter the topic they want to research.

### Pipeline Visualization

The UI displays the major stages:

```text
Search Agent
     ↓
Reader Agent
     ↓
Writer Chain
     ↓
Critic Chain
```

### Results

After execution, users can inspect:

- Search results
- Extracted reader content
- Final research report
- Critic feedback

The final report can also be downloaded as a Markdown file.

---

# 🔗 GitHub Repository

The project is hosted here:

https://github.com/Ramandeep-Singh17/ResearchMind

---

# 🚀 Deployment

The application is designed to be deployed using **Streamlit Community Cloud**.

The deployment flow is:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
Select app.py
       ↓
Configure Secrets
       ↓
Deploy
```

For cloud deployment, API keys should be configured as Streamlit Secrets rather than uploading `.env`.

Required secrets:

```text
GROQ_API_KEY
TAVILY_API_KEY
```

The application entry point is:

```text
app.py
```

---

# 🔒 Security Practices

ResearchMind follows basic credential-management practices:

- API keys are stored in environment variables.
- `.env` is excluded through `.gitignore`.
- Python cache files are excluded.
- Virtual environments are excluded.
- API credentials are not hard-coded in the application.

---

# 📊 Advantages of the Multi-Agent Architecture

Instead of asking a single LLM to perform the complete research task, ResearchMind separates responsibilities.

```text
Search Agent
    ↓
Responsible for finding information

Reader Agent
    ↓
Responsible for understanding source content

Writer Agent
    ↓
Responsible for generating the report

Critic Agent
    ↓
Responsible for reviewing the report
```

This modular approach makes each stage easier to understand, debug, and extend.

---

# 🔮 Future Improvements

Possible future improvements include:

- Better source ranking
- More robust web scraping
- Parallel source processing
- Source reliability evaluation
- Citation-aware report generation
- Persistent research history
- Research report export to PDF
- More advanced agent orchestration
- Improved error handling
- Human-in-the-loop review
- Research quality scoring
- Additional research tools

---

# 🎯 Learning Outcomes

This project demonstrates practical experience with:

- Generative AI application development
- Multi-agent architecture
- LangChain
- LangGraph
- LLM integration
- Prompt-based workflows
- Tool calling
- Web search integration
- Web scraping
- Streamlit application development
- Environment variable management
- Git and GitHub
- AI workflow orchestration

---

# 👨‍💻 Author

**Ramandeep Singh**

B.Tech — Computer Science & Engineering (AI & ML)

NIET Greater Noida

---

## ⭐ Project Summary

ResearchMind demonstrates how multiple specialized AI components can work together to automate a complete research workflow:

```text
User
 ↓
Search Agent
 ↓
Reader Agent
 ↓
Writer Agent
 ↓
Critic Agent
 ↓
Research Report
```

The project combines **LLMs, web search, web scraping, agentic workflows, and an interactive Streamlit interface** into a single end-to-end AI research application.
