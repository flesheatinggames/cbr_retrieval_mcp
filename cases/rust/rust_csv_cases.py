RUST_CSV_CASES = [
    {
        "problem": """
High-performance CSV reading, writing, and data transformation.
""",
        "solution": """
use csv::{Reader, Writer, StringRecord};
use serde::{Deserialize, Serialize};
use std::error::Error;
use std::io;

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Customer {
    pub id: u32,
    pub name: String,
    pub email: String,
    pub age: u32,
    pub country: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Order {
    pub order_id: u32,
    pub customer_id: u32,
    pub product: String,
    pub quantity: u32,
    pub price: f64,
}

// Read CSV into structs
pub fn read_customers(path: &str) -> Result<Vec<Customer>, Box<dyn Error>> {
    let mut reader = Reader::from_path(path)?;
    let mut customers = Vec::new();

    for result in reader.deserialize() {
        let customer: Customer = result?;
        customers.push(customer);
    }

    Ok(customers)
}

// Write structs to CSV
pub fn write_customers(path: &str, customers: &[Customer]) -> Result<(), Box<dyn Error>> {
    let mut writer = Writer::from_path(path)?;

    for customer in customers {
        writer.serialize(customer)?;
    }

    writer.flush()?;
    Ok(())
}

// Stream processing for large files
pub fn process_large_csv<F>(
    input_path: &str,
    output_path: &str,
    mut processor: F,
) -> Result<usize, Box<dyn Error>>
where
    F: FnMut(&mut Customer) -> bool,
{
    let mut reader = Reader::from_path(input_path)?;
    let mut writer = Writer::from_path(output_path)?;
    let mut processed_count = 0;

    for result in reader.deserialize() {
        let mut customer: Customer = result?;
        
        if processor(&mut customer) {
            writer.serialize(&customer)?;
            processed_count += 1;
        }
    }

    writer.flush()?;
    Ok(processed_count)
}

// Aggregate data from CSV
pub fn aggregate_by_country(path: &str) -> Result<std::collections::HashMap<String, Vec<Customer>>, Box<dyn Error>> {
    let customers = read_customers(path)?;
    let mut by_country = std::collections::HashMap::new();

    for customer in customers {
        by_country
            .entry(customer.country.clone())
            .or_insert_with(Vec::new)
            .push(customer);
    }

    Ok(by_country)
}

// Join two CSV files
pub fn join_customers_orders(
    customers_path: &str,
    orders_path: &str,
) -> Result<Vec<(Customer, Vec<Order>)>, Box<dyn Error>> {
    let customers = read_customers(customers_path)?;
    let mut orders_reader = Reader::from_path(orders_path)?;
    
    let mut orders_by_customer: std::collections::HashMap<u32, Vec<Order>> = std::collections::HashMap::new();
    
    for result in orders_reader.deserialize() {
        let order: Order = result?;
        orders_by_customer
            .entry(order.customer_id)
            .or_insert_with(Vec::new)
            .push(order);
    }

    let joined: Vec<_> = customers
        .into_iter()
        .map(|customer| {
            let orders = orders_by_customer
                .remove(&customer.id)
                .unwrap_or_default();
            (customer, orders)
        })
        .collect();

    Ok(joined)
}

// CSV transformation with custom delimiter
pub fn convert_delimiter(
    input_path: &str,
    output_path: &str,
    input_delimiter: u8,
    output_delimiter: u8,
) -> Result<(), Box<dyn Error>> {
    let mut reader = csv::ReaderBuilder::new()
        .delimiter(input_delimiter)
        .from_path(input_path)?;

    let mut writer = csv::WriterBuilder::new()
        .delimiter(output_delimiter)
        .from_path(output_path)?;

    // Write headers
    let headers = reader.headers()?.clone();
    writer.write_record(&headers)?;

    // Copy all records
    for result in reader.records() {
        let record = result?;
        writer.write_record(&record)?;
    }

    writer.flush()?;
    Ok(())
}

// Statistics from CSV
#[derive(Debug)]
pub struct Statistics {
    pub count: usize,
    pub avg_age: f64,
    pub min_age: u32,
    pub max_age: u32,
}

pub fn calculate_statistics(path: &str) -> Result<Statistics, Box<dyn Error>> {
    let customers = read_customers(path)?;
    
    if customers.is_empty() {
        return Ok(Statistics {
            count: 0,
            avg_age: 0.0,
            min_age: 0,
            max_age: 0,
        });
    }

    let sum: u32 = customers.iter().map(|c| c.age).sum();
    let avg_age = sum as f64 / customers.len() as f64;
    let min_age = customers.iter().map(|c| c.age).min().unwrap();
    let max_age = customers.iter().map(|c| c.age).max().unwrap();

    Ok(Statistics {
        count: customers.len(),
        avg_age,
        min_age,
        max_age,
    })
}

// Filter and export
pub fn export_filtered(
    path: &str,
    output_path: &str,
    min_age: u32,
    country: Option<&str>,
) -> Result<usize, Box<dyn Error>> {
    process_large_csv(path, output_path, |customer| {
        let age_ok = customer.age >= min_age;
        let country_ok = country.map_or(true, |c| customer.country == c);
        age_ok && country_ok
    })
}

// Parallel CSV processing
use rayon::prelude::*;

pub fn parallel_process_csv(path: &str) -> Result<Vec<Customer>, Box<dyn Error>> {
    let customers = read_customers(path)?;
    
    let processed: Vec<_> = customers
        .into_par_iter()
        .map(|mut customer| {
            // Simulate expensive processing
            customer.email = customer.email.to_lowercase();
            customer.name = customer.name.trim().to_string();
            customer
        })
        .collect();

    Ok(processed)
}

// Example usage
fn main() -> Result<(), Box<dyn Error>> {
    // Create sample data
    let customers = vec![
        Customer {
            id: 1,
            name: "John Doe".to_string(),
            email: "john@example.com".to_string(),
            age: 30,
            country: "USA".to_string(),
        },
        Customer {
            id: 2,
            name: "Jane Smith".to_string(),
            email: "jane@example.com".to_string(),
            age: 25,
            country: "UK".to_string(),
        },
        Customer {
            id: 3,
            name: "Bob Johnson".to_string(),
            email: "bob@example.com".to_string(),
            age: 35,
            country: "USA".to_string(),
        },
    ];

    // Write to CSV
    write_customers("customers.csv", &customers)?;
    println!("Wrote {} customers", customers.len());

    // Read from CSV
    let loaded = read_customers("customers.csv")?;
    println!("Loaded {} customers", loaded.len());

    // Calculate statistics
    let stats = calculate_statistics("customers.csv")?;
    println!("Statistics: {:?}", stats);

    // Group by country
    let by_country = aggregate_by_country("customers.csv")?;
    for (country, customers) in by_country {
        println!("{}: {} customers", country, customers.len());
    }

    // Export filtered data
    let filtered_count = export_filtered("customers.csv", "filtered.csv", 28, Some("USA"))?;
    println!("Exported {} filtered customers", filtered_count);

    Ok(())
}
""",
        "category": "rust",
        "subcategory": "csv",
        "tags": ["csv", "filter", "form", "orm", "performance", "rayon", "rust"],
    }
]
