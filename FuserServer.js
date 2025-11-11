// server.js
import { WebSocketServer } from 'ws';

const wss = new WebSocketServer({ port: 8080 });
let clients = {}; // { userId: ws }

wss.on('connection', (ws) => {
  let userId = null;

  ws.on('message', (msg) => {
    let data;
    try { data = JSON.parse(msg); } 
    catch(e) { console.log("Invalid JSON", msg); return; }

    if(data.type === "register") {
      userId = data.userId;
      clients[userId] = ws;
      broadcastUserList();
    } else if(data.type === "chat") {
      if(data.target && clients[data.target]) {
        // chat privé
        clients[data.target].send(JSON.stringify(data));
      } else {
        // chat public
        broadcast(JSON.stringify(data));
      }
    } else if(data.type === "control") {
      // event clavier/souris
      if(data.to && clients[data.to]) {
        clients[data.to].send(JSON.stringify(data));
      }
    }
  });

  ws.on('close', () => {
    if(userId) {
      delete clients[userId];
      broadcastUserList();
    }
  });

  function broadcastUserList() {
    const list = Object.keys(clients);
    broadcast(JSON.stringify({ type: "userlist", users: list }));
  }

  function broadcast(message) {
    Object.values(clients).forEach(c => {
      try { c.send(message); } catch(e){ }
    });
  }
});

console.log("WebSocket server running on ws://0.0.0.0:8080");
