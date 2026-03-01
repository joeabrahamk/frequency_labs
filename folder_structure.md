# Folder Structure - Frequency Labs

```
frequency_labs/
│
├── .git/                           # Git version control
├── .venv/                          # Python virtual environment
├── .gitignore                      # Git ignore rules
├── .vercelignore                   # Vercel deployment ignore rules
├── vercel.json                     # Vercel deployment config
│
├── README.md                       # Project overview and setup guide
├── BUILD_PROCESS.md                # Development journey and decisions
├── THOUGHT_PROCESS.md              # Architectural decisions
├── RESEARCH_LOG.md                 # Research references and AI prompts
├── SCORE.md                        # Scoring methodology documentation
├── STRATEGY_DESIGN.md              # Use case strategies design
├── Design_Diagram.md               # System design diagrams
├── OPENROUTER_SETUP.md             # OpenRouter API setup guide
├── folder_structure.md             # This file
│
├── backend/                        # FastAPI Backend
│   ├── .env                        # Environment variables (API keys)
│   ├── .gitignore                  # Backend-specific ignore rules
│   ├── .python-version             # Python version specification
│   ├── requirements.txt            # Python dependencies
│   ├── render.yaml                 # Render deployment config
│   │
│   ├── api/                        # API endpoints
│   │   ├── routes.py               # Main API routes (/evaluate, /evaluate-amazon)
│   │   ├── response_structure.json # API response schema reference
│   │   └── __pycache__/
│   │
│   ├── models/                     # Data models
│   │   ├── headphone.py            # Headphone & UseCase Pydantic models
│   │   └── __pycache__/
│   │
│   └── scoring/                    # Scoring engine
│       ├── scoring_logic.py        # Core scoring algorithms
│       ├── strategies.py           # Use case strategy implementations
│       ├── weight_profiles.py      # Weight definitions per use case
│       └── __pycache__/
│
└── frontend/                       # React + Vite Frontend
    ├── .env.example                # Example environment variables
    ├── .gitignore                  # Frontend-specific ignore rules
    ├── index.html                  # Entry HTML (includes favicon links)
    ├── package.json                # Node dependencies
    ├── package-lock.json           # Locked dependency versions
    ├── vite.config.js              # Vite build configuration
    ├── postcss.config.js           # PostCSS configuration
    ├── tailwind.config.js          # TailwindCSS configuration
    ├── vercel.json                 # Vercel frontend deployment config
    │
    ├── public/                     # Static assets
    │   ├── applle.png              # Apple touch icon
    │   ├── Architecture_diagram.png
    │   ├── Component_diagram.png
    │   ├── Data_flow_diagram.png
    │   └── Decision_Logic_Diagram.png
    │
    ├── node_modules/               # Node.js dependencies (ignored in git)
    │
    └── src/                        # Source code
        ├── main.jsx                # React entry point
        ├── App.jsx                 # Main app component
        ├── index.css               # Global styles (Tailwind imports)
        │
        ├── assets/                 # Assets bundled with app
        │   └── applee.webp         # Logo/branding asset
        │
        ├── components/             # React components
        │   ├── HeroSection.jsx             # Landing/hero section
        │   ├── UseCaseSelector.jsx         # Use case selection UI
        │   ├── HeadphoneForm.jsx           # Manual spec input form
        │   ├── HeadphoneCard.jsx           # Individual headphone card
        │   ├── AmazonUrlForm.jsx           # Amazon/Flipkart URL input
        │   ├── ResultsSection.jsx          # Results display container
        │   ├── RankingCard.jsx             # Individual ranking card
        │   └── InvalidProductCard.jsx      # Invalid/non-headphone product card
        │
        ├── services/               # API communication
        │   └── api.js              # Backend API calls (evaluate, health check)
        │
        └── config/                 # Configuration
            └── environment.prod.js # Production environment config
```

## Key Files Explained

### Backend Core

- **routes.py**: Main API logic including LLM-based product extraction and scoring endpoints
- **headphone.py**: Pydantic models for validation (Headphone, UseCase, UserRequest)
- **strategies.py**: Use case strategies (Gaming, Music, Calls, Fitness, Travel, Studio)
- **weight_profiles.py**: Weight definitions for each spec per use case
- **scoring_logic.py**: Normalization and scoring algorithms

### Frontend Core

- **App.jsx**: Main app state management and section navigation
- **api.js**: Backend communication (POST /evaluate, POST /evaluate-amazon)
- **HeroSection.jsx**: Landing page with "Start" CTA
- **UseCaseSelector.jsx**: Multi-select use case picker with percentages
- **AmazonUrlForm.jsx**: URL input for link-based comparison
- **HeadphoneForm.jsx**: Manual spec entry form
- **ResultsSection.jsx**: Displays ranked headphones (performance + value)
- **RankingCard.jsx**: Individual headphone ranking card with expandable details
- **InvalidProductCard.jsx**: Shows non-headphone products from URL extraction

### Documentation

- **README.md**: Setup instructions, deployment guide, API usage
- **BUILD_PROCESS.md**: Development journey, mistakes, refactorings, API evolution
- **STRATEGY_DESIGN.md**: Use case strategy architecture and weight justification
- **SCORE.md**: Scoring methodology and normalization formulas
- **OPENROUTER_SETUP.md**: OpenRouter integration guide with model options

### Configuration

- **backend/.env**: OPENROUTER_API_KEY, OPENROUTER_MODEL
- **requirements.txt**: fastapi, uvicorn, pydantic, requests, httpx, python-dotenv
- **package.json**: react, vite, tailwindcss dependencies
- **render.yaml**: Backend deployment on Render free tier
- **vercel.json**: Frontend deployment on Vercel

### Static Assets

- **public/**: Diagrams and branding assets
- **src/assets/**: App-bundled assets (logo, icons)
