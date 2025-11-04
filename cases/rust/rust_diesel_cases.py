RUST_DIESEL_CASES = [
    {
        "problem": """
A Diesel ORM setup with migrations, complex queries, transactions, and connection pooling.
""",
        "solution": """
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager, Pool};
use diesel::pg::PgConnection;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

// Define the schema
pub mod schema {
    table! {
        users (id) {
            id -> Int4,
            email -> Varchar,
            username -> Varchar,
            password_hash -> Varchar,
            is_active -> Bool,
            created_at -> Timestamptz,
            updated_at -> Timestamptz,
        }
    }

    table! {
        posts (id) {
            id -> Int4,
            user_id -> Int4,
            title -> Varchar,
            content -> Text,
            published -> Bool,
            created_at -> Timestamptz,
            updated_at -> Timestamptz,
        }
    }

    table! {
        comments (id) {
            id -> Int4,
            post_id -> Int4,
            user_id -> Int4,
            content -> Text,
            created_at -> Timestamptz,
        }
    }

    joinable!(posts -> users (user_id));
    joinable!(comments -> posts (post_id));
    joinable!(comments -> users (user_id));

    allow_tables_to_appear_in_same_query!(users, posts, comments);
}

use schema::{users, posts, comments};

// Models
#[derive(Debug, Queryable, Identifiable, Serialize)]
#[diesel(table_name = users)]
pub struct User {
    pub id: i32,
    pub email: String,
    pub username: String,
    #[serde(skip_serializing)]
    pub password_hash: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = users)]
pub struct NewUser<'a> {
    pub email: &'a str,
    pub username: &'a str,
    pub password_hash: &'a str,
}

#[derive(Debug, AsChangeset)]
#[diesel(table_name = users)]
pub struct UpdateUser<'a> {
    pub email: Option<&'a str>,
    pub username: Option<&'a str>,
    pub is_active: Option<bool>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Queryable, Identifiable, Associations, Serialize)]
#[diesel(belongs_to(User))]
#[diesel(table_name = posts)]
pub struct Post {
    pub id: i32,
    pub user_id: i32,
    pub title: String,
    pub content: String,
    pub published: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = posts)]
pub struct NewPost<'a> {
    pub user_id: i32,
    pub title: &'a str,
    pub content: &'a str,
    pub published: bool,
}

#[derive(Debug, Queryable, Identifiable, Associations, Serialize)]
#[diesel(belongs_to(Post))]
#[diesel(belongs_to(User))]
#[diesel(table_name = comments)]
pub struct Comment {
    pub id: i32,
    pub post_id: i32,
    pub user_id: i32,
    pub content: String,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Insertable)]
#[diesel(table_name = comments)]
pub struct NewComment<'a> {
    pub post_id: i32,
    pub user_id: i32,
    pub content: &'a str,
}

// Custom result type with joined data
#[derive(Debug, Serialize)]
pub struct PostWithAuthor {
    pub post: Post,
    pub author: User,
}

#[derive(Debug, Serialize)]
pub struct PostWithDetails {
    pub post: Post,
    pub author: User,
    pub comment_count: i64,
}

// Connection pool type
pub type DbPool = Pool<ConnectionManager<PgConnection>>;
pub type DbConnection = r2d2::PooledConnection<ConnectionManager<PgConnection>>;

// Initialize connection pool
pub fn establish_connection_pool(database_url: &str) -> Result<DbPool, r2d2::Error> {
    let manager = ConnectionManager::<PgConnection>::new(database_url);
    Pool::builder()
        .max_size(15)
        .connection_timeout(std::time::Duration::from_secs(30))
        .build(manager)
}

// Repository pattern for users
pub struct UserRepository;

impl UserRepository {
    pub fn create(
        conn: &mut PgConnection,
        email: &str,
        username: &str,
        password: &str,
    ) -> QueryResult<User> {
        let password_hash = Self::hash_password(password);
        let new_user = NewUser {
            email,
            username,
            password_hash: &password_hash,
        };

        diesel::insert_into(users::table)
            .values(&new_user)
            .get_result(conn)
    }

    pub fn find_by_id(conn: &mut PgConnection, user_id: i32) -> QueryResult<User> {
        users::table.find(user_id).first(conn)
    }

    pub fn find_by_email(conn: &mut PgConnection, email: &str) -> QueryResult<User> {
        users::table
            .filter(users::email.eq(email))
            .first(conn)
    }

    pub fn find_by_username(conn: &mut PgConnection, username: &str) -> QueryResult<User> {
        users::table
            .filter(users::username.eq(username))
            .first(conn)
    }

    pub fn list(
        conn: &mut PgConnection,
        limit: i64,
        offset: i64,
    ) -> QueryResult<Vec<User>> {
        users::table
            .order(users::created_at.desc())
            .limit(limit)
            .offset(offset)
            .load(conn)
    }

    pub fn update(
        conn: &mut PgConnection,
        user_id: i32,
        update_data: UpdateUser,
    ) -> QueryResult<User> {
        diesel::update(users::table.find(user_id))
            .set(&update_data)
            .get_result(conn)
    }

    pub fn delete(conn: &mut PgConnection, user_id: i32) -> QueryResult<usize> {
        diesel::delete(users::table.find(user_id)).execute(conn)
    }

    pub fn count_active_users(conn: &mut PgConnection) -> QueryResult<i64> {
        users::table
            .filter(users::is_active.eq(true))
            .count()
            .get_result(conn)
    }

    fn hash_password(password: &str) -> String {
        // In production, use a proper password hashing library
        format!("hashed_{}", password)
    }
}

// Repository for posts with complex queries
pub struct PostRepository;

impl PostRepository {
    pub fn create(
        conn: &mut PgConnection,
        user_id: i32,
        title: &str,
        content: &str,
        published: bool,
    ) -> QueryResult<Post> {
        let new_post = NewPost {
            user_id,
            title,
            content,
            published,
        };

        diesel::insert_into(posts::table)
            .values(&new_post)
            .get_result(conn)
    }

    pub fn find_with_author(
        conn: &mut PgConnection,
        post_id: i32,
    ) -> QueryResult<PostWithAuthor> {
        let (post, author) = posts::table
            .inner_join(users::table)
            .filter(posts::id.eq(post_id))
            .first::<(Post, User)>(conn)?;

        Ok(PostWithAuthor { post, author })
    }

    pub fn find_with_details(
        conn: &mut PgConnection,
        post_id: i32,
    ) -> QueryResult<PostWithDetails> {
        let (post, author) = posts::table
            .inner_join(users::table)
            .filter(posts::id.eq(post_id))
            .first::<(Post, User)>(conn)?;

        let comment_count = Comment::belonging_to(&post)
            .count()
            .get_result(conn)?;

        Ok(PostWithDetails {
            post,
            author,
            comment_count,
        })
    }

    pub fn find_by_user(
        conn: &mut PgConnection,
        user_id: i32,
        published_only: bool,
    ) -> QueryResult<Vec<Post>> {
        let mut query = posts::table
            .filter(posts::user_id.eq(user_id))
            .into_boxed();

        if published_only {
            query = query.filter(posts::published.eq(true));
        }

        query.order(posts::created_at.desc()).load(conn)
    }

    pub fn search(
        conn: &mut PgConnection,
        search_term: &str,
        limit: i64,
    ) -> QueryResult<Vec<PostWithAuthor>> {
        let search_pattern = format!("%{}%", search_term);

        posts::table
            .inner_join(users::table)
            .filter(
                posts::title.ilike(&search_pattern)
                    .or(posts::content.ilike(&search_pattern))
            )
            .filter(posts::published.eq(true))
            .order(posts::created_at.desc())
            .limit(limit)
            .load::<(Post, User)>(conn)
            .map(|results| {
                results
                    .into_iter()
                    .map(|(post, author)| PostWithAuthor { post, author })
                    .collect()
            })
    }

    pub fn published_posts_with_comments(
        conn: &mut PgConnection,
    ) -> QueryResult<Vec<(Post, Vec<Comment>)>> {
        let posts = posts::table
            .filter(posts::published.eq(true))
            .order(posts::created_at.desc())
            .load::<Post>(conn)?;

        let comments = Comment::belonging_to(&posts)
            .load::<Comment>(conn)?
            .grouped_by(&posts);

        Ok(posts.into_iter().zip(comments).collect())
    }
}

// Transaction example
pub struct BlogService {
    pool: DbPool,
}

impl BlogService {
    pub fn new(pool: DbPool) -> Self {
        Self { pool }
    }

    pub fn create_user_with_post(
        &self,
        email: &str,
        username: &str,
        password: &str,
        post_title: &str,
        post_content: &str,
    ) -> QueryResult<(User, Post)> {
        let mut conn = self.pool.get().expect("Failed to get connection");

        conn.transaction(|conn| {
            let user = UserRepository::create(conn, email, username, password)?;

            let post = PostRepository::create(
                conn,
                user.id,
                post_title,
                post_content,
                false,
            )?;

            Ok((user, post))
        })
    }

    pub fn publish_post_batch(
        &self,
        post_ids: &[i32],
    ) -> QueryResult<usize> {
        let mut conn = self.pool.get().expect("Failed to get connection");

        diesel::update(posts::table)
            .filter(posts::id.eq_any(post_ids))
            .set(posts::published.eq(true))
            .execute(&mut conn)
    }
}

// Example usage
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgres://localhost/mydb".to_string());

    let pool = establish_connection_pool(&database_url)?;

    let service = BlogService::new(pool.clone());

    // Create user with initial post
    let (user, post) = service.create_user_with_post(
        "user@example.com",
        "johndoe",
        "password123",
        "My First Post",
        "This is the content of my first post.",
    )?;

    println!("Created user: {} with post: {}", user.username, post.title);

    // Search for posts
    let mut conn = pool.get()?;
    let results = PostRepository::search(&mut conn, "first", 10)?;

    for result in results {
        println!(
            "Found post '{}' by {}",
            result.post.title, result.author.username
        );
    }

    Ok(())
}
""",
        "category": "rust",
        "subcategory": "diesel",
        "tags": [
            "auth",
            "database",
            "diesel",
            "filter",
            "form",
            "hashing",
            "migration",
        ],
    }
]
