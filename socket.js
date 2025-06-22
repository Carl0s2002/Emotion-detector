import { io } from "socket.io-client";

export const socket = io(
  window.location.protocol === "https:"        
    ? "wss://localhost:5000"
    : "ws://localhost:5000",
  {
    transports: ["websocket"],               
  }
);
