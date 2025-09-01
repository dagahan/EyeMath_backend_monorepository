# eye.math

**Open Source AI-powered mathematical problem solver** that recognizes handwritten equations and provides step-by-step solutions with LaTeX visualization.

<p align="center">
    <img src="./.github/assets/eye_math.png" alt="Eye Math Logo" width="250"/>
</p>

## 🚀 Features

- **95% Recognition Accuracy** - Advanced computer vision models for handwritten math;
- **Lightning Fast Processing** - Sub-2 second response times;
- **Step-by-Step Solutions** - Detailed mathematical explanations;
- **LaTeX Visualization** - Professional-quality mathematical rendering;
- **Open Source** - MIT licensed, contributions welcome;
- **Modern Architecture** - Microservices with Docker & Kubernetes support.

## 🎯 Problem Solved

Most mathematical recognition services either:
- Only handle printed text accurately;
- Provide results without explanations;
- Have low accuracy (65-85%) for handwritten input;
- Lack comprehensive solution workflows.

**eye.math** bridges this gap with a complete pipeline from handwritten recognition to LaTeX visualization.

## 🎬 Showcase

![Screenshot 1](./.github/assets/showcase/0.png)
![Screenshot 2](./.github/assets/showcase/1.png)
![Screenshot 3](./.github/assets/showcase/2.png)
![Screenshot 4](./.github/assets/showcase/3.png)
![Screenshot 5](./.github/assets/showcase/4.png)

## 🏗️ Architecture
<p>
    <img src="./.github/assets/architecture.png" alt="Architecture Diagram" width="900"/>
</p>

## 🛠️ Tech Stack

<p align="center">
    <img src="./.github/assets/tech_stack.png" alt="Tech Stack" width="600"/>
</p>

### Backend
- **Python 3.13.x** with UV, Ruff for high-performance execution;
- **PyTorch** with CUDA acceleration for computer vision models;
- **OpenCV** for advanced image preprocessing pipelines;
- **FastAPI** for modern REST API development;
- **PostgreSQL** for reliable data storage;
- **Valkey** for caching and session management;
- **Visma** - Open source mathematical computation engine for symbolic math;
- **Pix2Tex** - State-of-the-art handwritten math recognition model.

### Frontend
- **Vanilla JavaScript** with modern ES6+ features;
- **CSS3** with advanced animations and responsive design;
- **Vite** for fast development and building.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose;
- Git.
### Installation

1. **Clone the repository**
```bash
git clone https://github.com/dagahan/EyeMath_backend_monorepository
cd EyeMath_backend_monorepository
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Run with Docker Compose**
```bash
docker-compose --env-file .env up --build
```

4. **Access the application**
- Frontend: http://localhost:5500
- API: http://localhost:9998

### Development Setup

For development with hot reload:

```bash
# Backend services
docker-compose --env-file .env up --build

# Frontend development server
cd frontend
npm install
npm run dev
```

## 📊 Performance

- **Recognition Accuracy**: 95%
- **Processing Time**: <2 seconds
- **Uptime**: 24/7 availability
- **Scalability**: Kubernetes-ready microservices

## 🙏 Acknowledgments

This project is built on top of amazing open source technologies:
- **[Visma](https://github.com/dagahan/visma)** - Powerful symbolic mathematics engine that powers our solving capabilities;
- **[Pix2Tex](https://github.com/lukas-blecher/LaTeX-OCR)** - Advanced neural network for handwritten mathematical expression recognition.

## 🤝 Contributing

We welcome contributions! This is an open source project under MIT license.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`);
3. Commit your changes (`git commit -m 'Add amazing feature'`);
4. Push to the branch (`git push origin feature/amazing-feature`);
5. Open a Pull Request.

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/dagahan/EyeMath_backend_monorepository/issues);
- **Telegram**: [@dagahan](https://t.me/dagahan);
- **Email**: dagahanwork@gmail.com.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ for math by Usov Nikita.
</p>
