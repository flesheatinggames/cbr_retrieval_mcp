"""
High-quality Leptos code examples for case-based reasoning.
Follows simple coding principles and idiomatic Rust standards.
"""

from typing import List, Dict, Any

RUST_LEPTOS_CASES: List[Dict[str, Any]] = [
    {
        "problem": """
A Leptos component for a user authentication form with reactive state management and validation.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use wasm_bindgen::JsCast;
use web_sys::{Event, SubmitEvent};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
struct LoginForm {
    email: String,
    password: String,
}

#[derive(Clone, Debug, Default)]
struct FormErrors {
    email: Option<String>,
    password: Option<String>,
    general: Option<String>,
}

#[component]
pub fn LoginComponent() -> impl IntoView {
    let (form_data, set_form_data) = create_signal(LoginForm::default());
    let (errors, set_errors) = create_signal(FormErrors::default());
    let (is_loading, set_is_loading) = create_signal(false);
    let (is_success, set_is_success) = create_signal(false);

    let validate_form = move || -> bool {
        let data = form_data.get();
        let mut new_errors = FormErrors::default();
        let mut is_valid = true;

        // Email validation
        if data.email.is_empty() {
            new_errors.email = Some("Email is required".to_string());
            is_valid = false;
        } else if !data.email.contains('@') {
            new_errors.email = Some("Please enter a valid email".to_string());
            is_valid = false;
        }

        // Password validation
        if data.password.is_empty() {
            new_errors.password = Some("Password is required".to_string());
            is_valid = false;
        } else if data.password.len() < 8 {
            new_errors.password = Some("Password must be at least 8 characters".to_string());
            is_valid = false;
        }

        set_errors.set(new_errors);
        is_valid
    };

    let on_submit = move |ev: SubmitEvent| {
        ev.prevent_default();
        
        if !validate_form() {
            return;
        }

        set_is_loading.set(true);
        set_errors.update(|e| e.general = None);

        let form_data_clone = form_data.get();
        
        spawn_local(async move {
            match login_user(form_data_clone).await {
                Ok(_) => {
                    set_is_success.set(true);
                    set_is_loading.set(false);
                }
                Err(e) => {
                    set_errors.update(|errors| {
                        errors.general = Some(format!("Login failed: {e}"));
                    });
                    set_is_loading.set(false);
                }
            }
        });
    };

    view! {
        <div class="login-container">
            <h2>"Login"</h2>
            
            <Show
                when=move || is_success.get()
                fallback=|| view! { <></> }
            >
                <div class="alert alert-success">
                    "Login successful!"
                </div>
            </Show>

            <Show
                when=move || errors.get().general.is_some()
                fallback=|| view! { <></> }
            >
                <div class="alert alert-danger">
                    {move || errors.get().general.unwrap_or_default()}
                </div>
            </Show>

            <form on:submit=on_submit>
                <div class="form-group">
                    <label for="email">"Email"</label>
                    <input
                        type="email"
                        id="email"
                        class="form-control"
                        class:is-invalid=move || errors.get().email.is_some()
                        prop:value=move || form_data.get().email
                        on:input=move |ev| {
                            set_form_data.update(|data| {
                                data.email = event_target_value(&ev);
                            });
                            set_errors.update(|e| e.email = None);
                        }
                    />
                    <Show
                        when=move || errors.get().email.is_some()
                        fallback=|| view! { <></> }
                    >
                        <div class="invalid-feedback">
                            {move || errors.get().email.unwrap_or_default()}
                        </div>
                    </Show>
                </div>

                <div class="form-group">
                    <label for="password">"Password"</label>
                    <input
                        type="password"
                        id="password"
                        class="form-control"
                        class:is-invalid=move || errors.get().password.is_some()
                        prop:value=move || form_data.get().password
                        on:input=move |ev| {
                            set_form_data.update(|data| {
                                data.password = event_target_value(&ev);
                            });
                            set_errors.update(|e| e.password = None);
                        }
                    />
                    <Show
                        when=move || errors.get().password.is_some()
                        fallback=|| view! { <></> }
                    >
                        <div class="invalid-feedback">
                            {move || errors.get().password.unwrap_or_default()}
                        </div>
                    </Show>
                </div>

                <button
                    type="submit"
                    class="btn btn-primary"
                    disabled=move || is_loading.get()
                >
                    <Show
                        when=move || is_loading.get()
                        fallback=|| view! { "Login" }
                    >
                        <span class="spinner-border spinner-border-sm"></span>
                        " Logging in..."
                    </Show>
                </button>
            </form>
        </div>
    }
}

async fn login_user(form_data: LoginForm) -> Result<(), String> {
    // Simulated API call
    gloo_timers::future::TimeoutFuture::new(1000).await;
    
    // In production, make actual API call
    if form_data.email == "test@example.com" && form_data.password == "password123" {
        Ok(())
    } else {
        Err("Invalid credentials".to_string())
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["api", "async", "auth", "authentication", "event", "form", "leptos", "validation"],
    },
    {
        "problem": """
A Leptos server function for fetching and caching data with error handling.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct User {
    pub id: u32,
    pub name: String,
    pub email: String,
    pub created_at: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ApiError {
    pub message: String,
    pub code: u16,
}

// Server function that can be called from the client
#[server(GetUsers, "/api")]
pub async fn get_users() -> Result<Vec<User>, ServerFnError> {
    use sqlx::PgPool;
    
    // Get database connection from context
    let pool = use_context::<PgPool>()
        .ok_or_else(|| ServerFnError::ServerError("Database connection not available".to_string()))?;
    
    // Query users from database
    let users = sqlx::query_as!(
        User,
        "SELECT id, name, email, created_at::text FROM users ORDER BY created_at DESC"
    )
    .fetch_all(&pool)
    .await
    .map_err(|e| ServerFnError::ServerError(format!("Database error: {e}")))?;
    
    Ok(users)
}

#[component]
pub fn UserList() -> impl IntoView {
    // Create resource for fetching users
    let users_resource = create_resource(
        || (),
        |_| async move { get_users().await },
    );

    view! {
        <div class="user-list">
            <h2>"Users"</h2>
            <Suspense fallback=move || view! { <div class="spinner">"Loading..."</div> }>
                {move || {
                    users_resource.get().map(|result| {
                        match result {
                            Ok(users) => {
                                view! {
                                    <ul class="list-group">
                                        <For
                                            each=move || users.clone()
                                            key=|user| user.id
                                            children=move |user: User| {
                                                view! {
                                                    <li class="list-group-item">
                                                        <div class="d-flex justify-content-between">
                                                            <div>
                                                                <strong>{user.name}</strong>
                                                                <br/>
                                                                <small>{user.email}</small>
                                                            </div>
                                                            <small class="text-muted">{user.created_at}</small>
                                                        </div>
                                                    </li>
                                                }
                                            }
                                        />
                                    </ul>
                                }
                            }
                            Err(e) => {
                                view! {
                                    <div class="alert alert-danger">
                                        "Error loading users: " {e.to_string()}
                                    </div>
                                }
                            }
                        }
                    })
                }}
            </Suspense>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["api", "async", "cache", "database", "error-handling", "leptos", "server-function"],
    },
    {
        "problem": """
A complex multi-step form with validation using custom hooks and separated concerns.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq)]
struct Address {
    street: String,
    city: String,
    state: String,
    zip: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize, PartialEq)]
pub struct UserProfile {
    first_name: String,
    last_name: String,
    email: String,
    phone: String,
    address: Address,
    preferences: HashMap<String, bool>,
}

#[derive(Clone, Debug, Default)]
pub struct ValidationErrors {
    errors: HashMap<String, String>,
}

impl ValidationErrors {
    fn add_error(&mut self, field: impl Into<String>, message: impl Into<String>) {
        self.errors.insert(field.into(), message.into());
    }

    fn get_error(&self, field: &str) -> Option<&String> {
        self.errors.get(field)
    }

    fn has_errors(&self) -> bool {
        !self.errors.is_empty()
    }

    fn clear_error(&mut self, field: &str) {
        self.errors.remove(field);
    }
}

pub fn use_form_validation() -> (
    ReadSignal<UserProfile>,
    WriteSignal<UserProfile>,
    ReadSignal<ValidationErrors>,
    impl Fn() -> bool + Clone,
    impl Fn(&str) + Clone,
) {
    let (profile, set_profile) = create_signal(UserProfile::default());
    let (errors, set_errors) = create_signal(ValidationErrors::default());

    let validate = move || -> bool {
        let data = profile.get();
        let mut new_errors = ValidationErrors::default();

        // First name validation
        if data.first_name.trim().is_empty() {
            new_errors.add_error("first_name", "First name is required");
        }

        // Last name validation
        if data.last_name.trim().is_empty() {
            new_errors.add_error("last_name", "Last name is required");
        }

        // Email validation
        let email_regex = regex::Regex::new(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
            .expect("Invalid regex pattern");
        if !email_regex.is_match(&data.email) {
            new_errors.add_error("email", "Please enter a valid email address");
        }

        // Phone validation
        let phone_regex = regex::Regex::new(r"^\d{10}$")
            .expect("Invalid regex pattern");
        let phone_digits: String = data.phone.chars().filter(|c| c.is_numeric()).collect();
        if !phone_regex.is_match(&phone_digits) {
            new_errors.add_error("phone", "Phone must be 10 digits");
        }

        // Address validation
        if data.address.street.trim().is_empty() {
            new_errors.add_error("address.street", "Street is required");
        }
        if data.address.city.trim().is_empty() {
            new_errors.add_error("address.city", "City is required");
        }
        if data.address.state.trim().is_empty() {
            new_errors.add_error("address.state", "State is required");
        }
        
        let zip_regex = regex::Regex::new(r"^\d{5}$")
            .expect("Invalid regex pattern");
        if !zip_regex.is_match(&data.address.zip) {
            new_errors.add_error("address.zip", "ZIP must be 5 digits");
        }

        let is_valid = !new_errors.has_errors();
        set_errors.set(new_errors);
        is_valid
    };

    let clear_field_error = move |field: &str| {
        set_errors.update(|e| e.clear_error(field));
    };

    (profile, set_profile, errors, validate, clear_field_error)
}

#[component]
pub fn UserProfileForm() -> impl IntoView {
    let (profile, set_profile, errors, validate, clear_field_error) = use_form_validation();
    let (is_submitting, set_is_submitting) = create_signal(false);
    let (submit_success, set_submit_success) = create_signal(false);

    let on_submit = move |ev: web_sys::SubmitEvent| {
        ev.prevent_default();
        
        if !validate() {
            return;
        }

        set_is_submitting.set(true);
        let profile_data = profile.get();
        
        spawn_local(async move {
            // Simulate API call
            gloo_timers::future::TimeoutFuture::new(1500).await;
            
            // In production, make actual API call
            log::info!("Submitting profile: {:?}", profile_data);
            
            set_submit_success.set(true);
            set_is_submitting.set(false);
        });
    };

    view! {
        <div class="container mt-4">
            <h2>"User Profile"</h2>
            
            <Show
                when=move || submit_success.get()
                fallback=|| view! { <></> }
            >
                <div class="alert alert-success">
                    "Profile updated successfully!"
                </div>
            </Show>

            <form on:submit=on_submit>
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">"First Name"</label>
                            <input
                                type="text"
                                class="form-control"
                                class:is-invalid=move || errors.get().get_error("first_name").is_some()
                                prop:value=move || profile.get().first_name
                                on:input=move |ev| {
                                    set_profile.update(|p| p.first_name = event_target_value(&ev));
                                    clear_field_error("first_name");
                                }
                            />
                            <Show
                                when=move || errors.get().get_error("first_name").is_some()
                                fallback=|| view! { <></> }
                            >
                                <div class="invalid-feedback">
                                    {move || errors.get().get_error("first_name").cloned().unwrap_or_default()}
                                </div>
                            </Show>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">"Last Name"</label>
                            <input
                                type="text"
                                class="form-control"
                                class:is-invalid=move || errors.get().get_error("last_name").is_some()
                                prop:value=move || profile.get().last_name
                                on:input=move |ev| {
                                    set_profile.update(|p| p.last_name = event_target_value(&ev));
                                    clear_field_error("last_name");
                                }
                            />
                            <Show
                                when=move || errors.get().get_error("last_name").is_some()
                                fallback=|| view! { <></> }
                            >
                                <div class="invalid-feedback">
                                    {move || errors.get().get_error("last_name").cloned().unwrap_or_default()}
                                </div>
                            </Show>
                        </div>
                    </div>
                </div>

                <h4 class="mt-4">"Address"</h4>
                <div class="mb-3">
                    <label class="form-label">"Street"</label>
                    <input
                        type="text"
                        class="form-control"
                        class:is-invalid=move || errors.get().get_error("address.street").is_some()
                        prop:value=move || profile.get().address.street
                        on:input=move |ev| {
                            set_profile.update(|p| p.address.street = event_target_value(&ev));
                            clear_field_error("address.street");
                        }
                    />
                </div>

                <button
                    type="submit"
                    class="btn btn-primary"
                    disabled=move || is_submitting.get()
                >
                    <Show
                        when=move || is_submitting.get()
                        fallback=|| view! { "Save Profile" }
                    >
                        <span class="spinner-border spinner-border-sm me-2"></span>
                        "Saving..."
                    </Show>
                </button>
            </form>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["api", "async", "event", "form", "hooks", "leptos", "validation"],
    },
    {
        "problem": """
A WebSocket-based real-time notification system with reconnection logic.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use futures::{SinkExt, StreamExt};
use gloo_net::websocket::{futures::WebSocket, Message};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Notification {
    pub id: String,
    pub message: String,
    pub notification_type: NotificationType,
    pub timestamp: i64,
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum NotificationType {
    Info,
    Success,
    Warning,
    Error,
}

#[derive(Clone, Debug, PartialEq)]
enum ConnectionStatus {
    Connecting,
    Connected,
    Disconnected,
    Error(String),
}

fn use_websocket(url: &'static str) -> (
    ReadSignal<Vec<Notification>>,
    ReadSignal<ConnectionStatus>,
    impl Fn() + Clone,
) {
    let (notifications, set_notifications) = create_signal(Vec::<Notification>::new());
    let (status, set_status) = create_signal(ConnectionStatus::Disconnected);

    let connect = move || {
        set_status.set(ConnectionStatus::Connecting);
        
        spawn_local(async move {
            match WebSocket::open(url) {
                Ok(ws) => {
                    set_status.set(ConnectionStatus::Connected);
                    let (mut write, mut read) = ws.split();
                    
                    // Handle incoming messages
                    while let Some(msg) = read.next().await {
                        match msg {
                            Ok(Message::Text(text)) => {
                                if let Ok(notification) = serde_json::from_str::<Notification>(&text) {
                                    set_notifications.update(|notifications| {
                                        notifications.push(notification);
                                    });
                                }
                            }
                            Err(e) => {
                                log::error!("WebSocket error: {:?}", e);
                                set_status.set(ConnectionStatus::Error(format!("Connection error: {e:?}")));
                                break;
                            }
                            _ => {}
                        }
                    }
                    
                    set_status.set(ConnectionStatus::Disconnected);
                }
                Err(e) => {
                    log::error!("Failed to connect: {:?}", e);
                    set_status.set(ConnectionStatus::Error(format!("Failed to connect: {e:?}")));
                }
            }
        });
    };

    (notifications, status, connect)
}

#[component]
pub fn NotificationCenter(url: &'static str) -> impl IntoView {
    let (notifications, status, connect) = use_websocket(url);
    let (show_panel, set_show_panel) = create_signal(false);
    
    // Auto-connect on mount
    create_effect(move |_| {
        connect();
    });
    
    let unread_count = move || notifications.get().len();
    
    let clear_notification = move |id: String| {
        set_notifications.update(|notifications| {
            notifications.retain(|n| n.id != id);
        });
    };

    view! {
        <div class="notification-center">
            <button
                class="notification-button"
                on:click=move |_| set_show_panel.update(|show| *show = !*show)
            >
                <i class="bell-icon"></i>
                <Show when=move || unread_count() > 0 fallback=|| view! { <></> }>
                    <span class="badge">{unread_count}</span>
                </Show>
            </button>
            
            <Show when=move || show_panel.get() fallback=|| view! { <></> }>
                <div class="notification-panel">
                    <div class="notification-header">
                        <h3>"Notifications"</h3>
                        <div class="status">
                            {move || match status.get() {
                                ConnectionStatus::Connected => view! { <span class="text-success">"Connected"</span> },
                                ConnectionStatus::Connecting => view! { <span class="text-warning">"Connecting..."</span> },
                                ConnectionStatus::Disconnected => view! { <span class="text-muted">"Disconnected"</span> },
                                ConnectionStatus::Error(e) => view! { <span class="text-danger">{e}</span> },
                            }}
                        </div>
                    </div>
                    
                    <div class="notification-list">
                        <For
                            each=move || notifications.get()
                            key=|n| n.id.clone()
                            children=move |notification: Notification| {
                                let notification_id = notification.id.clone();
                                let type_class = match notification.notification_type {
                                    NotificationType::Info => "notification-info",
                                    NotificationType::Success => "notification-success",
                                    NotificationType::Warning => "notification-warning",
                                    NotificationType::Error => "notification-error",
                                };
                                
                                view! {
                                    <div class={format!("notification-item {}", type_class)}>
                                        <div class="notification-content">
                                            <p>{notification.message}</p>
                                            <small>{notification.timestamp}</small>
                                        </div>
                                        <button
                                            class="close-btn"
                                            on:click=move |_| clear_notification(notification_id.clone())
                                        >
                                            "×"
                                        </button>
                                    </div>
                                }
                            }
                        />
                    </div>
                </div>
            </Show>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["async", "leptos", "real-time", "websocket", "notifications"],
    },
    {
        "problem": """
An infinite scroll component with pagination and loading states.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use wasm_bindgen::JsCast;
use web_sys::{Element, IntersectionObserver, IntersectionObserverEntry};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Post {
    pub id: u32,
    pub title: String,
    pub content: String,
    pub author: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PagedResponse {
    pub items: Vec<Post>,
    pub total: u32,
    pub page: u32,
    pub has_more: bool,
}

async fn fetch_posts(page: u32) -> Result<PagedResponse, String> {
    // Simulate API call
    gloo_timers::future::TimeoutFuture::new(500).await;
    
    let items = (0..20)
        .map(|i| Post {
            id: page * 20 + i,
            title: format!("Post {} - Page {}", i, page),
            content: format!("Content for post {}", i),
            author: format!("Author {}", i % 5),
        })
        .collect();
    
    Ok(PagedResponse {
        items,
        total: 1000,
        page,
        has_more: page < 50,
    })
}

#[component]
pub fn InfiniteScrollList() -> impl IntoView {
    let (posts, set_posts) = create_signal(Vec::<Post>::new());
    let (current_page, set_current_page) = create_signal(0_u32);
    let (is_loading, set_is_loading) = create_signal(false);
    let (has_more, set_has_more) = create_signal(true);
    let (error, set_error) = create_signal(None::<String>);
    
    let load_more = move || {
        if is_loading.get() || !has_more.get() {
            return;
        }
        
        set_is_loading.set(true);
        set_error.set(None);
        
        let next_page = current_page.get() + 1;
        
        spawn_local(async move {
            match fetch_posts(next_page).await {
                Ok(response) => {
                    set_posts.update(|posts| {
                        posts.extend(response.items);
                    });
                    set_current_page.set(next_page);
                    set_has_more.set(response.has_more);
                    set_is_loading.set(false);
                }
                Err(e) => {
                    set_error.set(Some(e));
                    set_is_loading.set(false);
                }
            }
        });
    };
    
    // Initial load
    create_effect(move |_| {
        if posts.get().is_empty() {
            load_more();
        }
    });
    
    let sentinel_ref = create_node_ref::<html::Div>();
    
    // Set up intersection observer
    create_effect(move |_| {
        if let Some(sentinel) = sentinel_ref.get() {
            let callback = Closure::wrap(Box::new(move |entries: Vec<IntersectionObserverEntry>| {
                if let Some(entry) = entries.first() {
                    if entry.is_intersecting() {
                        load_more();
                    }
                }
            }) as Box<dyn FnMut(Vec<IntersectionObserverEntry>)>);
            
            let observer = IntersectionObserver::new(callback.as_ref().unchecked_ref())
                .expect("Failed to create IntersectionObserver");
            
            observer.observe(&sentinel);
            callback.forget();
        }
    });

    view! {
        <div class="infinite-scroll-container">
            <h2>"Posts"</h2>
            
            <div class="post-list">
                <For
                    each=move || posts.get()
                    key=|post| post.id
                    children=move |post: Post| {
                        view! {
                            <div class="post-card">
                                <h3>{post.title}</h3>
                                <p>{post.content}</p>
                                <small class="text-muted">"by " {post.author}</small>
                            </div>
                        }
                    }
                />
            </div>
            
            <Show when=move || error.get().is_some() fallback=|| view! { <></> }>
                <div class="alert alert-danger">
                    {move || error.get().unwrap_or_default()}
                    <button class="btn btn-sm" on:click=move |_| load_more()>
                        "Retry"
                    </button>
                </div>
            </Show>
            
            <Show when=move || is_loading.get() fallback=|| view! { <></> }>
                <div class="loading-spinner">
                    <div class="spinner-border"></div>
                    <p>"Loading more posts..."</p>
                </div>
            </Show>
            
            <Show when=move || !has_more.get() && !is_loading.get() fallback=|| view! { <></> }>
                <div class="text-center text-muted">
                    "No more posts to load"
                </div>
            </Show>
            
            <div node_ref=sentinel_ref class="sentinel"></div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["async", "infinite-scroll", "leptos", "pagination", "scroll"],
    },
    {
        "problem": """
A dark mode toggle with local storage persistence using Leptos.
""",
        "solution": r"""
use leptos::*;
use wasm_bindgen::JsCast;
use web_sys::window;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Theme {
    Light,
    Dark,
}

impl Theme {
    fn as_str(&self) -> &str {
        match self {
            Theme::Light => "light",
            Theme::Dark => "dark",
        }
    }
    
    fn from_str(s: &str) -> Self {
        match s {
            "dark" => Theme::Dark,
            _ => Theme::Light,
        }
    }
    
    fn toggle(&self) -> Self {
        match self {
            Theme::Light => Theme::Dark,
            Theme::Dark => Theme::Light,
        }
    }
}

fn get_stored_theme() -> Theme {
    window()
        .and_then(|w| w.local_storage().ok().flatten())
        .and_then(|storage| storage.get_item("theme").ok().flatten())
        .map(|theme_str| Theme::from_str(&theme_str))
        .unwrap_or(Theme::Light)
}

fn store_theme(theme: Theme) {
    if let Some(storage) = window()
        .and_then(|w| w.local_storage().ok().flatten())
    {
        let _ = storage.set_item("theme", theme.as_str());
    }
}

fn apply_theme_to_document(theme: Theme) {
    if let Some(document) = window().and_then(|w| w.document()) {
        if let Some(body) = document.body() {
            let _ = body.set_attribute("data-theme", theme.as_str());
        }
    }
}

pub fn use_theme() -> (ReadSignal<Theme>, impl Fn() + Clone) {
    let (theme, set_theme) = create_signal(get_stored_theme());
    
    // Apply theme on mount
    create_effect(move |_| {
        apply_theme_to_document(theme.get());
    });
    
    let toggle_theme = move || {
        set_theme.update(|current| {
            let new_theme = current.toggle();
            store_theme(new_theme);
            *current = new_theme;
        });
    };
    
    (theme, toggle_theme)
}

#[component]
pub fn ThemeToggle() -> impl IntoView {
    let (theme, toggle_theme) = use_theme();
    
    let icon = move || match theme.get() {
        Theme::Light => "🌙",
        Theme::Dark => "☀️",
    };
    
    let label = move || match theme.get() {
        Theme::Light => "Dark Mode",
        Theme::Dark => "Light Mode",
    };

    view! {
        <button
            class="theme-toggle-btn"
            on:click=move |_| toggle_theme()
            aria-label=move || label()
        >
            <span class="theme-icon">{icon}</span>
            <span class="theme-label">{label}</span>
        </button>
    }
}

#[component]
pub fn AppWithTheme() -> impl IntoView {
    let (theme, _) = use_theme();
    
    view! {
        <div class="app-container">
            <header class="app-header">
                <h1>"My Application"</h1>
                <ThemeToggle />
            </header>
            
            <main class="app-content">
                <p>
                    "Current theme: "
                    <strong>{move || theme.get().as_str()}</strong>
                </p>
            </main>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["hooks", "leptos", "local-storage", "state", "theme", "toggle"],
    },
    {
        "problem": """
A file upload component with progress tracking and validation.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use wasm_bindgen::JsCast;
use web_sys::{Event, File, FileList, FormData, XmlHttpRequest};

#[derive(Clone, Debug, PartialEq)]
pub enum UploadStatus {
    Idle,
    Uploading(f64),
    Success(String),
    Error(String),
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct UploadResponse {
    pub url: String,
    pub filename: String,
    pub size: u64,
}

const MAX_FILE_SIZE: u64 = 10 * 1024 * 1024; // 10MB
const ALLOWED_TYPES: &[&str] = &["image/jpeg", "image/png", "image/gif", "application/pdf"];

fn validate_file(file: &File) -> Result<(), String> {
    let file_type = file.type_();
    if !ALLOWED_TYPES.contains(&file_type.as_str()) {
        return Err(format!("File type not allowed: {file_type}"));
    }
    
    let file_size = file.size() as u64;
    if file_size > MAX_FILE_SIZE {
        return Err(format!("File too large: {} bytes (max: {} bytes)", file_size, MAX_FILE_SIZE));
    }
    
    Ok(())
}

#[component]
pub fn FileUpload(
    #[prop(into)] upload_url: String,
    #[prop(optional)] on_success: Option<Box<dyn Fn(UploadResponse)>>,
) -> impl IntoView {
    let (selected_file, set_selected_file) = create_signal(None::<File>);
    let (upload_status, set_upload_status) = create_signal(UploadStatus::Idle);
    let (validation_error, set_validation_error) = create_signal(None::<String>);
    
    let file_input_ref = create_node_ref::<html::Input>();
    
    let on_file_change = move |ev: Event| {
        set_validation_error.set(None);
        
        let target = ev.target().and_then(|t| t.dyn_into::<web_sys::HtmlInputElement>().ok());
        
        if let Some(input) = target {
            if let Some(files) = input.files() {
                if files.length() > 0 {
                    if let Some(file) = files.get(0) {
                        match validate_file(&file) {
                            Ok(()) => {
                                set_selected_file.set(Some(file));
                                set_upload_status.set(UploadStatus::Idle);
                            }
                            Err(e) => {
                                set_validation_error.set(Some(e));
                                set_selected_file.set(None);
                            }
                        }
                    }
                }
            }
        }
    };
    
    let upload_file = move || {
        if let Some(file) = selected_file.get() {
            set_upload_status.set(UploadStatus::Uploading(0.0));
            
            let xhr = XmlHttpRequest::new().expect("Failed to create XHR");
            let form_data = FormData::new().expect("Failed to create FormData");
            
            form_data.append_with_blob("file", &file).expect("Failed to append file");
            
            let xhr_clone = xhr.clone();
            let upload_progress = Closure::wrap(Box::new(move |ev: web_sys::ProgressEvent| {
                if ev.length_computable() {
                    let progress = (ev.loaded() as f64 / ev.total() as f64) * 100.0;
                    set_upload_status.set(UploadStatus::Uploading(progress));
                }
            }) as Box<dyn FnMut(_)>);
            
            if let Some(upload) = xhr.upload() {
                upload.set_onprogress(Some(upload_progress.as_ref().unchecked_ref()));
            }
            
            let on_load = Closure::wrap(Box::new(move |_: Event| {
                if xhr_clone.status().unwrap_or(0) == 200 {
                    if let Ok(response_text) = xhr_clone.response_text() {
                        if let Some(text) = response_text {
                            match serde_json::from_str::<UploadResponse>(&text) {
                                Ok(response) => {
                                    set_upload_status.set(UploadStatus::Success(response.url.clone()));
                                    if let Some(ref callback) = on_success {
                                        callback(response);
                                    }
                                }
                                Err(e) => {
                                    set_upload_status.set(UploadStatus::Error(format!("Parse error: {e}")));
                                }
                            }
                        }
                    }
                } else {
                    set_upload_status.set(UploadStatus::Error(format!("Upload failed with status: {}", xhr_clone.status().unwrap_or(0))));
                }
            }) as Box<dyn FnMut(_)>);
            
            xhr.set_onload(Some(on_load.as_ref().unchecked_ref()));
            
            let on_error = Closure::wrap(Box::new(move |_: Event| {
                set_upload_status.set(UploadStatus::Error("Network error".to_string()));
            }) as Box<dyn FnMut(_)>);
            
            xhr.set_onerror(Some(on_error.as_ref().unchecked_ref()));
            
            let _ = xhr.open("POST", &upload_url);
            let _ = xhr.send_with_opt_form_data(Some(&form_data));
            
            upload_progress.forget();
            on_load.forget();
            on_error.forget();
        }
    };

    view! {
        <div class="file-upload-container">
            <div class="upload-area">
                <input
                    node_ref=file_input_ref
                    type="file"
                    class="file-input"
                    on:change=on_file_change
                    accept=ALLOWED_TYPES.join(",")
                />
                
                <Show
                    when=move || selected_file.get().is_none()
                    fallback=move || {
                        let file = selected_file.get().unwrap();
                        view! {
                            <div class="file-info">
                                <p><strong>"Selected: "</strong> {file.name()}</p>
                                <p><strong>"Size: "</strong> {file.size() / 1024} " KB"</p>
                            </div>
                        }
                    }
                >
                    <p>"Click to select a file or drag and drop"</p>
                    <p class="text-muted">"Max size: 10MB. Allowed: JPEG, PNG, GIF, PDF"</p>
                </Show>
            </div>
            
            <Show when=move || validation_error.get().is_some() fallback=|| view! { <></> }>
                <div class="alert alert-danger">
                    {move || validation_error.get().unwrap_or_default()}
                </div>
            </Show>
            
            {move || match upload_status.get() {
                UploadStatus::Idle => view! {
                    <button
                        class="btn btn-primary"
                        disabled=move || selected_file.get().is_none()
                        on:click=move |_| upload_file()
                    >
                        "Upload"
                    </button>
                },
                UploadStatus::Uploading(progress) => view! {
                    <div class="progress">
                        <div
                            class="progress-bar"
                            style:width=format!("{}%", progress)
                            role="progressbar"
                        >
                            {format!("{:.0}%", progress)}
                        </div>
                    </div>
                },
                UploadStatus::Success(url) => view! {
                    <div class="alert alert-success">
                        "Upload successful! "
                        <a href={url} target="_blank">"View file"</a>
                    </div>
                },
                UploadStatus::Error(error) => view! {
                    <div class="alert alert-danger">
                        {error}
                        <button class="btn btn-sm" on:click=move |_| upload_file()>
                            "Retry"
                        </button>
                    </div>
                },
            }}
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["file", "leptos", "progress", "upload", "validation"],
    },
    {
        "problem": """
A debounced search input component for efficient API calls.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct SearchResult {
    pub id: u32,
    pub title: String,
    pub description: String,
}

async fn search_api(query: String) -> Result<Vec<SearchResult>, String> {
    if query.trim().is_empty() {
        return Ok(Vec::new());
    }
    
    // Simulate API delay
    gloo_timers::future::TimeoutFuture::new(300).await;
    
    // Mock results
    let results = (0..5)
        .map(|i| SearchResult {
            id: i,
            title: format!("Result {} for '{}'", i + 1, query),
            description: format!("Description for result {}", i + 1),
        })
        .collect();
    
    Ok(results)
}

pub fn use_debounced_search(
    initial_query: String,
    debounce_ms: u32,
) -> (
    ReadSignal<String>,
    WriteSignal<String>,
    Signal<Option<Result<Vec<SearchResult>, String>>>,
    ReadSignal<bool>,
) {
    let (query, set_query) = create_signal(initial_query.clone());
    let (debounced_query, set_debounced_query) = create_signal(initial_query);
    
    // Debounce logic
    create_effect(move |_| {
        let current_query = query.get();
        
        let timeout = gloo_timers::callback::Timeout::new(debounce_ms, move || {
            set_debounced_query.set(current_query);
        });
        
        timeout.forget();
    });
    
    // Create resource that triggers on debounced query changes
    let results = create_resource(
        move || debounced_query.get(),
        |query| async move {
            if query.trim().is_empty() {
                return Ok(Vec::new());
            }
            search_api(query).await
        },
    );
    
    let is_searching = Signal::derive(move || results.loading().get());
    
    (query, set_query, results.into(), is_searching)
}

#[component]
pub fn DebouncedSearch() -> impl IntoView {
    let (query, set_query, results, is_searching) = use_debounced_search(
        String::new(),
        500, // 500ms debounce
    );
    
    let on_input = move |ev| {
        let value = event_target_value(&ev);
        set_query.set(value);
    };
    
    let clear_search = move |_| {
        set_query.set(String::new());
    };

    view! {
        <div class="search-container">
            <div class="search-input-wrapper">
                <input
                    type="text"
                    class="search-input"
                    placeholder="Search..."
                    prop:value=move || query.get()
                    on:input=on_input
                />
                
                <Show when=move || !query.get().is_empty() fallback=|| view! { <></> }>
                    <button class="clear-btn" on:click=clear_search>
                        "×"
                    </button>
                </Show>
                
                <Show when=move || is_searching.get() fallback=|| view! { <></> }>
                    <div class="search-spinner">
                        <div class="spinner-border spinner-border-sm"></div>
                    </div>
                </Show>
            </div>
            
            <div class="search-results">
                <Suspense fallback=move || view! { <></> }>
                    {move || {
                        results.get().map(|result_option| {
                            match result_option {
                                Some(Ok(items)) if !items.is_empty() => {
                                    view! {
                                        <ul class="results-list">
                                            <For
                                                each=move || items.clone()
                                                key=|item| item.id
                                                children=move |item: SearchResult| {
                                                    view! {
                                                        <li class="result-item">
                                                            <h4>{item.title}</h4>
                                                            <p>{item.description}</p>
                                                        </li>
                                                    }
                                                }
                                            />
                                        </ul>
                                    }
                                }
                                Some(Ok(_)) => {
                                    view! {
                                        <div class="no-results">
                                            "No results found"
                                        </div>
                                    }
                                }
                                Some(Err(e)) => {
                                    view! {
                                        <div class="alert alert-danger">
                                            "Error: " {e}
                                        </div>
                                    }
                                }
                                None => view! { <></> }
                            }
                        })
                    }}
                </Suspense>
            </div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["api", "async", "debounce", "hooks", "leptos", "search"],
    },
    {
        "problem": """
A reusable modal dialog component with focus management and accessibility.
""",
        "solution": r"""
use leptos::*;
use wasm_bindgen::JsCast;
use web_sys::{window, Event, KeyboardEvent};

#[derive(Clone, Copy, PartialEq)]
pub enum ModalSize {
    Small,
    Medium,
    Large,
}

impl ModalSize {
    fn class(&self) -> &str {
        match self {
            ModalSize::Small => "modal-sm",
            ModalSize::Medium => "modal-md",
            ModalSize::Large => "modal-lg",
        }
    }
}

#[component]
pub fn Modal(
    #[prop(into)] show: Signal<bool>,
    #[prop(into)] on_close: Box<dyn Fn()>,
    #[prop(optional)] title: Option<String>,
    #[prop(optional)] size: ModalSize,
    #[prop(optional)] close_on_backdrop: bool,
    children: Children,
) -> impl IntoView {
    let size = size;
    let close_on_backdrop = close_on_backdrop;
    
    // Handle ESC key
    create_effect(move |_| {
        if show.get() {
            let on_keydown = Closure::wrap(Box::new(move |ev: KeyboardEvent| {
                if ev.key() == "Escape" {
                    on_close();
                }
            }) as Box<dyn FnMut(_)>);
            
            if let Some(window) = window() {
                let _ = window.add_event_listener_with_callback(
                    "keydown",
                    on_keydown.as_ref().unchecked_ref(),
                );
            }
            
            on_keydown.forget();
        }
    });
    
    // Prevent body scroll when modal is open
    create_effect(move |_| {
        if let Some(window) = window() {
            if let Some(document) = window.document() {
                if let Some(body) = document.body() {
                    if show.get() {
                        let _ = body.style().set_property("overflow", "hidden");
                    } else {
                        let _ = body.style().remove_property("overflow");
                    }
                }
            }
        }
    });
    
    let handle_backdrop_click = move |ev: Event| {
        if close_on_backdrop {
            let target = ev.target();
            let current_target = ev.current_target();
            
            if target == current_target {
                on_close();
            }
        }
    };

    view! {
        <Show when=move || show.get() fallback=|| view! { <></> }>
            <div
                class="modal-backdrop"
                on:click=handle_backdrop_click
                role="dialog"
                aria-modal="true"
                aria-labelledby="modal-title"
            >
                <div class={format!("modal-content {}", size.class())}>
                    <Show when=move || title.is_some() fallback=|| view! { <></> }>
                        <div class="modal-header">
                            <h2 id="modal-title" class="modal-title">
                                {title.clone().unwrap_or_default()}
                            </h2>
                            <button
                                class="modal-close-btn"
                                on:click=move |_| on_close()
                                aria-label="Close"
                            >
                                "×"
                            </button>
                        </div>
                    </Show>
                    
                    <div class="modal-body">
                        {children()}
                    </div>
                </div>
            </div>
        </Show>
    }
}

#[component]
pub fn ModalExample() -> impl IntoView {
    let (show_modal, set_show_modal) = create_signal(false);
    
    let open_modal = move |_| set_show_modal.set(true);
    let close_modal = move || set_show_modal.set(false);

    view! {
        <div>
            <button class="btn btn-primary" on:click=open_modal>
                "Open Modal"
            </button>
            
            <Modal
                show=show_modal.into()
                on_close=Box::new(close_modal)
                title=Some("Example Modal".to_string())
                size=ModalSize::Medium
                close_on_backdrop=true
            >
                <p>"This is the modal content."</p>
                <p>"Press ESC or click outside to close."</p>
                
                <div class="modal-footer">
                    <button class="btn btn-secondary" on:click=move |_| close_modal()>
                        "Cancel"
                    </button>
                    <button class="btn btn-primary" on:click=move |_| {
                        log::info!("Confirmed!");
                        close_modal();
                    }>
                        "Confirm"
                    </button>
                </div>
            </Modal>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["accessibility", "component", "dialog", "leptos", "modal"],
    },
    {
        "problem": """
A toast notification system with auto-dismiss and animation.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use std::time::Duration;
use uuid::Uuid;

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum ToastType {
    Success,
    Error,
    Warning,
    Info,
}

impl ToastType {
    fn class(&self) -> &str {
        match self {
            ToastType::Success => "toast-success",
            ToastType::Error => "toast-error",
            ToastType::Warning => "toast-warning",
            ToastType::Info => "toast-info",
        }
    }
    
    fn icon(&self) -> &str {
        match self {
            ToastType::Success => "✓",
            ToastType::Error => "✕",
            ToastType::Warning => "⚠",
            ToastType::Info => "ℹ",
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub struct Toast {
    pub id: String,
    pub message: String,
    pub toast_type: ToastType,
    pub duration: Option<u32>,
}

impl Toast {
    pub fn new(message: impl Into<String>, toast_type: ToastType) -> Self {
        Self {
            id: Uuid::new_v4().to_string(),
            message: message.into(),
            toast_type,
            duration: Some(5000),
        }
    }
    
    pub fn success(message: impl Into<String>) -> Self {
        Self::new(message, ToastType::Success)
    }
    
    pub fn error(message: impl Into<String>) -> Self {
        Self::new(message, ToastType::Error)
    }
    
    pub fn warning(message: impl Into<String>) -> Self {
        Self::new(message, ToastType::Warning)
    }
    
    pub fn info(message: impl Into<String>) -> Self {
        Self::new(message, ToastType::Info)
    }
}

#[derive(Clone)]
pub struct ToastContext {
    toasts: RwSignal<Vec<Toast>>,
}

impl ToastContext {
    pub fn new() -> Self {
        Self {
            toasts: create_rw_signal(Vec::new()),
        }
    }
    
    pub fn show(&self, toast: Toast) {
        let toast_id = toast.id.clone();
        let duration = toast.duration;
        
        self.toasts.update(|toasts| {
            toasts.push(toast);
        });
        
        if let Some(duration_ms) = duration {
            let toasts = self.toasts;
            let timeout = gloo_timers::callback::Timeout::new(duration_ms, move || {
                toasts.update(|toasts| {
                    toasts.retain(|t| t.id != toast_id);
                });
            });
            timeout.forget();
        }
    }
    
    pub fn dismiss(&self, toast_id: String) {
        self.toasts.update(|toasts| {
            toasts.retain(|t| t.id != toast_id);
        });
    }
    
    pub fn clear(&self) {
        self.toasts.update(|toasts| toasts.clear());
    }
}

impl Default for ToastContext {
    fn default() -> Self {
        Self::new()
    }
}

#[component]
pub fn ToastProvider(children: Children) -> impl IntoView {
    let toast_context = ToastContext::new();
    provide_context(toast_context.clone());

    view! {
        <div>
            {children()}
            <ToastContainer />
        </div>
    }
}

#[component]
fn ToastContainer() -> impl IntoView {
    let toast_context = use_context::<ToastContext>()
        .expect("ToastContext must be provided");
    
    let toasts = toast_context.toasts;

    view! {
        <div class="toast-container">
            <For
                each=move || toasts.get()
                key=|toast| toast.id.clone()
                children=move |toast: Toast| {
                    let toast_id = toast.id.clone();
                    let context = toast_context.clone();
                    
                    view! {
                        <div class={format!("toast {}", toast.toast_type.class())}>
                            <div class="toast-icon">
                                {toast.toast_type.icon()}
                            </div>
                            <div class="toast-message">
                                {toast.message}
                            </div>
                            <button
                                class="toast-close"
                                on:click=move |_| context.dismiss(toast_id.clone())
                            >
                                "×"
                            </button>
                        </div>
                    }
                }
            />
        </div>
    }
}

#[component]
pub fn ToastExample() -> impl IntoView {
    let toast_context = use_context::<ToastContext>()
        .expect("ToastContext must be provided");
    
    let show_success = move |_| {
        toast_context.show(Toast::success("Operation completed successfully!"));
    };
    
    let show_error = move |_| {
        toast_context.show(Toast::error("An error occurred!"));
    };
    
    let show_warning = move |_| {
        toast_context.show(Toast::warning("Warning: Please check your input"));
    };
    
    let show_info = move |_| {
        toast_context.show(Toast::info("Did you know? You can dismiss toasts manually"));
    };

    view! {
        <div class="toast-example">
            <h2>"Toast Notifications"</h2>
            <div class="button-group">
                <button class="btn btn-success" on:click=show_success>
                    "Show Success"
                </button>
                <button class="btn btn-danger" on:click=show_error>
                    "Show Error"
                </button>
                <button class="btn btn-warning" on:click=show_warning>
                    "Show Warning"
                </button>
                <button class="btn btn-info" on:click=show_info>
                    "Show Info"
                </button>
            </div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["context", "leptos", "notifications", "toast"],
    },
    {
        "problem": """
A sortable and filterable data table component.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Person {
    pub id: u32,
    pub name: String,
    pub email: String,
    pub age: u32,
    pub city: String,
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum SortDirection {
    Ascending,
    Descending,
}

impl SortDirection {
    fn toggle(&self) -> Self {
        match self {
            SortDirection::Ascending => SortDirection::Descending,
            SortDirection::Descending => SortDirection::Ascending,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum SortColumn {
    Name,
    Email,
    Age,
    City,
}

fn sort_people(people: &mut [Person], column: SortColumn, direction: SortDirection) {
    people.sort_by(|a, b| {
        let comparison = match column {
            SortColumn::Name => a.name.cmp(&b.name),
            SortColumn::Email => a.email.cmp(&b.email),
            SortColumn::Age => a.age.cmp(&b.age),
            SortColumn::City => a.city.cmp(&b.city),
        };
        
        match direction {
            SortDirection::Ascending => comparison,
            SortDirection::Descending => comparison.reverse(),
        }
    });
}

fn filter_people(people: &[Person], filter: &str) -> Vec<Person> {
    let filter_lower = filter.to_lowercase();
    people
        .iter()
        .filter(|person| {
            person.name.to_lowercase().contains(&filter_lower)
                || person.email.to_lowercase().contains(&filter_lower)
                || person.city.to_lowercase().contains(&filter_lower)
        })
        .cloned()
        .collect()
}

#[component]
pub fn DataTable(
    #[prop(into)] data: Signal<Vec<Person>>,
) -> impl IntoView {
    let (sort_column, set_sort_column) = create_signal(SortColumn::Name);
    let (sort_direction, set_sort_direction) = create_signal(SortDirection::Ascending);
    let (filter_text, set_filter_text) = create_signal(String::new());
    
    let sorted_and_filtered_data = create_memo(move |_| {
        let mut people = filter_people(&data.get(), &filter_text.get());
        sort_people(&mut people, sort_column.get(), sort_direction.get());
        people
    });
    
    let handle_sort = move |column: SortColumn| {
        if sort_column.get() == column {
            set_sort_direction.update(|d| *d = d.toggle());
        } else {
            set_sort_column.set(column);
            set_sort_direction.set(SortDirection::Ascending);
        }
    };
    
    let sort_indicator = move |column: SortColumn| {
        if sort_column.get() == column {
            match sort_direction.get() {
                SortDirection::Ascending => " ↑",
                SortDirection::Descending => " ↓",
            }
        } else {
            ""
        }
    };

    view! {
        <div class="data-table-container">
            <div class="table-controls">
                <input
                    type="text"
                    class="table-filter"
                    placeholder="Filter by name, email, or city..."
                    prop:value=move || filter_text.get()
                    on:input=move |ev| set_filter_text.set(event_target_value(&ev))
                />
                <div class="table-info">
                    "Showing " {move || sorted_and_filtered_data.get().len()} " of " {move || data.get().len()} " records"
                </div>
            </div>
            
            <table class="table">
                <thead>
                    <tr>
                        <th
                            class="sortable"
                            on:click=move |_| handle_sort(SortColumn::Name)
                        >
                            "Name" {move || sort_indicator(SortColumn::Name)}
                        </th>
                        <th
                            class="sortable"
                            on:click=move |_| handle_sort(SortColumn::Email)
                        >
                            "Email" {move || sort_indicator(SortColumn::Email)}
                        </th>
                        <th
                            class="sortable"
                            on:click=move |_| handle_sort(SortColumn::Age)
                        >
                            "Age" {move || sort_indicator(SortColumn::Age)}
                        </th>
                        <th
                            class="sortable"
                            on:click=move |_| handle_sort(SortColumn::City)
                        >
                            "City" {move || sort_indicator(SortColumn::City)}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <For
                        each=move || sorted_and_filtered_data.get()
                        key=|person| person.id
                        children=move |person: Person| {
                            view! {
                                <tr>
                                    <td>{person.name}</td>
                                    <td>{person.email}</td>
                                    <td>{person.age}</td>
                                    <td>{person.city}</td>
                                </tr>
                            }
                        }
                    />
                </tbody>
            </table>
            
            <Show
                when=move || sorted_and_filtered_data.get().is_empty()
                fallback=|| view! { <></> }
            >
                <div class="table-empty">
                    "No records found matching your filter"
                </div>
            </Show>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["data", "filter", "leptos", "sort", "table"],
    },
    {
        "problem": """
A multi-step wizard form with step validation and navigation.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct WizardData {
    pub personal_info: PersonalInfo,
    pub contact_info: ContactInfo,
    pub preferences: Preferences,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct PersonalInfo {
    pub first_name: String,
    pub last_name: String,
    pub date_of_birth: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct ContactInfo {
    pub email: String,
    pub phone: String,
    pub address: String,
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct Preferences {
    pub newsletter: bool,
    pub notifications: bool,
    pub theme: String,
}

#[derive(Clone, Copy, Debug, PartialEq)]
enum Step {
    Personal,
    Contact,
    Preferences,
    Review,
}

impl Step {
    fn title(&self) -> &str {
        match self {
            Step::Personal => "Personal Information",
            Step::Contact => "Contact Information",
            Step::Preferences => "Preferences",
            Step::Review => "Review & Submit",
        }
    }
    
    fn number(&self) -> usize {
        match self {
            Step::Personal => 1,
            Step::Contact => 2,
            Step::Preferences => 3,
            Step::Review => 4,
        }
    }
    
    fn next(&self) -> Option<Step> {
        match self {
            Step::Personal => Some(Step::Contact),
            Step::Contact => Some(Step::Preferences),
            Step::Preferences => Some(Step::Review),
            Step::Review => None,
        }
    }
    
    fn previous(&self) -> Option<Step> {
        match self {
            Step::Personal => None,
            Step::Contact => Some(Step::Personal),
            Step::Preferences => Some(Step::Contact),
            Step::Review => Some(Step::Preferences),
        }
    }
}

fn validate_personal_info(data: &PersonalInfo) -> Result<(), String> {
    if data.first_name.trim().is_empty() {
        return Err("First name is required".to_string());
    }
    if data.last_name.trim().is_empty() {
        return Err("Last name is required".to_string());
    }
    if data.date_of_birth.trim().is_empty() {
        return Err("Date of birth is required".to_string());
    }
    Ok(())
}

fn validate_contact_info(data: &ContactInfo) -> Result<(), String> {
    if data.email.trim().is_empty() || !data.email.contains('@') {
        return Err("Valid email is required".to_string());
    }
    if data.phone.trim().is_empty() {
        return Err("Phone is required".to_string());
    }
    Ok(())
}

#[component]
pub fn WizardForm() -> impl IntoView {
    let (current_step, set_current_step) = create_signal(Step::Personal);
    let (wizard_data, set_wizard_data) = create_signal(WizardData::default());
    let (validation_error, set_validation_error) = create_signal(None::<String>);
    let (is_submitting, set_is_submitting) = create_signal(false);
    
    let can_proceed = move || -> bool {
        set_validation_error.set(None);
        let data = wizard_data.get();
        
        match current_step.get() {
            Step::Personal => validate_personal_info(&data.personal_info).is_ok(),
            Step::Contact => validate_contact_info(&data.contact_info).is_ok(),
            Step::Preferences => true,
            Step::Review => true,
        }
    };
    
    let go_next = move || {
        if !can_proceed() {
            let data = wizard_data.get();
            let error = match current_step.get() {
                Step::Personal => validate_personal_info(&data.personal_info).err(),
                Step::Contact => validate_contact_info(&data.contact_info).err(),
                _ => None,
            };
            set_validation_error.set(error);
            return;
        }
        
        if let Some(next_step) = current_step.get().next() {
            set_current_step.set(next_step);
        }
    };
    
    let go_previous = move || {
        if let Some(previous_step) = current_step.get().previous() {
            set_current_step.set(previous_step);
        }
    };
    
    let submit_form = move || {
        set_is_submitting.set(true);
        let data = wizard_data.get();
        
        spawn_local(async move {
            gloo_timers::future::TimeoutFuture::new(1500).await;
            log::info!("Form submitted: {:?}", data);
            set_is_submitting.set(false);
        });
    };

    view! {
        <div class="wizard-container">
            <div class="wizard-steps">
                <div class={move || if current_step.get().number() >= 1 { "step active" } else { "step" }}>
                    "1. Personal"
                </div>
                <div class={move || if current_step.get().number() >= 2 { "step active" } else { "step" }}>
                    "2. Contact"
                </div>
                <div class={move || if current_step.get().number() >= 3 { "step active" } else { "step" }}>
                    "3. Preferences"
                </div>
                <div class={move || if current_step.get().number() >= 4 { "step active" } else { "step" }}>
                    "4. Review"
                </div>
            </div>
            
            <div class="wizard-content">
                <h2>{move || current_step.get().title()}</h2>
                
                <Show when=move || validation_error.get().is_some() fallback=|| view! { <></> }>
                    <div class="alert alert-danger">
                        {move || validation_error.get().unwrap_or_default()}
                    </div>
                </Show>
                
                {move || match current_step.get() {
                    Step::Personal => view! {
                        <div class="form-section">
                            <div class="mb-3">
                                <label>"First Name"</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    prop:value=move || wizard_data.get().personal_info.first_name
                                    on:input=move |ev| {
                                        set_wizard_data.update(|data| {
                                            data.personal_info.first_name = event_target_value(&ev);
                                        });
                                    }
                                />
                            </div>
                            <div class="mb-3">
                                <label>"Last Name"</label>
                                <input
                                    type="text"
                                    class="form-control"
                                    prop:value=move || wizard_data.get().personal_info.last_name
                                    on:input=move |ev| {
                                        set_wizard_data.update(|data| {
                                            data.personal_info.last_name = event_target_value(&ev);
                                        });
                                    }
                                />
                            </div>
                            <div class="mb-3">
                                <label>"Date of Birth"</label>
                                <input
                                    type="date"
                                    class="form-control"
                                    prop:value=move || wizard_data.get().personal_info.date_of_birth
                                    on:input=move |ev| {
                                        set_wizard_data.update(|data| {
                                            data.personal_info.date_of_birth = event_target_value(&ev);
                                        });
                                    }
                                />
                            </div>
                        </div>
                    },
                    Step::Contact => view! {
                        <div class="form-section">
                            <div class="mb-3">
                                <label>"Email"</label>
                                <input
                                    type="email"
                                    class="form-control"
                                    prop:value=move || wizard_data.get().contact_info.email
                                    on:input=move |ev| {
                                        set_wizard_data.update(|data| {
                                            data.contact_info.email = event_target_value(&ev);
                                        });
                                    }
                                />
                            </div>
                            <div class="mb-3">
                                <label>"Phone"</label>
                                <input
                                    type="tel"
                                    class="form-control"
                                    prop:value=move || wizard_data.get().contact_info.phone
                                    on:input=move |ev| {
                                        set_wizard_data.update(|data| {
                                            data.contact_info.phone = event_target_value(&ev);
                                        });
                                    }
                                />
                            </div>
                        </div>
                    },
                    Step::Preferences => view! {
                        <div class="form-section">
                            <div class="mb-3">
                                <label>
                                    <input
                                        type="checkbox"
                                        prop:checked=move || wizard_data.get().preferences.newsletter
                                        on:change=move |ev| {
                                            set_wizard_data.update(|data| {
                                                data.preferences.newsletter = event_target_checked(&ev);
                                            });
                                        }
                                    />
                                    " Subscribe to newsletter"
                                </label>
                            </div>
                            <div class="mb-3">
                                <label>
                                    <input
                                        type="checkbox"
                                        prop:checked=move || wizard_data.get().preferences.notifications
                                        on:change=move |ev| {
                                            set_wizard_data.update(|data| {
                                                data.preferences.notifications = event_target_checked(&ev);
                                            });
                                        }
                                    />
                                    " Enable notifications"
                                </label>
                            </div>
                        </div>
                    },
                    Step::Review => view! {
                        <div class="review-section">
                            <h3>"Personal Information"</h3>
                            <p><strong>"Name: "</strong> {move || format!("{} {}", wizard_data.get().personal_info.first_name, wizard_data.get().personal_info.last_name)}</p>
                            <p><strong>"Date of Birth: "</strong> {move || wizard_data.get().personal_info.date_of_birth.clone()}</p>
                            
                            <h3>"Contact Information"</h3>
                            <p><strong>"Email: "</strong> {move || wizard_data.get().contact_info.email.clone()}</p>
                            <p><strong>"Phone: "</strong> {move || wizard_data.get().contact_info.phone.clone()}</p>
                        </div>
                    },
                }}
            </div>
            
            <div class="wizard-actions">
                <button
                    class="btn btn-secondary"
                    disabled=move || current_step.get().previous().is_none()
                    on:click=move |_| go_previous()
                >
                    "Previous"
                </button>
                
                <Show
                    when=move || current_step.get().next().is_some()
                    fallback=move || view! {
                        <button
                            class="btn btn-primary"
                            disabled=move || is_submitting.get()
                            on:click=move |_| submit_form()
                        >
                            {move || if is_submitting.get() { "Submitting..." } else { "Submit" }}
                        </button>
                    }
                >
                    <button class="btn btn-primary" on:click=move |_| go_next()>
                        "Next"
                    </button>
                </Show>
            </div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["form", "leptos", "multi-step", "validation", "wizard"],
    },
    {
        "problem": """
A drag-and-drop kanban board component.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use wasm_bindgen::JsCast;
use web_sys::{DragEvent, HtmlElement};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Task {
    pub id: String,
    pub title: String,
    pub description: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TaskStatus {
    Todo,
    InProgress,
    Done,
}

impl TaskStatus {
    fn title(&self) -> &str {
        match self {
            TaskStatus::Todo => "To Do",
            TaskStatus::InProgress => "In Progress",
            TaskStatus::Done => "Done",
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TaskWithStatus {
    pub task: Task,
    pub status: TaskStatus,
}

#[component]
pub fn KanbanBoard() -> impl IntoView {
    let (tasks, set_tasks) = create_signal(vec![
        TaskWithStatus {
            task: Task {
                id: "1".to_string(),
                title: "Task 1".to_string(),
                description: "Description for task 1".to_string(),
            },
            status: TaskStatus::Todo,
        },
        TaskWithStatus {
            task: Task {
                id: "2".to_string(),
                title: "Task 2".to_string(),
                description: "Description for task 2".to_string(),
            },
            status: TaskStatus::InProgress,
        },
    ]);
    
    let (dragging_task_id, set_dragging_task_id) = create_signal(None::<String>);
    
    let tasks_by_status = move |status: TaskStatus| {
        tasks
            .get()
            .into_iter()
            .filter(|t| t.status == status)
            .collect::<Vec<_>>()
    };
    
    let on_drag_start = move |task_id: String| {
        move |ev: DragEvent| {
            set_dragging_task_id.set(Some(task_id.clone()));
            if let Some(data_transfer) = ev.data_transfer() {
                let _ = data_transfer.set_data("text/plain", &task_id);
                data_transfer.set_effect_allowed("move");
            }
        }
    };
    
    let on_drag_over = move |ev: DragEvent| {
        ev.prevent_default();
        if let Some(data_transfer) = ev.data_transfer() {
            data_transfer.set_drop_effect("move");
        }
    };
    
    let on_drop = move |new_status: TaskStatus| {
        move |ev: DragEvent| {
            ev.prevent_default();
            
            if let Some(task_id) = dragging_task_id.get() {
                set_tasks.update(|tasks| {
                    if let Some(task) = tasks.iter_mut().find(|t| t.task.id == task_id) {
                        task.status = new_status;
                    }
                });
                set_dragging_task_id.set(None);
            }
        }
    };

    view! {
        <div class="kanban-board">
            <For
                each=|| vec![TaskStatus::Todo, TaskStatus::InProgress, TaskStatus::Done]
                key=|status| *status
                children=move |status: TaskStatus| {
                    view! {
                        <div
                            class="kanban-column"
                            on:dragover=on_drag_over
                            on:drop=on_drop(status)
                        >
                            <h3 class="column-title">{status.title()}</h3>
                            <div class="task-list">
                                <For
                                    each=move || tasks_by_status(status)
                                    key=|task_with_status| task_with_status.task.id.clone()
                                    children=move |task_with_status: TaskWithStatus| {
                                        let task_id = task_with_status.task.id.clone();
                                        let is_dragging = move || {
                                            dragging_task_id.get().as_ref() == Some(&task_id)
                                        };
                                        
                                        view! {
                                            <div
                                                class={move || if is_dragging() { "task-card dragging" } else { "task-card" }}
                                                draggable="true"
                                                on:dragstart=on_drag_start(task_id.clone())
                                            >
                                                <h4>{task_with_status.task.title}</h4>
                                                <p>{task_with_status.task.description}</p>
                                            </div>
                                        }
                                    }
                                />
                            </div>
                        </div>
                    }
                }
            />
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["drag-drop", "kanban", "leptos"],
    },
    {
        "problem": """
Global state management using Context API with proper encapsulation.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use std::rc::Rc;

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
    pub role: UserRole,
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum UserRole {
    Admin,
    User,
    Guest,
}

#[derive(Clone)]
pub struct AuthContext {
    user: RwSignal<Option<User>>,
    is_loading: RwSignal<bool>,
}

impl AuthContext {
    pub fn new() -> Self {
        Self {
            user: create_rw_signal(None),
            is_loading: create_rw_signal(false),
        }
    }
    
    pub fn user(&self) -> ReadSignal<Option<User>> {
        self.user.read_only()
    }
    
    pub fn is_loading(&self) -> ReadSignal<bool> {
        self.is_loading.read_only()
    }
    
    pub fn is_authenticated(&self) -> bool {
        self.user.get().is_some()
    }
    
    pub fn has_role(&self, role: UserRole) -> bool {
        self.user
            .get()
            .map(|u| u.role == role)
            .unwrap_or(false)
    }
    
    pub async fn login(&self, email: String, password: String) -> Result<(), String> {
        self.is_loading.set(true);
        
        // Simulate API call
        gloo_timers::future::TimeoutFuture::new(1000).await;
        
        // Mock authentication
        if email == "admin@example.com" && password == "password" {
            let user = User {
                id: "1".to_string(),
                name: "Admin User".to_string(),
                email,
                role: UserRole::Admin,
            };
            self.user.set(Some(user));
            self.is_loading.set(false);
            Ok(())
        } else {
            self.is_loading.set(false);
            Err("Invalid credentials".to_string())
        }
    }
    
    pub fn logout(&self) {
        self.user.set(None);
    }
}

impl Default for AuthContext {
    fn default() -> Self {
        Self::new()
    }
}

#[component]
pub fn AuthProvider(children: Children) -> impl IntoView {
    let auth_context = AuthContext::new();
    provide_context(auth_context);

    view! {
        <div>
            {children()}
        </div>
    }
}

pub fn use_auth() -> AuthContext {
    use_context::<AuthContext>()
        .expect("AuthContext must be provided via AuthProvider")
}

#[component]
pub fn LoginForm() -> impl IntoView {
    let auth = use_auth();
    let (email, set_email) = create_signal(String::new());
    let (password, set_password) = create_signal(String::new());
    let (error, set_error) = create_signal(None::<String>);
    
    let on_submit = move |ev: web_sys::SubmitEvent| {
        ev.prevent_default();
        set_error.set(None);
        
        let email_value = email.get();
        let password_value = password.get();
        let auth_clone = auth.clone();
        
        spawn_local(async move {
            match auth_clone.login(email_value, password_value).await {
                Ok(()) => {
                    set_email.set(String::new());
                    set_password.set(String::new());
                }
                Err(e) => set_error.set(Some(e)),
            }
        });
    };

    view! {
        <Show
            when=move || !auth.is_authenticated()
            fallback=move || view! {
                <div>
                    <p>"Welcome, " {move || auth.user().get().map(|u| u.name).unwrap_or_default()}</p>
                    <button class="btn" on:click=move |_| auth.logout()>
                        "Logout"
                    </button>
                </div>
            }
        >
            <form on:submit=on_submit class="login-form">
                <h2>"Login"</h2>
                
                <Show when=move || error.get().is_some() fallback=|| view! { <></> }>
                    <div class="alert alert-danger">
                        {move || error.get().unwrap_or_default()}
                    </div>
                </Show>
                
                <div class="mb-3">
                    <label>"Email"</label>
                    <input
                        type="email"
                        class="form-control"
                        prop:value=move || email.get()
                        on:input=move |ev| set_email.set(event_target_value(&ev))
                    />
                </div>
                
                <div class="mb-3">
                    <label>"Password"</label>
                    <input
                        type="password"
                        class="form-control"
                        prop:value=move || password.get()
                        on:input=move |ev| set_password.set(event_target_value(&ev))
                    />
                </div>
                
                <button
                    type="submit"
                    class="btn btn-primary"
                    disabled=move || auth.is_loading().get()
                >
                    {move || if auth.is_loading().get() { "Loading..." } else { "Login" }}
                </button>
            </form>
        </Show>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["auth", "context", "global-state", "leptos", "state-management"],
    },
    {
        "problem": """
Protected routes with authentication guard using Leptos Router.
""",
        "solution": r"""
use leptos::*;
use leptos_router::*;

#[derive(Clone)]
pub struct AuthState {
    is_authenticated: RwSignal<bool>,
}

impl AuthState {
    pub fn new() -> Self {
        Self {
            is_authenticated: create_rw_signal(false),
        }
    }
    
    pub fn is_authenticated(&self) -> bool {
        self.is_authenticated.get()
    }
    
    pub fn login(&self) {
        self.is_authenticated.set(true);
    }
    
    pub fn logout(&self) {
        self.is_authenticated.set(false);
    }
}

impl Default for AuthState {
    fn default() -> Self {
        Self::new()
    }
}

#[component]
pub fn ProtectedRoute<F, IV>(
    path: &'static str,
    view: F,
) -> impl IntoView
where
    F: Fn() -> IV + 'static,
    IV: IntoView,
{
    let auth = use_context::<AuthState>()
        .expect("AuthState must be provided");
    
    view! {
        <Route
            path=path
            view=move || {
                if auth.is_authenticated() {
                    view().into_view()
                } else {
                    view! {
                        <Redirect path="/login" />
                    }.into_view()
                }
            }
        />
    }
}

#[component]
pub fn HomePage() -> impl IntoView {
    view! {
        <div class="page">
            <h1>"Home Page"</h1>
            <p>"This is a public page accessible to everyone."</p>
        </div>
    }
}

#[component]
pub fn LoginPage() -> impl IntoView {
    let auth = use_context::<AuthState>()
        .expect("AuthState must be provided");
    let navigate = use_navigate();
    
    let on_login = move |_| {
        auth.login();
        navigate("/dashboard", Default::default());
    };

    view! {
        <div class="page">
            <h1>"Login Page"</h1>
            <button class="btn btn-primary" on:click=on_login>
                "Login"
            </button>
        </div>
    }
}

#[component]
pub fn DashboardPage() -> impl IntoView {
    let auth = use_context::<AuthState>()
        .expect("AuthState must be provided");
    let navigate = use_navigate();
    
    let on_logout = move |_| {
        auth.logout();
        navigate("/", Default::default());
    };

    view! {
        <div class="page">
            <h1>"Dashboard"</h1>
            <p>"This is a protected page. Only authenticated users can see this."</p>
            <button class="btn btn-secondary" on:click=on_logout>
                "Logout"
            </button>
        </div>
    }
}

#[component]
pub fn ProfilePage() -> impl IntoView {
    view! {
        <div class="page">
            <h1>"Profile"</h1>
            <p>"This is your protected profile page."</p>
        </div>
    }
}

#[component]
pub fn AppWithProtectedRoutes() -> impl IntoView {
    let auth_state = AuthState::new();
    provide_context(auth_state.clone());

    view! {
        <Router>
            <nav class="navbar">
                <A href="/">"Home"</A>
                <Show
                    when=move || auth_state.is_authenticated()
                    fallback=move || view! {
                        <A href="/login">"Login"</A>
                    }
                >
                    <A href="/dashboard">"Dashboard"</A>
                    <A href="/profile">"Profile"</A>
                </Show>
            </nav>
            
            <main>
                <Routes>
                    <Route path="/" view=HomePage />
                    <Route path="/login" view=LoginPage />
                    <ProtectedRoute path="/dashboard" view=DashboardPage />
                    <ProtectedRoute path="/profile" view=ProfilePage />
                </Routes>
            </main>
        </Router>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["auth", "guard", "leptos", "protected-routes", "router"],
    },
    {
        "problem": """
Optimistic UI updates with rollback on error.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Todo {
    pub id: String,
    pub text: String,
    pub completed: bool,
}

async fn update_todo_on_server(todo: Todo) -> Result<Todo, String> {
    // Simulate API call with 90% success rate
    gloo_timers::future::TimeoutFuture::new(1000).await;
    
    if rand::random::<f64>() > 0.1 {
        Ok(todo)
    } else {
        Err("Server error occurred".to_string())
    }
}

async fn delete_todo_on_server(id: String) -> Result<(), String> {
    // Simulate API call
    gloo_timers::future::TimeoutFuture::new(1000).await;
    
    if rand::random::<f64>() > 0.1 {
        Ok(())
    } else {
        Err("Failed to delete todo".to_string())
    }
}

#[component]
pub fn OptimisticTodoList() -> impl IntoView {
    let (todos, set_todos) = create_signal(vec![
        Todo {
            id: "1".to_string(),
            text: "Learn Leptos".to_string(),
            completed: false,
        },
        Todo {
            id: "2".to_string(),
            text: "Build an app".to_string(),
            completed: false,
        },
    ]);
    
    let (error_message, set_error_message) = create_signal(None::<String>);
    
    let toggle_todo = move |todo_id: String| {
        // Store the previous state for rollback
        let previous_todos = todos.get();
        
        // Optimistically update the UI
        set_todos.update(|todos| {
            if let Some(todo) = todos.iter_mut().find(|t| t.id == todo_id) {
                todo.completed = !todo.completed;
            }
        });
        
        // Get the updated todo
        let updated_todo = todos
            .get()
            .iter()
            .find(|t| t.id == todo_id)
            .cloned()
            .expect("Todo not found");
        
        // Send update to server
        spawn_local(async move {
            match update_todo_on_server(updated_todo).await {
                Ok(_) => {
                    set_error_message.set(None);
                }
                Err(e) => {
                    // Rollback on error
                    set_todos.set(previous_todos);
                    set_error_message.set(Some(format!("Failed to update: {e}")));
                }
            }
        });
    };
    
    let delete_todo = move |todo_id: String| {
        // Store the previous state for rollback
        let previous_todos = todos.get();
        
        // Optimistically remove from UI
        set_todos.update(|todos| {
            todos.retain(|t| t.id != todo_id);
        });
        
        // Send delete to server
        let todo_id_clone = todo_id.clone();
        spawn_local(async move {
            match delete_todo_on_server(todo_id_clone).await {
                Ok(()) => {
                    set_error_message.set(None);
                }
                Err(e) => {
                    // Rollback on error
                    set_todos.set(previous_todos);
                    set_error_message.set(Some(format!("Failed to delete: {e}")));
                }
            }
        });
    };
    
    let add_todo = move |text: String| {
        let new_todo = Todo {
            id: uuid::Uuid::new_v4().to_string(),
            text,
            completed: false,
        };
        
        let previous_todos = todos.get();
        
        // Optimistically add to UI
        set_todos.update(|todos| {
            todos.push(new_todo.clone());
        });
        
        spawn_local(async move {
            match update_todo_on_server(new_todo).await {
                Ok(_) => {
                    set_error_message.set(None);
                }
                Err(e) => {
                    set_todos.set(previous_todos);
                    set_error_message.set(Some(format!("Failed to add: {e}")));
                }
            }
        });
    };

    view! {
        <div class="optimistic-todo-list">
            <h2>"Optimistic Todo List"</h2>
            <p class="text-muted">"Updates happen instantly, with automatic rollback on error"</p>
            
            <Show when=move || error_message.get().is_some() fallback=|| view! { <></> }>
                <div class="alert alert-danger">
                    {move || error_message.get().unwrap_or_default()}
                </div>
            </Show>
            
            <ul class="todo-list">
                <For
                    each=move || todos.get()
                    key=|todo| todo.id.clone()
                    children=move |todo: Todo| {
                        let todo_id = todo.id.clone();
                        let todo_id_delete = todo.id.clone();
                        
                        view! {
                            <li class="todo-item">
                                <input
                                    type="checkbox"
                                    prop:checked=todo.completed
                                    on:change=move |_| toggle_todo(todo_id.clone())
                                />
                                <span class={if todo.completed { "completed" } else { "" }}>
                                    {todo.text}
                                </span>
                                <button
                                    class="btn-delete"
                                    on:click=move |_| delete_todo(todo_id_delete.clone())
                                >
                                    "Delete"
                                </button>
                            </li>
                        }
                    }
                />
            </ul>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["async", "leptos", "optimistic-ui", "rollback", "state"],
    },
    {
        "problem": """
An error boundary component for graceful error handling.
""",
        "solution": r"""
use leptos::*;
use std::rc::Rc;

#[derive(Clone)]
pub struct ErrorBoundaryContext {
    error: RwSignal<Option<String>>,
}

impl ErrorBoundaryContext {
    pub fn new() -> Self {
        Self {
            error: create_rw_signal(None),
        }
    }
    
    pub fn set_error(&self, error: String) {
        self.error.set(Some(error));
    }
    
    pub fn clear_error(&self) {
        self.error.set(None);
    }
    
    pub fn has_error(&self) -> bool {
        self.error.get().is_some()
    }
    
    pub fn error(&self) -> ReadSignal<Option<String>> {
        self.error.read_only()
    }
}

impl Default for ErrorBoundaryContext {
    fn default() -> Self {
        Self::new()
    }
}

#[component]
pub fn ErrorBoundary(
    #[prop(optional)] fallback: Option<Box<dyn Fn(String) -> View>>,
    children: Children,
) -> impl IntoView {
    let error_context = ErrorBoundaryContext::new();
    provide_context(error_context.clone());
    
    let default_fallback = move |error: String| {
        view! {
            <div class="error-boundary">
                <div class="alert alert-danger">
                    <h3>"An error occurred"</h3>
                    <p>{error}</p>
                    <button
                        class="btn btn-primary"
                        on:click=move |_| error_context.clear_error()
                    >
                        "Try Again"
                    </button>
                </div>
            </div>
        }.into_view()
    };

    view! {
        <Show
            when=move || error_context.has_error()
            fallback=move || children().into_view()
        >
            {move || {
                if let Some(error) = error_context.error().get() {
                    if let Some(ref custom_fallback) = fallback {
                        custom_fallback(error)
                    } else {
                        default_fallback(error)
                    }
                } else {
                    view! { <></> }.into_view()
                }
            }}
        </Show>
    }
}

pub fn use_error_boundary() -> ErrorBoundaryContext {
    use_context::<ErrorBoundaryContext>()
        .expect("ErrorBoundaryContext must be provided via ErrorBoundary")
}

#[component]
fn RiskyComponent() -> impl IntoView {
    let error_boundary = use_error_boundary();
    let (count, set_count) = create_signal(0);
    
    let do_risky_operation = move |_| {
        let new_count = count.get() + 1;
        set_count.set(new_count);
        
        // Simulate an error every 3 clicks
        if new_count % 3 == 0 {
            error_boundary.set_error(format!("Error after {} clicks!", new_count));
        }
    };

    view! {
        <div class="risky-component">
            <h3>"Risky Component"</h3>
            <p>"Clicks: " {count}</p>
            <button class="btn btn-primary" on:click=do_risky_operation>
                "Do Risky Operation"
            </button>
            <p class="text-muted">"Will error every 3 clicks"</p>
        </div>
    }
}

#[component]
pub fn ErrorBoundaryExample() -> impl IntoView {
    view! {
        <div>
            <h2>"Error Boundary Example"</h2>
            
            <ErrorBoundary>
                <RiskyComponent />
            </ErrorBoundary>
            
            <div class="mt-4">
                <h3>"Custom Fallback Example"</h3>
                <ErrorBoundary
                    fallback=Some(Box::new(|error: String| {
                        view! {
                            <div class="custom-error">
                                <h4>"Custom Error Handler"</h4>
                                <p>"Something went wrong: " {error}</p>
                            </div>
                        }.into_view()
                    }))
                >
                    <RiskyComponent />
                </ErrorBoundary>
            </div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["error-boundary", "error-handling", "leptos"],
    },
    {
        "problem": """
A real-time chart component with live data updates.
""",
        "solution": r"""
use leptos::*;
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;
use web_sys::HtmlCanvasElement;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DataPoint {
    pub timestamp: f64,
    pub value: f64,
}

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = Chart)]
    type ChartJs;
    
    #[wasm_bindgen(constructor, js_namespace = Chart)]
    fn new(ctx: &web_sys::CanvasRenderingContext2d, config: &JsValue) -> ChartJs;
    
    #[wasm_bindgen(method)]
    fn update(this: &ChartJs);
    
    #[wasm_bindgen(method)]
    fn destroy(this: &ChartJs);
}

#[component]
pub fn RealtimeChart(
    #[prop(into)] title: String,
    #[prop(default = 50)] max_points: usize,
    #[prop(default = 1000)] update_interval_ms: u32,
) -> impl IntoView {
    let (data_points, set_data_points) = create_signal(Vec::<DataPoint>::new());
    let canvas_ref = create_node_ref::<html::Canvas>();
    let chart_instance = store_value(None::<ChartJs>);
    
    // Generate random data point
    let generate_data_point = move || {
        let timestamp = js_sys::Date::now();
        let value = (js_sys::Math::random() * 100.0).floor();
        DataPoint { timestamp, value }
    };
    
    // Initialize chart
    create_effect(move |_| {
        if let Some(canvas) = canvas_ref.get() {
            let canvas_element: &HtmlCanvasElement = &canvas;
            
            if let Ok(Some(ctx)) = canvas_element.get_context("2d") {
                let ctx: web_sys::CanvasRenderingContext2d = ctx.unchecked_into();
                
                let config = serde_json::json!({
                    "type": "line",
                    "data": {
                        "labels": [],
                        "datasets": [{
                            "label": title,
                            "data": [],
                            "borderColor": "rgb(75, 192, 192)",
                            "tension": 0.1
                        }]
                    },
                    "options": {
                        "responsive": true,
                        "maintainAspectRatio": false,
                        "scales": {
                            "x": {
                                "display": true,
                                "title": {
                                    "display": true,
                                    "text": "Time"
                                }
                            },
                            "y": {
                                "display": true,
                                "title": {
                                    "display": true,
                                    "text": "Value"
                                }
                            }
                        }
                    }
                });
                
                let config_js = serde_wasm_bindgen::to_value(&config)
                    .expect("Failed to serialize chart config");
                let chart = ChartJs::new(&ctx, &config_js);
                chart_instance.set_value(Some(chart));
            }
        }
    });
    
    // Update chart with new data
    create_effect(move |_| {
        let points = data_points.get();
        
        if let Some(chart) = chart_instance.get_value() {
            // Update chart data (simplified - in production use Chart.js API)
            chart.update();
        }
    });
    
    // Start data generation
    create_effect(move |_| {
        let interval = gloo_timers::callback::Interval::new(update_interval_ms, move || {
            set_data_points.update(|points| {
                points.push(generate_data_point());
                
                // Keep only the last N points
                if points.len() > max_points {
                    points.remove(0);
                }
            });
        });
        
        interval.forget();
    });
    
    // Cleanup on unmount
    on_cleanup(move || {
        if let Some(chart) = chart_instance.get_value() {
            chart.destroy();
        }
    });

    view! {
        <div class="realtime-chart-container">
            <div class="chart-header">
                <h3>{title.clone()}</h3>
                <div class="chart-stats">
                    <span>"Points: " {move || data_points.get().len()}</span>
                    <span class="separator">"|"</span>
                    <span>
                        "Latest: "
                        {move || {
                            data_points.get()
                                .last()
                                .map(|p| format!("{:.1}", p.value))
                                .unwrap_or_else(|| "N/A".to_string())
                        }}
                    </span>
                </div>
            </div>
            <div class="chart-wrapper">
                <canvas
                    node_ref=canvas_ref
                    width="400"
                    height="200"
                ></canvas>
            </div>
        </div>
    }
}

#[component]
pub fn ChartDashboard() -> impl IntoView {
    view! {
        <div class="chart-dashboard">
            <h2>"Real-time Data Dashboard"</h2>
            <div class="chart-grid">
                <RealtimeChart
                    title="CPU Usage".to_string()
                    max_points=30
                    update_interval_ms=2000
                />
                <RealtimeChart
                    title="Memory Usage".to_string()
                    max_points=30
                    update_interval_ms=2000
                />
                <RealtimeChart
                    title="Network Traffic".to_string()
                    max_points=50
                    update_interval_ms=1000
                />
            </div>
        </div>
    }
}
""",
        "category": "rust",
        "subcategory": "leptos",
        "tags": ["chart", "data-visualization", "leptos", "real-time"],
    },
]