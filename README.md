# 🌍 AI Travel Agent - Multi-Agent Travel Planning System

A sophisticated, production-ready AI-powered travel planning application that uses multi-agent architecture with LangGraph to provide intelligent flight and hotel booking assistance. Features real-time WebSocket communication, multi-leg flight support, and a beautiful dark/light mode interface.

## ✨ Features

### 🤖 Intelligent Multi-Agent System
- **Natural Language Understanding**: Uses Google Gemini 2.5-flash-lite for intent classification
- **Multi-Agent Architecture**: Built with LangGraph for stateful, graph-based workflows
- **Context-Aware Responses**: Maintains conversation history and user preferences
- **Real-time Communication**: WebSocket-based bidirectional streaming
- **Voice Interface**: Speech-to-Text input and Text-to-Speech responses for hands-free interaction

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

## 🏗️ Architecture Overview

### Multi-Agent System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                             │
│                    (React + TypeScript)                         │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/WebSocket
┌─────────────────────────▼───────────────────────────────────────┐
│                   FASTAPI BACKEND                               │
│  ┌─────────────────┐  ┌─────────────────────────────────────┐  │
│  │   WebSocket     │  │          HTTP Endpoints            │  │
│  │   Manager       │  │                                     │  │
│  └─────────────────┘  └─────────────────────────────────────┘  │
└─────────────┬─────────────────────────┬─────────────────────────┘
              │                         │
              │                         │
