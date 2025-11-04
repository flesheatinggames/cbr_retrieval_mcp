RUST_RAYON_CASES = [
    {
        "problem": """
Parallel data processing using Rayon with custom iterators, error handling, and progress tracking.
""",
        "solution": """
use rayon::prelude::*;
use std::sync::{Arc, Mutex};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::time::{Duration, Instant};
use indicatif::{ProgressBar, ProgressStyle};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum ProcessingError {
    #[error("Failed to process item {item_id}: {reason}")]
    ItemProcessingFailed { item_id: String, reason: String },
    
    #[error("Validation failed: {0}")]
    ValidationError(String),
    
    #[error("Resource exhausted")]
    ResourceExhausted,
}

#[derive(Debug, Clone)]
pub struct DataItem {
    pub id: String,
    pub value: f64,
    pub metadata: Vec<String>,
}

#[derive(Debug)]
pub struct ProcessedItem {
    pub id: String,
    pub result: f64,
    pub processing_time_ms: u128,
}

#[derive(Debug)]
pub struct ProcessingStats {
    pub total_items: usize,
    pub successful: AtomicUsize,
    pub failed: AtomicUsize,
    pub total_time: Duration,
}

impl ProcessingStats {
    pub fn new(total_items: usize) -> Self {
        Self {
            total_items,
            successful: AtomicUsize::new(0),
            failed: AtomicUsize::new(0),
            total_time: Duration::default(),
        }
    }

    pub fn record_success(&self) {
        self.successful.fetch_add(1, Ordering::Relaxed);
    }

    pub fn record_failure(&self) {
        self.failed.fetch_add(1, Ordering::Relaxed);
    }

    pub fn print_summary(&self) {
        let successful = self.successful.load(Ordering::Relaxed);
        let failed = self.failed.load(Ordering::Relaxed);
        
        println!("\n=== Processing Summary ===");
        println!("Total items: {}", self.total_items);
        println!("Successful: {} ({:.2}%)", successful, 
            (successful as f64 / self.total_items as f64) * 100.0);
        println!("Failed: {} ({:.2}%)", failed,
            (failed as f64 / self.total_items as f64) * 100.0);
        println!("Total time: {:.2}s", self.total_time.as_secs_f64());
        println!("Throughput: {:.2} items/sec", 
            self.total_items as f64 / self.total_time.as_secs_f64());
    }
}

// Complex processing function
fn process_item(item: &DataItem) -> Result<ProcessedItem, ProcessingError> {
    let start = Instant::now();
    
    // Validation
    if item.value < 0.0 {
        return Err(ProcessingError::ValidationError(
            format!("Item {} has negative value", item.id)
        ));
    }
    
    // Simulate complex computation
    std::thread::sleep(Duration::from_millis(10));
    
    // Compute result
    let result = item.value.sqrt() * item.metadata.len() as f64;
    
    Ok(ProcessedItem {
        id: item.id.clone(),
        result,
        processing_time_ms: start.elapsed().as_millis(),
    })
}

// Parallel batch processing with progress tracking
pub fn process_batch_parallel(
    items: Vec<DataItem>,
) -> (Vec<ProcessedItem>, Vec<(String, ProcessingError)>) {
    let total = items.len();
    let stats = Arc::new(ProcessingStats::new(total));
    
    // Create progress bar
    let pb = ProgressBar::new(total as u64);
    pb.set_style(
        ProgressStyle::default_bar()
            .template("[{elapsed_precise}] {bar:40.cyan/blue} {pos}/{len} ({eta})")
            .unwrap()
            .progress_chars("##-")
    );
    
    let start = Instant::now();
    
    // Process items in parallel
    let (successes, errors): (Vec<_>, Vec<_>) = items
        .par_iter()
        .map(|item| {
            let result = process_item(item);
            
            match &result {
                Ok(_) => stats.record_success(),
                Err(_) => stats.record_failure(),
            }
            
            pb.inc(1);
            
            match result {
                Ok(processed) => Ok(processed),
                Err(e) => Err((item.id.clone(), e)),
            }
        })
        .partition_map(|result| match result {
            Ok(item) => rayon::iter::Either::Left(item),
            Err(error) => rayon::iter::Either::Right(error),
        });
    
    pb.finish_with_message("Processing complete");
    
    let mut stats = Arc::try_unwrap(stats).unwrap();
    stats.total_time = start.elapsed();
    stats.print_summary();
    
    (successes, errors)
}

// Chunked parallel processing for very large datasets
pub fn process_large_dataset_chunked(
    items: Vec<DataItem>,
    chunk_size: usize,
) -> Vec<ProcessedItem> {
    items
        .par_chunks(chunk_size)
        .flat_map(|chunk| {
            chunk
                .iter()
                .filter_map(|item| process_item(item).ok())
                .collect::<Vec<_>>()
        })
        .collect()
}

// Parallel aggregation with custom reducer
pub fn parallel_sum_of_values(items: &[DataItem]) -> f64 {
    items
        .par_iter()
        .map(|item| item.value)
        .sum()
}

pub fn parallel_statistics(items: &[DataItem]) -> Statistics {
    let results: Vec<_> = items
        .par_iter()
        .map(|item| {
            let val = item.value;
            PartialStats {
                sum: val,
                sum_squared: val * val,
                min: val,
                max: val,
                count: 1,
            }
        })
        .collect();
    
    // Reduce to final statistics
    let total = results.par_iter().reduce(
        || PartialStats::default(),
        |a, b| PartialStats {
            sum: a.sum + b.sum,
            sum_squared: a.sum_squared + b.sum_squared,
            min: a.min.min(b.min),
            max: a.max.max(b.max),
            count: a.count + b.count,
        },
    );
    
    let mean = total.sum / total.count as f64;
    let variance = (total.sum_squared / total.count as f64) - (mean * mean);
    
    Statistics {
        count: total.count,
        sum: total.sum,
        mean,
        variance,
        std_dev: variance.sqrt(),
        min: total.min,
        max: total.max,
    }
}

#[derive(Debug, Default)]
struct PartialStats {
    sum: f64,
    sum_squared: f64,
    min: f64,
    max: f64,
    count: usize,
}

#[derive(Debug)]
pub struct Statistics {
    pub count: usize,
    pub sum: f64,
    pub mean: f64,
    pub variance: f64,
    pub std_dev: f64,
    pub min: f64,
    pub max: f64,
}

// Parallel filtering and transformation
pub fn parallel_filter_transform(
    items: Vec<DataItem>,
    threshold: f64,
) -> Vec<ProcessedItem> {
    items
        .into_par_iter()
        .filter(|item| item.value > threshold)
        .filter_map(|item| process_item(&item).ok())
        .collect()
}

// Parallel grouping
use std::collections::HashMap;

pub fn parallel_group_by_range(items: Vec<DataItem>) -> HashMap<String, Vec<DataItem>> {
    let ranges = vec![
        ("low", 0.0..=10.0),
        ("medium", 10.0..=50.0),
        ("high", 50.0..=100.0),
    ];
    
    let groups: Vec<_> = ranges
        .into_par_iter()
        .map(|(label, range)| {
            let filtered: Vec<_> = items
                .iter()
                .filter(|item| range.contains(&item.value))
                .cloned()
                .collect();
            (label.to_string(), filtered)
        })
        .collect();
    
    groups.into_iter().collect()
}

// Example usage
fn main() {
    // Generate sample data
    let items: Vec<DataItem> = (0..1000)
        .map(|i| DataItem {
            id: format!("item-{}", i),
            value: (i as f64) * 0.5,
            metadata: vec![format!("tag-{}", i % 10)],
        })
        .collect();
    
    println!("Processing {} items in parallel...\n", items.len());
    
    // Parallel batch processing
    let (successes, errors) = process_batch_parallel(items.clone());
    
    if !errors.is_empty() {
        println!("\nErrors encountered:");
        for (id, error) in errors.iter().take(5) {
            println!("  {}: {}", id, error);
        }
        if errors.len() > 5 {
            println!("  ... and {} more errors", errors.len() - 5);
        }
    }
    
    // Compute statistics
    println!("\nComputing statistics...");
    let stats = parallel_statistics(&items);
    println!("Statistics:");
    println!("  Count: {}", stats.count);
    println!("  Mean: {:.2}", stats.mean);
    println!("  Std Dev: {:.2}", stats.std_dev);
    println!("  Min: {:.2}", stats.min);
    println!("  Max: {:.2}", stats.max);
    
    // Group by range
    println!("\nGrouping by ranges...");
    let groups = parallel_group_by_range(items.clone());
    for (label, group) in groups {
        println!("  {}: {} items", label, group.len());
    }
}
""",
        "category": "rust",
        "subcategory": "rayon",
        "tags": ["error-handling", "filter", "form", "orm", "rayon", "rust", "sse"],
    }
]
