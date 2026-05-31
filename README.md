# Xuanji General Strategic Prototype

**Author:** Peng Hao
**Affiliation:** Python Historical Strategy Lab  
**License:** MIT

PHSL: Xuanji Strategic Audit Terminal 🛡️

Python Historical Strategy Lab (PHSL) presents the Xuanji Strategic Audit Terminal, an advanced, AI-driven wargaming and strategic simulation system.

Xuanji acts as a **digital wind tunnel** for strategy, performing rigorous "Red Team" audits on strategic visions by mapping them to historical prototypes and stress-testing them in simulated environments. By integrating systems thinking,the system quantifies the physical viability of a strategy against real-world environmental noise, friction, and resistance.

📐 The Core Strategic Axiom

At the heart of the Xuanji engine is the structural conservation of historical and realistic isomorphism. Strategic effectiveness is calculated using the following core formula:

$$E = \frac{P \cdot (ssc\_d \cdot L)}{(I \cdot (1 + vol)) + P}$$

Dimensional Variables:

$E$ (Strategic Effectiveness): The actualized impact of the strategy.  
$P$ (Resource Pressure): The resources and effort applied.  
$ssc\_d$ (SSC Density / Logical Density): The binding strength between the strategic vision and physical assets, which is mathematically equivalent to the likelihood P(E|H) in Bayes' theorem.  
$L$ (Leverage): The strategic multiplier (e.g., technological generation gaps).  
$I$ (Inertia): The inherent resistance or friction of the target environment.  
$vol$ (Volatility): Geopolitical or market fluctuations.

✨ Key Features

Strategic Oracle (AI Intelligence): Powered by Google's Gemini 2.5 Pro model, the Oracle module dynamically searches for historical prototypes, estimates Bayesian parameters, and outputs comprehensive JSON-formatted intelligence reports.

Bayesian Cognitive Engine: Refines the probability of success using Bayesian noise filtration (FRE Validation) and Monte Carlo simulations to find the "Truth Distribution."

Physics-Based Stress Testing:  
* ERT (Environmental Resilience Test): Calculates system stability and identifies the critical Collapse Line (Break Point / BP).  
* SIP (Strategic Ignition Point): Models efficiency against environmental resistance to find the exact Activation Pressure (AP) needed for a strategy to take effect across different leverage tiers (L1-L3 vs. L-0 Baseline).

Interactive UI & Visualizations: A sleek Streamlit dashboard (app.py) combined with matplotlib logic (visualizer.py) to render structural resilience audits and truth curves.

📂 Project StructurePlaintextphsl/

├── app.py                  # Main Streamlit web application and UI layout

├── controller.py           # Central nervous system orchestrating Oracle and Engine

├── engine.py               # Core mathematical and Bayesian calculation engine

├── arena.py               # Acts as the Dynamic Digital Wind Tunnel for strategy testing.

├── oracle.py               # Gemini API integration for historical & intelligence mapping

├── protocol.py             # Isomorphism protocol for contextual switching

├── report_generator.py     # CLI-based comprehensive strategy report generation

├── visualizer.py           # Custom Matplotlib plotting library (Truth curves, SIP, ERT)
 
└── __init__.py             # Package initialization

🚀 Installation & Setup
1. Clone the repository and navigate to the project directory:(Ensure you have Python 3.8+ installed)
2. Install required dependencies:Bashpip install streamlit google-genai matplotlib pandas numpy
3. Configure Network/Proxy (If applicable):By default, oracle.py is configured with local proxies. If you are running this in an environment without proxy requirements, you may need to comment out lines 10-11 in oracle.py.
4. 💻 Usage  Run the Streamlit application from your terminal:Bash streamlit run app.py

Operating the Terminal:

Open the local web address provided by Streamlit.In the sidebar console, enter your Google Gemini API Key.Input your Strategic Vision Description (e.g., "The impact of the Belt and Road Initiative on restructuring global supply chains...").Click "⚡ 启动全领域审计" (Initiate All-Domain Audit).

Review the generated intelligence reports, historical isomorphism mappings, and physics-based stress test charts.

🛠️ System Components Breakdown

* **The Oracle (oracle.py):** Acts as the Chief Auditing Officer. It enforces logical dimensionality reduction, applies real-time intelligence gathering, and matches inputs with evolutionary or military history.

* **The Engine (engine.py):** Executes the mathematical heavy lifting. It applies noise filters to leverage factors, ensuring that technological or structural advantages decay appropriately in high-noise environments.

* **The Visualizer (visualizer.py):** Generates high-fidelity, cyberpunk-styled (dark theme) charts to visualize the Monte Carlo truth curves and strategic hedge auditing.

* **The Arena (arena.py):** Acts as the Dynamic Digital Wind Tunnel. It orchestrates multi-agent, double-blind red/blue adversarial simulations across multiple parallel universes. By pit-testing the red team's strategy against dynamic environmental blowbacks round-by-round, it tracks physical attrition, applies life/death isolation statistics, and calculates the true Emergent Break Point  and absolute survival rates under extreme resistance.
