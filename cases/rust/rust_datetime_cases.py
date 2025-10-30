
RUST_DATETIME_CASES = [
    
    # ============================================
    # CHRONO DATE/TIME
    # ============================================
    {
        "problem": "Comprehensive date and time handling using chrono with timezones, formatting, and parsing.",
        "solution": """
use chrono::{DateTime, Utc, Local, NaiveDate, NaiveTime, NaiveDateTime, Duration};
use chrono::{Datelike, Timelike, Weekday};
use chrono_tz::{Tz, America, Europe, Asia};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TimeRange {
    pub start: DateTime<Utc>,
    pub end: DateTime<Utc>,
}

impl TimeRange {
    pub fn new(start: DateTime<Utc>, end: DateTime<Utc>) -> Self {
        Self { start, end }
    }

    pub fn duration(&self) -> Duration {
        self.end - self.start
    }

    pub fn contains(&self, dt: &DateTime<Utc>) -> bool {
        dt >= &self.start && dt <= &self.end
    }

    pub fn overlaps(&self, other: &TimeRange) -> bool {
        self.start < other.end && other.start < self.end
    }
}

// Working with different timezones
pub fn timezone_conversions() {
    let utc_now = Utc::now();
    println!("UTC: {}", utc_now.to_rfc3339());

    // Convert to different timezones
    let ny_time = utc_now.with_timezone(&America::New_York);
    println!("New York: {}", ny_time.format("%Y-%m-%d %H:%M:%S %Z"));

    let london_time = utc_now.with_timezone(&Europe::London);
    println!("London: {}", london_time.format("%Y-%m-%d %H:%M:%S %Z"));

    let tokyo_time = utc_now.with_timezone(&Asia::Tokyo);
    println!("Tokyo: {}", tokyo_time.format("%Y-%m-%d %H:%M:%S %Z"));
}

// Date arithmetic and business logic
pub fn calculate_business_days(start: NaiveDate, end: NaiveDate) -> i64 {
    let mut current = start;
    let mut business_days = 0;

    while current <= end {
        let weekday = current.weekday();
        if weekday != Weekday::Sat && weekday != Weekday::Sun {
            business_days += 1;
        }
        current = current.succ_opt().unwrap();
    }

    business_days
}

pub fn add_business_days(start: NaiveDate, days: i64) -> NaiveDate {
    let mut current = start;
    let mut remaining = days;

    while remaining > 0 {
        current = current.succ_opt().unwrap();
        let weekday = current.weekday();
        if weekday != Weekday::Sat && weekday != Weekday::Sun {
            remaining -= 1;
        }
    }

    current
}

// Parsing and formatting
pub fn parse_various_formats(input: &str) -> Result<DateTime<Utc>, chrono::ParseError> {
    // Try multiple formats
    let formats = vec![
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S%.f",
        "%d/%m/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
    ];

    for format in formats {
        if let Ok(naive) = NaiveDateTime::parse_from_str(input, format) {
            return Ok(DateTime::from_naive_utc_and_offset(naive, Utc));
        }
    }

    // Try RFC3339
    input.parse::<DateTime<Utc>>()
}

pub fn format_human_readable(dt: DateTime<Utc>) -> String {
    let now = Utc::now();
    let diff = now - dt;

    if diff < Duration::minutes(1) {
        "just now".to_string()
    } else if diff < Duration::hours(1) {
        format!("{} minutes ago", diff.num_minutes())
    } else if diff < Duration::days(1) {
        format!("{} hours ago", diff.num_hours())
    } else if diff < Duration::days(7) {
        format!("{} days ago", diff.num_days())
    } else if diff < Duration::days(30) {
        format!("{} weeks ago", diff.num_weeks())
    } else {
        dt.format("%B %d, %Y").to_string()
    }
}

// Recurring events
#[derive(Debug)]
pub enum RecurrenceRule {
    Daily,
    Weekly { day: Weekday },
    Monthly { day_of_month: u32 },
    Yearly { month: u32, day: u32 },
}

pub fn generate_occurrences(
    start: DateTime<Utc>,
    rule: RecurrenceRule,
    count: usize,
) -> Vec<DateTime<Utc>> {
    let mut occurrences = Vec::new();
    let mut current = start;

    for _ in 0..count {
        occurrences.push(current);
        
        current = match rule {
            RecurrenceRule::Daily => current + Duration::days(1),
            RecurrenceRule::Weekly { day } => {
                let mut next = current + Duration::days(1);
                while next.weekday() != day {
                    next = next + Duration::days(1);
                }
                next
            }
            RecurrenceRule::Monthly { day_of_month } => {
                let next_month = if current.month() == 12 {
                    NaiveDate::from_ymd_opt(current.year() + 1, 1, day_of_month)
                } else {
                    NaiveDate::from_ymd_opt(current.year(), current.month() + 1, day_of_month)
                };
                
                if let Some(date) = next_month {
                    DateTime::from_naive_utc_and_offset(
                        date.and_time(current.time()),
                        Utc,
                    )
                } else {
                    current
                }
            }
            RecurrenceRule::Yearly { month, day } => {
                if let Some(date) = NaiveDate::from_ymd_opt(current.year() + 1, month, day) {
                    DateTime::from_naive_utc_and_offset(
                        date.and_time(current.time()),
                        Utc,
                    )
                } else {
                    current
                }
            }
        };
    }

    occurrences
}

// Working hours calculation
pub struct WorkingHours {
    pub start: NaiveTime,
    pub end: NaiveTime,
}

impl WorkingHours {
    pub fn standard() -> Self {
        Self {
            start: NaiveTime::from_hms_opt(9, 0, 0).unwrap(),
            end: NaiveTime::from_hms_opt(17, 0, 0).unwrap(),
        }
    }

    pub fn is_within_hours(&self, dt: DateTime<Utc>) -> bool {
        let time = dt.time();
        time >= self.start && time <= self.end
    }

    pub fn next_available_time(&self, dt: DateTime<Utc>) -> DateTime<Utc> {
        let mut current = dt;

        loop {
            // Skip weekends
            let weekday = current.weekday();
            if weekday == Weekday::Sat || weekday == Weekday::Sun {
                current = current + Duration::days(1);
                current = current
                    .date_naive()
                    .and_time(self.start)
                    .and_utc();
                continue;
            }

            // Check if within working hours
            if current.time() < self.start {
                return current.date_naive().and_time(self.start).and_utc();
            } else if current.time() > self.end {
                current = current + Duration::days(1);
                current = current.date_naive().and_time(self.start).and_utc();
            } else {
                return current;
            }
        }
    }
}

// Example usage
fn main() {
    // Timezone conversions
    timezone_conversions();

    // Business days
    let start_date = NaiveDate::from_ymd_opt(2025, 1, 1).unwrap();
    let end_date = NaiveDate::from_ymd_opt(2025, 1, 31).unwrap();
    let business_days = calculate_business_days(start_date, end_date);
    println!("Business days in January 2025: {}", business_days);

    // Add 10 business days
    let future_date = add_business_days(start_date, 10);
    println!("10 business days from Jan 1: {}", future_date);

    // Human-readable formatting
    let past = Utc::now() - Duration::hours(5);
    println!("Relative time: {}", format_human_readable(past));

    // Recurring events
    let start = Utc::now();
    let weekly_meetings = generate_occurrences(
        start,
        RecurrenceRule::Weekly { day: Weekday::Mon },
        4,
    );
    println!("Next 4 Monday meetings:");
    for meeting in weekly_meetings {
        println!("  {}", meeting.format("%Y-%m-%d %H:%M"));
    }

    // Working hours
    let hours = WorkingHours::standard();
    let now = Utc::now();
    if hours.is_within_hours(now) {
        println!("Currently within working hours");
    } else {
        let next = hours.next_available_time(now);
        println!("Next available time: {}", next.format("%Y-%m-%d %H:%M"));
    }
}
"""
    }

]