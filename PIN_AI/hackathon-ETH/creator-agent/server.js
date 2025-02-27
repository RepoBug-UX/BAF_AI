const express = require('express');
const { OpenAI } = require('openai');
const { ethers } = require('ethers');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs').promises;
const path = require('path');
const dotenv = require('dotenv');

dotenv.config();

// Initialize Express
const app = express();
app.use(cors());
app.use(bodyParser.json());

// Configure OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Configure Ethereum with better error handling
const RPC_URL = process.env.RPC_URL || "https://sepolia.base.org";
console.log("Connecting to network:", RPC_URL);

// Create provider with more reliable connection
let provider;
try {
  // Try more reliable RPC URLs if the default doesn't work
  provider = new ethers.providers.JsonRpcProvider(RPC_URL);
  
  // Test the connection
  provider.getNetwork().then(network => {
    console.log("Successfully connected to network:", network.name);
    console.log("Chain ID:", network.chainId);
  }).catch(error => {
    console.error("Network test failed, trying fallback URLs...");
    // Try alternative URLs
    tryFallbackProviders();
  });
} catch (error) {
  console.error("Error creating provider:", error);
  tryFallbackProviders();
}

function tryFallbackProviders() {
  // List of fallback RPC URLs for Base Sepolia
  const fallbackUrls = [
    "https://base-sepolia-rpc.publicnode.com",
    "https://sepolia.base.org",
    "https://1rpc.io/base-sepolia"
  ];
  
  let connected = false;
  
  // Try each fallback URL
  for (const url of fallbackUrls) {
    try {
      console.log("Trying fallback RPC URL:", url);
      provider = new ethers.providers.JsonRpcProvider(url);
      
      // Test if it works
      provider.getBlockNumber().then(() => {
        console.log("Connected to fallback RPC:", url);
        connected = true;
        // Initialize wallet with the working provider
        wallet = new ethers.Wallet(process.env.PRIVATE_KEY || "", provider);
        console.log("Wallet initialized with address:", wallet.address);
      }).catch(err => {
        console.log("Fallback connection failed:", url);
      });
      
      if (connected) break;
    } catch (error) {
      console.error("Error with fallback URL:", url, error.message);
    }
  }
  
  if (!connected) {
    console.error("CRITICAL ERROR: Could not connect to any RPC endpoint!");
    console.error("Please check your internet connection and RPC URL configuration.");
  }
}

// Initialize wallet after provider is set up
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY || "", provider);
console.log("Wallet address:", wallet.address);

// Registry address on Base Sepolia
const REGISTRY_ADDRESS = "0x9c7a943f0c1686d68136831bd502bc7925bd4f43";
const REGISTRY_ABI = [
  "function create(address owner, bytes32 hash, uint256[] memory dependencies) external payable returns (uint256 unitId)",
  "function getUnitById(uint256 unitId) external view returns (address)",
  "event CreateUnit(uint256 indexed unitId, address indexed owner, bytes32 indexed hash)"
];

// Store deployed agents
const AGENTS_DIR = path.join(__dirname, 'deployed-agents');

// Make sure the agents directory exists
(async () => {
  try {
    await fs.mkdir(AGENTS_DIR, { recursive: true });
  } catch (err) {
    console.error("Error creating agents directory:", err);
  }
})();

// Chat history for context
let chatHistory = [];

// Main chat endpoint
app.post('/chat', async (req, res) => {
  try {
    const { message } = req.body;
    chatHistory.push({ role: 'user', content: message });
    
    console.log("User:", message);
    
    // Check if this is a deployment request
    if (message.toLowerCase().includes("create") && 
        message.toLowerCase().includes("agent") && 
        message.toLowerCase().includes("deploy")) {
      
      // This is a deployment request
      const creatorResponse = "I'll create and deploy an agent for you. First, let me design it...";
      chatHistory.push({ role: 'assistant', content: creatorResponse });
      console.log("Creator:", creatorResponse);
      
      // Send initial response
      res.json({ 
        response: creatorResponse,
        deploying: true
      });
      
      // Start the deployment process asynchronously
      deployAgent(message)
        .then(deploymentResult => {
          // Log the completion (client will poll for updates)
          console.log("Deployment complete:", deploymentResult.agentId);
        })
        .catch(err => {
          console.error("Deployment error:", err);
        });
      
      return;
    }
    
    // Regular conversation
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        { 
          role: 'system', 
          content: 'You are the Creator Agent, an AI that can deploy other AIs to the blockchain. You can create agents when asked with phrases like "create and deploy an agent that..." or "make an agent for...". Be helpful and informative about blockchain deployment.'
        },
        ...chatHistory
      ]
    });
    
    const creatorResponse = completion.choices[0].message.content;
    chatHistory.push({ role: 'assistant', content: creatorResponse });
    console.log("Creator:", creatorResponse);
    
    res.json({ response: creatorResponse });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: error.message });
  }
});

