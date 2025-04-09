# Supervity Research Platform

An advanced corporate research and analysis platform that allows users to research companies, upload documents, and interact with AI-powered reports through a modern user interface.

## Project Structure

This project consists of two main components:

1. **Frontend**: A Next.js web application with a modern UI for interacting with the research platform.
2. **Backend**: A Flask API server that integrates with the existing Python-based research agent.

## Features

- User authentication (login/register)
- Company research with AI-powered analysis
- Document upload for RAG chatbot
- Integration with third-party services (Salesforce, HubSpot, Snowflake)
- Interactive chat interface with research assistant
- Beautiful report visualization with download options
- Responsive, modern UI with dark mode theme

## Tech Stack

### Frontend
- **Framework**: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **State Management**: React Context API, React Hooks
- **UI Libraries**: Framer Motion, Lucide React icons

### Backend
- **Server**: Flask
- **Authentication**: JWT-based authentication
- **Integration**: Python-based research agent

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- npm or yarn
- Python 3.10 or higher

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

For convenience, you can use the start script to run both frontend and backend:

```bash
chmod +x start.sh
./start.sh
```

Or run them separately:

**Frontend**:
```bash
cd frontend
npm run dev
```

**Backend**:
```bash
cd backend
FLASK_ENV=development python app.py
```

The frontend will be available at http://localhost:3000 and the backend API at http://localhost:5000.

## API Documentation

The backend API provides endpoints for:

- Authentication (/api/auth/*)
- Company research (/api/company/*)
- Document management (/api/documents/*)
- Report generation (/api/reports/*)
- Chat functionality (/api/chat/*)

For detailed API documentation, see the README.md in the backend directory.

## Development Roadmap

1. Enhance the backend integration with more sophisticated AI capabilities
2. Add analytics dashboard for research insights
3. Implement real-time collaboration features
4. Expand third-party integrations
5. Add support for more document types and analysis methods

## License

Proprietary - All rights reserved 