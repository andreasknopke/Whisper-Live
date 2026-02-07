# Whisper-Live Server

A real-time speech recognition server using OpenAI's Whisper model for local transcription via WebSocket connections.

## Overview

Whisper-Live Server is a WebSocket-based server (WSS) that provides real-time speech-to-text transcription using the Whisper AI model. It supports dynamic prompt updates, GPU acceleration, and secure connections via SSL/TLS.

## Features

- **Real-time Transcription**: Live speech-to-text conversion with partial and final results
- **Dynamic Prompt Support**: Update transcription context on-the-fly via WebSocket messages
- **GPU Acceleration**: Automatic model selection based on available GPU hardware
- **Secure WebSocket (WSS)**: SSL/TLS encrypted connections for secure communication
- **Auto Model Selection**: Intelligently chooses the best Whisper model based on GPU capabilities
- **Multi-client Support**: Handle multiple concurrent client connections
- **German Language Support**: Optimized for German language transcription (configurable)