// Check deployment status endpoint
app.get('/deployment/status', async (req, res) => {
  try {
    // Get the latest deployment if any
    const files = await fs.readdir(AGENTS_DIR);
    if (files.length === 0) {
      return res.json({ status: 'none' });
    }
    
    // Sort files by date (newest first)
    const sortedFiles = files.sort((a, b) => {
      return parseInt(b.split('-')[0]) - parseInt(a.split('-')[0]);
    });
    
    const latestFile = sortedFiles[0];
    const deploymentData = JSON.parse(
      await fs.readFile(path.join(AGENTS_DIR, latestFile), 'utf8')
    );
    
    res.json({
      status: 'complete',
      agent: deploymentData
    });
    
  } catch (error) {
    console.error("Error checking deployment status:", error);
    res.status(500).json({ error: error.message });
  }
});

// Helper function to design and deploy an agent
async function deployAgent(userRequest) {
  try {
    console.log("Designing agent based on request:", userRequest);
    
    // Get AI design for the agent
    const design = await designAgent(userRequest);
    console.log("Agent design:", design);
    
    // Check network connection before deploying
    try {
      const network = await provider.getNetwork();
      console.log("Current network:", network.name, "Chain ID:", network.chainId);
      
      const balance = await wallet.getBalance();
      console.log("Wallet balance:", ethers.utils.formatEther(balance), "ETH");
      
      if (balance.lt(ethers.utils.parseEther("0.02"))) {
        throw new Error("Wallet balance too low to deploy agent! Need at least 0.02 ETH");
      }
    } catch (networkError) {
      console.error("Network check failed:", networkError.message);
      throw new Error("Cannot connect to blockchain network. Please check your RPC configuration.");
    }
    
    // Create the component
    const registry = new ethers.Contract(REGISTRY_ADDRESS, REGISTRY_ABI, wallet);
    
    console.log("Creating component...");
    const componentTx = await registry.create(
      wallet.address,
      design.componentHash,
      [],
      { 
        gasLimit: 500000,
        gasPrice: ethers.utils.parseUnits("1.5", "gwei")
      }
    );
    
    console.log("Component transaction sent:", componentTx.hash);
    const componentReceipt = await componentTx.wait();
    
    // Get component ID from logs
    let componentId = null;
    if (componentReceipt.logs && componentReceipt.logs[0] && componentReceipt.logs[0].topics && componentReceipt.logs[0].topics[1]) {
      componentId = ethers.BigNumber.from(componentReceipt.logs[0].topics[1]);
    } else {
      // Fallback ID
      componentId = ethers.BigNumber.from(1);
    }
    
    console.log("Component created, ID:", componentId.toString());
    
    // Wait a moment before creating the agent
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create the agent
    console.log("Creating agent...");
    const agentTx = await registry.create(
      wallet.address,
      design.agentHash,
      [componentId],
      {
        value: ethers.utils.parseEther("0.01"),
        gasLimit: 1000000,
        gasPrice: ethers.utils.parseUnits("1.5", "gwei")
      }
    );
    
    console.log("Agent transaction sent:", agentTx.hash);
    const agentReceipt = await agentTx.wait();
    
    // Get agent ID from logs
    let agentId = null;
    if (agentReceipt.logs && agentReceipt.logs[0] && agentReceipt.logs[0].topics && agentReceipt.logs[0].topics[1]) {
      agentId = ethers.BigNumber.from(agentReceipt.logs[0].topics[1]);
    } else {
      // Fallback ID
      agentId = ethers.BigNumber.from(2);
    }
    
    console.log("Agent created, ID:", agentId.toString());
    
    // Save deployment info
    const deploymentInfo = {
      request: userRequest,
      timestamp: new Date().toISOString(),
      agent: {
        id: agentId.toString(),
        hash: design.agentHash,
        transaction: agentTx.hash,
        description: design.description
      },
      component: {
        id: componentId.toString(),
        hash: design.componentHash,
        transaction: componentTx.hash
      },
      network: {
        name: "Base Sepolia",
        registryAddress: REGISTRY_ADDRESS
      },
      interactionCommands: {
        hardhat: `npx hardhat run scripts/interact.js --network baseSepolia`,
        curl: `curl -X POST -H "Content-Type: application/json" -d '{"agentId": "${agentId}"}'`
      }
    };
    
    const filename = `${Date.now()}-agent-${agentId}.json`;
    await fs.writeFile(
      path.join(AGENTS_DIR, filename),
      JSON.stringify(deploymentInfo, null, 2)
    );
    
    // Update chat history
    const deploymentSummary = `
✅ Agent successfully deployed!

**Agent Details:**
- ID: ${agentId}
- Transaction: ${agentTx.hash}
- Description: ${design.description}

**How to Interact:**
You can interact with this agent by sending messages to it through the registry contract. Use the agent ID ${agentId} to address your messages.
`;
    
    chatHistory.push({ role: 'assistant', content: deploymentSummary });
    
    return {
      agentId: agentId.toString(),
      txHash: agentTx.hash
    };
    
  } catch (error) {
    console.error("Deployment error:", error);
    
    // Update chat history with error
    chatHistory.push({ 
      role: 'assistant', 
      content: `I encountered an error while trying to deploy the agent: ${error.message}` 
    });
    
    throw error;
  }
}

