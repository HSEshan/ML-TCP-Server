# ML TCP Server

A high-performance, production-ready TCP server designed for real-time machine learning inference with comprehensive monitoring and metrics collection.

## Features

- **High-Performance TCP Server**: Built with Python's asyncio for handling multiple concurrent connections
- **Real-Time ML Inference**: Extensible interface for processing ML models with configurable payload handling
- **Dual-Protocol Architecture**: TCP for ML inference + HTTP/WebSocket for monitoring
- **Comprehensive Metrics**: Real-time performance monitoring with request rates, error tracking, and connection management
- **Production Ready**: Robust error handling, timeout management, and graceful shutdown procedures
- **Flexible Protocol**: Configurable binary protocol supporting various length field sizes
- **Extensible Design**: Modular architecture with clear separation of concerns

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   TCP Clients  │<>───│   TCP Server    │─── <>│  ML Interface │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Metrics &     │
                       │   Monitoring    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ HTTP/WebSocket  │
                       │   Endpoints     │
                       └─────────────────┘
```

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ml-tcp-server.git
   cd ml-tcp-server
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

The server can be configured through environment variables or by modifying `src/config.py`:

- `HOST`: Server host address (default: localhost)
- `PORT`: TCP server port (default: 8081)
- `MAX_CONNECTIONS`: Maximum concurrent connections (default: 100)
- `MAX_PAYLOAD_SIZE_KB`: Maximum payload size in KB (default: 1024)
- `PAYLOAD_TIMEOUT_SECONDS`: Timeout for payload reading (default: 30)

## 🚀 Usage

### Starting the Server

```bash
python main.py
```

The server will start both the TCP server and HTTP monitoring endpoints.

### TCP Simulation

An example simulation can be found in `tcp_simulation.py`

### Monitoring Endpoints

- **HTTP Metrics**: `GET /metrics` - Get current server metrics, can be polled
- **WebSocket Metrics**: `WS /metrics` - Real-time metrics streaming using websocket

## 🧪 Testing

Run the test suite to validate server functionality:

```bash
# Run all tests
python -m pytest ./tests

# Run with verbose output, optional stdout and logs
python -m pytest ./tests -v #-vv -s --log-cli-level=DEBUG

# Run specific test file
python -m pytest ./tests/test_tcp_client.py
```

## 📊 Metrics & Monitoring

The server provides comprehensive metrics including:

- **Performance Metrics**: Requests per second, uptime, active connections
- **Error Tracking**: Error rates, inference errors, connection failures
- **Real-time Updates**: WebSocket endpoint for live monitoring
- **Resource Management**: Connection limits, payload validation, timeout handling

To access metrics, see `Monitoring Endpoints` above
