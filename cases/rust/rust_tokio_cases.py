"""
    },

    # ============================================
    # TOKIO SELECT AND JOIN
    # ============================================
    {
        "problem": "Advanced tokio concurrency patterns using select!, join!, and timeout with cancellation support.",
        "solution": """

RUST_TOKIO_CASES = [
    {
        "problem": """
A tokio-based concurrent task processor with rate limiting, retries, and graceful shutdown.
""",
        "solution": """
use tokio::{
    sync::{mpsc, Semaphore},
    time::{sleep, Duration, interval},
    select,
    signal,
};
use std::sync::Arc;
use thiserror::Error;
use tracing::{error, info, warn};

#[derive(Debug, Error)]
pub enum ProcessError {
    #[error("Task failed: {0}")]
    TaskFailed(String),
    
    #[error("Rate limit exceeded")]
    RateLimitExceeded,
    
    #[error("Timeout")]
    Timeout,
}

#[derive(Debug, Clone)]
pub struct Task {
    pub id: String,
    pub data: String,
    pub priority: u8,
}

#[derive(Debug, Clone)]
pub struct TaskResult {
    pub task_id: String,
    pub success: bool,
    pub error: Option<String>,
    pub duration: Duration,
}

pub struct TaskProcessor {
    max_concurrent_tasks: usize,
    max_retries: u32,
    retry_delay: Duration,
    rate_limit_per_second: usize,
    shutdown_tx: mpsc::Sender<()>,
    shutdown_rx: mpsc::Receiver<()>,
}

impl TaskProcessor {
    pub fn new(
        max_concurrent_tasks: usize,
        max_retries: u32,
        retry_delay: Duration,
        rate_limit_per_second: usize,
    ) -> Self {
        let (shutdown_tx, shutdown_rx) = mpsc::channel(1);
        
        Self {
            max_concurrent_tasks,
            max_retries,
            retry_delay,
            rate_limit_per_second,
            shutdown_tx,
            shutdown_rx,
        }
    }

    pub async fn process_tasks(
        mut self,
        mut task_rx: mpsc::Receiver<Task>,
        result_tx: mpsc::Sender<TaskResult>,
    ) -> anyhow::Result<()> {
        info!("Task processor started with {} concurrent tasks", self.max_concurrent_tasks);

        // Semaphore for controlling concurrent tasks
        let semaphore = Arc::new(Semaphore::new(self.max_concurrent_tasks));
        
        // Rate limiter using a token bucket approach
        let rate_limiter = Arc::new(Semaphore::new(self.rate_limit_per_second));
        let rate_limit_permits = self.rate_limit_per_second;
        
        // Spawn rate limiter refill task
        let rate_limiter_clone = rate_limiter.clone();
        tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(1));
            loop {
                interval.tick().await;
                // Refill permits up to the limit
                let current_permits = rate_limiter_clone.available_permits();
                if current_permits < rate_limit_permits {
                    rate_limiter_clone.add_permits(rate_limit_permits - current_permits);
                }
            }
        });

        // Main processing loop
        loop {
            select! {
                // Receive new tasks
                Some(task) = task_rx.recv() => {
                    let semaphore = semaphore.clone();
                    let rate_limiter = rate_limiter.clone();
                    let result_tx = result_tx.clone();
                    let max_retries = self.max_retries;
                    let retry_delay = self.retry_delay;

                    tokio::spawn(async move {
                        // Wait for rate limit permit
                        let _rate_permit = match rate_limiter.acquire().await {
                            Ok(p) => p,
                            Err(_) => {
                                error!("Rate limiter closed");
                                return;
                            }
                        };

                        // Wait for concurrency permit
                        let _permit = match semaphore.acquire().await {
                            Ok(p) => p,
                            Err(_) => {
                                error!("Semaphore closed");
                                return;
                            }
                        };

                        info!("Processing task: {}", task.id);
                        let start = tokio::time::Instant::now();

                        // Execute task with retries
                        let result = Self::execute_with_retries(
                            task.clone(),
                            max_retries,
                            retry_delay,
                        ).await;

                        let duration = start.elapsed();
                        
                        let task_result = match result {
                            Ok(_) => {
                                info!("Task {} completed successfully in {:?}", task.id, duration);
                                TaskResult {
                                    task_id: task.id,
                                    success: true,
                                    error: None,
                                    duration,
                                }
                            }
                            Err(e) => {
                                error!("Task {} failed after retries: {}", task.id, e);
                                TaskResult {
                                    task_id: task.id,
                                    success: false,
                                    error: Some(e.to_string()),
                                    duration,
                                }
                            }
                        };

                        let _ = result_tx.send(task_result).await;
                    });
                }
                
                // Handle shutdown signal
                _ = self.shutdown_rx.recv() => {
                    info!("Shutdown signal received, draining remaining tasks...");
                    
                    // Wait for all tasks to complete
                    while task_rx.recv().await.is_some() {
                        // Process remaining tasks
                    }
                    
                    info!("All tasks completed, shutting down");
                    break;
                }
            }
        }

        Ok(())
    }

    async fn execute_with_retries(
        task: Task,
        max_retries: u32,
        retry_delay: Duration,
    ) -> Result<(), ProcessError> {
        let mut attempts = 0;
        
        loop {
            match Self::execute_task(&task).await {
                Ok(_) => return Ok(()),
                Err(e) => {
                    attempts += 1;
                    
                    if attempts > max_retries {
                        return Err(e);
                    }
                    
                    warn!(
                        "Task {} failed (attempt {}/{}): {}. Retrying in {:?}...",
                        task.id, attempts, max_retries, e, retry_delay
                    );
                    
                    sleep(retry_delay).await;
                }
            }
        }
    }

    async fn execute_task(task: &Task) -> Result<(), ProcessError> {
        // Simulate task processing with potential failure
        sleep(Duration::from_millis(100)).await;
        
        // Simulate random failures for demonstration
        use rand::Rng;
        let mut rng = rand::thread_rng();
        if rng.gen_bool(0.2) {  // 20% chance of failure
            return Err(ProcessError::TaskFailed("Random failure".to_string()));
        }
        
        // Process the task
        info!("Task {} processing data: {}", task.id, task.data);
        
        Ok(())
    }

    pub fn shutdown_handle(&self) -> mpsc::Sender<()> {
        self.shutdown_tx.clone()
    }
}

// Example usage
pub async fn run_task_processing_system() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_max_level(tracing::Level::INFO)
        .init();

    // Create channels
    let (task_tx, task_rx) = mpsc::channel::<Task>(100);
    let (result_tx, mut result_rx) = mpsc::channel::<TaskResult>(100);

    // Create processor
    let processor = TaskProcessor::new(
        5,  // max concurrent tasks
        3,  // max retries
        Duration::from_secs(1),  // retry delay
        10, // rate limit per second
    );

    let shutdown_handle = processor.shutdown_handle();

    // Spawn processor task
    let processor_handle = tokio::spawn(async move {
        processor.process_tasks(task_rx, result_tx).await
    });

    // Spawn result collector
    let result_collector = tokio::spawn(async move {
        let mut successful = 0;
        let mut failed = 0;
        
        while let Some(result) = result_rx.recv().await {
            if result.success {
                successful += 1;
            } else {
                failed += 1;
            }
            
            info!("Stats - Successful: {}, Failed: {}", successful, failed);
        }
        
        info!("Final stats - Successful: {}, Failed: {}", successful, failed);
    });

    // Spawn task generator
    let task_generator = tokio::spawn(async move {
        for i in 0..20 {
            let task = Task {
                id: format!("task-{}", i),
                data: format!("data-{}", i),
                priority: (i % 3) as u8,
            };
            
            if task_tx.send(task).await.is_err() {
                error!("Failed to send task");
                break;
            }
            
            sleep(Duration::from_millis(100)).await;
        }
        
        info!("All tasks submitted");
    });

    // Wait for Ctrl+C
    signal::ctrl_c().await?;
    info!("Received shutdown signal");

    // Trigger graceful shutdown
    let _ = shutdown_handle.send(()).await;

    // Wait for all tasks to complete
    task_generator.await?;
    processor_handle.await??;
    result_collector.await?;

    info!("System shutdown complete");
    Ok(())
}
""",
        "category": 'rust',
        "subcategory": 'tokio',
        "tags": ['async', 'concurrency', 'form', 'orm', 'rust', 'sse', 'token']
    },
    {
        "problem": """
Advanced tokio concurrency patterns using select!, join!, and timeout with cancellation support.
""",
        "solution": """
use tokio::{select, time::{sleep, Duration, timeout, interval}, sync::{mpsc, oneshot}};
use tokio::task::JoinHandle;
use futures::future::{join, join_all, try_join, try_join_all};
use std::sync::Arc;
use tokio::sync::RwLock;

#[derive(Debug, Clone)]
pub struct Task {
    pub id: String,
    pub duration_ms: u64,
}

#[derive(Debug)]
pub struct TaskResult {
    pub task_id: String,
    pub success: bool,
    pub elapsed_ms: u128,
}

// Pattern 1: Racing multiple operations with select!
pub async fn race_operations() -> String {
    let operation1 = async {
        sleep(Duration::from_millis(100)).await;
        "Operation 1 completed"
    };

    let operation2 = async {
        sleep(Duration::from_millis(150)).await;
        "Operation 2 completed"
    };

    let operation3 = async {
        sleep(Duration::from_millis(50)).await;
        "Operation 3 completed"
    };

    select! {
        result = operation1 => result,
        result = operation2 => result,
        result = operation3 => result,
    }.to_string()
}

// Pattern 2: Processing with timeout and fallback
pub async fn operation_with_timeout_and_fallback(
    primary_task: Task,
    timeout_ms: u64,
) -> Result<TaskResult, String> {
    let start = std::time::Instant::now();

    let primary = async {
        sleep(Duration::from_millis(primary_task.duration_ms)).await;
        TaskResult {
            task_id: primary_task.id.clone(),
            success: true,
            elapsed_ms: start.elapsed().as_millis(),
        }
    };

    let fallback = async {
        sleep(Duration::from_millis(timeout_ms + 100)).await;
        TaskResult {
            task_id: "fallback".to_string(),
            success: false,
            elapsed_ms: start.elapsed().as_millis(),
        }
    };

    select! {
        result = primary => Ok(result),
        _ = sleep(Duration::from_millis(timeout_ms)) => {
            tracing::warn!("Primary task timed out, executing fallback");
            Ok(fallback.await)
        }
    }
}

// Pattern 3: Graceful shutdown with cancellation
pub struct Worker {
    shutdown_tx: Option<oneshot::Sender<()>>,
    handle: Option<JoinHandle<()>>,
}

impl Worker {
    pub fn new(interval_ms: u64) -> Self {
        let (shutdown_tx, mut shutdown_rx) = oneshot::channel();
        
        let handle = tokio::spawn(async move {
            let mut ticker = interval(Duration::from_millis(interval_ms));
            let mut count = 0;

            loop {
                select! {
                    _ = ticker.tick() => {
                        count += 1;
                        tracing::info!("Worker tick #{}", count);
                    }
                    _ = &mut shutdown_rx => {
                        tracing::info!("Worker received shutdown signal");
                        break;
                    }
                }
            }

            tracing::info!("Worker shutting down gracefully");
        });

        Self {
            shutdown_tx: Some(shutdown_tx),
            handle: Some(handle),
        }
    }

    pub async fn shutdown(mut self) {
        if let Some(tx) = self.shutdown_tx.take() {
            let _ = tx.send(());
        }
        if let Some(handle) = self.handle.take() {
            let _ = handle.await;
        }
    }
}

// Pattern 4: Concurrent task processing with join!
pub async fn process_tasks_concurrently(tasks: Vec<Task>) -> Vec<TaskResult> {
    let futures: Vec<_> = tasks
        .into_iter()
        .map(|task| async move {
            let start = std::time::Instant::now();
            sleep(Duration::from_millis(task.duration_ms)).await;
            TaskResult {
                task_id: task.id,
                success: true,
                elapsed_ms: start.elapsed().as_millis(),
            }
        })
        .collect();

    join_all(futures).await
}

// Pattern 5: Try join with error handling
pub async fn fetch_multiple_resources() -> Result<(String, String, String), String> {
    let fetch1 = async {
        sleep(Duration::from_millis(100)).await;
        Ok::<_, String>("Resource 1".to_string())
    };

    let fetch2 = async {
        sleep(Duration::from_millis(150)).await;
        Ok::<_, String>("Resource 2".to_string())
    };

    let fetch3 = async {
        sleep(Duration::from_millis(50)).await;
        Ok::<_, String>("Resource 3".to_string())
    };

    try_join!(fetch1, fetch2, fetch3)
}

// Pattern 6: Channel-based work distribution
pub struct WorkerPool {
    workers: Vec<JoinHandle<()>>,
    task_tx: mpsc::Sender<Task>,
}

impl WorkerPool {
    pub fn new(num_workers: usize) -> (Self, mpsc::Receiver<TaskResult>) {
        let (task_tx, task_rx) = mpsc::channel::<Task>(100);
        let (result_tx, result_rx) = mpsc::channel::<TaskResult>(100);
        let task_rx = Arc::new(tokio::sync::Mutex::new(task_rx));

        let mut workers = Vec::new();

        for worker_id in 0..num_workers {
            let task_rx = task_rx.clone();
            let result_tx = result_tx.clone();

            let handle = tokio::spawn(async move {
                loop {
                    let task = {
                        let mut rx = task_rx.lock().await;
                        rx.recv().await
                    };

                    match task {
                        Some(task) => {
                            let start = std::time::Instant::now();
                            sleep(Duration::from_millis(task.duration_ms)).await;
                            
                            let result = TaskResult {
                                task_id: task.id,
                                success: true,
                                elapsed_ms: start.elapsed().as_millis(),
                            };

                            tracing::info!("Worker {} completed task", worker_id);
                            
                            if result_tx.send(result).await.is_err() {
                                break;
                            }
                        }
                        None => break,
                    }
                }
            });

            workers.push(handle);
        }

        (Self { workers, task_tx }, result_rx)
    }

    pub async fn submit(&self, task: Task) -> Result<(), String> {
        self.task_tx
            .send(task)
            .await
            .map_err(|e| format!("Failed to submit task: {}", e))
    }

    pub async fn shutdown(self) {
        drop(self.task_tx);
        for handle in self.workers {
            let _ = handle.await;
        }
    }
}

// Pattern 7: Adaptive timeout based on system load
pub struct AdaptiveTimeout {
    base_timeout_ms: u64,
    current_timeout_ms: Arc<RwLock<u64>>,
}

impl AdaptiveTimeout {
    pub fn new(base_timeout_ms: u64) -> Self {
        Self {
            base_timeout_ms,
            current_timeout_ms: Arc::new(RwLock::new(base_timeout_ms)),
        }
    }

    pub async fn execute_with_timeout<F, T>(
        &self,
        operation: F,
    ) -> Result<T, String>
    where
        F: std::future::Future<Output = T>,
    {
        let timeout_ms = *self.current_timeout_ms.read().await;
        
        match timeout(Duration::from_millis(timeout_ms), operation).await {
            Ok(result) => {
                // Success - maybe decrease timeout
                self.adjust_timeout(0.95).await;
                Ok(result)
            }
            Err(_) => {
                // Timeout - increase timeout
                self.adjust_timeout(1.5).await;
                Err("Operation timed out".to_string())
            }
        }
    }

    async fn adjust_timeout(&self, factor: f64) {
        let mut current = self.current_timeout_ms.write().await;
        let new_timeout = (*current as f64 * factor) as u64;
        *current = new_timeout.clamp(self.base_timeout_ms / 2, self.base_timeout_ms * 4);
        tracing::debug!("Adjusted timeout to {}ms", *current);
    }
}

// Pattern 8: Complex select with multiple channels and timers
pub async fn multiplexed_event_handler() {
    let (data_tx, mut data_rx) = mpsc::channel::<String>(10);
    let (control_tx, mut control_rx) = mpsc::channel::<String>(10);
    let mut ticker = interval(Duration::from_secs(5));
    let mut shutdown_signal = tokio::signal::ctrl_c();

    // Spawn some producers
    tokio::spawn(async move {
        for i in 0..10 {
            sleep(Duration::from_millis(500)).await;
            let _ = data_tx.send(format!("Data {}", i)).await;
        }
    });

    tokio::spawn(async move {
        sleep(Duration::from_secs(3)).await;
        let _ = control_tx.send("status_check".to_string()).await;
    });

    loop {
        select! {
            Some(data) = data_rx.recv() => {
                tracing::info!("Received data: {}", data);
            }
            Some(control) = control_rx.recv() => {
                tracing::info!("Received control message: {}", control);
            }
            _ = ticker.tick() => {
                tracing::info!("Periodic health check");
            }
            _ = &mut shutdown_signal => {
                tracing::info!("Shutting down gracefully");
                break;
            }
        }
    }
}

// Example usage
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();

    // Pattern 1: Race
    tracing::info!("Racing operations...");
    let winner = race_operations().await;
    tracing::info!("Winner: {}", winner);

    // Pattern 2: Timeout with fallback
    let task = Task {
        id: "task-1".to_string(),
        duration_ms: 200,
    };
    let result = operation_with_timeout_and_fallback(task, 100).await?;
    tracing::info!("Result: {:?}", result);

    // Pattern 3: Graceful shutdown
    let worker = Worker::new(1000);
    sleep(Duration::from_secs(3)).await;
    worker.shutdown().await;

    // Pattern 4: Concurrent processing
    let tasks = vec![
        Task { id: "1".to_string(), duration_ms: 100 },
        Task { id: "2".to_string(), duration_ms: 150 },
        Task { id: "3".to_string(), duration_ms: 50 },
    ];
    let results = process_tasks_concurrently(tasks).await;
    tracing::info!("Processed {} tasks", results.len());

    // Pattern 6: Worker pool
    let (pool, mut result_rx) = WorkerPool::new(3);
    
    for i in 0..10 {
        pool.submit(Task {
            id: format!("task-{}", i),
            duration_ms: 100,
        }).await?;
    }

    // Collect results
    tokio::spawn(async move {
        while let Some(result) = result_rx.recv().await {
            tracing::info!("Task completed: {:?}", result);
        }
    });

    sleep(Duration::from_secs(2)).await;
    pool.shutdown().await;

    Ok(())
}
""",
        "category": 'rust',
        "subcategory": 'tokio',
        "tags": ['async', 'concurrency', 'error-handling', 'event', 'form', 'handler', 'orm']
    }
]
