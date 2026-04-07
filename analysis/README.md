## 📁 Directory Structure

```
analysis/
├── README.md
├── conversations_data_cleaning/          # Student conversation analysis pipelines
│   ├── NALA/                            # NALA dataset processing
│   │   ├── data_cleaning_NALA.ipynb      # Data preprocessing and cleaning
│   │   └── majority_voting_pipeline_NALA.ipynb  # LLM-based classification with self-consistency
│   └── NALA_Assess/                     # NALA_Assess dataset processing
│       ├── data_cleaning_NALA_Assess.ipynb
│       └── majority_voting_pipeline_NALA_Assess.ipynb
└── survey_data_cleaning/                # Survey feedback analysis
    └── survey_analysis.ipynb
```

## 📊 Notebooks Overview

### Conversations Data Cleaning

#### 1. **data_cleaning_NALA.ipynb** & **data_cleaning_NALA_Assess.ipynb**

**Purpose**: Prepare cleaned conversation data for SOLO classification analysis.

**Key Steps**:
- Load conversation data from CSV files
- Remove irrelevant columns and rows with missing values
- Handle empty/null text entries
- Standardize data types (e.g., convert timestamps to datetime objects)
- Export cleaned datasets for downstream processing

---

#### 2. **majority_voting_pipeline_NALA.ipynb** & **majority_voting_pipeline_NALA_Assess.ipynb**

**Purpose**: Classify student questions using LLM-based self-consistency voting with course topic knowledge.

**Key Steps**:

- **Self-Consistency Decoding**: Generates multiple independent LLM predictions and reasoning for a question input
- **Majority Voting**: Selects the most common classification label but flags ambiguous cases to be later redirected to domain experts

**Two-Stage Classification Pipeline**:

1. **Stage 1 - Intent & Topic Classification**
   - Categorizes student input as:
     - "Technical Question"
     - "Prestructural Irrelevant"
     - "Follow-up Answer"
   - Identifies relevant course topics from a predefined topic list

2. **Stage 2 - SOLO Taxonomy Classification**
   - Generates 5 parallel LLM predictions of the SOLO (Structural Object Learning Outcomes) taxonomy levels:
     - **Unistructural**: Single fact or definition
     - **Multistructural**: Multiple concepts from the same topic
     - **Relational**: Comparisons and integration across topics
     - **Extended Abstract**: Real-world application of concepts
   - Applies majority voting to determine the final SOLO level consensus
   - Routes unresolved cases to domain experts for manual review

**Domain Knowledge**:
- Course topics specific to Process Control and Dynamics
- SOLO taxonomy framework for cognitive complexity assessment
- LLM-based classification with calibrated confidence scoring

---

### Survey Analysis

#### 3. **survey_analysis.ipynb**

**Purpose**: Analyze user feedback and survey responses about the chatbot system.

**Key Steps**:
- Load survey response data
- Clean and preprocess survey answers
- Perform statistical analysis on user feedback on SRL processes
- Generate visualizations of survey metrics
- Identify trends and patterns in SRL processes

**Output**: Aggregated survey statistics and visual reports

---

## 🔧 Requirements & Setup

### Python Dependencies

Ensure the following packages are installed before running the notebooks:

```bash
pip install pandas pydantic aiohttp
```

### Environment Variables

For notebooks that interact with LLM APIs (majority voting pipelines), set the following environment variables:

```bash
export NALA_API_KEY="your_api_key_here"
export NALA_BASE_URL="https://your_api_endpoint"
```

### Input Data Files

- `NALA_full_data.csv` - Raw conversation data for NALA dataset
- `NALA_Assess_full_data.csv` - Raw conversation data for NALA_Assess dataset
- Survey response data file (format specified in `survey_analysis.ipynb`)

