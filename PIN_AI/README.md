# Creator Agent: AI Agent Deployment Platform

This project allows you to design and deploy AI agents to the Base Sepolia blockchain using natural language. The Creator Agent uses OpenAI's GPT models to design agents based on your description and deploys them as on-chain components.

## Overview

The Creator Agent consists of:
- A Node.js server that handles agent design and blockchain deployment
- A command-line client for interacting with the Creator Agent
- Blockchain integration with the Base Sepolia network

## Prerequisites

- Node.js (v14 or higher)
- npm
- Git
- An OpenAI API key
- A crypto wallet with Base Sepolia ETH (for gas fees)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/creator-agent.git
   cd creator-agent
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Configuration

1. Create a `.env` file in the project root with the following variables:
   ```
   # OpenAI API Key - Get this from https://platform.openai.com/api-keys
   OPENAI_API_KEY=sk-your-openai-key-here
   
   # Blockchain Configuration
   PRIVATE_KEY=0xyour-wallet-private-key-here
   RPC_URL=https://base-sepolia-rpc.publicnode.com
   
   # Optional: Server port (defaults to 3000)
   PORT=3000
   ```

2. Get Base Sepolia ETH for your wallet:
   - Use the Base Sepolia faucet: https://www.coinbase.com/faucets/base-sepolia-faucet
   - You'll need a small amount (0.02 ETH) to deploy agents

## Running the Creator Agent

1. Start the server:
   ```bash
   node server.js
   ```
   You should see output confirming connection to the Base Sepolia network and your wallet address.

2. In a separate terminal, start the client:
   ```bash
   node client.js
   ```

## Creating Your First AI Agent

Once both the server and client are running:

1. In the client terminal, you'll see a prompt asking for input
2. Enter a natural language description of the agent you want to create, for example:
   ```
   Create and deploy an agent that responds with a random joke whenever someone interacts with it
   ```

3. The Creator Agent will:
   - Design an agent based on your description
   - Deploy a component to Base Sepolia (this contains the agent's logic)
   - Deploy the agent itself, connecting it to the component
   - Provide you with details about your deployed agent

4. The deployment process takes approximately 1-2 minutes. You'll receive the following information when complete:
   - Agent ID
   - Transaction hash
   - Description of what your agent does

## How Agents Work

- Each agent consists of a component that defines its behavior
- Agents deployed through Creator Agent use a simple response pattern
- Anyone can interact with your agent by sending messages to it through the Base registry contract
- Agents run entirely on-chain, with no external dependencies after deployment

## Viewing Your Deployed Agents

Deployment information is stored in the `deployed-agents` directory as JSON files. Each file includes:
- Agent ID and hash
- Component ID and hash
- Transaction details
- Network information

## Troubleshooting

### Connection Issues
- If you see "Cannot detect network" errors, try changing your RPC_URL in the .env file
- Alternatives: `https://sepolia.base.org` or `https://1rpc.io/base-sepolia`

### Deployment Failures
- Ensure your wallet has sufficient Base Sepolia ETH (at least 0.02 ETH)
- Check that your PRIVATE_KEY is correctly formatted (should start with '0x')
- Verify that the Base Sepolia network is operational

## License

This project is licensed under the MIT License - see the LICENSE file for details.