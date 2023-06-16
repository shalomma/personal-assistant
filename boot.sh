#!/bin/bash
echo "Booting Wizi"
echo "Wait for 5 seconds"
sleep 5
echo "Source venv"
source venv\bin\activate
echo "Source .env"
source .env
echo "Run Wizi"
python main.py