import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';

function App() {
  const [username, setUsername] = useState('');
  const [registered, setRegistered] = useState(false);
  const [peers, setPeers] = useState({});
  const [message, setMessage] = useState('');
  const [recipient, setRecipient] = useState('');
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const newSocket = io('http://localhost:5000');
    setSocket(newSocket);

    newSocket.on('registration_response', (response) => {
      alert(response.message);
      if (response.status === 'success') {
        setRegistered(true);
      }
    });

    newSocket.on('receive_message', (data) => {
      alert(`New message from ${data.from}: ${data.content}`);
    });

    newSocket.on('message_status', (response) => {
      alert(response.message);
    });

    newSocket.on('update_peers', (peers) => {
      setPeers(peers);
    });

    return () => newSocket.close();
  }, [setSocket]);

  const handleRegister = () => {
    socket.emit('register', { username });
  };

  const sendMessage = () => {
    if (!recipient) {
      alert('Select a recipient');
      return;
    }
    socket.emit('send_message', {
      from: username,
      to: recipient,
      content: message
    });
  };

  return (
    <div>
      {!registered && (
        <div>
          <input type="text" placeholder="Enter username" value={username} onChange={e => setUsername(e.target.value)} />
          <button onClick={handleRegister}>Register</button>
        </div>
      )}
      {registered && (
        <div>
          <h2>Peers</h2>
          <select onChange={e => setRecipient(e.target.value)}>
            <option value="">Select a peer</option>
            {Object.keys(peers).map((peerName) => (
              <option key={peerName} value={peerName}>{peerName}</option>
            ))}
          </select>
          <textarea value={message} onChange={e => setMessage(e.target.value)}></textarea>
          <button onClick={sendMessage}>Send Message</button>
        </div>
      )}
    </div>
  );
}

export default App;
