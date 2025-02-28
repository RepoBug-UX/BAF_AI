# NEAR AI X PIN AI Agents
## A Collection of Specialized AI Agents

### Developed agents built using NEAR AI's and PIN AI's tech stacks, in collaboration with the Blockchain Acceleration Foundation (BAF).

## Agents

### 1. Crypto Agent
- Real-time cryptocurrency price tracking using CoinMarketCap API
- Natural language query parsing for crypto prices
- Cryptocurrency conversion calculations
- Support for multiple cryptocurrencies and fiat currencies

### 2. Travel Agent
- Intelligent trip planning and organization
- Itinerary creation and management
- Accommodation recommendations
- Activity suggestions and travel tips
- Real-time travel assistance

### 3. Legal Agent
- Automated legal document generation
- Rental agreement creation with customizable templates
- PDF document generation with proper formatting
- Local document storage and management
- Support for various legal document types

## Features
- Multi-threaded agent execution
- Natural language processing
- Real-time API integrations
- PIN AI integration for enhanced reasoning capabilities
- Parallel request processing
- Thread-based conversation management

## Technical Integration
- Built on NEAR AI's agent framework
- Enhanced with PIN AI's advanced processing capabilities
- Modular architecture for easy extension
- Environment-based configuration
- Exception handling and graceful degradation

## Setup
Before starting, ensure you have:

1. macOS or Linux (Windows users should use WSL2 or a VM)
2. Python 3.9 - 3.11 (NEAR AI does not support Python 3.12+ yet)
3. Git installed
4. A NEAR Wallet

### **1. Check if **Homebrew** is already installed:**

```
which brew
```

If the output is empty, install Homebrew (**otherwise, skip this step**):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then, update your system:

```
brew update
```
---
### **2 Install Python Must Have 3.9-3.11**

First, check your Python version:

```
python3 --version
```

If you see **Python 3.9 - 3.11**, **If not, install Python 3.11**:

```
brew install python@3.11
```

Verify the installation:

```
python3 --version
```
---
### **3 Set Up a Virtual Environment**

To **isolate dependencies** and avoid conflicts, create a **virtual environment**:

```
cd ~
python3.11 -m venv nearai-env
source nearai-env/bin/activate
```

Confirm the virtual environment is active:

```
which python3
```

If everything is correct, you should see:

```
/Users/your_username/nearai-env/bin/python3
```

## **4. Installing NEAR AI**

Now, install **NEAR AI CLI**:

```
pip install --upgrade pip setuptools
pip install nearai
```

Verify the installation:

```
python3 -m nearai version
```

Expected output (example):
```
0.1.13
```

## **5. Connecting Your NEAR Wallet**

Before creating an agent through NEAR, you need to **log in** to your NEAR Wallet:

```
nearai login
```

This will open a browser window asking you to **approve the authentication request** with your wallet.

## **6. Understanding Agent Files**

Agent folder contains:

**`agent.py`** – The core logic of the AI agent
**`metadata.json`** – The agent's metadata

Navigate to the agent directory:

```
cd ~/.nearai/registry/your_wallet.near/agent_name/0.0.1
```

### Setting The Agents


```
nearai agent create --name "agent_name"
```

For each agent, you'll need to:

1. Navigate to the agent directory
2. Update the metadata.json
3. Modify the agent.py file

#### Updating Metadata

For each agent, edit the `metadata.json` file:

```bash
nano metadata.json
```

Update the metadata according to the agent type:

#### Modifying agent.py

For each agent, you have two options:

1. Download the pre-built agents in the repository:

```bash
# Download An Agent

nearai registry download <your_wallet>.near/<agent_name>/latest

```

After downloading, the agents will be available in your local NEAR AI registry. You can then modify them according to your needs:

## **8. Running The Agents Locally**

To test each agent locally, run:

```bash
nearai agent interactive ~/.nearai/registry/<your_wallet>.near/<agent_name>/0.0.1 --local
```

## **9. Next Steps**

For further reading, check the [NEAR AI Documentation](https://docs.near.ai/)

## Usage
Each agent can be run independently or as part of the multi-threaded system:
- For crypto tracking: Use keywords related to cryptocurrencies
- For travel planning: Include travel-related terms in your query
- For legal planning: Specify the type of document needed

<<<<<<< HEAD
=======
 Built using NearAI's and PINAI's tech stacks, in collaboration with the Blockchain Acceleration Foundation. 
>>>>>>> f04e7019b7c6d8ef66d45d4a08dcd04608c6a6ba