// Helper function to design an agent based on user request
async function designAgent(userRequest) {
  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4",
      messages: [
        {
          role: 'system',
          content: `You are an expert blockchain agent designer. You need to create hash values for an agent that will be deployed on-chain.
          
  The agent should be designed based on the user's request. Create a component hash and an agent hash that encodes the functionality.
  
  Return a JSON object with the following format:
  {
    "componentHash": "0x...",
    "agentHash": "0x...",
    "description": "Brief description of what the agent does"
  }
  
  For the hashes, use the keccak256 hash of ABI-encoded values.
  For a component that responds with a specific message, encode: ["STATIC_RESPONSE", "The response message"]
  For an agent, encode: ["STATIC_AGENT", "Agent Name", "static://description"]`
        },
        {
          role: 'user',
          content: userRequest
        }
      ]
    });
    
    const responseText = completion.choices[0].message.content;
    console.log("AI response:", responseText);
    
    // Try to parse JSON from the text response
    try {
      // Look for JSON in the response
      const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/) || 
                        responseText.match(/```\n([\s\S]*?)\n```/) ||
                        responseText.match(/{[\s\S]*?}/);
                        
      let jsonStr = jsonMatch ? jsonMatch[0] : responseText;
      
      // Clean up the string if needed
      if (jsonStr.startsWith("```")) {
        jsonStr = jsonStr.replace(/```json\n|```\n|```/g, "");
      }
      
      const design = JSON.parse(jsonStr);
      
      // Fallback to creating our own hashes if the AI didn't provide valid ones
      if (!design.componentHash || !design.componentHash.startsWith("0x")) {
        // Extract a response message from the description
        const responseMessage = design.description || "Hello from the blockchain!";
        
        design.componentHash = ethers.utils.keccak256(
          ethers.utils.defaultAbiCoder.encode(
            ["string", "string"],
            ["STATIC_RESPONSE", responseMessage]
          )
        );
      }
      
      if (!design.agentHash || !design.agentHash.startsWith("0x")) {
        design.agentHash = ethers.utils.keccak256(
          ethers.utils.defaultAbiCoder.encode(
            ["string", "string", "string"],
            ["STATIC_AGENT", "Blockchain Agent", "static://blockchain-agent"]
          )
        );
      }
      
      return design;
    } catch (jsonError) {
      console.error("Error parsing JSON from response:", jsonError);
      throw jsonError;
    }
  } catch (error) {
    console.error("Error in designAgent function:", error);
    
    // Fallback to default values
    return {
      componentHash: ethers.utils.keccak256(
        ethers.utils.defaultAbiCoder.encode(
          ["string", "string"],
          ["STATIC_RESPONSE", "Hello from the blockchain!"]
        )
      ),
      agentHash: ethers.utils.keccak256(
        ethers.utils.defaultAbiCoder.encode(
          ["string", "string", "string"],
          ["STATIC_AGENT", "Blockchain Agent", "static://blockchain-agent"]
        )
      ),
      description: "A simple agent that responds with a greeting"
    };
  }
}

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Creator Agent server running on port ${PORT}`);
}); 