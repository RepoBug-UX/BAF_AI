const readline = require('readline');
const axios = require('axios');
const chalk = require('chalk'); // Make sure to use version 4.1.2

// Create readline interface
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// Server URL
const SERVER_URL = 'http://localhost:3000';

// Store if we're waiting for deployment
let waitingForDeployment = false;

async function checkDeploymentStatus() {
  try {
    const response = await axios.get(`${SERVER_URL}/deployment/status`);
    
    if (response.data.status === 'complete') {
      const agent = response.data.agent;
      console.log(chalk.green.bold("\n✅ Agent deployed successfully!"));
      console.log(chalk.cyan("Agent ID:"), agent.agent.id);
      console.log(chalk.cyan("Description:"), agent.agent.description);
      console.log(chalk.cyan("Transaction:"), agent.agent.transaction);
      console.log(chalk.yellow("\nTo interact with this agent:"));
      console.log(chalk.yellow("- Use agent ID:"), agent.agent.id);
      
      waitingForDeployment = false;
      startChat(); // Back to chat mode
    } else {
      // Still deploying or no deployment
      console.log(chalk.yellow("Still waiting for deployment to complete..."));
      setTimeout(checkDeploymentStatus, 5000); // Check again in 5 seconds
    }
  } catch (error) {
    console.error(chalk.red("Error checking deployment status:"), error.message);
    waitingForDeployment = false;
    startChat(); // Back to chat mode anyway
  }
}

async function sendMessage(message) {
  try {
    console.log(chalk.blue("Sending message to Creator Agent..."));
    
    const response = await axios.post(`${SERVER_URL}/chat`, { message });
    
    console.log(chalk.green.bold("\nCreator Agent:"));
    console.log(chalk.green(response.data.response));
    
    // Check if this triggered a deployment
    if (response.data.deploying) {
      waitingForDeployment = true;
      console.log(chalk.yellow("\nDeploying agent to the blockchain..."));
      console.log(chalk.yellow("This may take a minute or two."));
      
      // Start checking for deployment status
      setTimeout(checkDeploymentStatus, 5000); // Start checking after 5 seconds
    } else {
      // Continue the chat
      startChat();
    }
    
  } catch (error) {
    console.error(chalk.red("Error:"), error.message);
    startChat(); // Continue the chat anyway
  }
}

function startChat() {
  if (waitingForDeployment) {
    console.log(chalk.yellow("\nStill waiting for deployment to complete..."));
    return;
  }
  
  rl.question(chalk.blue.bold('\nYou: '), (message) => {
    if (message.toLowerCase() === 'exit' || message.toLowerCase() === 'quit') {
      console.log(chalk.green('Goodbye!'));
      rl.close();
      process.exit(0);
    } else {
      sendMessage(message);
    }
  });
}

// Check connection to server before starting
async function checkServerConnection() {
  try {
    console.log(chalk.blue("Connecting to Creator Agent server..."));
    await axios.get(`${SERVER_URL}/deployment/status`);
    console.log(chalk.green("✅ Connected to server successfully!"));
    return true;
  } catch (error) {
    console.error(chalk.red("❌ Cannot connect to Creator Agent server!"));
    console.error(chalk.red(`Make sure the server is running at ${SERVER_URL}`));
    console.error(chalk.yellow("Run 'node server.js' in another terminal to start the server."));
    return false;
  }
}

// Start the application
async function main() {
  console.log(chalk.green.bold('=== Creator Agent Client ==='));
  
  const serverConnected = await checkServerConnection();
  if (!serverConnected) {
    console.log(chalk.red("Exiting due to server connection failure."));
    rl.close();
    process.exit(1);
  }
  
  console.log(chalk.green('I can deploy AI agents to the blockchain for you.'));
  console.log(chalk.green('Try: "Create and deploy an agent that responds with a joke"'));
  console.log(chalk.green('Type "exit" to quit.'));

  // Start the conversation
  startChat();
}

main();