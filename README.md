# 🚀 Smart Task Planner - Hugging Face Edition

An AI-powered task planning application that breaks down goals into actionable tasks with timelines and dependencies using **Hugging Face LLMs**.

---

## 🎥 Demo Video

Watch the complete walkthrough and demo:

**[📺 Click here to watch the demo video](https://drive.google.com/file/d/1DOYwmD_IrLN2hJNQVGm2JTt8E7hEY9wT/view?usp=sharing)**


## ✨ Features

- 🤖 **AI-Powered Planning**: Uses Hugging Face Mixtral-8x7B for intelligent task breakdown  
- 📊 **Task Management**: Track tasks with priorities, dependencies, and durations  
- 💾 **Persistent Storage**: SQLite database for storing projects and tasks  
- 📈 **Analytics Dashboard**: Visualize project progress and statistics  
- 🎯 **Critical Path Analysis**: Identify key tasks for project success  
- ⚡ **Real-time Updates**: Update task status and track progress instantly  
- 🆓 **100% Free**: Uses Hugging Face Inference API (free tier)  

---

## 🛠️ Installation

### 1. Clone the repository

```
git clone https://github.com/yourusername/smart-task-planner.git
cd smart-task-planner
```

### 2. Create a virtual environment (recommended)

```
python -m venv venv

# Activate the environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Get a Hugging Face API key

1. Go to [Hugging Face](https://huggingface.co/) and sign up or log in
2. Navigate to **Settings** → **Access Tokens** → **New Token**
3. Copy your token (keep it secret!)

### 5. Create a `.env` file

In the project root, create a `.env` file:

```
HF_API_KEY=your_huggingface_api_key_here
```

### 6. Run the app

```
streamlit run app.py
```

Open your browser at [http://localhost:8501](http://localhost:8501) to access the Smart Task Planner.

---

## 🚀 Quick Start

For a one-command setup (after cloning):

```
pip install -r requirements.txt && streamlit run app.py
```

> **Note:** Make sure you've created the `.env` file with your Hugging Face API key first!

---

## 📖 Usage

1. Navigate to the **Create New Plan** tab
2. Enter your goal and optional context
3. Click **Generate Task Plan**
4. Tasks are automatically saved and displayed with priority, dependencies, and duration
5. Manage projects and tasks in **View Projects**
6. Track analytics in **Analytics Dashboard**

---

## 🗂️ Project Structure

```
smart-task-planner/
├── app.py              # Streamlit frontend
├── database.py         # SQLite database handler
├── llm_handler.py      # Hugging Face LLM integration
├── requirements.txt    # Python dependencies
├── tasks.db           # SQLite database (auto-generated)
├── .env               # Hugging Face API key (create this)
└── README.md          # Project documentation
```

---

## 💡 Notes

- If the Hugging Face model fails to respond or generates invalid JSON, the app will fallback to a basic task plan to ensure usability
- All data is stored locally in `tasks.db`
- The free tier of Hugging Face Inference API may have rate limits during peak usage

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ❤️ Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Hugging Face Inference API](https://huggingface.co/inference-api)
- LLM: Mixtral-8x7B by Mistral AI
- Icons and emojis inspired by [Twemoji](https://twemoji.twitter.com/)

---

## 📧 Contact

For questions or feedback, please open an issue or reach out via [your email/social media].

---

**Made with ❤️ by Asad**
```
```