┌─────────────▼─────┐        ┌──────────▼─────────────────────┐
│  LangGraph Graph  │        │        Services Layer          │
│                   │        │  ┌────────────────────────────┐ │
│  Coordinator      │        │  │ Booking Service            │ │
│  Agent            │◄───────┤  │ Preferences Manager         │ │
│  (Intent Route)   │        │  │ Event Manager              │ │
│                   │        │  │ Summarization Service      │ │
│  Flight Agent ────┼────────┼─►│ Travel Mock Data          │ │
│  Hotel Agent  ────┼────────┼─►│ - Mock Flights             │ │
│  Response Agent ◄─┼────────┼─►│ - Mock Hotels              │ │
│                   │        │  └────────────────────────────┘ │
│  State Management │        └─────────────────────────────────┘
│  (SharedState)    │
└───────────────────┘
```

### Agent Interactions and Data Flow

**1. Coordinator Agent** - The Master Router
- **Responsibilities**: Intent classification, parameter extraction, preference learning
- **Inputs**: User messages, conversation history, learned preferences  
- **Outputs**: Intent classification, flight/hotel search parameters
- **Agent Flow**: 
  ```
  User Message → LLM Classification → Parameter Extraction → Route Decision
                              ↓
              ┌─────────────────────────────────────┐
              │          Routing Logic              │
              ├─────────────────────────────────────┤
              │ FLIGHT → Flight Agent               │
              │ HOTEL  → Hotel Agent                │  
              │ BOTH   → Flight → Hotel → Response  │
              │ OTHER  → Response Agent             │
              └─────────────────────────────────────┘
  ```

**2. Flight Agent** - Flight Search Specialist
- **Responsibilities**: Multi-leg flight search, price comparison, route optimization
- **Inputs**: FlightSearchParams (origin, destination, dates, passengers, cabin class)
- **Outputs**: FlightResult objects with segments, layovers, pricing
- **Data Sources**: Mock flight generator + Tavily web search (with fallback)

**3. Hotel Agent** - Hotel Search Specialist  
- **Responsibilities**: Location-based hotel search, amenity filtering, pricing
- **Inputs**: HotelSearchParams (city, dates, guests, budget, rating)
- **Outputs**: HotelResult objects with amenities, pricing, location data
- **Data Sources**: Mock hotel generator + Tavily web search (with fallback)

**4. Response Agent** - Natural Language Generator
- **Responsibilities**: Context-aware response generation, conversation flow management
- **Inputs**: Flight/hotel results, user intent, conversation context
- **Outputs**: Natural language responses, conversation history updates

### State Management Architecture

**LangGraph SharedState Pattern**:
```
SharedState {
  session_id: str,
  conversation_history: [ConversationTurn],
  user_preferences: UserPreferences,
  current_intent: Intent,
  flight_params: FlightSearchParams | None,
  hotel_params: HotelSearchParams | None,  
  flight_results: [FlightResult],
  hotel_results: [HotelResult],
  selected_flight_id: str | None,
  selected_hotel_id: str | None,
  is_interrupted: bool,
  current_run_id: str | None,
  pending_flight_booking: str | None,
  pending_hotel_booking: str | None
}
```

**Context Transfer Mechanism**:
- **Conversation Compression**: Older messages summarized for memory efficiency
- **Preference Persistence**: User preferences learned and stored across sessions  
- **Selection Preservation**: Bookings and selections maintained during interruptions
- **State Synchronization**: WebSocket real-time state updates to frontend

## 🤖 Agent Design

### Agent Capabilities and Inputs/Outputs

#### Coordinator Agent (Master Router)
- **Primary Function**: Intent classification and request routing
- **Inputs**: 
  - User message text
  - Last 5 conversation turns (context window)
  - Current user preferences
  - Session metadata
- **Processing**: 
  - Gemini LLM classifies intent (FLIGHT/HOTEL/COMBINED/OTHER)
  - Extracts search parameters from natural language
  - Learns user preferences from conversation
  - Determines optimal agent routing
- **Outputs**:
  - Intent classification (Intent enum)
  - FlightSearchParams or HotelSearchParams objects
  - Updated user preferences
  - Routing decision for LangGraph workflow

#### Flight Agent (Flight Search Specialist)
- **Primary Function**: Multi-leg flight search and price comparison
- **Inputs**:
  - FlightSearchParams: origin, destination, depart_date, return_date, passengers, cabin_class, max_stops
  - User preferences (preferred airlines, flight times, etc.)
- **Processing**:
  - Tavily web search with fallback to mock data
  - Multi-leg flight generation with realistic layovers
  - Price calculation and filtering
  - Airport coordinate mapping
- **Outputs**:
  - FlightResult[] with segments, layovers, total journey duration
  - Source tracking (live web search vs mock data)
  - Partial results flag for interruption handling

#### Hotel Agent (Hotel Search Specialist)
- **Primary Function**: Location-based hotel search with amenity filtering
- **Inputs**:
  - HotelSearchParams: city, check_in, check_out, guests, budget, min_rating
  - Current flight destination (auto-derivation)
- **Processing**:
  - Tavily web search with fallback to mock data
  - Hotel amenity filtering and rating assessment
  - Price per night calculation
  - Location coordinate mapping
- **Outputs**:
  - HotelResult[] with amenities, pricing, location data
  - Source tracking and partial results flag

#### Response Agent (Natural Language Generator)
- **Primary Function**: Context-aware response generation
- **Inputs**:
  - FlightResults[] and/or HotelResults[]
  - Current user intent
  - Conversation context and history
  - User selections and pending bookings
- **Processing**:
  - Gemini streaming response generation
  - Context-aware response formatting
  - Selection validation and confirmation prompts
- **Outputs**:
  - Natural language response text
  - Updated conversation history
  - Streaming tokens for real-time display

### LangGraph Coordination Workflows

#### Standard Workflow Triggers

**1. Flight Search Workflow**:
```
User: "Find flights from NYC to London"
↓
Coordinator: Intent=FLIGHT, extract params
↓
Flight Agent: Search flights, generate results
↓
Response Agent: Format and present results
```

**2. Hotel Search Workflow**:
```
User: "Hotels in Tokyo"  
↓
Coordinator: Intent=HOTEL, extract params
↓
Hotel Agent: Search hotels, generate results  
↓
Response Agent: Format and present results
```

**3. Combined Search Workflow**:
```
User: "Plan a trip to Paris - flights and hotels"
↓
Coordinator: Intent=COMBINED, extract both params
↓ (parallel or sequential)
Flight Agent → Hotel Agent → Response Agent
```

**4. Refinement Workflow**:
```
User: "Show me cheaper options" 
↓
Coordinator: Intent=REFINE, modify existing params
↓
Relevant Agent: Re-search with updated criteria
↓
Response Agent: Present refined results
```

## ⚡ Double-Texting / Request Interruption

### Technical Approach to Request Interruption

Our system implements robust interruption handling to support "double-texting" - when users send new requests while previous ones are still processing.

#### 1. Detection Mechanism

**Active Run Registry**:
```python
# In main.py - Tracks active processing
active_runs: Dict[str, ActiveRun] = {}
active_tasks: Dict[str, asyncio.Task] = {}

