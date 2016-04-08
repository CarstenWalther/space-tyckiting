AI1_CMD="node cli.js --ai=mastermind" 
AI2_CMD="node cli.js --ai=mastermind" 

cd server
node start-server.js &
sleep 0.5
firefox http://localhost:3000/ &
sleep 3
cd ../clients/javascript
($AI1_CMD) &
($AI2_CMD)
sleep 0.1