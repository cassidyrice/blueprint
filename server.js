
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Endpoint to run the Python script
app.post('/api/calculate', (req, res) => {
    const { birthdate } = req.body;
    if (!birthdate) {
        return res.status(400).json({ error: 'Birthdate is required' });
    }

    // Format birthdate as MM/DD/YYYY if it isn't already
    // The Python script expects MM/DD/YYYY
    
    const scriptPath = path.join(__dirname, 'calculate_blueprint.py');
    
    // The Python script expects: calculate_blueprint.py <month> <day> <year>
    const dateParts = birthdate.split('/');
    if (dateParts.length !== 3) {
        return res.status(400).json({ error: 'Invalid date format. Use MM/DD/YYYY' });
    }
    const [month, day, year] = dateParts;
    const pythonCmd = `python "${scriptPath}" ${month} ${day} ${year}`;

    exec(pythonCmd, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).json({ error: 'Failed to calculate blueprint', details: stderr });
        }
        
        // The script outputs the result to stdout
        res.json({ output: stdout });
    });
});

// Endpoint to interact with NotebookLM via the MCP client
// This will be a "mock" or "stub" for now until we define the exact automation flow
app.post('/api/generate-assets', async (req, res) => {
    const { blueprintData, type } = req.body;
    
    // In a real implementation, we would call the `notebooklm-mcp` CLI or library here
    // since we've already authenticated.
    
    const promptMap = {
        podcast: "Create a long detailed podcast based on this blueprint data. Focus on relative insights for the year.",
        infographic: "Create a detailed infographic layout based on this blueprint data.",
        slides: "Create a slide deck outline based on this blueprint data."
    };

    const prompt = promptMap[type] || "Process this blueprint data.";
    
    // Construct the CLI command to chat with NotebookLM
    // python -c "from notebooklm_mcp import cli; import sys; sys.argv=['notebooklm-mcp', '--config', 'notebooklm-config.json', 'chat', '--message', '...']; cli.main()"
    
    const fullMessage = `${prompt}\n\nData:\n${blueprintData}`;
    const truncatedMessage = fullMessage.substring(0, 5000); // Safety truncation

    const pythonCmd = `python -c "from notebooklm_mcp import cli; import sys; sys.argv=['notebooklm-mcp', '--config', 'notebooklm-config.json', 'chat', '--message', ${JSON.stringify(truncatedMessage)}]; cli.main()"`;

    exec(pythonCmd, (error, stdout, stderr) => {
        if (error) {
            console.error(`NotebookLM error: ${error}`);
            return res.status(500).json({ error: 'Failed to generate asset', details: stderr });
        }
        res.json({ result: stdout });
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