class ActiveRun(BaseModel):
    run_id: str
    agent_type: AgentType  
    started_at: float
    session_id: str
```

**Interruption Detection Flow**:
```
New User Message Received
↓
Check session_id in active_runs
↓
If found → Interruption detected
↓
Mark session state as is_interrupted = True
↓  
Cancel existing asyncio task
↓
Create new run with fresh request_id
```

#### 2. Graceful Cancellation Implementation

**Asyncio Task Cancellation**:
```python
# Cancel existing task with timeout
if session_id in active_tasks:
    existing_task = active_tasks[session_id]
    existing_task.cancel()
    
    # Wait for cancellation with timeout
    try:
        await asyncio.wait_for(existing_task, timeout=2.0)
    except asyncio.CancelledError:
        print("Previous task cancelled successfully")
    except asyncio.TimeoutError:
        print("Timeout waiting for task cancellation")
```

**State Preservation During Cancellation**:
```python
# Clear results but preserve selections
session.shared_state.is_interrupted = True
session.shared_state.flight_results = []  # Clear search results
session.shared_state.hotel_results = []   # Clear search results
# PRESERVE: selected_flight_id, selected_hotel_id, pending bookings
```

#### 3. Partial Results Preservation Strategy

**Result Flagging System**:
- All search results include `is_partial: bool` flag
- Partial results displayed with visual indicators (amber "PARTIAL" badge)
- Context includes which results are from interrupted runs

**Context Transfer Mechanism**:
```python
def preserve_context_during_interruption(session):
    # What gets preserved:
    preserved_state = {
        'selected_flight_id': session.selected_flight_id,
        'selected_hotel_id': session.selected_hotel_id,
        'pending_flight_booking': session.pending_flight_booking,
        'pending_hotel_booking': session.pending_hotel_booking,
        'conversation_history': session.conversation_history,
        'user_preferences': session.user_preferences
    }
    
    # What gets cleared:
    cleared_state = {
        'flight_results': [],    # Fresh search needed
        'hotel_results': [],     # Fresh search needed  
        'flight_params': None,   # Extract new from user input
        'hotel_params': None     # Extract new from user input
    }
