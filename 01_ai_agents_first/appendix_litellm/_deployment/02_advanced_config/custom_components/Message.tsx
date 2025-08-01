import React from 'react';
import { Box, Typography, useTheme } from '@mui/material';
import { Message as ChainlitMessage } from '@chainlit/components';

interface MessageProps {
  content: string;
  avatar?: string;
  author: string;
  createdAt: string;
  type: 'user' | 'assistant';
}

export const CustomMessage: React.FC<MessageProps> = ({
  content,
  avatar,
  author,
  createdAt,
  type
}) => {
  const theme = useTheme();
  
  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        padding: 2,
        borderRadius: 2,
        backgroundColor: type === 'user' 
          ? theme.message.user.background 
          : theme.message.assistant.background,
        color: type === 'user'
          ? theme.message.user.text
          : theme.message.assistant.text,
        maxWidth: '80%',
        alignSelf: type === 'user' ? 'flex-end' : 'flex-start'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {avatar && (
          <img 
            src={avatar} 
            alt={author}
            style={{ 
              width: 24, 
              height: 24, 
              borderRadius: '50%' 
            }} 
          />
        )}
        <Typography variant="subtitle2">{author}</Typography>
        <Typography variant="caption" color="text.secondary">
          {new Date(createdAt).toLocaleTimeString()}
        </Typography>
      </Box>
      
      <Typography variant="body1">
        {content}
      </Typography>
    </Box>
  );
};

// Register the custom component with Chainlit
ChainlitMessage.register('custom', CustomMessage); 