# Advanced Chainlit Configuration

This project demonstrates advanced Chainlit features including custom themes, authentication, and components.

## Project Structure

```
02_advanced_config/
├── app.py                  # Main application with advanced features
├── pyproject.toml         # Project dependencies
├── Dockerfile             # Container configuration
├── custom_theme/         # Custom UI theme configuration
│   ├── theme.py         # Theme definition
│   └── styles.css       # Custom CSS
├── custom_auth/         # Authentication implementation
│   ├── auth.py         # Auth providers setup
│   └── middleware.py   # Auth middleware
└── custom_components/   # Custom React components
    ├── Message.tsx     # Custom message component
    └── Sidebar.tsx     # Custom sidebar component
```

## Features

### 1. Custom Theme
- Custom color scheme
- Dark/light mode toggle
- Responsive design
- Custom fonts and styling

### 2. Authentication
- Multiple auth providers (Google, GitHub)
- Role-based access control
- Session management
- Protected routes

### 3. Custom Components
- Enhanced message display
- Custom sidebar navigation
- Interactive elements
- Markdown extensions

## Setup Instructions

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Configure authentication:
   - Set up OAuth credentials
   - Configure auth providers
   - Set environment variables

3. Customize theme:
   - Modify theme.py
   - Update styles.css
   - Test different configurations

4. Build and run:
   ```bash
   docker build -t chainlit-advanced .
   docker run -p 7860:7860 -e GEMINI_API_KEY=your-key chainlit-advanced
   ```

## Development Guidelines

1. Theme Customization
   - Use CSS variables for consistency
   - Follow accessibility guidelines
   - Test across devices

2. Authentication Setup
   - Implement secure session handling
   - Use environment variables for secrets
   - Add rate limiting

3. Component Development
   - Follow React best practices
   - Maintain type safety
   - Document props and usage

## Configuration

### Environment Variables
```env
GEMINI_API_KEY=your-key
AUTH_SECRET=your-secret
OAUTH_CLIENT_ID=your-client-id
OAUTH_CLIENT_SECRET=your-client-secret
```

### Theme Configuration
```python
# theme.py
CUSTOM_THEME = {
    "primary": "#007AFF",
    "secondary": "#6C757D",
    "background": "#F8F9FA"
}
```

## Deployment

1. Build the Docker image
2. Set up environment variables
3. Deploy to Hugging Face Spaces
4. Configure authentication providers
5. Test all features

## Notes

- Keep sensitive information in environment variables
- Test authentication flows thoroughly
- Monitor performance with custom components
- Update theme according to brand guidelines 