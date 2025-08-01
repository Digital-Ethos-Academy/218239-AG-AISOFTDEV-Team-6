import React, { useState, useRef, useEffect } from 'react';

/**
 * Chat component for Momentum Dashboard
 * Features:
 * - WebSocket connection to /chat endpoint
 * - Message input
 * - Message history
 * - Scroll to latest message
 * - Simple styling
 */
const Chat = () => {
  const [messages, setMessages] = useState([
    { sender: 'assistant', text: 'Hello! How can I help you today!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const [username] = useState(() => `User${Math.floor(Math.random() * 1000)}`);
  const processedMessages = useRef(new Set()); // Track processed messages to prevent duplicates

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // WebSocket connection management
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = new WebSocket('ws://localhost:8000/chat');
        wsRef.current = ws;

        ws.onopen = () => {
          setConnectionStatus('connected');
          setMessages(prev => [...prev, { 
            sender: 'system', 
            text: 'Connected to chat server' 
          }]);
        };

        ws.onmessage = (event) => {
          try {
            const messageData = JSON.parse(event.data);
            console.log('Received WebSocket message:', messageData);
            console.log('Current username:', username);
            
            // Create a unique identifier for each message
            const messageId = `${messageData.user}-${messageData.timestamp}-${messageData.message}`;
            
            if (messageData.type === 'message') {
              if (messageData.user !== username) {
                // Check if we've already processed this message
                if (!processedMessages.current.has(messageId)) {
                  console.log('Adding message from other user:', messageData.user);
                  processedMessages.current.add(messageId);
                  
                  // Received message from another user
                  setMessages(prev => {
                    const newMessage = {
                      sender: 'other',
                      text: `${messageData.user}: ${messageData.message}`,
                      timestamp: messageData.timestamp
                    };
                    console.log('Current messages count:', prev.length);
                    return [...prev, newMessage];
                  });
                } else {
                  console.log('Duplicate message detected, ignoring');
                }
              } else {
                console.log('Ignoring own message from WebSocket');
              }
            } else if (messageData.type === 'response') {
              console.log('Adding response message');
              // Received echo response
              setMessages(prev => [...prev, {
                sender: 'assistant',
                text: messageData.message,
                timestamp: messageData.timestamp
              }]);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          setConnectionStatus('disconnected');
          setMessages(prev => [...prev, { 
            sender: 'system', 
            text: 'Disconnected from chat server' 
          }]);
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setConnectionStatus('error');
        };
      } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        setConnectionStatus('error');
      }
    };

    connectWebSocket();

    // Cleanup on component unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [username]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    
    console.log('Sending message:', input);
    console.log('Username:', username);
    
    const userMsg = { sender: 'user', text: input };
    setMessages((msgs) => {
      console.log('Adding local message, current count:', msgs.length);
      return [...msgs, userMsg];
    });
    
    // Send message via WebSocket
    const messageData = {
      type: 'broadcast',
      user: username,
      message: input,
      timestamp: new Date().toISOString()
    };
    
    console.log('Sending WebSocket message:', messageData);
    wsRef.current.send(JSON.stringify(messageData));
    setInput('');
  };

  return (
    <div className="flex flex-col h-full w-full bg-white border border-gray-200 shadow-md p-4">
      {/* Connection Status */}
      <div className="mb-2 text-xs text-center">
        <span className={`inline-block w-2 h-2 rounded-full mr-2 ${
          connectionStatus === 'connected' ? 'bg-green-500' : 
          connectionStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
        }`}></span>
        {connectionStatus === 'connected' ? 'Connected' : 
         connectionStatus === 'error' ? 'Connection Error' : 'Connecting...'}
      </div>
      
      <div className="flex-1 overflow-y-auto mb-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`mb-2 flex ${
            msg.sender === 'user' ? 'justify-end' : 
            msg.sender === 'system' ? 'justify-center' : 'justify-start'
          }`}>
            <div className={`px-4 py-2 rounded-lg text-sm max-w-xs ${
              msg.sender === 'user' ? 'bg-blue-500 text-white' : 
              msg.sender === 'other' ? 'bg-green-500 text-white' :
              msg.sender === 'system' ? 'bg-yellow-100 text-yellow-800 text-xs' :
              'bg-gray-200 text-gray-800'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="flex">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded-l-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder={connectionStatus !== 'connected' ? "Connecting..." : "Type your message..."}
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={connectionStatus !== 'connected'}
        />
        <button
          type="submit"
          className="bg-[#5887E8] text-white px-4 py-2 rounded-r-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          disabled={connectionStatus !== 'connected' || !input.trim()}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
