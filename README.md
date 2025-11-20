# 🌍 AI Travel Agent - Multi-Agent Travel Planning System

A sophisticated, production-ready AI-powered travel planning application that uses multi-agent architecture with LangGraph to provide intelligent flight and hotel booking assistance. Features real-time WebSocket communication, multi-leg flight support, and a beautiful dark/light mode interface.

![React](https://img.shields.io/badge/React-19.2.0-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-3178C6?logo=typescript)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Latest-FF6B6B)
![Google Gemini](https://img.shields.io/badge/Gemini-2.5--flash-4285F4?logo=google)

## ✨ Features

### 🤖 Intelligent Multi-Agent System
- **Natural Language Understanding**: Uses Google Gemini 2.5-flash-lite for intent classification
- **Multi-Agent Architecture**: Built with LangGraph for stateful, graph-based workflows
- **Context-Aware Responses**: Maintains conversation history and user preferences
- **Real-time Communication**: WebSocket-based bidirectional streaming

### ✈️ Advanced Flight Search
- **Multi-Leg Flight Support**: Handle complex itineraries (e.g., NYC → London → Paris → NYC)
- **Layover Visualization**: Display connection times and layover cities
- **Realistic Flight Data**: Mock data with actual airport codes, airlines, and flight numbers
- **Price Comparison**: Interactive charts showing price trends
- **Interactive Maps**: Real-time flight path visualization with React-Leaflet

### 🏨 Comprehensive Hotel Booking
- **Smart Hotel Search**: Location-based hotel recommendations
- **Amenity Filtering**: Search by facilities (WiFi, pool, gym, etc.)
- **Guest Management**: Flexible check-in/check-out date selection
- **Room Selection**: Multiple room types (Standard, Deluxe, Suite, Penthouse)
- **Map Integration**: Hotel location visualization

### 🎨 Modern User Interface
- **Dark/Light Mode**: Persistent theme switching with smooth transitions
- **Responsive Design**: Mobile-first approach, works on all devices
- **Loading States**: Skeleton loaders and smooth animations
- **Real-time Updates**: Live agent status indicators
- **Accessibility**: ARIA labels and keyboard navigation support

### 📧 Booking Management
- **Separate Booking Flows**: Different workflows for flights vs. hotels
- **HTML Itineraries**: Beautiful, printable confirmation emails
- **Passenger/Guest Information**: Comprehensive data collection
- **Payment Integration**: Mock payment processing (ready for real integration)

## 🏗️ Architecture

### Backend Architecture
```
FastAPI Application
├── Multi-Agent System (LangGraph)
│   ├── Intent Classification (Gemini)
│   ├── Flight Search Agent
│   ├── Hotel Search Agent
│   ├── Booking Agent
│   └── Summarization Agent
├── WebSocket Manager (Real-time Communication)
├── Event Manager (Server-Sent Events)
├── Services
│   ├── Booking Service (Itinerary Generation)
│   ├── Preferences Manager
│   └── Summarization Service
└── Mock Data Providers
    ├── Flight Generator (Multi-leg Support)
    └── Hotel Generator
```

### Frontend Architecture
```
React 19 + TypeScript
├── WebSocket Hook (Real-time Updates)
├── Theme Context (Dark/Light Mode)
├── Components
│   ├── MessageList (Chat Interface)
│   ├── BookingModal (Multi-step Forms)
│   ├── AgentStatus (Live Indicators)
│   ├── PreferencesPanel (User Settings)
│   └── Visualizations
│       ├── FlightMap (Route Visualization)
│       ├── FlightTimeline (Multi-leg Display)
│       ├── HotelMap (Location Markers)
│       └── PriceChart (Comparison Charts)
└── Types (TypeScript Definitions)
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.9+** (Backend)
- **Node.js 18+** (Frontend)
- **Google Gemini API Key** (Required for NLU)
- **Tavily API Key** (Optional - for web search)

### Installation

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd PECATHON
```

#### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Environment Variables
Create a `.env` file in the `backend` directory:
```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional
TAVILY_API_KEY=your_tavily_api_key_here
```

**Getting API Keys:**
- **Google Gemini**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Tavily** (optional): Visit [Tavily](https://tavily.com/)

#### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

### Running the Application

#### Quick Start (Using Shell Scripts)
```bash
# From project root
chmod +x start.sh
./start.sh
```

#### Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Cleanup
```bash
# Stop all processes
chmod +x cleanup.sh
./cleanup.sh
```

## 📖 Usage Guide

### Basic Conversation
1. **Start a conversation**: Type naturally, e.g., "I need a flight to Paris"
2. **Review results**: Browse flights or hotels with detailed information
3. **Book**: Click "Book Now" and complete the multi-step form
4. **Download itinerary**: Receive a beautiful HTML confirmation

### Multi-Leg Flights
```
User: "Book a round-trip flight from New York to Paris with a layover in London"
Agent: [Displays multi-leg flight options with segment details and layover times]
```

### Hotel Search
```
User: "Find me a luxury hotel in Tokyo with a pool"
Agent: [Shows hotels with amenities, pricing, and location maps]
```

### Setting Preferences
- Click the preferences icon in the input box
- Set budget ranges, preferred airlines, amenities
- Preferences persist across the session

## 🛠️ Tech Stack

### Backend
| Technology | Purpose | Version |
|-----------|---------|---------|
| FastAPI | Web framework | Latest |
| Python | Core language | 3.9+ |
| LangGraph | Multi-agent orchestration | Latest |
| LangChain | LLM integrations | Latest |
| Google Gemini | Natural language processing | 2.5-flash-lite |
| Pydantic | Data validation | 2.x |
| Uvicorn | ASGI server | Latest |
| WebSockets | Real-time communication | Latest |
| Tavily | Web search (optional) | Latest |

### Frontend
| Technology | Purpose | Version |
|-----------|---------|---------|
| React | UI framework | 19.2.0 |
| TypeScript | Type safety | 5.9.3 |
| Vite | Build tool | 5.1.1 |
| Axios | HTTP client | Latest |
| React-Leaflet | Map visualization | Latest |
| Recharts | Data visualization | Latest |
| Lucide Icons | Icon library | Latest |

## 📁 Project Structure

```
PECATHON/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Configuration
│   │   ├── constants.py         # Constants and enums
│   │   ├── models.py            # Pydantic models
│   │   ├── llm.py               # Gemini client
│   │   ├── tools.py             # Agent tools
│   │   ├── graph/
│   │   │   └── travel_graph.py  # LangGraph workflow
│   │   ├── services/
│   │   │   ├── booking_service.py
│   │   │   ├── event_manager.py
│   │   │   ├── preferences.py
│   │   │   └── summarization.py
│   │   ├── travel/
│   │   │   ├── mock_flights.py  # Flight data generator
│   │   │   └── mock_hotels.py   # Hotel data generator
│   │   └── websocket/
│   │       └── manager.py       # WebSocket handler
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app component
│   │   ├── main.tsx             # Entry point
│   │   ├── types.ts             # TypeScript types
│   │   ├── components/
│   │   │   ├── MessageList.tsx
│   │   │   ├── BookingModal.tsx
│   │   │   ├── AgentStatus.tsx
│   │   │   ├── PreferencesPanel.tsx
│   │   │   └── Visualizations/
│   │   ├── contexts/
│   │   │   └── ThemeContext.tsx
│   │   └── hooks/
│   │       └── useWebSocket.ts
│   ├── package.json
│   └── vite.config.ts
├── start.sh                      # Quick start script
├── cleanup.sh                    # Cleanup script
└── README.md
```

## 🔌 API Endpoints

### WebSocket
- **`/ws/{session_id}`** - Real-time bidirectional communication

### HTTP Endpoints
- **`GET /`** - Health check
- **`POST /chat`** - Process user message
- **`POST /booking/complete`** - Complete booking and generate itinerary
- **`GET /sse/{session_id}`** - Server-sent events stream

## 🎯 Key Features Explained

### Multi-Leg Flight Implementation
The system generates realistic multi-leg flights with:
- **Flight Segments**: Individual legs with airline, flight number, duration
- **Layover Calculation**: Realistic connection times (45-180 minutes)
- **Total Journey Duration**: Sum of flight times + layovers
- **Visual Indicators**: Orange dots for each layover city
- **Expandable Details**: Click to see full segment breakdown

### Separate Booking Flows
- **Flights**: Passenger Info → Seat Selection → Payment → Confirmation
- **Hotels**: Guest Info → Room Selection → Payment → Confirmation
- Different data models and validation for each type

### Theme System
- **Persistent Storage**: Saves preference in localStorage
- **System Detection**: Auto-detects OS dark mode preference
- **Smooth Transitions**: CSS transitions for theme changes
- **Context-based**: React Context for global state

## 🔧 Configuration

### Backend Configuration (`backend/app/config.py`)
```python
GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")  # Required
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")  # Optional
MODEL_NAME="gemini-2.0-flash-exp"
TEMPERATURE=0.7
MAX_TOKENS=8000
```

### Frontend Configuration (`frontend/vite.config.ts`)
```typescript
server: {
  port: 5173,
  proxy: {
    '/ws': 'ws://localhost:8000',
    '/api': 'http://localhost:8000'
  }
}
```

## 🐛 Troubleshooting

### Backend Issues

**Port Already in Use:**
```bash
lsof -ti:8000 | xargs kill -9
```

**Missing API Key:**
```
Error: GOOGLE_API_KEY not found
Solution: Create .env file with valid API key
```

**Module Not Found:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 in Use:**
```bash
lsof -ti:5173 | xargs kill -9
```

**Dependency Errors:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**WebSocket Connection Failed:**
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`

## 🚀 Production Deployment

### Backend (Recommended: Railway, Render, AWS)
```bash
# Example for Railway
railway login
railway init
railway up
```

### Frontend (Recommended: Vercel, Netlify)
```bash
# Example for Vercel
vercel --prod
```

### Environment Variables
Set these in your hosting platform:
- `GOOGLE_API_KEY`
- `TAVILY_API_KEY` (optional)
- `FRONTEND_URL` (for CORS)

## 📝 Development Notes

### Adding New Features
1. **Backend**: Add tools in `tools.py`, update graph in `travel_graph.py`
2. **Frontend**: Create component in `components/`, add types in `types.ts`
3. **State**: Update `models.py` for new data structures

### Code Quality
- **Backend**: PEP 8 compliant, type hints everywhere
- **Frontend**: ESLint configured, strict TypeScript

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** for powerful NLU capabilities
- **LangGraph** for multi-agent orchestration
- **React-Leaflet** for beautiful map visualizations
- **Recharts** for interactive data visualization
- **FastAPI** for high-performance async API framework

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
---

**Built with ❤️ for intelligent travel planning**

*Last updated: January 2025*
