
RUST_CROSSBEAM_CASES = [
    
    # ============================================
    # CROSSBEAM CONCURRENT DATA STRUCTURES
    # ============================================
    {
        "problem": "Lock-free concurrent programming using crossbeam channels and atomic operations.",
        "solution": """
use crossbeam::{
    channel::{bounded, unbounded, select, Sender, Receiver},
    thread,
};
use std::sync::Arc;
use std::sync::atomic::{AtomicU64, AtomicBool, Ordering};
use std::time::Duration;

// Lock-free counter
pub struct Counter {
    value: AtomicU64,
}

impl Counter {
    pub fn new() -> Self {
        Self {
            value: AtomicU64::new(0),
        }
    }

    pub fn increment(&self) -> u64 {
        self.value.fetch_add(1, Ordering::SeqCst)
    }

    pub fn get(&self) -> u64 {
        self.value.load(Ordering::SeqCst)
    }
}

// Multi-producer, multi-consumer queue
pub struct WorkQueue<T> {
    sender: Sender<T>,
    receiver: Receiver<T>,
    shutdown: Arc<AtomicBool>,
}

impl<T: Send + 'static> WorkQueue<T> {
    pub fn new(capacity: usize) -> Self {
        let (sender, receiver) = bounded(capacity);
        Self {
            sender,
            receiver,
            shutdown: Arc::new(AtomicBool::new(false)),
        }
    }

    pub fn sender(&self) -> Sender<T> {
        self.sender.clone()
    }

    pub fn spawn_workers<F>(&self, num_workers: usize, mut work_fn: F)
    where
        F: FnMut(T) + Send + Clone + 'static,
    {
        let receiver = self.receiver.clone();
        let shutdown = self.shutdown.clone();

        for id in 0..num_workers {
            let receiver = receiver.clone();
            let shutdown = shutdown.clone();
            let mut work_fn = work_fn.clone();

            thread::spawn(move || {
                println!("Worker {} started", id);
                
                while !shutdown.load(Ordering::Relaxed) {
                    match receiver.recv_timeout(Duration::from_millis(100)) {
                        Ok(item) => {
                            work_fn(item);
                        }
                        Err(crossbeam::channel::RecvTimeoutError::Timeout) => continue,
                        Err(crossbeam::channel::RecvTimeoutError::Disconnected) => break,
                    }
                }
                
                println!("Worker {} stopped", id);
            });
        }
    }

    pub fn shutdown(&self) {
        self.shutdown.store(true, Ordering::Relaxed);
    }
}

// Select pattern for multiple channels
pub fn multiplexed_receiver<T: Send>(receivers: Vec<Receiver<T>>) -> Vec<T> {
    let mut results = Vec::new();
    let mut active_receivers = receivers;

    loop {
        let mut sel = select! {};
        
        for (idx, rx) in active_receivers.iter().enumerate() {
            sel = sel.recv(rx, move |msg| (idx, msg));
        }

        match sel {
            Ok((idx, Ok(value))) => {
                results.push(value);
            }
            Ok((idx, Err(_))) => {
                active_receivers.remove(idx);
                if active_receivers.is_empty() {
                    break;
                }
            }
            Err(_) => break,
        }
    }

    results
}

// Pipeline pattern
pub fn create_pipeline() {
    let (input_tx, input_rx) = unbounded::<i32>();
    let (stage1_tx, stage1_rx) = unbounded::<i32>();
    let (stage2_tx, stage2_rx) = unbounded::<i32>();

    // Stage 1: Double the input
    thread::spawn(move || {
        for num in input_rx {
            let result = num * 2;
            println!("Stage 1: {} -> {}", num, result);
            let _ = stage1_tx.send(result);
        }
    });

    // Stage 2: Add 10
    thread::spawn(move || {
        for num in stage1_rx {
            let result = num + 10;
            println!("Stage 2: {} -> {}", num, result);
            let _ = stage2_tx.send(result);
        }
    });

    // Output consumer
    thread::spawn(move || {
        for result in stage2_rx {
            println!("Final result: {}", result);
        }
    });

    // Send some data through the pipeline
    for i in 1..=5 {
        input_tx.send(i).unwrap();
    }
    
    drop(input_tx); // Close the pipeline

    thread::sleep(Duration::from_secs(1));
}

// Fan-out / Fan-in pattern
pub fn fan_out_fan_in() {
    let (input_tx, input_rx) = unbounded::<i32>();
    let output_receivers: Vec<_> = (0..3)
        .map(|worker_id| {
            let (tx, rx) = unbounded();
            let input_rx = input_rx.clone();

            thread::spawn(move || {
                for num in input_rx {
                    let result = num * worker_id;
                    println!("Worker {} processed: {}", worker_id, result);
                    thread::sleep(Duration::from_millis(100));
                    let _ = tx.send(result);
                }
            });

            rx
        })
        .collect();

    drop(input_rx);

    // Fan-in: collect results from all workers
    thread::spawn(move || {
        let results = multiplexed_receiver(output_receivers);
        println!("Collected {} results", results.len());
        for result in results {
            println!("Result: {}", result);
        }
    });

    // Send work
    for i in 1..=10 {
        input_tx.send(i).unwrap();
    }

    drop(input_tx);
    thread::sleep(Duration::from_secs(2));
}

fn main() {
    // Lock-free counter
    let counter = Arc::new(Counter::new());
    let handles: Vec<_> = (0..10)
        .map(|_| {
            let counter = counter.clone();
            thread::spawn(move || {
                for _ in 0..1000 {
                    counter.increment();
                }
            })
        })
        .collect();

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final count: {}", counter.get());

    // Work queue
    let queue = WorkQueue::new(10);
    queue.spawn_workers(3, |item: i32| {
        println!("Processing item: {}", item);
        thread::sleep(Duration::from_millis(100));
    });

    let sender = queue.sender();
    for i in 0..20 {
        sender.send(i).unwrap();
    }

    thread::sleep(Duration::from_secs(3));
    queue.shutdown();

    // Pipeline
    println!("\\nRunning pipeline...");
    create_pipeline();

    // Fan-out/Fan-in
    println!("\\nRunning fan-out/fan-in...");
    fan_out_fan_in();
}
"""
    }

]