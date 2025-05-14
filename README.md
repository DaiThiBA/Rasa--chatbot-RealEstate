
```markdown
# 🏠 Rasa Chatbot – Real Estate Recommendation Assistant

This project is a real estate chatbot built using the **Rasa framework**. The assistant is designed to help users receive personalized property suggestions through conversational AI.

---

## 📁 Project Structure

```
Rasa--chatbot-RealEstate/
├── data/                # Training data: intents, examples, stories
│   ├── nlu.yml          # NLU training examples (user intents)
│   ├── rules.yml        # Rule-based conversation flows
│   └── stories.yml      # Sample user-bot dialogues
├── actions/             # Custom Python actions
│   └── actions.py       # Logic for recommendation, slot filling
├── domain.yml           # Main config: intents, slots, entities, responses, actions
├── config.yml           # Pipeline & policies configuration
├── credentials.yml      # Channel configuration (e.g., REST, Telegram)
├── endpoints.yml        # Endpoint for custom actions
└── README.md            # Documentation and project guide
```

---

## 🚀 How to Run the Chatbot

### 1. Clone the Repository
```bash
git clone https://github.com/DaiThiBA/Rasa--chatbot-RealEstate.git
cd Rasa--chatbot-RealEstate
```

### 2. Set Up Environment
Make sure you have Python 3.8+ and [Rasa](https://rasa.com/docs/rasa/installation/) installed.
```bash
pip install rasa
```

### 3. Train the Model
```bash
rasa train
```

### 4. Run the Action Server
In one terminal tab:
```bash
rasa run actions
```

### 5. Run the Chatbot
In another terminal tab:
```bash
rasa shell
```

You can now chat with the assistant!

---

## 🧠 What the Bot Can Do

- Answer basic real estate-related questions.
- Recommend properties based on user input (e.g., location, price range, type).
- Use custom logic from `actions.py` to match user profiles with suitable property options.
- Respond using contextual conversation flows (via `stories.yml` and `rules.yml`).

---

## 🛠️ Customize or Expand

- Add new **intents** or user messages → edit `data/nlu.yml`
- Add new **bot replies** or change existing ones → edit `domain.yml`
- Modify **conversation flow** → update `stories.yml` and `rules.yml`
- Add more complex logic → update `actions/actions.py`

---

## 📌 Requirements

- Python 3.8+
- Rasa 3.x
- (Optional) Rasa SDK for custom actions

---

## 📫 Contact

Maintained by [Quang Đại Thi](https://github.com/DaiThiBA)  
If you have questions or suggestions, feel free to open an issue or contribute!

```
