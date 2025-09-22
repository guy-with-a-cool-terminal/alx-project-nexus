-- E-Commerce API Database Schema for dbdiagram.io
-- Multi-role system: Sellers, Consumers, Admins with analytics and email automation

Table users {
  id integer [primary key, increment]
  username varchar(150) [unique, not null]
  email varchar(254) [unique, not null]
  password varchar(128) [not null]
  first_name varchar(150)
  last_name varchar(150)
  role varchar(10) [not null, default: 'CONSUMER'] -- SELLER, CONSUMER, ADMIN
  phone_number varchar(20)
  address text
  store_name varchar(200) -- Only for SELLER role
  profile_picture varchar(200) -- Cloudinary URL
  is_email_verified boolean [default: false]
  is_active boolean [default: true]
  date_joined timestamp [default: `now()`]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table categories {
  id integer [primary key, increment]
  name varchar(100) [unique, not null]
  description text
  slug varchar(100) [unique] -- Auto-generated from name
  parent_category_id integer
  is_active boolean [default: true]
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table products {
  id integer [primary key, increment]
  name varchar(200) [not null]
  description text [not null]
  price decimal(10,2) [not null]
  sku varchar(100) [unique, not null]   -- Stock Keeping Unit
  category_id integer [not null]
  seller_id integer [not null]
  stock_quantity integer [default: 0, not null]
  is_active boolean [default: true]
  is_featured boolean [default: false]
  sales_count integer [default: 0] -- Auto-updated
  brand varchar(100)
  tags text -- JSON or comma-separated
  created_at timestamp [default: `now()`]
  updated_at timestamp [default: `now()`]
}

Table product_images {
  id integer [primary key, increment]
  product_id integer [not null]
  image varchar(200) [not null] -- Cloudinary URL
  alt_text varchar(255)
  is_primary boolean [default: false]
  created_at timestamp [default: `now()`]
}

Table product_sales {
  id integer [primary key, increment]
  product_id integer [not null]
  seller_id integer [not null]
  buyer_id integer -- Nullable for guest purchases
  quantity integer [not null, default: 1]
  price_at_sale decimal(10,2) [not null]
  sale_date timestamp [default: `now()`]
}

Table email_logs {
  id integer [primary key, increment]
  recipient_email varchar(254) [not null]
  recipient_user_id integer -- Link to user if registered
  email_type varchar(50) [not null] -- WELCOME, ANALYTICS_REPORT, LOW_STOCK
  subject varchar(255) [not null]
  status varchar(20) [default: 'PENDING'] -- PENDING, SENT, FAILED
  sent_at timestamp // When actually sent
  error_message text // If failed
  created_at timestamp [default: `now()`]
}

-- Relationships
Ref: categories.parent_category_id > categories.id
Ref: products.category_id > categories.id
Ref: products.seller_id > users.id
Ref: product_images.product_id > products.id
Ref: product_sales.product_id > products.id
Ref: product_sales.seller_id > users.id
Ref: product_sales.buyer_id > users.id
Ref: email_logs.recipient_user_id > users.id