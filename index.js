#!/usr/bin/env node

const { spawn } = require("child_process");
const path = require("path");

const pythonProcess = spawn(
    "python",
    [path.join(__dirname, "main.py")],
    {
        stdio: "inherit"
    }
);

pythonProcess.on("exit", (code) => {
    process.exit(code);
});
