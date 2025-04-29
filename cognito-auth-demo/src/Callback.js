import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';

const Callback = () => {
  const [tokens, setTokens] = useState(null);
  const [error, setError] = useState(null);
  const hasFetched = useRef(false);

  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;

    const fetchTokens = async () => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');

      if (!code) {
        setError('Authorization code not found.');
        return;
      }

      const clientId = "r5n1u8dodck65qnftsc26bb4u";
      const clientSecret = 'ol6qjprdhfmd5hnvrn48vcl07uak4l4l4d33cfm878ljqcssc08';
      const redirectUri = "http://localhost:3000/callback";
      const tokenUrl = 'https://eu-west-2imng8pdh4.auth.eu-west-2.amazoncognito.com/oauth2/token';

      const basicAuth = btoa(`${clientId}:${clientSecret}`);

      try {
        const response = await axios.post(tokenUrl, 
          new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: clientId,
            code: code,
            redirect_uri: redirectUri,
          }),
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
              Authorization: `Basic ${basicAuth}`,
            },
          }
        );

        // Copy id_token to clipboard
        if (navigator.clipboard) {
          await navigator.clipboard.writeText(response.data.id_token);
          console.log('ID token copied to clipboard.');
        }

        setTokens(response.data);
      } catch (err) {
        console.error(err);
        setError('Failed to fetch tokens');
      }
    };

    fetchTokens();
  }, []);

  if (error) return <div>Error: {error}</div>;
  if (!tokens) return <div>Loading...</div>;

  return (
    <div>
      <h2>Tokens Received:</h2>
      <pre>{JSON.stringify(tokens, null, 2)}</pre>
    </div>
  );
};

export default Callback;