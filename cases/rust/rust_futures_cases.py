
RUST_FUTURES_CASES = [
    
    # ============================================
    # FUTURES AND ASYNC STREAMS
    # ============================================
    {
        "problem": "Advanced async programming with futures, streams, and combinators.",
        "solution": """
use futures::{
    future::{BoxFuture, FutureExt, join_all, try_join_all, select, Either},
    stream::{Stream, StreamExt, FuturesUnordered},
    sink::{Sink, SinkExt},
};
use std::pin::Pin;
use std::task::{Context, Poll};
use std::time::Duration;
use tokio::time::{sleep, interval};

// Custom Future implementation
pub struct DelayedValue<T> {
    value: Option<T>,
    delay: Duration,
    started: Option<tokio::time::Instant>,
}

impl<T> DelayedValue<T> {
    pub fn new(value: T, delay: Duration) -> Self {
        Self {
            value: Some(value),
            delay,
            started: None,
        }
    }
}

impl<T: Unpin> std::future::Future for DelayedValue<T> {
    type Output = T;

    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output> {
        let started = self.started.get_or_insert_with(tokio::time::Instant::now);
        
        if started.elapsed() >= self.delay {
            Poll::Ready(self.value.take().unwrap())
        } else {
            cx.waker().wake_by_ref();
            Poll::Pending
        }
    }
}

// Custom Stream implementation
pub struct NumberStream {
    current: u64,
    max: u64,
    delay: Duration,
}

impl NumberStream {
    pub fn new(max: u64, delay: Duration) -> Self {
        Self {
            current: 0,
            max,
            delay,
        }
    }
}

impl Stream for NumberStream {
    type Item = u64;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if self.current >= self.max {
            return Poll::Ready(None);
        }

        let current = self.current;
        self.current += 1;
        
        cx.waker().wake_by_ref();
        Poll::Ready(Some(current))
    }
}

// Stream utilities
pub async fn process_stream_with_timeout<S, T>(
    mut stream: S,
    timeout_duration: Duration,
) -> Vec<T>
where
    S: Stream<Item = T> + Unpin,
{
    let mut results = Vec::new();
    let timeout = sleep(timeout_duration);
    tokio::pin!(timeout);

    loop {
        tokio::select! {
            item = stream.next() => {
                match item {
                    Some(value) => results.push(value),
                    None => break,
                }
            }
            _ = &mut timeout => {
                break;
            }
        }
    }

    results
}

// Buffered stream processing
pub async fn process_stream_buffered<S, F, Fut, T, R>(
    stream: S,
    buffer_size: usize,
    f: F,
) -> Vec<R>
where
    S: Stream<Item = T> + Unpin,
    F: Fn(T) -> Fut,
    Fut: std::future::Future<Output = R>,
{
    stream
        .map(f)
        .buffered(buffer_size)
        .collect()
        .await
}

// Racing futures with early termination
pub async fn race_with_cancellation<F1, F2, T>(
    future1: F1,
    future2: F2,
) -> Either<T, T>
where
    F1: std::future::Future<Output = T>,
    F2: std::future::Future<Output = T>,
{
    tokio::select! {
        result = future1 => Either::Left(result),
        result = future2 => Either::Right(result),
    }
}

// Retry with exponential backoff
pub async fn retry_with_backoff<F, Fut, T, E>(
    mut operation: F,
    max_retries: u32,
    initial_delay: Duration,
) -> Result<T, E>
where
    F: FnMut() -> Fut,
    Fut: std::future::Future<Output = Result<T, E>>,
    E: std::fmt::Display,
{
    let mut delay = initial_delay;
    let mut attempts = 0;

    loop {
        match operation().await {
            Ok(result) => return Ok(result),
            Err(e) => {
                attempts += 1;
                if attempts >= max_retries {
                    return Err(e);
                }

                println!("Attempt {} failed: {}. Retrying in {:?}...", attempts, e, delay);
                sleep(delay).await;
                delay *= 2;
            }
        }
    }
}

// Parallel task execution with result collection
pub async fn execute_parallel_tasks<F, Fut, T>(
    tasks: Vec<F>,
) -> Vec<T>
where
    F: FnOnce() -> Fut,
    Fut: std::future::Future<Output = T> + Send + 'static,
    T: Send + 'static,
{
    let mut futures = FuturesUnordered::new();

    for task in tasks {
        futures.push(tokio::spawn(task()));
    }

    let mut results = Vec::new();
    while let Some(result) = futures.next().await {
        if let Ok(value) = result {
            results.push(value);
        }
    }

    results
}

// Stream throttling
pub async fn throttle_stream<S, T>(
    stream: S,
    rate_per_second: u64,
) -> impl Stream<Item = T>
where
    S: Stream<Item = T>,
{
    let delay_between = Duration::from_millis(1000 / rate_per_second);
    
    stream.then(move |item| async move {
        sleep(delay_between).await;
        item
    })
}

// Chunked stream processing
pub async fn process_in_chunks<S, F, Fut, T, R>(
    stream: S,
    chunk_size: usize,
    process_chunk: F,
) -> Vec<R>
where
    S: Stream<Item = T> + Unpin,
    F: Fn(Vec<T>) -> Fut,
    Fut: std::future::Future<Output = R>,
{
    let mut results = Vec::new();
    let mut chunks = stream.chunks(chunk_size);

    while let Some(chunk) = chunks.next().await {
        let result = process_chunk(chunk).await;
        results.push(result);
    }

    results
}

// Example async task with combinators
pub async fn complex_async_workflow(user_id: String) -> Result<String, String> {
    // Fetch user data
    let user_data = fetch_user(&user_id)
        .then(|result| async move {
            result.map_err(|e| format!("Failed to fetch user: {}", e))
        })
        .await?;

    // Fetch related data in parallel
    let (posts, comments) = tokio::try_join!(
        fetch_user_posts(&user_id),
        fetch_user_comments(&user_id),
    ).map_err(|e| format!("Failed to fetch related data: {}", e))?;

    // Process data
    let summary = format!(
        "User: {}, Posts: {}, Comments: {}",
        user_data,
        posts.len(),
        comments.len()
    );

    Ok(summary)
}

// Helper functions for the example
async fn fetch_user(user_id: &str) -> Result<String, String> {
    sleep(Duration::from_millis(100)).await;
    Ok(format!("User({})", user_id))
}

async fn fetch_user_posts(user_id: &str) -> Result<Vec<String>, String> {
    sleep(Duration::from_millis(150)).await;
    Ok(vec!["Post1".to_string(), "Post2".to_string()])
}

async fn fetch_user_comments(user_id: &str) -> Result<Vec<String>, String> {
    sleep(Duration::from_millis(120)).await;
    Ok(vec!["Comment1".to_string()])
}

#[tokio::main]
async fn main() {
    // Custom Future
    let delayed = DelayedValue::new(42, Duration::from_millis(100));
    let value = delayed.await;
    println!("Delayed value: {}", value);

    // Custom Stream
    let stream = NumberStream::new(5, Duration::from_millis(50));
    let numbers: Vec<_> = stream.collect().await;
    println!("Stream numbers: {:?}", numbers);

    // Stream with timeout
    let infinite_stream = futures::stream::repeat(1);
    let results = process_stream_with_timeout(infinite_stream, Duration::from_secs(1)).await;
    println!("Collected {} items before timeout", results.len());

    // Buffered processing
    let stream = futures::stream::iter(0..10);
    let results = process_stream_buffered(stream, 3, |n| async move {
        sleep(Duration::from_millis(100)).await;
        n * 2
    }).await;
    println!("Buffered results: {:?}", results);

    // Retry with backoff
    let mut attempt = 0;
    let result = retry_with_backoff(
        || {
            attempt += 1;
            async move {
                if attempt < 3 {
                    Err("Temporary failure")
                } else {
                    Ok("Success!")
                }
            }
        },
        5,
        Duration::from_millis(100),
    ).await;
    println!("Retry result: {:?}", result);

    // Complex workflow
    match complex_async_workflow("user123".to_string()).await {
        Ok(summary) => println!("Workflow result: {}", summary),
        Err(e) => println!("Workflow error: {}", e),
    }
}
"""
    }

]