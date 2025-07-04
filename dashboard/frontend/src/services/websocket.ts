import { io, Socket } from 'socket.io-client'
import type { WebSocketEvent } from '../types'

class WebSocketService {
  private socket: Socket | null = null
  private listeners: Map<string, Function[]> = new Map()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private isProduction = process.env.NODE_ENV === 'production'

  connect(): void {
    // Disable WebSocket in production for Vercel deployment
    if (this.isProduction) {
      console.log('WebSocket disabled in production environment')
      return
    }

    if (this.socket) return

    this.socket = io('http://localhost:8000', {
      transports: ['websocket'],
      timeout: 10000,
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.handleReconnect()
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.handleReconnect()
    })

    // Handle incoming events
    this.socket.onAny((eventType: string, data: any) => {
      const event: WebSocketEvent = {
        type: eventType as any,
        data,
        timestamp: new Date().toISOString(),
      }
      this.notifyListeners(eventType, event)
    })
  }

  private handleReconnect(): void {
    if (this.isProduction) return // Don't reconnect in production
    
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
        this.connect()
      }, 1000 * this.reconnectAttempts)
    }
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  subscribe(eventType: string, callback: (event: WebSocketEvent) => void): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, [])
    }
    this.listeners.get(eventType)!.push(callback)
  }

  unsubscribe(eventType: string, callback: (event: WebSocketEvent) => void): void {
    const eventListeners = this.listeners.get(eventType)
    if (eventListeners) {
      const index = eventListeners.indexOf(callback)
      if (index > -1) {
        eventListeners.splice(index, 1)
      }
    }
  }

  private notifyListeners(eventType: string, event: WebSocketEvent): void {
    const eventListeners = this.listeners.get(eventType)
    if (eventListeners) {
      eventListeners.forEach(callback => callback(event))
    }
  }

  isConnected(): boolean {
    // In production, return false since WebSocket is disabled
    if (this.isProduction) return false
    return this.socket?.connected || false
  }

  emit(eventType: string, data: any): void {
    if (this.isProduction) return // Don't emit in production
    if (this.socket?.connected) {
      this.socket.emit(eventType, data)
    }
  }
}

export const websocketService = new WebSocketService()
export default websocketService 