```

#### 4. Libraries and Technologies Used

**Core Interruption Libraries**:
- **`asyncio`**: Async task management and cancellation
- **`asyncio.wait_for()`**: Timeout handling for graceful shutdown
- **`FastAPI`**: Background task coordination
- **`LangGraph`**: State persistence across agent boundaries

**Implementation Details**:
- **Task Registry**: Dictionary mapping session_id → asyncio.Task
- **Run Tracking**: Unique request_id for each user request
- **State Synchronization**: WebSocket real-time updates during interruption
- **Timeout Handling**: 2-second timeout for task cancellation

#### 5. User Experience During Interruption

**Visual Feedback**:
- Status badge: "⚠️ Interrupted - Updating..."
- Loading skeleton continues with interruption indicator
- Partial results grayed out with warning styling

**Seamless Continuation**:
- User selections preserved across interruptions
- Conversation history maintained
- Preferences learned over time persist
- New search starts fresh but context-aware

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

## 🎮 Demo Instructions

### Sample Queries for Flight Search

**Basic Flight Search**:
```
"I need a flight from New York to Los Angeles"
"Find flights to Paris next weekend"
"Show me flights from JFK to LAX"
```

**Advanced Flight Search**:
```
"I need a round-trip flight from New York to Paris with a layover in London"
"Find me business class flights to Tokyo for 2 passengers"
"Look for direct flights to Miami under $400"
```

**Multi-Leg Flight Example**:
```
"Book a trip from New York to Paris to London and back to New York"
"Plan a multi-city European tour: NYC → London → Paris → NYC"
```

### Sample Queries for Hotel Search

**Basic Hotel Search**:
```
"Find hotels in Tokyo"
"Show me hotels in Paris for next week"
"Hotels in London near the Tower Bridge"
```

**Advanced Hotel Search**:
```
"Find a 5-star hotel in Tokyo with a pool and spa"
"Looking for budget hotels in Miami under $150 per night"
"Hotels in Paris with WiFi and breakfast included"
```

### Interruption Scenarios Testing

**Test Case 1: Flight Search Interruption**
1. Send: "Find flights to London" (wait 3-5 seconds)
2. While processing, send: "Actually, show me hotels in Paris instead"
3. **Expected**: Flight search cancels, hotel search starts
4. **Verify**: Previous results cleared, new hotel results displayed

**Test Case 2: Double-Texting During Results**
1. Search for flights: "Flights to Los Angeles"
2. When results appear, immediately send: "Now find hotels in LA"
3. **Expected**: Seamless transition, results updated appropriately
4. **Verify**: No conflicting displays or partial results

**Test Case 3: Partial Selection Preservation**
1. Search flights: "Flights to Paris"
2. Click "Select" on a flight option
3. While waiting to book, send: "Actually show me cheaper flights"
4. **Expected**: Previous selection preserved, new search in background
5. **Verify**: Selected flight still shows as chosen, new results available

**Test Case 4: Context Transfer**
1. Search: "Hotels in Tokyo" 
2. Set preference: "I prefer hotels with pools"
3. Send: "Now find flights to Tokyo"
4. **Expected**: Hotel search should include pool preference
5. **Verify**: Preferences learned and applied to new searches

### Common User Flows to Reproduce

#### Flow 1: Complete Flight Booking
1. Start: "I need a flight to London"
2. Review results with maps and price charts
3. Click "Book Now" on preferred flight
4. Complete passenger information form
5. Select seat from seat map
6. Enter payment details (mock)
7. **Result**: Download HTML itinerary, confirmation message

#### Flow 2: Combined Flight + Hotel Search
1. Start: "Plan a trip to Tokyo for next month"
2. Review flight options with multi-leg support
3. Review hotel options with amenities and maps
4. Select flight: "I'll take the United Airlines flight"
5. Select hotel: "Book the Hilton Tokyo Bay"
6. **Result**: Both selections processed, individual booking flows

#### Flow 3: Preference Learning
1. Search: "Flights to Paris" 
2. User says: "I prefer morning flights and business class"
3. Search: "Hotels in London" 
4. User says: "I need WiFi and prefer luxury hotels"
5. Search: "Flights to London" (new request)
6. **Verify**: Preferences automatically applied to search parameters

#### Flow 4: Interruption Recovery
1. Start long search: "Find multi-leg flights around Europe"
2. Send interruption: "Wait, show me hotels in Paris instead"
3. Complete hotel search and make selection
4. Send: "Now continue with the Europe flights from Paris"
5. **Verify**: System remembers Paris as starting point, previous context preserved

### Testing Checklist

**Core Functionality**:
- [ ] Basic flight search returns results
- [ ] Basic hotel search returns results  
- [ ] WebSocket connection establishes successfully
- [ ] Real-time status updates during processing
- [ ] Result selection works (flights and hotels)
- [ ] Booking modal opens with correct data
- [ ] Dark/light theme switching works

**Advanced Features**:
- [ ] Multi-leg flights display segments correctly
- [ ] Flight maps show route visualization
- [ ] Hotel maps display location markers
- [ ] Price charts render correctly
- [ ] Preferences panel shows learned preferences
- [ ] Conversation history maintained

**Interruption Handling**:
- [ ] New requests cancel previous processing
- [ ] Partial results show appropriate indicators
- [ ] User selections preserved across interruptions
- [ ] Context transfers correctly between agents
- [ ] Status messages clearly indicate interruption state

**Error Handling**:
- [ ] Graceful handling of API failures
- [ ] Fallback to mock data when web search unavailable
- [ ] WebSocket disconnection recovery
- [ ] Invalid input handling with helpful messages

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
