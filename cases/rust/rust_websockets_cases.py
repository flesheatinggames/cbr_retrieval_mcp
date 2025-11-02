
RUST_WEBSOCKETS_CASES = [
    {
        "problem": """
A WebSocket client and server implementation using tokio-tungstenite with message routing and reconnection logic.
""",
        "solution": """
use tokio_tungstenite::{
    connect_async, tungstenite::protocol::Message, MaybeTlsStream, WebSocketStream,
};
use tokio::net::{TcpListener, TcpStream};
use tokio_tungstenite::accept_async;
use futures_util::{StreamExt, SinkExt, stream::{SplitSink, SplitStream}};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::{mpsc, RwLock};
use std::collections::HashMap;
use std::time::Duration;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum WsMessage {
    Ping { timestamp: i64 },
    Pong { timestamp: i64 },
    Subscribe { channels: Vec<String> },
    Unsubscribe { channels: Vec<String> },
    Message { channel: String, data: String },
    Error { code: String, message: String },
    Auth { token: String },
    AuthSuccess { user_id: String },
}

impl WsMessage {
    pub fn to_text(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string(self)
    }

    pub fn from_text(text: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(text)
    }
}

// ============================================
// WebSocket Client with Auto-Reconnect
// ============================================

pub struct WsClient {
    url: String,
    sender: mpsc::UnboundedSender<WsMessage>,
    receiver: Arc<RwLock<mpsc::UnboundedReceiver<WsMessage>>>,
}

impl WsClient {
    pub async fn connect(url: impl Into<String>) -> anyhow::Result<Self> {
        let url = url.into();
        let (tx, rx) = mpsc::unbounded_channel();
        let (internal_tx, internal_rx) = mpsc::unbounded_channel();

        let client = Self {
            url: url.clone(),
            sender: internal_tx,
            receiver: Arc::new(RwLock::new(rx)),
        };

        // Spawn connection handler
        tokio::spawn(Self::connection_handler(
            url.clone(),
            tx,
            internal_rx,
        ));

        Ok(client)
    }

    async fn connection_handler(
        url: String,
        outbound: mpsc::UnboundedSender<WsMessage>,
        mut inbound: mpsc::UnboundedReceiver<WsMessage>,
    ) {
        let mut retry_count = 0;
        const MAX_RETRIES: u32 = 5;
        const RETRY_DELAY: Duration = Duration::from_secs(2);

        loop {
            match Self::maintain_connection(&url, &outbound, &mut inbound).await {
                Ok(_) => {
                    tracing::info!("WebSocket connection closed normally");
                    break;
                }
                Err(e) => {
                    retry_count += 1;
                    tracing::error!(
                        "WebSocket error (attempt {}/{}): {}",
                        retry_count,
                        MAX_RETRIES,
                        e
                    );

                    if retry_count >= MAX_RETRIES {
                        tracing::error!("Max retries reached, giving up");
                        let _ = outbound.send(WsMessage::Error {
                            code: "max_retries".to_string(),
                            message: "Failed to connect after maximum retries".to_string(),
                        });
                        break;
                    }

                    tokio::time::sleep(RETRY_DELAY).await;
                }
            }
        }
    }

    async fn maintain_connection(
        url: &str,
        outbound: &mpsc::UnboundedSender<WsMessage>,
        inbound: &mut mpsc::UnboundedReceiver<WsMessage>,
    ) -> anyhow::Result<()> {
        tracing::info!("Connecting to {}", url);
        let (ws_stream, _) = connect_async(url).await?;
        tracing::info!("WebSocket connected");

        let (mut write, mut read) = ws_stream.split();

        // Spawn heartbeat task
        let heartbeat_tx = outbound.clone();
        let heartbeat = tokio::spawn(async move {
            let mut interval = tokio::time::interval(Duration::from_secs(30));
            loop {
                interval.tick().await;
                let msg = WsMessage::Ping {
                    timestamp: chrono::Utc::now().timestamp(),
                };
                if heartbeat_tx.send(msg).is_err() {
                    break;
                }
            }
        });

        loop {
            tokio::select! {
                // Handle incoming messages from WebSocket
                msg = read.next() => {
                    match msg {
                        Some(Ok(Message::Text(text))) => {
                            if let Ok(ws_msg) = WsMessage::from_text(&text) {
                                if outbound.send(ws_msg).is_err() {
                                    break;
                                }
                            }
                        }
                        Some(Ok(Message::Close(_))) => {
                            tracing::info!("Received close frame");
                            break;
                        }
                        Some(Err(e)) => {
                            tracing::error!("WebSocket error: {}", e);
                            break;
                        }
                        None => break,
                        _ => {}
                    }
                }

                // Handle outgoing messages
                msg = inbound.recv() => {
                    match msg {
                        Some(ws_msg) => {
                            if let Ok(text) = ws_msg.to_text() {
                                write.send(Message::Text(text)).await?;
                            }
                        }
                        None => break,
                    }
                }
            }
        }

        heartbeat.abort();
        Ok(())
    }

    pub fn send(&self, msg: WsMessage) -> anyhow::Result<()> {
        self.sender
            .send(msg)
            .map_err(|e| anyhow::anyhow!("Failed to send message: {}", e))
    }

    pub async fn recv(&self) -> Option<WsMessage> {
        self.receiver.write().await.recv().await
    }
}

// ============================================
// WebSocket Server with Channel Management
// ============================================

type ClientId = String;
type ChannelName = String;

#[derive(Clone)]
struct Client {
    id: ClientId,
    sender: mpsc::UnboundedSender<WsMessage>,
    subscriptions: Arc<RwLock<Vec<ChannelName>>>,
}

pub struct WsServer {
    clients: Arc<RwLock<HashMap<ClientId, Client>>>,
    channels: Arc<RwLock<HashMap<ChannelName, Vec<ClientId>>>>,
}

impl WsServer {
    pub fn new() -> Self {
        Self {
            clients: Arc::new(RwLock::new(HashMap::new())),
            channels: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn start(self: Arc<Self>, addr: &str) -> anyhow::Result<()> {
        let listener = TcpListener::bind(addr).await?;
        tracing::info!("WebSocket server listening on {}", addr);

        while let Ok((stream, peer)) = listener.accept().await {
            tracing::info!("New connection from {}", peer);
            let server = self.clone();
            tokio::spawn(async move {
                if let Err(e) = server.handle_connection(stream).await {
                    tracing::error!("Error handling connection: {}", e);
                }
            });
        }

        Ok(())
    }

    async fn handle_connection(&self, stream: TcpStream) -> anyhow::Result<()> {
        let ws_stream = accept_async(stream).await?;
        let (write, read) = ws_stream.split();

        let client_id = uuid::Uuid::new_v4().to_string();
        let (tx, rx) = mpsc::unbounded_channel();

        let client = Client {
            id: client_id.clone(),
            sender: tx,
            subscriptions: Arc::new(RwLock::new(Vec::new())),
        };

        self.clients.write().await.insert(client_id.clone(), client.clone());

        // Spawn writer task
        tokio::spawn(Self::write_task(write, rx));

        // Handle incoming messages
        self.handle_messages(client_id.clone(), read, client).await?;

        // Cleanup
        self.remove_client(&client_id).await;

        Ok(())
    }

    async fn write_task(
        mut write: SplitSink<WebSocketStream<TcpStream>, Message>,
        mut rx: mpsc::UnboundedReceiver<WsMessage>,
    ) {
        while let Some(msg) = rx.recv().await {
            if let Ok(text) = msg.to_text() {
                if write.send(Message::Text(text)).await.is_err() {
                    break;
                }
            }
        }
    }

    async fn handle_messages(
        &self,
        client_id: String,
        mut read: SplitStream<WebSocketStream<TcpStream>>,
        client: Client,
    ) -> anyhow::Result<()> {
        while let Some(msg) = read.next().await {
            match msg? {
                Message::Text(text) => {
                    if let Ok(ws_msg) = WsMessage::from_text(&text) {
                        self.handle_message(client_id.clone(), ws_msg, &client).await;
                    }
                }
                Message::Close(_) => break,
                _ => {}
            }
        }
        Ok(())
    }

    async fn handle_message(&self, client_id: String, msg: WsMessage, client: &Client) {
        match msg {
            WsMessage::Ping { timestamp } => {
                let _ = client.sender.send(WsMessage::Pong { timestamp });
            }
            WsMessage::Subscribe { channels } => {
                for channel in channels {
                    self.subscribe_client(&client_id, &channel).await;
                    client.subscriptions.write().await.push(channel);
                }
            }
            WsMessage::Unsubscribe { channels } => {
                for channel in channels {
                    self.unsubscribe_client(&client_id, &channel).await;
                    client
                        .subscriptions
                        .write()
                        .await
                        .retain(|c| c != &channel);
                }
            }
            WsMessage::Message { channel, data } => {
                self.broadcast_to_channel(&channel, WsMessage::Message { channel, data })
                    .await;
            }
            _ => {}
        }
    }

    async fn subscribe_client(&self, client_id: &str, channel: &str) {
        let mut channels = self.channels.write().await;
        channels
            .entry(channel.to_string())
            .or_insert_with(Vec::new)
            .push(client_id.to_string());
        
        tracing::info!("Client {} subscribed to channel {}", client_id, channel);
    }

    async fn unsubscribe_client(&self, client_id: &str, channel: &str) {
        let mut channels = self.channels.write().await;
        if let Some(subscribers) = channels.get_mut(channel) {
            subscribers.retain(|id| id != client_id);
        }
        
        tracing::info!("Client {} unsubscribed from channel {}", client_id, channel);
    }

    async fn broadcast_to_channel(&self, channel: &str, msg: WsMessage) {
        let channels = self.channels.read().await;
        if let Some(subscribers) = channels.get(channel) {
            let clients = self.clients.read().await;
            for client_id in subscribers {
                if let Some(client) = clients.get(client_id) {
                    let _ = client.sender.send(msg.clone());
                }
            }
        }
    }

    async fn remove_client(&self, client_id: &str) {
        // Remove from all channels
        let mut channels = self.channels.write().await;
        for subscribers in channels.values_mut() {
            subscribers.retain(|id| id != client_id);
        }

        // Remove client
        self.clients.write().await.remove(client_id);
        tracing::info!("Client {} disconnected", client_id);
    }
}

// Example usage
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    // Start server
    let server = Arc::new(WsServer::new());
    let server_clone = server.clone();
    tokio::spawn(async move {
        if let Err(e) = server_clone.start("127.0.0.1:9001").await {
            tracing::error!("Server error: {}", e);
        }
    });

    // Give server time to start
    tokio::time::sleep(Duration::from_millis(100)).await;

    // Connect client
    let client = WsClient::connect("ws://127.0.0.1:9001").await?;

    // Subscribe to channels
    client.send(WsMessage::Subscribe {
        channels: vec!["chat".to_string(), "notifications".to_string()],
    })?;

    // Send a message
    client.send(WsMessage::Message {
        channel: "chat".to_string(),
        data: "Hello, WebSocket!".to_string(),
    })?;

    // Receive messages
    tokio::spawn(async move {
        while let Some(msg) = client.recv().await {
            tracing::info!("Received: {:?}", msg);
        }
    });

    tokio::time::sleep(Duration::from_secs(60)).await;

    Ok(())
}
""",
        "category": 'rust',
        "subcategory": 'websockets',
        "tags": ['async', 'auth', 'error-handling', 'handler', 'json', 'listener', 'orm']
    }
]
